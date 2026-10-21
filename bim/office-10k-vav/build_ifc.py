"""
Build an IFC4 model of the office and its HVAC from design.py.

Output: Office-10k-VAV-Mechanical.ifc  (link or open in Revit: Insert > Link IFC,
or File > Open > IFC).  The IFC length unit is FEET (IfcConversionBasedUnit),
so every coordinate in the file matches design.py one to one.

    pip install ifcopenshell
    python build_ifc.py
"""
import math
import os

import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.system
import ifcopenshell.api.type
import ifcopenshell.api.unit

import design

FT = 1.0        # IFC project length unit is feet
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Office-10k-VAV-Mechanical.ifc")

D = design.build()
B = D["building"]

model = ifcopenshell.api.project.create_file(version="IFC4")
project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name=D["project"])
ifcopenshell.api.unit.assign_unit(model, length={"is_metric": False, "raw": "FEET"})
model_ctx = ifcopenshell.api.context.add_context(model, context_type="Model")
body = ifcopenshell.api.context.add_context(model, context_type="Model", context_identifier="Body",
                                           target_view="MODEL_VIEW", parent=model_ctx)

site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="Site")
building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="10,000 sf Office")
storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Level 1")
storey.Elevation = 0.0
roof_storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Roof")
roof_storey.Elevation = design.ROOF * FT
ifcopenshell.api.aggregate.assign_object(model, products=[site], relating_object=project)
ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=site)
ifcopenshell.api.aggregate.assign_object(model, products=[storey, roof_storey], relating_object=building)
for s in (site, building, storey, roof_storey):
    ifcopenshell.api.geometry.edit_object_placement(model, product=s, matrix=np.eye(4))

counts = {}


# --------------------------------------------------------------------------
# geometry helpers (all arguments in feet, converted here)
# --------------------------------------------------------------------------
def rect_profile(w_ft, h_ft):
    return model.createIfcRectangleProfileDef("AREA", None, None, w_ft * FT, h_ft * FT)


def circle_profile(d_ft):
    return model.createIfcCircleProfileDef("AREA", None, None, d_ft * FT / 2.0)


def poly_profile(pts_ft):
    pts = [model.createIfcCartesianPoint((x * FT, y * FT)) for x, y in pts_ft]
    pts.append(pts[0])
    return model.createIfcArbitraryClosedProfileDef("AREA", None, model.createIfcPolyline(pts))


def extrusion(profile, depth_ft):
    solid = model.createIfcExtrudedAreaSolid(profile, None, model.createIfcDirection((0.0, 0.0, 1.0)), depth_ft * FT)
    return model.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])


def place(product, origin_ft, xdir=(1, 0, 0), zdir=(0, 0, 1)):
    x = np.array(xdir, dtype=float)
    z = np.array(zdir, dtype=float)
    x /= np.linalg.norm(x)
    z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = x, y, z
    m[:3, 3] = np.array(origin_ft, dtype=float) * FT
    ifcopenshell.api.geometry.edit_object_placement(model, product=product, matrix=m, is_si=False)


def element(ifc_class, name, rep, origin, xdir=(1, 0, 0), zdir=(0, 0, 1), predefined_type=None,
            container=None, tag=None, description=None):
    e = ifcopenshell.api.root.create_entity(model, ifc_class=ifc_class, name=name, predefined_type=predefined_type)
    if tag:
        e.Tag = tag
    if description:
        e.Description = description
    ifcopenshell.api.spatial.assign_container(model, products=[e], relating_structure=container or storey)
    place(e, origin, xdir, zdir)
    ifcopenshell.api.geometry.assign_representation(model, product=e, representation=rep)
    counts[ifc_class] = counts.get(ifc_class, 0) + 1
    return e


def pset(e, name, props):
    ps = ifcopenshell.api.pset.add_pset(model, product=e, name=name)
    ifcopenshell.api.pset.edit_pset(model, pset=ps, properties=props)


_types = {}


def typed(e, type_class, type_name, predefined_type=None):
    key = (type_class, type_name)
    if key not in _types:
        _types[key] = ifcopenshell.api.root.create_entity(model, ifc_class=type_class, name=type_name,
                                                          predefined_type=predefined_type)
    ifcopenshell.api.type.assign_type(model, related_objects=[e], relating_type=_types[key],
                                      should_map_representations=False)


