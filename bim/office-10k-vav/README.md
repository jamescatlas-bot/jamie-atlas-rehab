# 10,000 sf Office - Revit model with central AHU, VAV and fan-powered boxes

Single-storey 100 ft x 100 ft office (10,000 sf) with a central air handler in an
interior mechanical room, interior single-duct VAV boxes and series fan-powered
boxes serving the perimeter.  Everything in this folder is generated from one
design file, `design.py`, so geometry, airflow and schedules always agree.

## What is in this folder

| File | What it is |
|---|---|
| `Office-10k-VAV-Mechanical.ifc` | IFC4 model, length unit feet. Link it (Insert > Link IFC) or open it (File > Open > IFC) in Revit 2020 or later. Revit maps IfcWall, IfcSlab, IfcColumn, IfcCovering, IfcSpace, IfcDuctSegment, IfcDuctFitting, IfcAirTerminal, IfcAirTerminalBox and IfcUnitaryEquipment to the matching Revit categories, and each element carries an `HVAC_Design` property set (airflow, size, velocity, zone). |
| `CreateOfficeModel.py` | Revit API script that builds the same model as **native** Revit elements: levels, grids, walls, floor, roof, ceilings, spaces, ducts with elbows / transitions / tees / crosses / takeoffs, equipment and air terminals, assigned to Supply, Return and Outside Air system types. Run it in a project started from the Mechanical template. |
| `design.json` | The design data the Revit script reads. Regenerate with `python design.py`. |
| `plan.svg` | Ceiling plan at 9 ft AFF with zones, ductwork, equipment and terminals. |
| `isometric.svg` | Axonometric of the IFC (roof and two walls removed). |
| `schedule_zones.csv`, `schedule_equipment.csv`, `schedule_ducts.csv`, `schedule_air_terminals.csv` | Schedules. |
| `design.py` | Design basis and all geometry. Edit this to change the building or the system. |
| `build_ifc.py`, `verify_ifc.py`, `make_drawings.py`, `render_iso.py` | Generators. `verify_ifc.py` validates the IFC against the schema and rebuilds every solid with the geometry kernel. |

Regenerate everything:

```bash
pip install -r requirements.txt
python design.py          # design.json
python make_drawings.py   # clash and velocity checks, schedules, plan.svg
python build_ifc.py       # Office-10k-VAV-Mechanical.ifc
python verify_ifc.py
python render_iso.py      # isometric.svg
```

## Using it in Revit

**Fastest: link the IFC.** Insert > Link IFC, pick `Office-10k-VAV-Mechanical.ifc`.
You get every wall, column, slab, ceiling, space, duct, fitting, box, diffuser and
grille with its properties, and can model against it, tag it and schedule it. Use
File > Open > IFC instead if you want the elements editable in a new project.

**Native elements: run the script.** Start a project from the Mechanical template,
put `CreateOfficeModel.py` and `design.json` in the same folder, and run the
script with pyRevit (Run), RevitPythonShell, or a Dynamo Python node (set
`DESIGN_JSON` at the top of the file for Dynamo). The script:

1. creates Level 1 (0 ft) and Roof (14 ft), grids A to E and 1 to 5 at 25 ft;
2. draws exterior walls, mechanical room walls, columns, floor, roof and ACT ceilings at 9 ft;
3. draws space separation lines and places a Space for each of the 12 zones plus the mechanical room, with its design supply airflow;
4. creates every duct run with the sizes below, then inserts elbows, transitions, tees, crosses and takeoffs from the duct type's routing preferences;
5. places AHU-1, the 4 VAV boxes, the 8 fan-powered boxes, 48 supply diffusers, 16 return grilles and the OA louver. It searches the open project, then the Revit content library, for suitable families (`VAV Unit - Single Duct`, `VAV Unit - ... Fan Powered`, `Supply Diffuser`, `Return Diffuser`) and otherwise places a DirectShape box of the right size in the right category so nothing is missing;
6. sets Mark, Comments and Flow on terminals and boxes.

Fittings are created with try/except around each one; anything Revit refuses is
listed in the dialog at the end so it can be fixed by hand (usually a routing
preference without a tee or takeoff family). Where a placeholder box was used,
swap in the real family and use Modify > Connect Into to join the ducts.

## Design basis

