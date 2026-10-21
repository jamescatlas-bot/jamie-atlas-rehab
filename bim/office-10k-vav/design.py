"""
Design basis and geometry for a 10,000 sf single-storey office with a central
air handler, interior VAV boxes and series fan-powered boxes on the perimeter.

This module is the single source of truth.  Everything else (IFC builder,
Revit script, plan drawing, schedules) reads the dictionaries produced by
``build()``.

Units: feet, cfm.  Origin at the south-west corner, X east, Y north, Z up.
"""
import json
import math
import os

# --------------------------------------------------------------------------
# Building envelope
# --------------------------------------------------------------------------
BLDG_X = 100.0
BLDG_Y = 100.0
LEVEL_1 = 0.0
ROOF = 14.0
CEILING = 9.0
Z_DUCT = 11.5           # centreline of all horizontal ductwork
Z_DIFFUSER_TOP = 9.5    # top of the lay-in diffuser (neck connection)
EXT_WALL_T = 1.0
INT_WALL_T = 0.5
SLAB_T = 0.5
ROOF_T = 0.5
GRID_SPACING = 25.0

MECH = dict(x0=38.0, x1=62.0, y0=54.0, y1=70.0)   # mechanical room M-101


def build():
    model = dict(
        project="10,000 sf Office - Central AHU with VAV / Fan-Powered Boxes",
        units="feet",
        building=_building(),
        zones=_zones(),
        equipment=[],
        runs=[],
        terminals=[],
    )
    _mechanical(model)
    _totals(model)
    return model


# --------------------------------------------------------------------------
# Architecture
# --------------------------------------------------------------------------
def _building():
    walls = []
    h = EXT_WALL_T / 2.0
    ext = [
        ("W-S", (0, h), (BLDG_X, h)),
        ("W-E", (BLDG_X - h, 0), (BLDG_X - h, BLDG_Y)),
        ("W-N", (BLDG_X, BLDG_Y - h), (0, BLDG_Y - h)),
        ("W-W", (h, BLDG_Y), (h, 0)),
    ]
    for name, a, b in ext:
        walls.append(dict(id=name, kind="exterior", start=a, end=b,
                          thickness=EXT_WALL_T, height=ROOF, base=LEVEL_1))
    m = MECH
    interior = [
        ("W-M1", (m["x0"], m["y0"]), (m["x1"], m["y0"])),
        ("W-M2", (m["x1"], m["y0"]), (m["x1"], m["y1"])),
        ("W-M3", (m["x1"], m["y1"]), (m["x0"], m["y1"])),
        ("W-M4", (m["x0"], m["y1"]), (m["x0"], m["y0"])),
    ]
    for name, a, b in interior:
        walls.append(dict(id=name, kind="interior", start=a, end=b,
                          thickness=INT_WALL_T, height=ROOF, base=LEVEL_1))

    columns = []
    n = 0
    for i in range(5):
        for j in range(5):
            n += 1
            columns.append(dict(id="C-%02d" % n, x=i * GRID_SPACING,
                                y=j * GRID_SPACING, size=1.0, height=ROOF))

    grids = [dict(id=chr(ord("A") + i), start=(i * GRID_SPACING, -5),
                  end=(i * GRID_SPACING, BLDG_Y + 5)) for i in range(5)]
    grids += [dict(id=str(j + 1), start=(-5, j * GRID_SPACING),
                   end=(BLDG_X + 5, j * GRID_SPACING)) for j in range(5)]

    outline = [(0, 0), (BLDG_X, 0), (BLDG_X, BLDG_Y), (0, BLDG_Y)]
    mech_rect = [(m["x0"], m["y0"]), (m["x1"], m["y0"]),
                 (m["x1"], m["y1"]), (m["x0"], m["y1"])]
    # ceiling = everything except the mechanical room, as four rectangles
    ceiling = [
        [(0, 0), (BLDG_X, 0), (BLDG_X, m["y0"]), (0, m["y0"])],
        [(0, m["y1"]), (BLDG_X, m["y1"]), (BLDG_X, BLDG_Y), (0, BLDG_Y)],
        [(0, m["y0"]), (m["x0"], m["y0"]), (m["x0"], m["y1"]), (0, m["y1"])],
        [(m["x1"], m["y0"]), (BLDG_X, m["y0"]), (BLDG_X, m["y1"]), (m["x1"], m["y1"])],
    ]
    return dict(
        size=(BLDG_X, BLDG_Y), area=BLDG_X * BLDG_Y,
        levels=[dict(name="Level 1", elevation=LEVEL_1),
                dict(name="Roof", elevation=ROOF)],
        ceiling_height=CEILING, duct_centreline=Z_DUCT,
        walls=walls, columns=columns, grids=grids,
        floor=dict(outline=outline, thickness=SLAB_T, top=LEVEL_1),
        roof=dict(outline=outline, thickness=ROOF_T, bottom=ROOF),
        ceilings=[dict(outline=c, elevation=CEILING, thickness=0.05) for c in ceiling],
        mech_room=mech_rect,
    )


