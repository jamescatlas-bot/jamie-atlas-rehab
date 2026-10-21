# -*- coding: utf-8 -*-
"""
CreateOfficeModel.py
Builds the 10,000 sf office and its HVAC as NATIVE Revit elements:
levels, grids, walls, floor, roof, ceilings, spaces (one per thermal zone),
ducts with elbows / transitions / tees / crosses / takeoffs, the air handler,
VAV and series fan-powered terminal boxes, supply diffusers, return grilles
and the outside-air louver.

How to run (inside Revit, with a Mechanical template project open):
  * pyRevit  : pyRevit tab > "Run" (or add this file as a pushbutton)
  * RevitPythonShell : open the shell and run the file
  * Dynamo   : Python Script node, paste the contents (set DESIGN_JSON below)

Input: design.json next to this file (generate it with `python design.py`).
Units: the design is in feet, which are Revit's internal length units.

Families: the script first looks for family symbols already in the project,
then in the Revit content library (C:\\ProgramData\\Autodesk\\RVT 20xx\\Libraries),
and finally falls back to a DirectShape box in the right category so the
model is always complete.  Replace placeholders with real families later and
use "Connect Into" to join the ducts.

Written for the Revit 2022-2025 API and runs under IronPython 2.7 or CPython 3.
"""
from __future__ import print_function

import clr
import glob
import json
import math
import os

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import (  # noqa: E402
    BuiltInCategory, BuiltInParameter, Ceiling, CurveArray, CurveLoop, DirectShape,
    ElementId, ElementTransformUtils, ElementTypeGroup, FamilySymbol, FilteredElementCollector, Floor, FloorType,
    GeometryCreationUtilities, GeometryObject, Grid, Level, Line, ModelCurveArray, Plane, SketchPlane, Transaction,
    UV, ViewFamily, ViewFamilyType, ViewPlan, Wall, WallKind, WallType, XYZ, UnitUtils, ConnectorProfileType,
    MEPSystemClassification, CeilingType,
)
from Autodesk.Revit.DB.Mechanical import Duct, DuctType, MechanicalSystemType, MechanicalUtils  # noqa: E402
from Autodesk.Revit.DB.Structure import StructuralType  # noqa: E402
from System.Collections.Generic import List  # noqa: E402

# --------------------------------------------------------------------------
# document / transaction plumbing (pyRevit, RPS and Dynamo)
# --------------------------------------------------------------------------
DESIGN_JSON = None   # set an absolute path here when running from Dynamo
IN_DYNAMO = False
try:
    doc = __revit__.ActiveUIDocument.Document          # pyRevit / RevitPythonShell
except NameError:
    clr.AddReference("RevitServices")
    from RevitServices.Persistence import DocumentManager
    from RevitServices.Transactions import TransactionManager
    doc = DocumentManager.Instance.CurrentDBDocument
    IN_DYNAMO = True

LOG = []


def log(msg):
    LOG.append(msg)
    print(msg)