# --------------------------------------------------------------------------
# architecture
# --------------------------------------------------------------------------
for w in B["walls"]:
    (x1, y1), (x2, y2) = w["start"], w["end"]
    L = math.hypot(x2 - x1, y2 - y1)
    e = element("IfcWall", w["id"], extrusion(rect_profile(L, w["thickness"]), w["height"]),
                ((x1 + x2) / 2.0, (y1 + y2) / 2.0, w["base"]), xdir=(x2 - x1, y2 - y1, 0),
                predefined_type="SOLIDWALL" if w["kind"] == "exterior" else "PARTITIONING")
    typed(e, "IfcWallType", "Exterior Wall 12in" if w["kind"] == "exterior" else "Interior Partition 6in",
          "SOLIDWALL" if w["kind"] == "exterior" else "PARTITIONING")
    pset(e, "Pset_WallCommon", {"IsExternal": w["kind"] == "exterior", "LoadBearing": w["kind"] == "exterior"})

for c in B["columns"]:
    e = element("IfcColumn", c["id"], extrusion(rect_profile(c["size"], c["size"]), c["height"]),
                (c["x"], c["y"], 0.0), predefined_type="COLUMN")
    typed(e, "IfcColumnType", "Steel Column 12x12", "COLUMN")

f = B["floor"]
e = element("IfcSlab", "Slab on grade", extrusion(poly_profile(f["outline"]), f["thickness"]),
            (0, 0, f["top"] - f["thickness"]), predefined_type="FLOOR")
typed(e, "IfcSlabType", "Slab on Grade 6in", "FLOOR")
r = B["roof"]
e = element("IfcSlab", "Roof deck", extrusion(poly_profile(r["outline"]), r["thickness"]),
            (0, 0, r["bottom"]), predefined_type="ROOF", container=roof_storey)
typed(e, "IfcSlabType", "Roof Deck 6in", "ROOF")
for i, c in enumerate(B["ceilings"]):
    e = element("IfcCovering", "ACT ceiling %d" % (i + 1), extrusion(poly_profile(c["outline"]), c["thickness"]),
                (0, 0, c["elevation"] - c["thickness"]), predefined_type="CEILING")
    typed(e, "IfcCoveringType", "2x4 ACT Ceiling", "CEILING")

for g in B["grids"]:
    pass  # IfcGrid is optional; Revit users will add grids in the host model

for z in D["zones"]:
    sp = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSpace", name=z["number"], predefined_type="INTERNAL")
    sp.LongName = z["name"]
    ifcopenshell.api.aggregate.assign_object(model, products=[sp], relating_object=storey)
    place(sp, (0, 0, 0))
    height = design.ROOF if z["kind"] == "mechanical" else design.CEILING
    ifcopenshell.api.geometry.assign_representation(model, product=sp, representation=extrusion(poly_profile(z["polygon"]), height))
    pset(sp, "HVAC_Zone", {"ZoneType": z["kind"], "TerminalBox": z["box"], "AreaSqFt": float(round(z["area"], 1)),
                           "DesignSupplyCFM": float(z["supply_cfm"])})
    counts["IfcSpace"] = counts.get("IfcSpace", 0) + 1

# --------------------------------------------------------------------------
# mechanical
# --------------------------------------------------------------------------
systems = {}
for key, name, ptype in (("SA", "Supply Air", "AIRCONDITIONING"), ("RA", "Return Air", "VENTILATION"),
                         ("OA", "Outside Air", "VENTILATION")):
    s = ifcopenshell.api.system.add_system(model, ifc_class="IfcDistributionSystem")
    s.Name = name
    s.PredefinedType = ptype
    systems[key] = s
members = {k: [] for k in systems}