# --------------------------------------------------------------------------
# Thermal zones (one per terminal box)
# --------------------------------------------------------------------------
def _zones():
    m = MECH
    Z = []

    def z(number, name, box, kind, poly, cfm):
        Z.append(dict(number=number, name=name, box=box, kind=kind,
                      polygon=poly, area=_area(poly), supply_cfm=cfm))

    # perimeter, 20 ft deep; corners belong to the north / south zones
    z("101", "North Office West", "FPB-N1", "perimeter", [(0, 80), (50, 80), (50, 100), (0, 100)], 1050)
    z("102", "North Office East", "FPB-N2", "perimeter", [(50, 80), (100, 80), (100, 100), (50, 100)], 1050)
    z("103", "South Office West", "FPB-S1", "perimeter", [(0, 0), (50, 0), (50, 20), (0, 20)], 1050)
    z("104", "South Office East", "FPB-S2", "perimeter", [(50, 0), (100, 0), (100, 20), (50, 20)], 1050)
    z("105", "East Office South", "FPB-E1", "perimeter", [(80, 20), (100, 20), (100, 50), (80, 50)], 750)
    z("106", "East Office North", "FPB-E2", "perimeter", [(80, 50), (100, 50), (100, 80), (80, 80)], 750)
    z("107", "West Office South", "FPB-W1", "perimeter", [(0, 20), (20, 20), (20, 50), (0, 50)], 750)
    z("108", "West Office North", "FPB-W2", "perimeter", [(0, 50), (20, 50), (20, 80), (0, 80)], 750)
    # interior
    z("109", "Interior NW Open Office", "VAV-1", "interior",
      [(20, 50), (50, 50), (50, m["y0"]), (m["x0"], m["y0"]), (m["x0"], m["y1"]), (50, m["y1"]), (50, 80), (20, 80)], 700)
    z("110", "Interior NE Open Office", "VAV-2", "interior",
      [(50, 50), (80, 50), (80, 80), (50, 80), (50, m["y1"]), (m["x1"], m["y1"]), (m["x1"], m["y0"]), (50, m["y0"])], 700)
    z("111", "Interior SW Open Office", "VAV-3", "interior", [(20, 20), (50, 20), (50, 50), (20, 50)], 900)
    z("112", "Interior SE Open Office", "VAV-4", "interior", [(50, 20), (80, 20), (80, 50), (50, 50)], 900)
    z("M-101", "Mechanical Room", "AHU-1", "mechanical",
      [(m["x0"], m["y0"]), (m["x1"], m["y0"]), (m["x1"], m["y1"]), (m["x0"], m["y1"])], 0)
    return Z


def _area(poly):
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