class Tx(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        if IN_DYNAMO:
            TransactionManager.Instance.EnsureInTransaction(doc)
        else:
            self.t = Transaction(doc, self.name)
            self.t.Start()
        return self

    def __exit__(self, et, ev, tb):
        if IN_DYNAMO:
            TransactionManager.Instance.TransactionTaskDone()
        else:
            if et is None:
                self.t.Commit()
            else:
                self.t.RollBack()
                log("transaction %s rolled back: %s" % (self.name, ev))
        return False


def load_design():
    path = DESIGN_JSON
    if not path:
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design.json")
        except NameError:
            raise Exception("Set DESIGN_JSON to the full path of design.json")
    with open(path) as f:
        return json.load(f)


D = load_design()
B = D["building"]
TOL = 0.01


def P(p):
    return XYZ(float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0)


def cfm_internal(cfm):
    try:
        from Autodesk.Revit.DB import UnitTypeId
        return UnitUtils.ConvertToInternalUnits(float(cfm), UnitTypeId.CubicFeetPerMinute)
    except Exception:  # Revit 2020 and earlier
        from Autodesk.Revit.DB import DisplayUnitType
        return UnitUtils.ConvertToInternalUnits(float(cfm), DisplayUnitType.DUT_CUBIC_FEET_PER_MINUTE)


def set_param(el, names, value):
    """Set the first writable parameter found.  Names are BuiltInParameter member
    names (e.g. "ALL_MODEL_MARK") or parameter display names (e.g. "Flow")."""
    for n in names:
        try:
            p = None
            bip = getattr(BuiltInParameter, n, None)
            if bip is not None:
                p = el.get_Parameter(bip)
            if p is None:
                p = el.LookupParameter(n)
            if p and not p.IsReadOnly:
                p.Set(value)
                return True
        except Exception:
            pass
    return False


# --------------------------------------------------------------------------
# levels, grids
# --------------------------------------------------------------------------
levels = {}
with Tx("Office model - levels and grids"):
    existing = list(FilteredElementCollector(doc).OfClass(Level))
    for lv in B["levels"]:
        match = [e for e in existing if abs(e.Elevation - lv["elevation"]) < TOL]
        if match:
            levels[lv["name"]] = match[0]
        else:
            new = Level.Create(doc, lv["elevation"])
            try:
                new.Name = lv["name"]
            except Exception:
                pass
            levels[lv["name"]] = new
    for g in B["grids"]:
        try:
            gr = Grid.Create(doc, Line.CreateBound(P(g["start"]), P(g["end"])))
            gr.Name = g["id"]
        except Exception as ex:
            log("grid %s: %s" % (g["id"], ex))
level1 = levels["Level 1"]
roof_level = levels["Roof"]

# --------------------------------------------------------------------------
# walls, columns, floor, roof, ceilings
# --------------------------------------------------------------------------
wall_types = sorted([w for w in FilteredElementCollector(doc).OfClass(WallType) if w.Kind == WallKind.Basic],
                    key=lambda w: w.Width)
ext_type = wall_types[-1] if wall_types else None
int_type = wall_types[0] if wall_types else None


def curve_loop(poly):
    loop = CurveLoop()
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        loop.Append(Line.CreateBound(P(a), P(b)))
    return loop


def curve_array(poly):
    ca = CurveArray()
    n = len(poly)
    for i in range(n):
        ca.Append(Line.CreateBound(P(poly[i]), P(poly[(i + 1) % n])))
    return ca


with Tx("Office model - architecture"):
    for w in B["walls"]:
        wt = ext_type if w["kind"] == "exterior" else int_type
        try:
            wall = Wall.Create(doc, Line.CreateBound(P(w["start"]), P(w["end"])), wt.Id, level1.Id,
                               float(w["height"]), 0.0, False, w["kind"] == "exterior")
            set_param(wall, ["ALL_MODEL_MARK"], w["id"])
        except Exception as ex:
            log("wall %s: %s" % (w["id"], ex))

    col_type_id = doc.GetDefaultFamilyTypeId(ElementId(BuiltInCategory.OST_Columns))
    col_sym = doc.GetElement(col_type_id) if col_type_id != ElementId.InvalidElementId else None
    if col_sym is None:
        col_type_id = doc.GetDefaultFamilyTypeId(ElementId(BuiltInCategory.OST_StructuralColumns))
        col_sym = doc.GetElement(col_type_id) if col_type_id != ElementId.InvalidElementId else None
    if col_sym is not None:
        if not col_sym.IsActive:
            col_sym.Activate()
        for c in B["columns"]:
            try:
                st = StructuralType.Column if col_sym.Category.Id == ElementId(BuiltInCategory.OST_StructuralColumns) else StructuralType.NonStructural
                inst = doc.Create.NewFamilyInstance(XYZ(c["x"], c["y"], 0.0), col_sym, level1, st)
                set_param(inst, ["FAMILY_TOP_LEVEL_PARAM"], roof_level.Id)
                set_param(inst, ["ALL_MODEL_MARK"], c["id"])
            except Exception as ex:
                log("column %s: %s" % (c["id"], ex))
    else:
        log("no column family in project: columns skipped (load a column family and re-run that part)")

    f = B["floor"]
    try:
        ft_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FloorType)
        if ft_id == ElementId.InvalidElementId:
            ft_id = FilteredElementCollector(doc).OfClass(FloorType).FirstElementId()
        try:
            loops = List[CurveLoop]([curve_loop(f["outline"])])
            Floor.Create(doc, loops, ft_id, level1.Id)
        except AttributeError:   # Revit 2021 and earlier
            doc.Create.NewFloor(curve_array(f["outline"]), False)
    except Exception as ex:
        log("floor: %s" % ex)

    r = B["roof"]
    try:
        rt_id = doc.GetDefaultElementTypeId(ElementTypeGroup.RoofType)
        rt = doc.GetElement(rt_id)
        result = doc.Create.NewFootPrintRoof(curve_array(r["outline"]), roof_level, rt)
        # IronPython / pythonnet return (roof, modelCurveMapping) for the out parameter
    except Exception as ex:
        log("footprint roof failed (%s); placing a floor slab at the roof level instead" % ex)
        try:
            loops = List[CurveLoop]([curve_loop(r["outline"])])
            Floor.Create(doc, loops, doc.GetDefaultElementTypeId(ElementTypeGroup.FloorType), roof_level.Id)
        except Exception as ex2:
            log("roof slab: %s" % ex2)

    try:
        ct_id = doc.GetDefaultElementTypeId(ElementTypeGroup.CeilingType)
        if ct_id == ElementId.InvalidElementId:
            ct_id = FilteredElementCollector(doc).OfClass(CeilingType).FirstElementId()
        for c in B["ceilings"]:
            loops = List[CurveLoop]([curve_loop(c["outline"])])
            ceil = Ceiling.Create(doc, loops, ct_id, level1.Id)
            set_param(ceil, ["CEILING_HEIGHTABOVELEVEL_PARAM"], float(c["elevation"]))
    except Exception as ex:
        log("ceilings skipped (needs Revit 2022+): %s" % ex)

