"""Axonometric SVG of the IFC model (ductwork, equipment, terminals, structure) using the ifcopenshell geometry kernel."""
import math
import os
import sys

import ifcopenshell
import ifcopenshell.geom
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Office-10k-VAV-Mechanical.ifc")
f = ifcopenshell.open(path)
settings = ifcopenshell.geom.settings()
settings.set("use-world-coords", True)

COLOR = {
    "IfcDuctSegment": "#1f6fd1", "IfcDuctFitting": "#5b8fd8", "IfcAirTerminal": "#8fc1ff",
    "IfcAirTerminalBox": "#f28c28", "IfcUnitaryEquipment": "#555555", "IfcColumn": "#333333",
    "IfcWall": "#d9d4c7", "IfcSlab": "#efede6",
}
SKIP = {"IfcCovering", "IfcSpace"}
SYSTEM = {}
for rel in f.by_type("IfcRelAssignsToGroup"):
    g = rel.RelatingGroup
    if g.is_a("IfcDistributionSystem"):
        for o in rel.RelatedObjects:
            SYSTEM[o.id()] = g.Name
SYS_COLOR = {"Return Air": "#d1431f", "Outside Air": "#1f9e5a"}

# isometric-ish projection: rotate 35 deg about Z then tilt
az, el = math.radians(-35), math.radians(30)
Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
Rx = np.array([[1, 0, 0], [0, math.cos(el), -math.sin(el)], [0, math.sin(el), math.cos(el)]])
R = Rx @ Rz

faces = []
for p in f.by_type("IfcProduct"):
    if not p.Representation or p.is_a() in SKIP:
        continue
    if p.is_a("IfcSlab") and p.PredefinedType == "ROOF":
        continue
    if p.is_a("IfcWall") and p.Name in ("W-N", "W-E"):
        continue   # drop the two far walls so the plenum is visible
    try:
        shape = ifcopenshell.geom.create_shape(settings, p)
    except Exception:
        continue
    v = np.array(shape.geometry.verts).reshape(-1, 3)
    tri = np.array(shape.geometry.faces).reshape(-1, 3)
    col = SYS_COLOR.get(SYSTEM.get(p.id()), COLOR.get(p.is_a(), "#aaaaaa"))
    pv = v @ R.T
    for t in tri:
        pts = pv[t]
        # face normal shading
        n = np.cross(v[t[1]] - v[t[0]], v[t[2]] - v[t[0]])
        nn = np.linalg.norm(n)
        shade = 0.75 + 0.25 * abs(n[2] / nn) if nn > 0 else 1.0
        layer = {"IfcSlab": 0, "IfcWall": 1, "IfcColumn": 2}.get(p.is_a(), 3)
        faces.append(((layer, -pts[:, 1].mean()), pts, col, shade))

# painter's algorithm: structure first, then everything else from far (large y) to near
faces.sort(key=lambda x: x[0])
allp = np.vstack([x[1] for x in faces])
xmin, xmax = allp[:, 0].min(), allp[:, 0].max()
zmin, zmax = allp[:, 2].min(), allp[:, 2].max()
S = 1100.0 / (xmax - xmin)
W, H = 1160, int((zmax - zmin) * S) + 110


def X(x): return 30 + (x - xmin) * S
def Y(z): return 60 + (zmax - z) * S


def shade_hex(col, k):
    r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Helvetica, Arial, sans-serif">' % (W, H, W, H),
       '<rect width="100%" height="100%" fill="white"/>',
       '<text x="30" y="30" font-size="16" font-weight="bold">Axonometric view of Office-10k-VAV-Mechanical.ifc (north and east walls and roof removed)</text>',
       '<text x="30" y="48" font-size="11" fill="#444">Blue: supply air ductwork and diffusers. Red: return. Green: outside air. Orange: VAV and fan-powered boxes. Grey: AHU, columns.</text>']
for _, pts, col, k in faces:
    out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.15"/>' % (
        " ".join("%.1f,%.1f" % (X(p[0]), Y(p[2])) for p in pts), shade_hex(col, k), shade_hex(col, k * 0.9)))
out.append("</svg>")
dest = os.path.join(HERE, "isometric.svg")
open(dest, "w").write("\n".join(out))
print("wrote", dest, len(faces), "faces")