# --------------------------------------------------------------------------
# Mechanical
# --------------------------------------------------------------------------
def _mechanical(model):
    eq = model["equipment"]
    runs = model["runs"]
    terms = model["terminals"]
    Z = Z_DUCT

    def equipment(tag, kind, centre, length, width, height, flow_dir, **props):
        dx, dy = flow_dir
        cx, cy, cz = centre
        e = dict(tag=tag, kind=kind, centre=centre, length=length, width=width,
                 height=height, flow_dir=flow_dir,
                 rotation_deg=math.degrees(math.atan2(dy, dx)),
                 inlet=(cx - dx * length / 2.0, cy - dy * length / 2.0, cz),
                 outlet=(cx + dx * length / 2.0, cy + dy * length / 2.0, cz))
        e.update(props)
        eq.append(e)
        return e

    def run(rid, system, name, pts, size, cfm, pressure="medium", **kw):
        pts = [tuple(float(v) for v in (p if len(p) == 3 else (p[0], p[1], Z))) for p in pts]
        r = dict(id=rid, system=system, name=name, points=pts, cfm=cfm,
                 pressure_class=pressure)
        if size[0] == "round":
            r.update(shape="round", diameter_in=size[1])
        else:
            r.update(shape="rect", width_in=size[0], height_in=size[1])
        r.update(kw)
        r["length_ft"] = sum(_dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        runs.append(r)
        return r

    def diffuser(tag, x, y, cfm, neck_in, served_by):
        terms.append(dict(tag=tag, kind="supply_diffuser", x=x, y=y, z=CEILING,
                          cfm=cfm, face_in=24, neck_in=neck_in, served_by=served_by))

    # ---- air handler ------------------------------------------------------
    equipment("AHU-1", "AHU", (50, 62, 0), 16, 6, 7, (1, 0),
              supply_cfm=8500, outside_air_cfm=1500, cooling_tons=22,
              heating_mbh=250, external_sp_in=2.5, fan_hp=10,
              description="Indoor central station AHU, VAV, DX or CHW coil, "
                          "economizer, MERV-13 filtration")
    equipment("L-1", "LOUVER", (47.5, 99.5, Z), 1.0, 3, 2.5, (0, -1),
              outside_air_cfm=1500, description="Drainable OA intake louver 36x30 on north wall")

    # ---- supply mains (medium pressure) -----------------------------------
    run("SA-01", "SA", "AHU-1 supply riser and main", [(54, 62, 7.0), (54, 62, Z), (54, 47, Z)], (36, 24), 8000, from_="AHU-1")
    run("SA-02", "SA", "Main east", [(54, 47), (72, 47)], (28, 18), 4000)
    run("SA-03", "SA", "Main west", [(54, 47), (28, 47)], (28, 18), 4000)
    run("SA-04", "SA", "Main east (reduced)", [(72, 47), (80, 47)], (22, 16), 2400)
    run("SA-05", "SA", "Main west (reduced)", [(28, 47), (20, 47)], (22, 16), 2400)
    run("SA-06", "SA", "East leg north", [(80, 47), (80, 72)], (14, 12), 1200)
    run("SA-07", "SA", "East leg south", [(80, 47), (80, 28)], (14, 12), 1200)
    run("SA-08", "SA", "East leg north to FPB-N2", [(80, 72), (80, 80), (70, 80), (70, 83.5)], (12, 10), 700, to="FPB-N2")
    run("SA-09", "SA", "East leg south to FPB-S2", [(80, 28), (80, 20), (70, 20), (70, 16.5)], (12, 10), 700, to="FPB-S2")
    run("SA-10", "SA", "West leg north", [(20, 47), (20, 72)], (14, 12), 1200)
    run("SA-11", "SA", "West leg south", [(20, 47), (20, 28)], (14, 12), 1200)
    run("SA-12", "SA", "West leg north to FPB-N1", [(20, 72), (20, 80), (30, 80), (30, 83.5)], (12, 10), 700, to="FPB-N1")
    run("SA-13", "SA", "West leg south to FPB-S1", [(20, 28), (20, 20), (30, 20), (30, 16.5)], (12, 10), 700, to="FPB-S1")
    run("SA-14", "SA", "Tap to FPB-E2", [(80, 70), (83.5, 70)], (12, 10), 500, tap_on="SA-06", to="FPB-E2")
    run("SA-15", "SA", "Tap to FPB-E1", [(80, 30), (83.5, 30)], (12, 10), 500, tap_on="SA-07", to="FPB-E1")
    run("SA-16", "SA", "Tap to FPB-W2", [(20, 70), (16.5, 70)], (12, 10), 500, tap_on="SA-10", to="FPB-W2")
    run("SA-17", "SA", "Tap to FPB-W1", [(20, 30), (16.5, 30)], (12, 10), 500, tap_on="SA-11", to="FPB-W1")
    run("SA-18", "SA", "Tap to VAV-2", [(70, 47), (70, 52.5)], (14, 12), 700, tap_on="SA-02", to="VAV-2")
    run("SA-19", "SA", "Tap to VAV-4", [(66, 47), (66, 41.5)], (16, 12), 900, tap_on="SA-02", to="VAV-4")
    run("SA-20", "SA", "Tap to VAV-1", [(30, 47), (30, 52.5)], (14, 12), 700, tap_on="SA-03", to="VAV-1")
    run("SA-21", "SA", "Tap to VAV-3", [(34, 47), (34, 41.5)], (16, 12), 900, tap_on="SA-03", to="VAV-3")

    # ---- return and outside air ------------------------------------------
    run("RA-01", "RA", "Plenum return to AHU-1", [(36, 62, Z), (44, 62, Z), (44, 62, 7.0)], (36, 24), 7000,
        pressure="low", to="AHU-1", from_="PLENUM")
    run("OA-01", "OA", "Outside air from L-1 to AHU-1", [(47.5, 99.0, Z), (47.5, 62, Z), (47.5, 62, 7.0)], (20, 14), 1500,
        pressure="low", from_="L-1", to="AHU-1")

    # ---- interior VAV boxes (cooling only) --------------------------------
    # tag, centre, flow dir, cfm, diffuser rows (y of taps), diffuser x offsets
    vav = [
        ("VAV-1", (30, 54), (0, 1), 700, "109"),
        ("VAV-2", (70, 54), (0, 1), 700, "110"),
        ("VAV-3", (34, 40), (0, -1), 900, "111"),
        ("VAV-4", (66, 40), (0, -1), 900, "112"),
    ]
    sd = 0
    for tag, (cx, cy), (dx, dy), cfm, zone in vav:
        e = equipment(tag, "VAV", (cx, cy, Z), 3.0, 2.0, 1.25, (dx, dy),
                      primary_cfm=cfm, min_cfm=int(cfm * 0.3), inlet_in=12, zone=zone,
                      description="Single-duct pressure-independent VAV terminal, cooling only")
        ox, oy, oz = e["outlet"]
        n = tag[-1]
        # header: 5.5 ft at full size, then 6.5 ft reduced; taps 2.5 ft and 10.5 ft past outlet
        p1 = (ox + dx * 5.5, oy + dy * 5.5)
        p2 = (ox + dx * 12.0, oy + dy * 12.0)
        h1 = run("LP-%s1" % n, "SA", "%s discharge header" % tag, [(ox, oy), p1], (14, 12) if cfm <= 800 else (16, 12), cfm, pressure="low", from_=tag)
        h2 = run("LP-%s2" % n, "SA", "%s discharge header (reduced)" % tag, [p1, p2], (10, 10) if cfm <= 800 else (12, 10), cfm // 2, pressure="low")
        per = cfm // 4
        for k, (hdr, off) in enumerate([(h1, 2.5), (h2, 10.5)]):
            tx, ty = ox + dx * off, oy + dy * off
            for side in (-6, 6):
                sd += 1
                tag_sd = "SD-%02d" % sd
                px, py = tx + side, ty
                run("LP-%s%d" % (n, 3 + k * 2 + (0 if side < 0 else 1)), "SA",
                    "Runout to %s" % tag_sd, [(tx, ty, Z), (px, py, Z), (px, py, Z_DIFFUSER_TOP)],
                    ("round", 10), per, pressure="low", tap_on=hdr["id"], to=tag_sd)
                diffuser(tag_sd, px, py, per, 10, tag)

    # ---- perimeter series fan-powered boxes --------------------------------
    # tag, centre, flow dir (box discharge direction), primary, fan, zone,
    # header length to the cross header, cross header axis, leg ends, diffuser positions
    fpb = [
        ("FPB-N1", (30, 86), (0, 1), 700, 1050, "101", 94, (9, 45), (10, 22, 34, 44)),
        ("FPB-N2", (70, 86), (0, 1), 700, 1050, "102", 94, (55, 91), (56, 68, 78, 90)),
        ("FPB-S1", (30, 14), (0, -1), 700, 1050, "103", 6, (9, 45), (10, 22, 34, 44)),
        ("FPB-S2", (70, 14), (0, -1), 700, 1050, "104", 6, (55, 91), (56, 68, 78, 90)),
        ("FPB-E1", (86, 30), (1, 0), 500, 750, "105", 94, (9, 45), (10, 22, 34, 44)),
        ("FPB-E2", (86, 70), (1, 0), 500, 750, "106", 94, (55, 91), (56, 68, 78, 90)),
        ("FPB-W1", (14, 30), (-1, 0), 500, 750, "107", 6, (9, 45), (10, 22, 34, 44)),
        ("FPB-W2", (14, 70), (-1, 0), 500, 750, "108", 6, (55, 91), (56, 68, 78, 90)),
    ]
    for tag, (cx, cy), (dx, dy), prim, fan, zone, hdr_line, legs, diffs in fpb:
        e = equipment(tag, "FPB", (cx, cy, Z), 5.0, 3.5, 1.5, (dx, dy),
                      primary_cfm=prim, fan_cfm=fan, min_primary_cfm=int(prim * 0.3),
                      inlet_in=10 if prim <= 500 else 12, heat_kw=5 if prim <= 500 else 7, zone=zone,
                      description="Series fan-powered terminal with electric reheat, ECM fan, plenum induction inlet")
        ox, oy, oz = e["outlet"]
        along_x = (dy != 0)          # box discharges N/S -> cross header runs E/W
        n = tag[-2:]
        hdr_size = (16, 10) if fan > 800 else (14, 10)
        leg_size = (12, 10) if fan > 800 else (10, 10)
        neck = 10 if fan > 800 else 8
        if along_x:
            node = (ox, hdr_line)
            run("LP-%s0" % n, "SA", "%s discharge header" % tag, [(ox, oy), node], hdr_size, fan, pressure="low", from_=tag)
            lw = run("LP-%sW" % n, "SA", "%s west leg" % tag, [node, (legs[0], hdr_line)], leg_size, fan // 2, pressure="low")
            le = run("LP-%sE" % n, "SA", "%s east leg" % tag, [node, (legs[1], hdr_line)], leg_size, fan // 2, pressure="low")
            pos = [(x, hdr_line) for x in diffs]
            owner = lambda p: lw if p[0] < node[0] else le
        else:
            node = (hdr_line, oy)
            run("LP-%s0" % n, "SA", "%s discharge header" % tag, [(ox, oy), node], hdr_size, fan, pressure="low", from_=tag)
            lw = run("LP-%sS" % n, "SA", "%s south leg" % tag, [node, (hdr_line, legs[0])], leg_size, fan // 2, pressure="low")
            le = run("LP-%sN" % n, "SA", "%s north leg" % tag, [node, (hdr_line, legs[1])], leg_size, fan // 2, pressure="low")
            pos = [(hdr_line, y) for y in diffs]
            owner = lambda p: lw if p[1] < node[1] else le
        per = fan // 4
        for k, (px, py) in enumerate(pos):
            sd += 1
            tag_sd = "SD-%02d" % sd
            run("LP-%s%d" % (n, k + 1), "SA", "Drop to %s" % tag_sd,
                [(px, py, Z), (px, py, Z_DIFFUSER_TOP)], ("round", neck), per,
                pressure="low", tap_on=owner((px, py))["id"], to=tag_sd)
            diffuser(tag_sd, px, py, per, neck, tag)

    # ---- plenum return grilles -------------------------------------------
    rg = [(12, 12), (40, 12), (60, 12), (88, 12), (12, 40), (40, 40), (60, 40), (88, 40),
          (12, 60), (34, 74), (66, 74), (88, 60), (12, 88), (40, 88), (60, 88), (88, 88)]
    for i, (x, y) in enumerate(rg):
        terms.append(dict(tag="RG-%02d" % (i + 1), kind="return_grille", x=x, y=y, z=CEILING,
                          cfm=440, face_in=24, neck_in=0, served_by="PLENUM"))


def _dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def _totals(model):
    t = dict(
        supply_primary_cfm=sum(e.get("primary_cfm", 0) for e in model["equipment"] if e["kind"] in ("VAV", "FPB")),
        diffuser_cfm=sum(x["cfm"] for x in model["terminals"] if x["kind"] == "supply_diffuser"),
        return_grille_cfm=sum(x["cfm"] for x in model["terminals"] if x["kind"] == "return_grille"),
        duct_length_ft=round(sum(r["length_ft"] for r in model["runs"]), 1),
        supply_diffusers=sum(1 for x in model["terminals"] if x["kind"] == "supply_diffuser"),
        return_grilles=sum(1 for x in model["terminals"] if x["kind"] == "return_grille"),
        vav_boxes=sum(1 for e in model["equipment"] if e["kind"] == "VAV"),
        fan_powered_boxes=sum(1 for e in model["equipment"] if e["kind"] == "FPB"),
        zone_area_sf=round(sum(z["area"] for z in model["zones"]), 1),
    )
    model["totals"] = t


def velocity_fpm(run):
    if run["shape"] == "round":
        a = math.pi * (run["diameter_in"] / 24.0) ** 2
    else:
        a = run["width_in"] * run["height_in"] / 144.0
    return run["cfm"] / a


def size_label(run):
    if run["shape"] == "round":
        return '%d" dia' % run["diameter_in"]
    return "%dx%d" % (run["width_in"], run["height_in"])


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    m = build()
    with open(os.path.join(here, "design.json"), "w") as f:
        json.dump(m, f, indent=1)
    print(json.dumps(m["totals"], indent=1))