# --------------------------------------------------------------------------
# spaces (thermal zones)
# --------------------------------------------------------------------------
def plan_view_for(level):
    for v in FilteredElementCollector(doc).OfClass(ViewPlan):
        if not v.IsTemplate and v.GenLevel is not None and v.GenLevel.Id == level.Id:
            return v
    vft = [t for t in FilteredElementCollector(doc).OfClass(ViewFamilyType) if t.ViewFamily == ViewFamily.FloorPlan][0]
    return ViewPlan.Create(doc, vft.Id, level.Id)


def centroid(poly):
    a = cx = cy = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        a += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    a *= 0.5
    return cx / (6 * a), cy / (6 * a)


with Tx("Office model - spaces"):
    try:
        view = plan_view_for(level1)
        sp = SketchPlane.Create(doc, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ(0, 0, level1.Elevation)))
        edges = set()
        ca = CurveArray()
        for z in D["zones"]:
            poly = z["polygon"]
            for i in range(len(poly)):
                a, b = tuple(poly[i]), tuple(poly[(i + 1) % len(poly)])
                key = tuple(sorted([a, b]))
                if key in edges:
                    continue
                edges.add(key)
                ca.Append(Line.CreateBound(P(a), P(b)))
        doc.Create.NewSpaceBoundaryLines(sp, ca, view)
        doc.Regenerate()
        for z in D["zones"]:
            cx, cy = centroid(z["polygon"])
            space = doc.Create.NewSpace(level1, UV(cx, cy))
            space.Name = z["name"]
            space.Number = z["number"]
            if z["supply_cfm"]:
                set_param(space, ["ROOM_DESIGN_SUPPLY_AIRFLOW_PARAM"], cfm_internal(z["supply_cfm"]))
    except Exception as ex:
        log("spaces: %s" % ex)

