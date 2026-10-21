"""Plan drawing (SVG), schedules (CSV) and a geometric sanity check for the design."""
import csv
import itertools
import os
import sys

import design

HERE = os.path.dirname(os.path.abspath(__file__))
M = design.build()
B = M["building"]

SYS_COLOR = {"SA": "#1f6fd1", "RA": "#d1431f", "OA": "#1f9e5a"}


def run_boxes(r):
    """Axis-aligned 3D boxes (one per straight segment) for clash checking."""
    pts = r["points"]
    if r["shape"] == "round":
        w = h = r["diameter_in"] / 12.0
    else:
        w, h = r["width_in"] / 12.0, r["height_in"] / 12.0
    out = []
    for a, b in zip(pts, pts[1:]):
        lo = [min(a[i], b[i]) for i in range(3)]
        hi = [max(a[i], b[i]) for i in range(3)]
        if a[2] != b[2]:                       # vertical
            half = [w / 2.0, w / 2.0, 0]
        elif a[0] != b[0]:                     # along X
            half = [0, w / 2.0, h / 2.0]
        else:                                  # along Y
            half = [w / 2.0, 0, h / 2.0]
        out.append(([lo[i] - half[i] for i in range(3)], [hi[i] + half[i] for i in range(3)]))
    return out


def overlap(b1, b2, tol=0.01):
    return all(b1[0][i] + tol < b2[1][i] and b2[0][i] + tol < b1[1][i] for i in range(3))


def related(r1, r2):
    """Runs that legitimately touch: share a node, or one taps the other."""
    if r1.get("tap_on") == r2["id"] or r2.get("tap_on") == r1["id"]:
        return True
    ends1 = {r1["points"][0], r1["points"][-1]}
    ends2 = {r2["points"][0], r2["points"][-1]}
    return bool(ends1 & ends2)


def check():
    problems = []
    runs = M["runs"]
    boxes = {r["id"]: run_boxes(r) for r in runs}
    for r1, r2 in itertools.combinations(runs, 2):
        if related(r1, r2):
            continue
        for b1 in boxes[r1["id"]]:
            for b2 in boxes[r2["id"]]:
                if overlap(b1, b2):
                    problems.append("duct clash %s / %s" % (r1["id"], r2["id"]))
    # columns vs ducts and equipment
    cols = [([c["x"] - c["size"] / 2, c["y"] - c["size"] / 2, 0],
             [c["x"] + c["size"] / 2, c["y"] + c["size"] / 2, c["height"]], c["id"]) for c in B["columns"]]
    for r in runs:
        for b in boxes[r["id"]]:
            for lo, hi, cid in cols:
                if overlap(b, (lo, hi)):
                    problems.append("duct %s hits column %s" % (r["id"], cid))
    eq_boxes = []
    for e in M["equipment"]:
        cx, cy, cz = e["centre"]
        dx, dy = e["flow_dir"]
        lx = e["length"] if dx else e["width"]
        ly = e["length"] if dy else e["width"]
        z0 = cz if e["kind"] == "AHU" else cz - e["height"] / 2.0
        box = ([cx - lx / 2, cy - ly / 2, z0], [cx + lx / 2, cy + ly / 2, z0 + e["height"]])
        eq_boxes.append((e["tag"], box))
        for lo, hi, cid in cols:
            if overlap(box, (lo, hi)):
                problems.append("equipment %s hits column %s" % (e["tag"], cid))
    for (t1, b1), (t2, b2) in itertools.combinations(eq_boxes, 2):
        if overlap(b1, b2):
            problems.append("equipment clash %s / %s" % (t1, t2))
    for r in runs:
        for b in boxes[r["id"]]:
            for t, eb in eq_boxes:
                if r.get("to") == t or r.get("from_") == t:
                    continue
                if overlap(b, eb):
                    problems.append("duct %s hits equipment %s" % (r["id"], t))
    # terminals vs each other
    for t1, t2 in itertools.combinations(M["terminals"], 2):
        if abs(t1["x"] - t2["x"]) < 2 and abs(t1["y"] - t2["y"]) < 2:
            problems.append("terminal clash %s / %s" % (t1["tag"], t2["tag"]))
    # velocity limits
    for r in runs:
        v = design.velocity_fpm(r)
        limit = 2000 if r["pressure_class"] == "medium" else 1200
        if v > limit:
            problems.append("velocity %s %.0f fpm > %d" % (r["id"], v, limit))
    # every run end that names equipment must land on that equipment's connector
    eq = {e["tag"]: e for e in M["equipment"]}
    for r in runs:
        for key, pt in (("from_", r["points"][0]), ("to", r["points"][-1])):
            tag = r.get(key)
            if tag in eq:
                e = eq[tag]
                conn = e["outlet"] if key == "from_" else e["inlet"]
                if e["kind"] in ("AHU",):
                    continue   # placeholder unit: connections at its top
                if design._dist(pt, conn) > 0.01:
                    problems.append("run %s end %s not at %s connector %s" % (r["id"], pt, tag, conn))
    return problems