equip = {}
for q in D["equipment"]:
    cx, cy, cz = q["centre"]
    dx, dy = q["flow_dir"]
    z0 = cz if q["kind"] == "AHU" else cz - q["height"] / 2.0
    rep = extrusion(rect_profile(q["length"], q["width"]), q["height"])
    if q["kind"] == "AHU":
        e = element("IfcUnitaryEquipment", q["tag"], rep, (cx, cy, z0), xdir=(dx, dy, 0),
                    predefined_type="AIRHANDLER", tag=q["tag"], description=q["description"])
        typed(e, "IfcUnitaryEquipmentType", "AHU - Indoor VAV Air Handler", "AIRHANDLER")
        pset(e, "HVAC_Design", {"SupplyAirflowCFM": float(q["supply_cfm"]), "OutsideAirCFM": float(q["outside_air_cfm"]),
                                "CoolingTons": float(q["cooling_tons"]), "HeatingMBH": float(q["heating_mbh"]),
                                "ExternalStaticInWG": float(q["external_sp_in"]), "FanHP": float(q["fan_hp"])})
        members["SA"].append(e)
    elif q["kind"] == "LOUVER":
        e = element("IfcAirTerminal", q["tag"], rep, (cx, cy, z0), xdir=(dx, dy, 0),
                    predefined_type="LOUVRE", tag=q["tag"], description=q["description"])
        typed(e, "IfcAirTerminalType", "Outside Air Louver 36x30", "LOUVRE")
        pset(e, "HVAC_Design", {"OutsideAirCFM": float(q["outside_air_cfm"])})
        members["OA"].append(e)
    else:
        e = element("IfcAirTerminalBox", q["tag"], rep, (cx, cy, z0), xdir=(dx, dy, 0),
                    predefined_type="VARIABLEFLOWPRESSUREINDEPENDANT", tag=q["tag"], description=q["description"])
        if q["kind"] == "VAV":
            typed(e, "IfcAirTerminalBoxType", "VAV Terminal - Single Duct Cooling Only", "VARIABLEFLOWPRESSUREINDEPENDANT")
            pset(e, "HVAC_Design", {"PrimaryAirflowCFM": float(q["primary_cfm"]), "MinimumAirflowCFM": float(q["min_cfm"]),
                                    "InletDiameterIn": float(q["inlet_in"]), "Zone": q["zone"]})
        else:
            typed(e, "IfcAirTerminalBoxType", "Series Fan-Powered Terminal - Electric Heat", "VARIABLEFLOWPRESSUREINDEPENDANT")
            pset(e, "HVAC_Design", {"PrimaryAirflowCFM": float(q["primary_cfm"]), "FanAirflowCFM": float(q["fan_cfm"]),
                                    "MinimumPrimaryCFM": float(q["min_primary_cfm"]), "InletDiameterIn": float(q["inlet_in"]),
                                    "ElectricHeatKW": float(q["heat_kw"]), "Zone": q["zone"]})
        members["SA"].append(e)
    equip[q["tag"]] = e

runs = {r["id"]: r for r in D["runs"]}


def run_dims(r):
    if r["shape"] == "round":
        d = r["diameter_in"] / 12.0
        return d, d
    return r["width_in"] / 12.0, r["height_in"] / 12.0


def fitting_size(r):
    w, h = run_dims(r)
    return max(w, h) + 2.0 / 12.0


# nodes where run ends meet (elbow / transition / tee / cross between runs)
node_runs = {}
for r in D["runs"]:
    if r.get("tap_on"):
        ends = [r["points"][-1]]
    else:
        ends = [r["points"][0], r["points"][-1]]
    for p in ends:
        key = tuple(round(v, 3) for v in p)
        node_runs.setdefault(key, []).append(r)


def end_direction(r, key):
    """Direction of the run's segment that touches node ``key``."""
    pts = r["points"]
    if tuple(round(v, 3) for v in pts[-1]) == key:
        return np.subtract(pts[-1], pts[-2])
    return np.subtract(pts[0], pts[1])


node_fittings = {}
for key, rs in node_runs.items():
    if len(rs) >= 2:
        size = max(fitting_size(r) for r in rs)
        if len(rs) == 2:
            da, db = (end_direction(r, key) for r in rs)
            collinear = abs(abs(np.dot(da, db)) / (np.linalg.norm(da) * np.linalg.norm(db)) - 1) < 1e-6
            kind = "TRANSITION" if collinear else "BEND"
        else:
            kind = "JUNCTION"
        node_fittings[key] = (kind, size, rs[0]["system"])


def trim(p, q, amount):
    """Move p towards q by amount (feet)."""
    v = np.subtract(q, p)
    n = np.linalg.norm(v)
    if n <= amount:
        return tuple(p)
    return tuple(np.add(p, v / n * amount))