# --------------------------------------------------------------------------
# duct and system types
# --------------------------------------------------------------------------
duct_types = list(FilteredElementCollector(doc).OfClass(DuctType))


def type_name(t):
    try:
        return t.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() or ""
    except Exception:
        return ""


def pick_duct_type(shape, prefer):
    cands = [t for t in duct_types if t.Shape == shape]
    for key in prefer:
        for t in cands:
            if key.lower() in type_name(t).lower():
                return t
    return cands[0] if cands else None


rect_type = pick_duct_type(ConnectorProfileType.Rectangular, ["Radius Elbows / Tees", "Tees", "Mitered Elbows / Tees"])
round_type = pick_duct_type(ConnectorProfileType.Round, ["Taps / Short Radius", "Taps"])
if rect_type is None or round_type is None:
    raise Exception("Project needs at least one rectangular and one round duct type (use the Mechanical template).")

sys_types = list(FilteredElementCollector(doc).OfClass(MechanicalSystemType))


def pick_system(classification, prefer_names):
    for n in prefer_names:
        for s in sys_types:
            if n.lower() in type_name(s).lower():
                return s
    for s in sys_types:
        if s.SystemClassification == classification:
            return s
    return sys_types[0]


system_type = {
    "SA": pick_system(MEPSystemClassification.SupplyAir, ["Supply Air"]),
    "RA": pick_system(MEPSystemClassification.ReturnAir, ["Return Air"]),
    "OA": pick_system(MEPSystemClassification.SupplyAir, ["Outside Air", "Outdoor Air", "Supply Air"]),
}

# --------------------------------------------------------------------------
# ducts
# --------------------------------------------------------------------------
runs = dict((r["id"], r) for r in D["runs"])
run_ducts = {}          # run id -> list of Duct elements (in order)


def make_duct(r, a, b):
    dt = round_type if r["shape"] == "round" else rect_type
    d = Duct.Create(doc, system_type[r["system"]].Id, dt.Id, level1.Id, P(a), P(b))
    if r["shape"] == "round":
        set_param(d, ["RBS_CURVE_DIAMETER_PARAM"], r["diameter_in"] / 12.0)
    else:
        set_param(d, ["RBS_CURVE_WIDTH_PARAM"], r["width_in"] / 12.0)
        set_param(d, ["RBS_CURVE_HEIGHT_PARAM"], r["height_in"] / 12.0)
    set_param(d, ["ALL_MODEL_INSTANCE_COMMENTS"], "%s %s %s cfm" % (r["id"], r["name"], r["cfm"]))
    set_param(d, ["ALL_MODEL_MARK"], r["id"])
    return d


def free_connector(el, pt, tol=0.05):
    cm = el.ConnectorManager if hasattr(el, "ConnectorManager") else el.MEPModel.ConnectorManager
    best = None
    for c in cm.Connectors:
        if c.IsConnected:
            continue
        dist = c.Origin.DistanceTo(pt)
        if dist < tol and (best is None or dist < best[0]):
            best = (dist, c)
    return best[1] if best else None


def duct_containing(run_id, pt):
    for d in run_ducts[run_id]:
        crv = d.Location.Curve
        if crv.Distance(pt) < TOL:
            return d
    return None


def is_collinear(c1, c2):
    return abs(abs(c1.CoordinateSystem.BasisZ.DotProduct(c2.CoordinateSystem.BasisZ)) - 1.0) < 1e-6


with Tx("Office model - ducts"):
    for r in D["runs"]:
        pts = r["points"]
        ducts = []
        for i in range(len(pts) - 1):
            try:
                ducts.append(make_duct(r, pts[i], pts[i + 1]))
            except Exception as ex:
                log("duct %s segment %d: %s" % (r["id"], i + 1, ex))
        run_ducts[r["id"]] = ducts