def schedules():
    with open(os.path.join(HERE, "schedule_ducts.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Run", "System", "Pressure class", "Description", "Shape", "Size (in)",
                    "Airflow (cfm)", "Velocity (fpm)", "Length (ft)", "Taps on", "From", "To"])
        for r in M["runs"]:
            w.writerow([r["id"], r["system"], r["pressure_class"], r["name"], r["shape"],
                        design.size_label(r), r["cfm"], round(design.velocity_fpm(r)),
                        round(r["length_ft"], 1), r.get("tap_on", ""), r.get("from_", ""), r.get("to", "")])
    with open(os.path.join(HERE, "schedule_equipment.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Tag", "Type", "Zone", "Primary / supply cfm", "Fan cfm", "Min cfm", "Inlet (in)",
                    "Heat (kW)", "Location X (ft)", "Location Y (ft)", "Elevation (ft)", "Size LxWxH (ft)", "Description"])
        for e in M["equipment"]:
            w.writerow([e["tag"], e["kind"], e.get("zone", ""), e.get("primary_cfm", e.get("supply_cfm", e.get("outside_air_cfm", ""))),
                        e.get("fan_cfm", ""), e.get("min_cfm", e.get("min_primary_cfm", "")), e.get("inlet_in", ""),
                        e.get("heat_kw", ""), e["centre"][0], e["centre"][1], e["centre"][2],
                        "%gx%gx%g" % (e["length"], e["width"], e["height"]), e.get("description", "")])
    with open(os.path.join(HERE, "schedule_air_terminals.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Tag", "Type", "Served by", "Airflow (cfm)", "Face (in)", "Neck (in)", "X (ft)", "Y (ft)", "Ceiling (ft)"])
        for t in M["terminals"]:
            w.writerow([t["tag"], t["kind"], t["served_by"], t["cfm"], t["face_in"], t["neck_in"] or "", t["x"], t["y"], t["z"]])
    with open(os.path.join(HERE, "schedule_zones.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Number", "Name", "Type", "Terminal box", "Area (sf)", "Design supply (cfm)", "cfm/sf"])
        for z in M["zones"]:
            w.writerow([z["number"], z["name"], z["kind"], z["box"], round(z["area"]), z["supply_cfm"],
                        round(z["supply_cfm"] / z["area"], 2) if z["supply_cfm"] else ""])