def duct_segment(r, a, b, idx):
    v = np.subtract(b, a)
    L = float(np.linalg.norm(v))
    if L < 1e-6:
        return None
    w, h = run_dims(r)
    if r["shape"] == "round":
        prof = circle_profile(w)
    else:
        prof = rect_profile(w, h)
    d = v / L
    if abs(d[2]) > 0.5:
        xdir = (1, 0, 0)
    else:
        xdir = (-d[1], d[0], 0)
    e = element("IfcDuctSegment", "%s.%d" % (r["id"], idx), extrusion(prof, L), a, xdir=xdir, zdir=tuple(d),
                predefined_type="RIGIDSEGMENT", tag=r["id"],
                description="%s %s %s cfm" % (r["name"], design.size_label(r), r["cfm"]))
    typed(e, "IfcDuctSegmentType", ("Round Duct %s" if r["shape"] == "round" else "Rect Duct %s") % design.size_label(r),
          "RIGIDSEGMENT")
    pset(e, "HVAC_Design", {"System": r["system"], "PressureClass": r["pressure_class"],
                            "AirflowCFM": float(r["cfm"]), "VelocityFPM": float(round(design.velocity_fpm(r))),
                            "Size": design.size_label(r), "Run": r["id"]})
    members[r["system"]].append(e)
    return e


def duct_fitting(kind, p, size, system, name):
    e = element("IfcDuctFitting", name, extrusion(rect_profile(size, size), size),
                (p[0], p[1], p[2] - size / 2.0), predefined_type=kind)
    typed(e, "IfcDuctFittingType", "Duct %s" % kind.title(), kind)
    members[system].append(e)
    return e


fitting_n = 0
for r in D["runs"]:
    pts = [tuple(p) for p in r["points"]]
    w, h = run_dims(r)
    elbow = fitting_size(r)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        # trim at interior vertices (elbows) and at node fittings
        if i > 0:
            a = trim(a, b, elbow / 2.0)
        elif tuple(round(v, 3) for v in a) in node_fittings and not r.get("tap_on"):
            a = trim(a, b, node_fittings[tuple(round(v, 3) for v in a)][1] / 2.0)
        elif r.get("tap_on"):
            mw, mh = run_dims(runs[r["tap_on"]])
            a = trim(a, b, (mw if abs(b[2] - a[2]) < 1e-6 and abs(b[0] - a[0]) < 1e-6 else mw) / 2.0)
        if i < len(pts) - 2:
            b = trim(b, a, elbow / 2.0)
        elif tuple(round(v, 3) for v in b) in node_fittings:
            b = trim(b, a, node_fittings[tuple(round(v, 3) for v in b)][1] / 2.0)
        duct_segment(r, a, b, i + 1)
    for i in range(1, len(pts) - 1):
        fitting_n += 1
        duct_fitting("BEND", pts[i], elbow, r["system"], "%s elbow %d" % (r["id"], i))
    if r.get("tap_on"):
        fitting_n += 1
        main = runs[r["tap_on"]]
        duct_fitting("JUNCTION", pts[0], fitting_size(r), r["system"], "%s takeoff on %s" % (r["id"], main["id"]))

for key, (kind, size, system) in node_fittings.items():
    fitting_n += 1
    names = "/".join(r["id"] for r in node_runs[key])
    duct_fitting(kind, key, size, system, "%s %s" % (kind.lower(), names))

for t in D["terminals"]:
    face = t["face_in"] / 12.0
    thick = 0.5
    rep = extrusion(rect_profile(face, face), thick)
    if t["kind"] == "supply_diffuser":
        e = element("IfcAirTerminal", t["tag"], rep, (t["x"], t["y"], t["z"]), predefined_type="DIFFUSER", tag=t["tag"])
        typed(e, "IfcAirTerminalType", "Supply Diffuser 24x24 Lay-in, %d in neck" % t["neck_in"], "DIFFUSER")
        pset(e, "HVAC_Design", {"AirflowCFM": float(t["cfm"]), "NeckDiameterIn": float(t["neck_in"]), "ServedBy": t["served_by"]})
        members["SA"].append(e)
    else:
        e = element("IfcAirTerminal", t["tag"], rep, (t["x"], t["y"], t["z"]), predefined_type="GRILLE", tag=t["tag"])
        typed(e, "IfcAirTerminalType", "Return Grille 24x24 Lay-in Egg Crate", "GRILLE")
        pset(e, "HVAC_Design", {"AirflowCFM": float(t["cfm"]), "ServedBy": "Ceiling plenum"})
        members["RA"].append(e)

for k, s in systems.items():
    ifcopenshell.api.system.assign_system(model, products=members[k], system=s)

model.write(OUT)
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
for k in sorted(counts):
    print("  %-22s %d" % (k, counts[k]))
print("  duct fittings total   ", fitting_n)

print("run verify_ifc.py to validate the schema and rebuild every solid")