with Tx("Office model - duct fittings"):
    # 1. elbows at the interior vertices of every run
    for r in D["runs"]:
        pts = r["points"]
        ducts = run_ducts[r["id"]]
        for i in range(1, len(pts) - 1):
            if i >= len(ducts):
                break
            node = P(pts[i])
            c1 = free_connector(ducts[i - 1], node)
            c2 = free_connector(ducts[i], node)
            try:
                doc.Create.NewElbowFitting(c1, c2)
            except Exception as ex:
                log("elbow %s vertex %d: %s" % (r["id"], i, ex))

    # 2. fittings where run ends meet (transition / elbow / tee / cross)
    nodes = {}
    for r in D["runs"]:
        ends = [r["points"][-1]] if r.get("tap_on") else [r["points"][0], r["points"][-1]]
        for p in ends:
            key = tuple(round(v, 3) for v in p)
            nodes.setdefault(key, []).append(r)
    for key, rs in nodes.items():
        if len(rs) < 2:
            continue
        node = XYZ(*key)
        conns = []
        for r in rs:
            for d in run_ducts[r["id"]]:
                c = free_connector(d, node)
                if c is not None:
                    conns.append(c)
                    break
        try:
            if len(conns) == 2:
                if is_collinear(conns[0], conns[1]):
                    doc.Create.NewTransitionFitting(conns[0], conns[1])
                else:
                    doc.Create.NewElbowFitting(conns[0], conns[1])
            elif len(conns) == 3:
                # the two collinear connectors are the "main"; the third is the branch
                order = None
                for i in range(3):
                    for j in range(i + 1, 3):
                        if is_collinear(conns[i], conns[j]):
                            k = 3 - i - j
                            order = (conns[i], conns[j], conns[k])
                if order is None:
                    order = tuple(conns)
                doc.Create.NewTeeFitting(order[0], order[1], order[2])
            elif len(conns) == 4:
                doc.Create.NewCrossFitting(conns[0], conns[1], conns[2], conns[3])
        except Exception as ex:
            log("node fitting at %s (%s): %s" % (key, "/".join(r["id"] for r in rs), ex))

    # 3. taps: round branches take off the main; rectangular branches get a tee (or cross)
    taps = {}
    for r in D["runs"]:
        if r.get("tap_on"):
            key = (r["tap_on"], tuple(round(v, 3) for v in r["points"][0]))
            taps.setdefault(key, []).append(r)
    for (main_id, key), branches in taps.items():
        node = XYZ(*key)
        main = duct_containing(main_id, node)
        if main is None:
            log("tap on %s at %s: main duct not found" % (main_id, key))
            continue
        bconns = []
        for br in branches:
            if run_ducts[br["id"]]:
                c = free_connector(run_ducts[br["id"]][0], node)
                if c is not None:
                    bconns.append(c)
        if not bconns:
            continue
        if all(b["shape"] == "round" for b in branches):
            for c in bconns:
                try:
                    doc.Create.NewTakeoffFitting(c, main)
                except Exception as ex:
                    log("takeoff %s on %s: %s" % ([b["id"] for b in branches], main_id, ex))
            continue
        try:
            new_id = MechanicalUtils.BreakCurve(doc, main.Id, node)
            second = doc.GetElement(new_id)
            run_ducts[main_id].append(second)
            m1 = free_connector(main, node)
            m2 = free_connector(second, node)
            if len(bconns) == 1:
                doc.Create.NewTeeFitting(m1, m2, bconns[0])
            else:
                doc.Create.NewCrossFitting(m1, m2, bconns[0], bconns[1])
        except Exception as ex:
            log("tee/cross %s on %s: %s; trying takeoff" % ([b["id"] for b in branches], main_id, ex))
            for c in bconns:
                try:
                    doc.Create.NewTakeoffFitting(c, main)
                except Exception as ex2:
                    log("takeoff fallback failed: %s" % ex2)