def svg():
    S = 7.0                      # px per ft
    PAD = 60
    W, H = B["size"][0] * S + 2 * PAD, B["size"][1] * S + 2 * PAD + 90

    def X(x): return PAD + x * S
    def Y(y): return PAD + (B["size"][1] - y) * S

    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Helvetica, Arial, sans-serif">' % (W, H, W, H))
    o.append('<rect width="100%" height="100%" fill="white"/>')
    o.append('<text x="%d" y="30" font-size="18" font-weight="bold">%s</text>' % (PAD, M["project"]))
    o.append('<text x="%d" y="48" font-size="11" fill="#444">Ceiling plan at 9 ft AFF looking up. Ductwork centreline 11 ft 6 in AFF. Grid 25 ft. Scale 1 ft = %g px.</text>' % (PAD, S))
    # zones
    zc = {"perimeter": "#fff4d6", "interior": "#e8f1ff", "mechanical": "#eeeeee"}
    for z in M["zones"]:
        pts = " ".join("%g,%g" % (X(x), Y(y)) for x, y in z["polygon"])
        o.append('<polygon points="%s" fill="%s" stroke="#bbb" stroke-width="0.5"/>' % (pts, zc[z["kind"]]))
        cx = sum(p[0] for p in z["polygon"]) / len(z["polygon"])
        cy = sum(p[1] for p in z["polygon"]) / len(z["polygon"])
        if z["kind"] == "mechanical":
            cx, cy = 50, 56
        if z["kind"] == "interior" and z["number"] in ("109", "110"):
            cy = 75
        o.append('<text x="%g" y="%g" font-size="9" fill="#666" text-anchor="middle">%s %s</text>' % (X(cx), Y(cy), z["number"], z["name"]))
        o.append('<text x="%g" y="%g" font-size="8" fill="#888" text-anchor="middle">%d sf</text>' % (X(cx), Y(cy) + 10, round(z["area"])))
    # grids
    for g in B["grids"]:
        (x1, y1), (x2, y2) = g["start"], g["end"]
        o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#999" stroke-dasharray="6,3" stroke-width="0.6"/>' % (X(x1), Y(y1), X(x2), Y(y2)))
        o.append('<circle cx="%g" cy="%g" r="8" fill="white" stroke="#555"/><text x="%g" y="%g" font-size="9" text-anchor="middle">%s</text>' % (X(x1), Y(y1), X(x1), Y(y1) + 3, g["id"]))
    # walls
    for w in B["walls"]:
        (x1, y1), (x2, y2) = w["start"], w["end"]
        o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#222" stroke-width="%g"/>' % (X(x1), Y(y1), X(x2), Y(y2), w["thickness"] * S))
    for c in B["columns"]:
        s = c["size"] * S
        o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="#222"/>' % (X(c["x"]) - s / 2, Y(c["y"]) - s / 2, s, s))
    # ducts (draw mains first so taps overlay)
    for r in sorted(M["runs"], key=lambda r: 0 if r["pressure_class"] == "medium" else 1):
        col = SYS_COLOR[r["system"]]
        wft = (r["diameter_in"] if r["shape"] == "round" else r["width_in"]) / 12.0
        pts = r["points"]
        for a, b in zip(pts, pts[1:]):
            if a[0] == b[0] and a[1] == b[1]:
                continue  # vertical segment, plan is a point
            o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="butt" opacity="0.85"/>'
                     % (X(a[0]), Y(a[1]), X(b[0]), Y(b[1]), col, max(1.5, wft * S)))
        if r["pressure_class"] == "medium" or r["id"].startswith(("RA", "OA")):
            a, b = pts[0], pts[-1]
            for p, q in zip(pts, pts[1:]):
                if design._dist(p, q) > 8 and p[2] == q[2]:
                    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
                    rot = 0 if p[1] == q[1] else -90
                    o.append('<text x="%g" y="%g" font-size="8" fill="white" text-anchor="middle" transform="rotate(%d %g %g)">%s %s</text>'
                             % (X(mx), Y(my) + 3, rot, X(mx), Y(my) + 3, r["id"], design.size_label(r)))
                    break
    # equipment
    for e in M["equipment"]:
        cx, cy, cz = e["centre"]
        dx, dy = e["flow_dir"]
        lx = e["length"] if dx else e["width"]
        ly = e["length"] if dy else e["width"]
        fill = {"AHU": "#555", "VAV": "#f28c28", "FPB": "#c2185b", "LOUVER": "#1f9e5a"}[e["kind"]]
        o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" stroke="black" stroke-width="0.8"/>'
                 % (X(cx - lx / 2), Y(cy + ly / 2), lx * S, ly * S, fill))
        o.append('<text x="%g" y="%g" font-size="8" fill="white" font-weight="bold" text-anchor="middle">%s</text>' % (X(cx), Y(cy) + 3, e["tag"]))
    # terminals
    for t in M["terminals"]:
        s = t["face_in"] / 12.0 * S
        x, y = X(t["x"]) - s / 2, Y(t["y"]) - s / 2
        if t["kind"] == "supply_diffuser":
            o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="white" stroke="#1f6fd1" stroke-width="1"/>' % (x, y, s, s))
            o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#1f6fd1" stroke-width="0.7"/><line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#1f6fd1" stroke-width="0.7"/>'
                     % (x, y, x + s, y + s, x + s, y, x, y + s))
        else:
            o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="white" stroke="#d1431f" stroke-width="1"/>' % (x, y, s, s))
            o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#d1431f" stroke-width="0.7"/>' % (x, y + s / 2, x + s, y + s / 2))
    # legend
    ly0 = H - 70
    items = [("Supply air (SA)", SYS_COLOR["SA"]), ("Return air (RA)", SYS_COLOR["RA"]), ("Outside air (OA)", SYS_COLOR["OA"]),
             ("VAV box", "#f28c28"), ("Fan-powered box", "#c2185b"), ("AHU", "#555")]
    for i, (lab, col) in enumerate(items):
        x = PAD + i * 125
        o.append('<rect x="%g" y="%g" width="14" height="14" fill="%s"/><text x="%g" y="%g" font-size="10">%s</text>' % (x, ly0, col, x + 20, ly0 + 11, lab))
    o.append('<text x="%d" y="%d" font-size="10">Square with X = 24x24 supply diffuser. Square with bar = 24x24 plenum return grille.</text>' % (PAD, ly0 + 32))
    t = M["totals"]
    ahu = [e for e in M["equipment"] if e["kind"] == "AHU"][0]
    o.append('<text x="%d" y="%d" font-size="10">AHU-1 %s cfm, %s cfm OA. Primary air %s cfm: %d VAV + %d FPB. %d diffusers, %d return grilles, %g ft duct.</text>'
             % (PAD, ly0 + 48, "{:,}".format(ahu["supply_cfm"]), "{:,}".format(ahu["outside_air_cfm"]), "{:,}".format(t["supply_primary_cfm"]),
                t["vav_boxes"], t["fan_powered_boxes"], t["supply_diffusers"], t["return_grilles"], t["duct_length_ft"]))
    o.append("</svg>")
    with open(os.path.join(HERE, "plan.svg"), "w") as f:
        f.write("\n".join(o))


if __name__ == "__main__":
    probs = check()
    schedules()
    svg()
    if probs:
        print("CHECK PROBLEMS:")
        for p in probs:
            print("  ", p)
        sys.exit(1)
    print("check OK, schedules and plan.svg written")
