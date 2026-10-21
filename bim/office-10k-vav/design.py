"""
Design basis and geometry for a 10,000 sf single-storey office with a central
air handler, interior VAV boxes and series fan-powered boxes on the perimeter.

Perimeter program (rev 2): private offices along all four facades, a conference
room at each corner, a 5 ft corridor behind the 15 ft deep rooms, open office
in the interior.  Up on the plan is north.  Airflows carry Denver, Colorado
exposure factors (south +50%, west +35%, east +25% over north).

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

ROOM_DEPTH = 15.0        # perimeter rooms, from the exterior face
CORRIDOR = 5.0           # corridor behind the rooms (part of the open office zone)
CONF = 20.0              # corner conference rooms, 20 x 20
OFFICE_W = 12.0          # 5 offices between the corner rooms on each facade
RING = 23.0              # medium-pressure ring main, distance from the exterior face

# Denver, Colorado: cooling airflow per sf of zone, by exposure (fan air for FPB zones)
CFM_SF = dict(N=1.00, E=1.25, S=1.50, W=1.35, INTERIOR=0.90)
CONF_BASE = 1.20                     # conference rooms, occupancy driven, before exposure
FPB_INDUCTION = 1.5                  # series box: fan cfm / primary cfm
HEAT_BTUH_SF = 25.0                  # perimeter electric reheat basis

# ----- facade frames ---------------------------------------------------------
# Each facade is laid out once in local coordinates (u along the facade from its
# left end when viewed from inside, v = depth from the exterior face) and mapped
# to the plan.  The corner room at u 0..20 belongs to that facade.
FACADES = {
    "N": dict(map=lambda u, v: (u, BLDG_Y - v), dir=lambda du, dv: (du, -dv), corner="NW", corner_exp="W"),
    "E": dict(map=lambda u, v: (BLDG_X - v, BLDG_Y - u), dir=lambda du, dv: (-dv, -du), corner="NE", corner_exp="N"),
    "S": dict(map=lambda u, v: (BLDG_X - u, v), dir=lambda du, dv: (-du, dv), corner="SE", corner_exp="E"),
    "W": dict(map=lambda u, v: (v, u), dir=lambda du, dv: (dv, du), corner="SW", corner_exp="S"),
}
FACADE_ORDER = ["N", "E", "S", "W"]
OFFICE_U = [20 + OFFICE_W * i for i in range(5)]          # left edges 20,32,44,56,68
OFFICE_GROUPS = [("1", [0, 1, 2]), ("2", [3, 4])]         # box 1 serves offices 1-3, box 2 serves 4-5


def build():
    model = dict(
        project="10,000 sf Office - Central AHU with VAV / Fan-Powered Boxes (perimeter offices, rev 2)",
        units="feet",
        north="plan up",
        climate="Denver, Colorado (ASHRAE 5B): south +50%, west +35%, east +25% airflow over north",
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
        ("W-M1", (m["x0"], m["y0"]), (m["x1"], m["y0"]), ROOF),
        ("W-M2", (m["x1"], m["y0"]), (m["x1"], m["y1"]), ROOF),
        ("W-M3", (m["x1"], m["y1"]), (m["x0"], m["y1"]), ROOF),
        ("W-M4", (m["x0"], m["y1"]), (m["x0"], m["y0"]), ROOF),
    ]
    # perimeter partitions, to the ceiling (plenum return above)
    for f in FACADE_ORDER:
        mp = FACADES[f]["map"]
        n = 0
        for u in OFFICE_U + [OFFICE_U[-1] + OFFICE_W]:
            n += 1
            interior.append(("W-%s-D%d" % (f, n), mp(u, EXT_WALL_T), mp(u, ROOM_DEPTH), CEILING))
        interior.append(("W-%s-COR" % f, mp(CONF, ROOM_DEPTH), mp(BLDG_X - CONF, ROOM_DEPTH), CEILING))
        interior.append(("W-%s-C1" % f, mp(CONF, EXT_WALL_T), mp(CONF, CONF), CEILING))       # conference side wall
        interior.append(("W-%s-C2" % f, mp(CONF, CONF), mp(EXT_WALL_T, CONF), CEILING))       # conference back wall
    for name, a, b, hgt in interior:
        walls.append(dict(id=name, kind="interior", start=tuple(round(c, 3) for c in a), end=tuple(round(c, 3) for c in b),
                          thickness=INT_WALL_T, height=hgt, base=LEVEL_1))

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
    mech_rect = [(m["x0"], m["y0"]), (m["x1"], m["y0"]), (m["x1"], m["y1"]), (m["x0"], m["y1"])]
    ceiling = [
        [(0, 0), (BLDG_X, 0), (BLDG_X, m["y0"]), (0, m["y0"])],
        [(0, m["y1"]), (BLDG_X, m["y1"]), (BLDG_X, BLDG_Y), (0, BLDG_Y)],
        [(0, m["y0"]), (m["x0"], m["y0"]), (m["x0"], m["y1"]), (0, m["y1"])],
        [(m["x1"], m["y0"]), (BLDG_X, m["y0"]), (BLDG_X, m["y1"]), (m["x1"], m["y1"])],
    ]
    return dict(
        size=(BLDG_X, BLDG_Y), area=BLDG_X * BLDG_Y,
        levels=[dict(name="Level 1", elevation=LEVEL_1), dict(name="Roof", elevation=ROOF)],
        ceiling_height=CEILING, duct_centreline=Z_DUCT,
        walls=walls, columns=columns, grids=grids,
        floor=dict(outline=outline, thickness=SLAB_T, top=LEVEL_1),
        roof=dict(outline=outline, thickness=ROOF_T, bottom=ROOF),
        ceilings=[dict(outline=c, elevation=CEILING, thickness=0.05) for c in ceiling],
        mech_room=mech_rect,
    )


# --------------------------------------------------------------------------
# Thermal zones
# --------------------------------------------------------------------------
def _round5(v):
    return int(5 * round(v / 5.0))


def _zones():
    m = MECH
    Z = []
    num = [100]

    def z(name, box, kind, poly, cfm, exposure, number=None):
        if number is None:
            num[0] += 1
            number = str(num[0])
        Z.append(dict(number=number, name=name, box=box, kind=kind, polygon=[tuple(p) for p in poly],
                      area=_area(poly), supply_cfm=cfm, exposure=exposure))

    names = dict(N="North", E="East", S="South", W="West")
    for f in FACADE_ORDER:
        F = FACADES[f]
        mp = F["map"]
        # corner conference room (two exposures)
        exp = f + F["corner_exp"]
        factor = max(CFM_SF[f], CFM_SF[F["corner_exp"]])
        poly = [mp(0, 0), mp(CONF, 0), mp(CONF, CONF), mp(0, CONF)]
        z("Conference %s" % F["corner"], "FPB-%s" % F["corner"], "conference", poly,
          _round5(CONF * CONF * CONF_BASE * factor), exp)
        for i, u in enumerate(OFFICE_U):
            poly = [mp(u, 0), mp(u + OFFICE_W, 0), mp(u + OFFICE_W, ROOM_DEPTH), mp(u, ROOM_DEPTH)]
            group = [g for g, idx in OFFICE_GROUPS if i in idx][0]
            z("%s Office %d" % (names[f], i + 1), "FPB-%s%s" % (f, group), "office", poly,
              _round5(OFFICE_W * ROOM_DEPTH * CFM_SF[f]), f)
    d = ROOM_DEPTH
    c = CONF
    interior = [
        ("Interior NW Open Office", "VAV-1",
         [(d, 50), (50, 50), (50, m["y0"]), (m["x0"], m["y0"]), (m["x0"], m["y1"]), (50, m["y1"]),
          (50, 100 - d), (c, 100 - d), (c, 100 - c), (d, 100 - c)]),
        ("Interior NE Open Office", "VAV-2",
         [(50, 50), (100 - d, 50), (100 - d, 100 - c), (100 - c, 100 - c), (100 - c, 100 - d), (50, 100 - d),
          (50, m["y1"]), (m["x1"], m["y1"]), (m["x1"], m["y0"]), (50, m["y0"])]),
        ("Interior SW Open Office", "VAV-3", [(d, c), (c, c), (c, d), (50, d), (50, 50), (d, 50)]),
        ("Interior SE Open Office", "VAV-4", [(50, d), (100 - c, d), (100 - c, c), (100 - d, c), (100 - d, 50), (50, 50)]),
    ]
    for name, box, poly in interior:
        z(name, box, "interior", poly, _round5(_area(poly) * CFM_SF["INTERIOR"]), "interior")
    z("Mechanical Room", "AHU-1", "mechanical",
      [(m["x0"], m["y0"]), (m["x1"], m["y0"]), (m["x1"], m["y1"]), (m["x0"], m["y1"])], 0, "none", number="M-101")
    return Z


def _area(poly):
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


# --------------------------------------------------------------------------
# Duct sizing
# --------------------------------------------------------------------------
RECT_SIZES = [(8, 8), (10, 8), (10, 10), (12, 10), (14, 10), (16, 10), (14, 12), (16, 12), (18, 12), (20, 12),
              (18, 14), (20, 14), (22, 14), (24, 14), (22, 16), (24, 16), (26, 16), (28, 16), (28, 18), (30, 18),
              (32, 18), (30, 20), (32, 20), (36, 20), (36, 22), (36, 24), (40, 24), (42, 24), (42, 26), (42, 28),
              (48, 28), (48, 30), (54, 30)]
V_MAX = dict(medium=1500.0, low=900.0)


def rect_size(cfm, pressure):
    for w, h in RECT_SIZES:
        if cfm / (w * h / 144.0) <= V_MAX[pressure]:
            return (w, h)
    return RECT_SIZES[-1]


def round_size(cfm):
    for d in (6, 8, 10, 12, 14):
        if cfm / (math.pi * (d / 24.0) ** 2) <= 800:
            return d
    return 16


def inlet_size(cfm):
    """Terminal box primary inlet, sized for 1,500 to 2,000 fpm at design primary air."""
    for d in (6, 8, 10, 12, 14, 16):
        if cfm / (math.pi * (d / 24.0) ** 2) <= 2000:
            return d
    return 16


# --------------------------------------------------------------------------
# Mechanical
# --------------------------------------------------------------------------
def _mechanical(model):
    eq = model["equipment"]
    runs = model["runs"]
    terms = model["terminals"]
    zones = dict((z["box"], z) for z in model["zones"] if z["kind"] != "office")
    office_zones = {}
    for z in model["zones"]:
        if z["kind"] == "office":
            office_zones.setdefault(z["box"], []).append(z)
    Z = Z_DUCT

    def equipment(tag, kind, centre, length, width, height, flow_dir, **props):
        dx, dy = flow_dir
        cx, cy, cz = centre
        e = dict(tag=tag, kind=kind, centre=tuple(round(v, 3) for v in centre), length=length, width=width,
                 height=height, flow_dir=(dx, dy), rotation_deg=round(math.degrees(math.atan2(dy, dx)), 3),
                 inlet=tuple(round(v, 3) for v in (cx - dx * length / 2.0, cy - dy * length / 2.0, cz)),
                 outlet=tuple(round(v, 3) for v in (cx + dx * length / 2.0, cy + dy * length / 2.0, cz)))
        e.update(props)
        eq.append(e)
        return e

    def run(rid, system, name, pts, size, cfm, pressure="medium", **kw):
        pts = [tuple(round(float(v), 3) for v in (p if len(p) == 3 else (p[0], p[1], Z))) for p in pts]
        r = dict(id=rid, system=system, name=name, points=pts, cfm=cfm, pressure_class=pressure)
        if size[0] == "round":
            r.update(shape="round", diameter_in=size[1])
        else:
            r.update(shape="rect", width_in=size[0], height_in=size[1])
        r.update(kw)
        r["length_ft"] = sum(_dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        runs.append(r)
        return r

    def terminal(tag, kind, x, y, cfm, neck_in, served_by, room):
        terms.append(dict(tag=tag, kind=kind, x=round(x, 3), y=round(y, 3), z=CEILING, cfm=cfm, face_in=24,
                          neck_in=neck_in, served_by=served_by, room=room))

    counters = dict(SD=0, RG=0)

    def tag(kind):
        counters[kind] += 1
        return "%s-%02d" % (kind, counters[kind])

    def trunk(prefix, system, name, path, taps, end_cfm=0, pressure="medium", min_size=(8, 8), **kw):
        """Build a trunk along ``path`` (2D points at Z).  ``taps`` = [(point_on_path, cfm)].
        Size reduces 2 ft after a tap when the remaining airflow allows a smaller duct.
        Returns a dict mapping each tap point to the run id that contains it."""
        path = [tuple(float(v) for v in p) for p in path]
        seg_len = [math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1)]
        total_len = sum(seg_len)

        def station(pt):
            s = 0.0
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                L = seg_len[i]
                t = ((pt[0] - a[0]) * (b[0] - a[0]) + (pt[1] - a[1]) * (b[1] - a[1])) / (L * L)
                if -1e-6 <= t <= 1 + 1e-6:
                    px, py = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
                    if abs(px - pt[0]) < 1e-6 and abs(py - pt[1]) < 1e-6:
                        return s + t * L
                s += L
            raise ValueError("tap %s is not on trunk %s" % (pt, prefix))

        def point_at(s):
            acc = 0.0
            for i in range(len(path) - 1):
                if s <= acc + seg_len[i] + 1e-9:
                    t = (s - acc) / seg_len[i]
                    a, b = path[i], path[i + 1]
                    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                acc += seg_len[i]
            return path[-1]

        def sub_path(s0, s1):
            pts = [point_at(s0)]
            acc = 0.0
            for i in range(len(path) - 1):
                acc += seg_len[i]
                if s0 + 1e-6 < acc < s1 - 1e-6:
                    pts.append(path[i + 1])
            pts.append(point_at(s1))
            return pts

        taps = sorted([(station(p), p, c) for p, c in taps])
        total = end_cfm + sum(c for _, _, c in taps)

        def rect_size(cfm, pressure):
            w, h = globals()["rect_size"](cfm, pressure)
            return (max(w, min_size[0]), max(h, min_size[1]))
        # stations where the size changes
        cuts = []
        remaining = total
        size = rect_size(total, pressure)
        for s, p, c in taps:
            remaining -= c
            new = rect_size(max(remaining, 1), pressure)
            if new != size and s + 2.0 < total_len - 0.5:
                nxt = [t for t in taps if t[0] > s + 2.0]
                if not nxt or nxt[0][0] > s + 3.0:
                    cuts.append((s + 2.0, remaining, new))
                    size = new
        bounds = [0.0] + [c[0] for c in cuts] + [total_len]
        flows = [total] + [c[1] for c in cuts]
        sizes = [rect_size(total, pressure)] + [c[2] for c in cuts]
        owner = {}
        n = 0
        for i in range(len(bounds) - 1):
            n += 1
            extra = dict(kw) if i == 0 else {}
            if i == len(bounds) - 2 and end_cfm == 0:
                extra["to"] = "CAP"
            r = run("%s-%d" % (prefix, n), system, name if i == 0 else "%s (reduced)" % name,
                    sub_path(bounds[i], bounds[i + 1]), sizes[i], flows[i], pressure, **extra)
            for s, p, c in taps:
                if bounds[i] - 1e-6 <= s <= bounds[i + 1] + 1e-6 and tuple(p) not in owner:
                    owner[tuple(p)] = r["id"]
        return owner

    # ---- air handler, louver -------------------------------------------------
    ahu = equipment("AHU-1", "AHU", (51, 62, 0), 16, 6, 7, (1, 0),
                    supply_cfm=10000, outside_air_cfm=1800, cooling_tons=25, heating_mbh=300,
                    external_sp_in=2.5, fan_hp=15,
                    description="Indoor central station VAV AHU, DX or CHW coil, economizer, MERV-13 filtration")
    equipment("L-1", "LOUVER", (58, 99.5, Z), 1.0, 3, 2.5, (0, -1),
              outside_air_cfm=1800, description="Drainable OA intake louver 36x30 on north wall")

    # ---- perimeter boxes: compute airflows and tap points first ----------------
    boxes = []        # dicts with tag, facade, kind, centre_local, dir_local, tap_local, branch_local, zone(s)
    for f in FACADE_ORDER:
        F = FACADES[f]
        for g, idx in OFFICE_GROUPS:
            zs = office_zones["FPB-%s%s" % (f, g)]
            fan = sum(z["supply_cfm"] for z in zs)
            u_mid = 38.0 if g == "1" else 68.0
            boxes.append(dict(tag="FPB-%s%s" % (f, g), facade=f, kind="offices", zones=zs, fan=fan,
                              centre=(u_mid, ROOM_DEPTH + CORRIDOR / 2.0), dir=(0, -1),
                              tap=(u_mid, RING), branch=[(u_mid, RING), (u_mid, ROOM_DEPTH + CORRIDOR)]))
        zc = zones["FPB-%s" % F["corner"]]
        boxes.append(dict(tag="FPB-%s" % F["corner"], facade=f, kind="conference", zones=[zc], fan=zc["supply_cfm"],
                          centre=(CONF + 4.0, ROOM_DEPTH + CORRIDOR / 2.0), dir=(-1, 0),
                          tap=(30.0, RING), branch=[(30.0, RING), (30.0, ROOM_DEPTH + CORRIDOR / 2.0),
                                                    (CONF + 6.5, ROOM_DEPTH + CORRIDOR / 2.0)]))
    for b in boxes:
        b["primary"] = _round5(b["fan"] / FPB_INDUCTION)
        F = FACADES[b["facade"]]
        b["tap_xy"] = tuple(round(v, 3) for v in F["map"](*b["tap"]))

    # interior VAV boxes
    vav = [("VAV-1", (30, 54), (0, 1)), ("VAV-2", (70, 54), (0, 1)), ("VAV-3", (34, 40), (0, -1)), ("VAV-4", (66, 40), (0, -1))]
    vav_cfm = dict((t, zones[t]["supply_cfm"]) for t, _, _ in vav)
    vav_tap = {"VAV-1": (30, 47), "VAV-2": (70, 47), "VAV-3": (34, 47), "VAV-4": (66, 47)}

    primary = dict((b["tag"], b["primary"]) for b in boxes)
    tap_cfm = dict((b["tap_xy"], b["primary"]) for b in boxes)
    for t in vav_tap:
        tap_cfm[vav_tap[t]] = vav_cfm[t]

    # ---- medium pressure distribution: riser, mains, ring legs -------------------
    def taps_on(points):
        return [(p, tap_cfm[p]) for p in points]

    leg = {}
    leg_total = {}
    legs = {
        "SA-EN": ("East leg north to north facade", [(77, 47), (77, 77), (67, 77)], [(77, 62), (77, 70), (68, 77)]),
        "SA-ES": ("East leg south to south facade", [(77, 47), (77, 23), (61, 23)], [(77, 32), (70, 23), (62, 23)]),
        "SA-WN": ("West leg north to north facade", [(23, 47), (23, 77), (39, 77)], [(23, 68), (30, 77), (38, 77)]),
        "SA-WS": ("West leg south to south facade", [(23, 47), (23, 23), (33, 23)], [(23, 38), (23, 30), (32, 23)]),
    }
    for k, (name, path, tp) in legs.items():
        leg_total[k] = sum(tap_cfm[p] for p in tp)
    owner = {}
    east_total = vav_cfm["VAV-2"] + vav_cfm["VAV-4"] + leg_total["SA-EN"] + leg_total["SA-ES"]
    west_total = vav_cfm["VAV-1"] + vav_cfm["VAV-3"] + leg_total["SA-WN"] + leg_total["SA-WS"]
    total_primary = east_total + west_total
    run("SA-01", "SA", "AHU-1 supply riser and main", [(54, 62, 7.0), (54, 62, Z), (54, 47, Z)],
        rect_size(total_primary, "medium"), total_primary, from_="AHU-1")
    owner.update(trunk("SA-ME", "SA", "Main east", [(54, 47), (77, 47)], taps_on([(70, 47), (66, 47)]),
                       end_cfm=leg_total["SA-EN"] + leg_total["SA-ES"]))
    owner.update(trunk("SA-MW", "SA", "Main west", [(54, 47), (23, 47)], taps_on([(30, 47), (34, 47)]),
                       end_cfm=leg_total["SA-WN"] + leg_total["SA-WS"]))
    for k in ("SA-EN", "SA-ES", "SA-WN", "SA-WS"):
        name, path, tp = legs[k]
        owner.update(trunk(k, "SA", name, path, taps_on(tp), min_size=(12, 10)))

    # ---- return and outside air --------------------------------------------------
    ra = ahu["supply_cfm"] - ahu["outside_air_cfm"]
    run("RA-01", "RA", "Plenum return to AHU-1", [(36, 62, Z), (45, 62, Z), (45, 62, 7.0)], rect_size(ra, "low"), ra,
        pressure="low", to="AHU-1", from_="PLENUM")
    run("OA-01", "OA", "Outside air from L-1 to AHU-1", [(58, 99.0, Z), (58, 62, Z), (58, 62, 7.0)],
        rect_size(ahu["outside_air_cfm"], "low"), ahu["outside_air_cfm"], pressure="low", from_="L-1", to="AHU-1")

    # ---- interior VAV boxes and their diffusers ------------------------------------
    n_lp = 0
    for t, (cx, cy), (dx, dy) in vav:
        cfm = vav_cfm[t]
        e = equipment(t, "VAV", (cx, cy, Z), 3.0, 2.0, 1.25, (dx, dy), primary_cfm=cfm, min_cfm=int(cfm * 0.3),
                      inlet_in=inlet_size(cfm), zone=zones[t]["number"],
                      description="Single-duct pressure-independent VAV terminal, cooling only")
        tp = vav_tap[t]
        run("SA-%s" % t, "SA", "Tap to %s" % t, [tp, e["inlet"][:2]], rect_size(cfm, "medium"), cfm,
            tap_on=owner[tp], to=t)
        ox, oy, oz = e["outlet"]
        p1 = (ox + dx * 5.5, oy + dy * 5.5)
        p2 = (ox + dx * 12.0, oy + dy * 12.0)
        h1 = run("LP-%s-1" % t, "SA", "%s discharge header" % t, [(ox, oy), p1], rect_size(cfm, "low"), cfm, pressure="low", from_=t)
        h2 = run("LP-%s-2" % t, "SA", "%s discharge header (reduced)" % t, [p1, p2], rect_size(cfm / 2, "low"), cfm // 2, pressure="low", to="CAP")
        per = _round5(cfm / 4.0)
        k = 0
        for hdr, off in ((h1, 2.5), (h2, 10.5)):
            tx, ty = ox + dx * off, oy + dy * off
            for side in (-5, 5):
                k += 1
                sd = tag("SD")
                px, py = tx + side, ty
                run("LP-%s-%d" % (t, 2 + k), "SA", "Runout to %s" % sd, [(tx, ty, Z), (px, py, Z), (px, py, Z_DIFFUSER_TOP)],
                    ("round", round_size(per)), per, pressure="low", tap_on=hdr["id"], to=sd)
                terminal(sd, "supply_diffuser", px, py, per, round_size(per), t, zones[t]["number"])

    # ---- perimeter fan-powered boxes, discharge ductwork, terminals ----------------
    for b in boxes:
        F = FACADES[b["facade"]]
        mp, md = F["map"], F["dir"]
        area = sum(z["area"] for z in b["zones"])
        gdir = md(*b["dir"])
        gc = mp(*b["centre"])
        e = equipment(b["tag"], "FPB", (gc[0], gc[1], Z), 5.0, 3.5, 1.5, gdir,
                      primary_cfm=b["primary"], fan_cfm=b["fan"], min_primary_cfm=int(b["primary"] * 0.3),
                      inlet_in=inlet_size(b["primary"]), heat_kw=int(math.ceil(area * HEAT_BTUH_SF / 3412.0)),
                      zone=", ".join(z["number"] for z in b["zones"]), exposure=b["zones"][0]["exposure"],
                      description="Series fan-powered terminal, ECM fan, electric reheat, plenum induction inlet")
        branch = [mp(*p) for p in b["branch"]]
        run("SA-%s" % b["tag"], "SA", "Tap to %s" % b["tag"], branch, rect_size(b["primary"], "medium"), b["primary"],
            tap_on=owner[b["tap_xy"]], to=b["tag"])
        tagn = b["tag"]
        fan = b["fan"]
        if b["kind"] == "offices":
            u0 = b["centre"][0]
            zs = b["zones"]
            per = [z["supply_cfm"] for z in zs]
            centres = [OFFICE_U[i] + OFFICE_W / 2.0 for i in range(5) if ("FPB-%s%s" % (b["facade"], "1" if i < 3 else "2")) == tagn]
            vmid = ROOM_DEPTH / 2.0
            run("LP-%s-0" % tagn, "SA", "%s discharge header" % tagn, [mp(u0, ROOM_DEPTH), mp(u0, vmid)],
                rect_size(fan, "low"), fan, pressure="low", from_=tagn)
            left = [c for c in centres if c < u0]
            right = [c for c in centres if c >= u0]
            # middle office of a 3-office group: diffuser 3 ft right of the tee
            diff_u = [(c, z) for c, z in zip(centres, zs)]
            lw = run("LP-%s-L" % tagn, "SA", "%s left leg" % tagn, [mp(u0, vmid), mp(min(left) - 1, vmid)],
                     rect_size(sum(per[:len(left)]), "low"), sum(per[:len(left)]), pressure="low", to="CAP")
            rw = run("LP-%s-R" % tagn, "SA", "%s right leg" % tagn, [mp(u0, vmid), mp(max(right) + 1, vmid)],
                     rect_size(sum(per[len(left):]), "low"), sum(per[len(left):]), pressure="low", to="CAP")
            for k, (c, z) in enumerate(diff_u):
                uc = c + 3.0 if abs(c - u0) < 1e-6 else c
                sd = tag("SD")
                gx, gy = mp(uc, vmid)
                run("LP-%s-%d" % (tagn, k + 1), "SA", "Drop to %s" % sd, [(gx, gy, Z), (gx, gy, Z_DIFFUSER_TOP)],
                    ("round", round_size(z["supply_cfm"])), z["supply_cfm"], pressure="low",
                    tap_on=(lw if uc < u0 else rw)["id"], to=sd)
                terminal(sd, "supply_diffuser", gx, gy, z["supply_cfm"], round_size(z["supply_cfm"]), tagn, z["number"])
                rx, ry = mp(c + 4.0, 12.0)
                terminal(tag("RG"), "return_grille", rx, ry, z["supply_cfm"], 0, "PLENUM", z["number"])
        else:
            zc = b["zones"][0]
            v0 = ROOM_DEPTH + CORRIDOR / 2.0
            hdr = run("LP-%s-0" % tagn, "SA", "%s discharge header" % tagn,
                      [mp(CONF + 1.5, v0), mp(10.0, v0), mp(10.0, 5.0)], rect_size(fan, "low"), fan,
                      pressure="low", from_=tagn, to="CAP")
            half = _round5(fan / 2.0)
            for k, (uu, vv, du) in enumerate([(10.0, 14.0, 6.0), (10.0, 6.0, 14.0)]):
                sd = tag("SD")
                ax, ay = mp(uu, vv)
                dx_, dy_ = mp(du, vv)
                run("LP-%s-%d" % (tagn, k + 1), "SA", "Runout to %s" % sd, [(ax, ay, Z), (dx_, dy_, Z), (dx_, dy_, Z_DIFFUSER_TOP)],
                    ("round", round_size(half)), half, pressure="low", tap_on=hdr["id"], to=sd)
                terminal(sd, "supply_diffuser", dx_, dy_, half, round_size(half), tagn, zc["number"])
            for uu, vv in ((14.0, 14.0), (6.0, 6.0)):
                rx, ry = mp(uu, vv)
                terminal(tag("RG"), "return_grille", rx, ry, half, 0, "PLENUM", zc["number"])

    # ---- open office return grilles --------------------------------------------------
    interior_supply = sum(vav_cfm.values())
    rg = [(40, 40), (60, 40), (34, 74), (66, 74), (26, 46), (74, 46), (50, 30), (50, 78)]
    for i, (x, y) in enumerate(rg):
        zn = [z for z in model["zones"] if z["kind"] == "interior" and _inside((x, y), z["polygon"])]
        terminal(tag("RG"), "return_grille", x, y, _round5(interior_supply / len(rg)), 0, "PLENUM",
                 zn[0]["number"] if zn else "")


def _inside(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def _dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def _totals(model):
    eqs = model["equipment"]
    t = dict(
        supply_primary_cfm=sum(e.get("primary_cfm", 0) for e in eqs if e["kind"] in ("VAV", "FPB")),
        zone_supply_cfm=sum(z["supply_cfm"] for z in model["zones"]),
        diffuser_cfm=sum(x["cfm"] for x in model["terminals"] if x["kind"] == "supply_diffuser"),
        return_grille_cfm=sum(x["cfm"] for x in model["terminals"] if x["kind"] == "return_grille"),
        duct_length_ft=round(sum(r["length_ft"] for r in model["runs"]), 1),
        supply_diffusers=sum(1 for x in model["terminals"] if x["kind"] == "supply_diffuser"),
        return_grilles=sum(1 for x in model["terminals"] if x["kind"] == "return_grille"),
        vav_boxes=sum(1 for e in eqs if e["kind"] == "VAV"),
        fan_powered_boxes=sum(1 for e in eqs if e["kind"] == "FPB"),
        offices=sum(1 for z in model["zones"] if z["kind"] == "office"),
        conference_rooms=sum(1 for z in model["zones"] if z["kind"] == "conference"),
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