# --------------------------------------------------------------------------
# families: equipment and air terminals
# --------------------------------------------------------------------------
LIBRARY_ROOTS = glob.glob(r"C:\ProgramData\Autodesk\RVT 20*\Libraries")
FAMILY_SEARCH = {
    "AHU": (BuiltInCategory.OST_MechanicalEquipment, ["Air Handling Unit*", "*Air Handler*", "*AHU*"]),
    "VAV": (BuiltInCategory.OST_MechanicalEquipment, ["VAV Unit - Single Duct*", "*VAV*Single*", "*VAV*"]),
    "FPB": (BuiltInCategory.OST_MechanicalEquipment, ["*Series Fan Powered*", "*Fan Powered*", "*VAV*"]),
    "LOUVER": (BuiltInCategory.OST_MechanicalEquipment, ["*Louver*"]),
    "supply_diffuser": (BuiltInCategory.OST_DuctTerminal, ["Supply Diffuser*Round Neck*", "Supply Diffuser*"]),
    "return_grille": (BuiltInCategory.OST_DuctTerminal, ["Return Diffuser*", "Return Grille*", "Return*"]),
}
_symbol_cache = {}
_library_files = []


def library_files():
    if not _library_files:
        for root in LIBRARY_ROOTS:
            for dirpath, dirnames, filenames in os.walk(root):
                for fn in filenames:
                    if fn.lower().endswith(".rfa"):
                        _library_files.append(os.path.join(dirpath, fn))
        _library_files.append("")   # sentinel so an empty library is not re-walked
    return [f for f in _library_files if f]


def _match(name, pattern):
    import fnmatch
    return fnmatch.fnmatch(name.lower(), pattern.lower()) and "hosted" not in name.lower() and "sidewall" not in name.lower()


def find_symbol(kind):
    if kind in _symbol_cache:
        return _symbol_cache[kind]
    category, patterns = FAMILY_SEARCH[kind]
    sym = None
    symbols = [s for s in FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(category)]
    for pat in patterns:
        for s in symbols:
            if _match(s.Family.Name, pat):
                sym = s
                break
        if sym:
            break
    if sym is None:
        for root in LIBRARY_ROOTS:
            for pat in patterns:
                hits = [h for h in library_files() if _match(os.path.basename(h)[:-4], pat) and h.startswith(root)]
                hits = [h for h in hits if "imperial" in h.lower()] + [h for h in hits if "imperial" not in h.lower()]
                if hits and doc.LoadFamily(hits[0]):
                    fam_name = os.path.splitext(os.path.basename(hits[0]))[0]
                    for s in FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(category):
                        if s.Family.Name == fam_name:
                            sym = s
                            break
                if sym:
                    break
            if sym:
                break
    if sym is not None and not sym.IsActive:
        sym.Activate()
    _symbol_cache[kind] = sym
    if sym is None:
        log("no family found for %s: DirectShape placeholders will be used" % kind)
    return sym