| Item | Value |
|---|---|
| Building | 100 ft x 100 ft, 10,000 sf, one storey, 14 ft to roof deck, 9 ft ceiling, 25 ft column grid |
| Mechanical room M-101 | 24 ft x 16 ft (384 sf) at the centre of the plan |
| AHU-1 | Indoor VAV air handler, 8,500 cfm supply, 1,500 cfm minimum outside air, 22 tons cooling, 250 MBH heating, 2.5 in. w.g. external static, 10 hp supply fan, airside economizer, MERV-13 |
| Primary (design) airflow | 8,000 cfm: 3,200 cfm to 4 interior VAV boxes, 4,800 cfm to 8 perimeter fan-powered boxes |
| Outside air | Louver L-1 (36 x 30) on the north wall, 20x14 duct to the AHU mixing section |
| Return | Ceiling plenum return, 16 x 24x24 egg-crate grilles (440 cfm each), 36x24 return duct open to the plenum outside the mechanical room |
| Distribution | Medium-pressure 2 in. w.g. class mains at 11 ft 6 in. centreline: 36x24 riser, 28x18 east / west mains, 14x12 perimeter legs; low-pressure 1 in. w.g. class downstream of the boxes; round runouts to 24x24 lay-in diffusers |
| Interior zones | 109 to 112: single-duct pressure-independent VAV, cooling only, 700 to 900 cfm, 30% minimum, 4 diffusers each on a 12 ft deep spine |
| Perimeter zones | 101 to 108, 20 ft deep: series fan-powered boxes with ECM fan and electric reheat. North and south boxes 700 cfm primary / 1,050 cfm fan, 7 kW; east and west boxes 500 / 750 cfm, 5 kW. Each box discharges into a 16x10 or 14x10 header feeding a cross header with 4 diffusers 6 ft off the exterior wall |
| Velocities | Mains at or below 1,550 fpm, low-pressure duct at or below 1,050 fpm (`schedule_ducts.csv`) |

### Zones

| Zone | Name | Box | Area (sf) | Supply (cfm) |
|---|---|---|---|---|
| 101 / 102 | North office west / east | FPB-N1 / N2 | 1,000 each | 1,050 each (700 primary) |
| 103 / 104 | South office west / east | FPB-S1 / S2 | 1,000 each | 1,050 each (700 primary) |
| 105 / 106 | East office south / north | FPB-E1 / E2 | 600 each | 750 each (500 primary) |
| 107 / 108 | West office south / north | FPB-W1 / W2 | 600 each | 750 each (500 primary) |
| 109 / 110 | Interior NW / NE open office | VAV-1 / 2 | 708 each | 700 each |
| 111 / 112 | Interior SW / SE open office | VAV-3 / 4 | 900 each | 900 each |
| M-101 | Mechanical room | AHU-1 | 384 | - |

### Duct routing

* AHU-1 discharges up through 36x24 riser SA-01, south through the mechanical
  room wall to the east-west main at Y = 47 ft.
* Mains SA-02 / SA-03 (28x18) run east and west, reduce to 22x16 after the
  interior VAV taps, and end in bull-head tees at X = 80 ft and X = 20 ft.
* Perimeter legs SA-06 / 07 / 10 / 11 (14x12) run north and south 20 ft inside
  the east and west walls, tap the east and west fan-powered boxes, reduce to
  12x10 and turn in along Y = 80 ft / 20 ft to feed the north and south boxes.
* Each interior VAV discharges into a header spine with two pairs of 10 in.
  round runouts to 24x24 diffusers.
* Each fan-powered box discharges toward the exterior wall into a cross header
  6 ft off the wall with four diffusers 10 to 12 ft apart. Induced plenum air
  enters the box through its plenum inlet (no duct).

### Checks run on the design

`make_drawings.py` fails if any duct, box or column clashes with another, if a
run end is not on its equipment connector, or if a velocity limit is exceeded.
`verify_ifc.py` validates the IFC4 schema and rebuilds every one of the 364
solids with the ifcopenshell geometry kernel.

## Assumptions and limits

* Single storey slab-on-grade with an exterior wall placeholder (12 in. generic) and
  a roof deck; no doors, windows, lighting or plumbing. The AHU is a box of the
  right footprint with its connections on top; replace it with a manufacturer family.
* Loads are rule-of-thumb (about 1 cfm/sf perimeter, 1 cfm/sf interior). Run a
  load calculation before sizing equipment for construction.
* Hot-water piping is avoided by using electric reheat in the perimeter boxes;
  swap to hot-water coils if a boiler plant is planned.
* The IFC contains geometry, types, systems and properties but no IfcRelConnectsPorts
  topology; Revit links it as geometry with properties. The native script builds
  the connected duct network, so use that when you need Revit's system browser,
  pressure-loss and sizing tools.
* The Revit script was written against the Revit 2022-2025 API and cannot be
  executed in this environment; the first run in your Revit build may report a
  few fittings that need a routing-preference family loaded.