def direct_shape_box(category, name, centre, length, width, height, angle_deg, z_bottom):
    cx, cy = centre[0], centre[1]
    hl, hw = length / 2.0, width / 2.0
    corners = [(-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)]
    a = math.radians(angle_deg)
    pts = [XYZ(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a), z_bottom) for x, y in corners]
    loop = CurveLoop()
    for i in range(4):
        loop.Append(Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    solid = GeometryCreationUtilities.CreateExtrusionGeometry(List[CurveLoop]([loop]), XYZ.BasisZ, height)
    ds = DirectShape.CreateElement(doc, ElementId(category))
    ds.SetShape(List[GeometryObject]([solid]))
    ds.Name = name
    set_param(ds, ["ALL_MODEL_MARK"], name)
    return ds


def place_family(sym, xy, z, angle_deg, mark):
    inst = doc.Create.NewFamilyInstance(XYZ(xy[0], xy[1], 0.0), sym, level1, StructuralType.NonStructural)
    if not set_param(inst, ["INSTANCE_FREE_HOST_OFFSET_PARAM", "INSTANCE_ELEVATION_PARAM", "Offset", "Elevation from Level"], float(z)):
        ElementTransformUtils.MoveElement(doc, inst.Id, XYZ(0, 0, z))
    if abs(angle_deg) > 1e-6:
        axis = Line.CreateBound(XYZ(xy[0], xy[1], 0), XYZ(xy[0], xy[1], 1))
        ElementTransformUtils.RotateElement(doc, inst.Id, axis, math.radians(angle_deg))
    set_param(inst, ["ALL_MODEL_MARK"], mark)
    return inst


def connect_nearby(inst, pt, tol=1.0):
    """Logically connect the unconnected duct connector at pt to the nearest family connector."""
    try:
        cm = inst.MEPModel.ConnectorManager
    except Exception:
        return
    for c in cm.Connectors:
        if c.IsConnected or c.Origin.DistanceTo(pt) > tol:
            continue
        for d in FilteredElementCollector(doc).OfClass(Duct):
            dc = free_connector(d, pt, tol)
            if dc is not None:
                try:
                    dc.ConnectTo(c)
                    return
                except Exception:
                    pass


with Tx("Office model - equipment and air terminals"):
    for q in D["equipment"]:
        cx, cy, cz = q["centre"]
        z_bottom = cz if q["kind"] == "AHU" else cz - q["height"] / 2.0
        sym = find_symbol(q["kind"])
        el = None
        if sym is not None:
            try:
                el = place_family(sym, (cx, cy), z_bottom, q["rotation_deg"], q["tag"])
                flow = q.get("primary_cfm") or q.get("supply_cfm") or q.get("outside_air_cfm")
                if flow:
                    set_param(el, ["Primary Air Flow", "Supply Air Flow", "Flow", "Air Flow"], cfm_internal(flow))
                for pt in (q["inlet"], q["outlet"]):
                    connect_nearby(el, P(pt), 2.0)
            except Exception as ex:
                log("%s family placement failed (%s); using DirectShape" % (q["tag"], ex))
                el = None
        if el is None:
            el = direct_shape_box(BuiltInCategory.OST_MechanicalEquipment, q["tag"], (cx, cy), q["length"],
                                  q["width"], q["height"], q["rotation_deg"], z_bottom)
        set_param(el, ["ALL_MODEL_INSTANCE_COMMENTS"], q.get("description", ""))

    for t in D["terminals"]:
        sym = find_symbol(t["kind"])
        el = None
        if sym is not None:
            try:
                el = place_family(sym, (t["x"], t["y"]), t["z"], 0.0, t["tag"])
                set_param(el, ["Flow", "Air Flow", "RBS_DUCT_FLOW_PARAM"], cfm_internal(t["cfm"]))
                if t["kind"] == "supply_diffuser":
                    connect_nearby(el, XYZ(t["x"], t["y"], t["z"] + 0.5), 1.5)
            except Exception as ex:
                log("%s family placement failed (%s); using DirectShape" % (t["tag"], ex))
                el = None
        if el is None:
            el = direct_shape_box(BuiltInCategory.OST_DuctTerminal, t["tag"], (t["x"], t["y"]),
                                  t["face_in"] / 12.0, t["face_in"] / 12.0, 0.5, 0.0, t["z"])
        set_param(el, ["ALL_MODEL_INSTANCE_COMMENTS"], "%s cfm, served by %s" % (t["cfm"], t["served_by"]))

n_ducts = sum(len(v) for v in run_ducts.values())
log("done: %d duct segments, %d equipment, %d air terminals, %d zones" % (
    n_ducts, len(D["equipment"]), len(D["terminals"]), len(D["zones"])))
if LOG:
    try:
        from Autodesk.Revit.UI import TaskDialog
        TaskDialog.Show("Office model", "\n".join(LOG[-25:]))
    except Exception:
        pass
