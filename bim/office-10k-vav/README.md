# 10,000 sf Office - Revit model with central AHU, VAV and fan-powered boxes

Single-storey 100 ft x 100 ft office (10,000 sf) with a central air handler in an
interior mechanical room, interior single-duct VAV boxes and series fan-powered
boxes serving perimeter private offices and corner conference rooms. Airflows are
sized for Denver, Colorado exposures with plan north up.  Everything in this folder is generated from one
design file, `design.py`, so geometry, airflow and schedules always agree.

## What is in this folder

| File | What it is |
|---|---|
| `Office-10k-VAV-Mechanical.ifc` | IFC4 model, length unit feet (rev 2 layout). Link it (Insert > Link IFC) or open it (File > Open > IFC) in Revit 2020 or later. Revit maps IfcWall, IfcSlab, IfcColumn, IfcCovering, IfcSpace, IfcDuctSegment, IfcDuctFitting, IfcAirTerminal, IfcAirTerminalBox and IfcUnitaryEquipment to the matching Revit categories, and each element carries an `HVAC_Design` property set (airflow, size, velocity, zone). |
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
2. draws exterior walls, mechanical room walls, office and conference room partitions, columns, floor, roof and ACT ceilings at 9 ft;
3. draws space separation lines and places a Space for each of the 28 zones plus the mechanical room, with its design supply airflow;
4. creates every duct run with the sizes below, then inserts elbows, transitions, tees, crosses and takeoffs from the duct type's routing preferences;
5. places AHU-1, the 4 VAV boxes, the 12 fan-powered boxes, 44 supply diffusers, 36 return grilles and the OA louver. It searches the open project, then the Revit content library, for suitable families (`VAV Unit - Single Duct`, `VAV Unit - ... Fan Powered`, `Supply Diffuser`, `Return Diffuser`) and otherwise places a DirectShape box of the right size in the right category so nothing is missing;
6. sets Mark, Comments and Flow on terminals and boxes.

Fittings are created with try/except around each one; anything Revit refuses is
listed in the dialog at the end so it can be fixed by hand (usually a routing
preference without a tee or takeoff family). Where a placeholder box was used,
swap in the real family and use Modify > Connect Into to join the ducts.

## Design basis (rev 2: perimeter offices and corner conference rooms, Denver)

Plan up is north. Airflows carry Denver, Colorado (ASHRAE climate zone 5B)
exposure factors: relative to a north zone, east x1.25, west x1.35, south x1.50.
Interior zones are load-driven at 0.9 cfm/sf.

| Item | Value |
|---|---|
| Building | 100 ft x 100 ft, 10,000 sf, one storey, 14 ft to roof deck, 9 ft ceiling, 25 ft column grid |
| Perimeter program | 15 ft deep private offices (12 ft wide, 180 sf) along all four facades, five per facade, a 20 ft x 20 ft conference room at each corner, 5 ft corridor behind the rooms. Partitions to the ceiling, plenum return above |
| Interior | Open office in four quadrants (708 sf NW and NE beside the mechanical room, 1,200 sf SW and SE, corridors included), 384 sf mechanical room M-101 at the centre |
| AHU-1 | Indoor VAV air handler, 10,000 cfm supply, 1,800 cfm minimum outside air, 25 tons cooling, 300 MBH heating, 2.5 in. w.g. external static, 15 hp supply fan, airside economizer, MERV-13 |
| Primary (design) airflow | 8,830 cfm: 3,970 cfm to 4 interior VAV boxes, 4,860 cfm to 12 perimeter fan-powered boxes (series boxes deliver 1.5 x primary to the rooms) |
| Outside air | Louver L-1 (36 x 30) on the north wall above the ceiling at X = 58 ft, 22x14 duct to the AHU |
| Return | Ceiling plenum: one 24x24 grille per office, two per conference room, eight in the open office (36 grilles); 48x28 return duct open to the plenum outside the mechanical room |
| Distribution | Medium-pressure ring main 23 ft inside the exterior face at 11 ft 6 in. centreline: 36x24 riser, 28x16 mains, 12x10 to 14x10 ring legs; low-pressure headers in the corridor ceilings; round runouts to 24x24 lay-in diffusers, one per office, two per conference room |
| Perimeter airflow (fan air) | North office 180 cfm (1.0 cfm/sf), east 225 (1.25), west 245 (1.35), south 270 (1.5); conference rooms 1.2 cfm/sf x worst exposure: NE 600, NW 650, SE 720, SW 720 cfm |
| Interior VAV | Single-duct pressure-independent, cooling only, 905 cfm (NW, NE) and 1,080 cfm (SW, SE), 30% minimum, 10 in. inlets, 4 diffusers each |
| Velocities | Mains at or below 1,500 fpm, low-pressure duct at or below 900 fpm (`schedule_ducts.csv`) |

### Perimeter boxes

Series fan-powered boxes with ECM fans and electric reheat (25 Btuh/sf), each
mounted above the corridor ceiling. Boxes 1 serve offices 1 to 3 of a facade,
boxes 2 serve offices 4 and 5, and each corner conference room has its own box.

| Box | Zones served | Primary cfm | Fan cfm | Inlet (in) | Heat (kW) |
|---|---|---|---|---|---|
| FPB-N1 | 102, 103, 104 | 360 | 540 | 6 | 4 |
| FPB-N2 | 105, 106 | 240 | 360 | 6 | 3 |
| FPB-NW | 101 | 435 | 650 | 8 | 3 |
| FPB-E1 | 108, 109, 110 | 450 | 675 | 8 | 4 |
| FPB-E2 | 111, 112 | 300 | 450 | 6 | 3 |
| FPB-NE | 107 | 400 | 600 | 8 | 3 |
| FPB-S1 | 114, 115, 116 | 540 | 810 | 8 | 4 |
| FPB-S2 | 117, 118 | 360 | 540 | 6 | 3 |
| FPB-SE | 113 | 480 | 720 | 8 | 3 |
| FPB-W1 | 120, 121, 122 | 490 | 735 | 8 | 4 |
| FPB-W2 | 123, 124 | 325 | 490 | 6 | 3 |
| FPB-SW | 119 | 480 | 720 | 8 | 3 |

### Zones

Zone numbers run clockwise from the NW corner: 101 Conference NW, 102 to 106
North Offices 1 to 5, 107 Conference NE, 108 to 112 East Offices, 113 Conference
SE, 114 to 118 South Offices, 119 Conference SW, 120 to 124 West Offices,
125 to 128 interior open office, M-101 mechanical room. `schedule_zones.csv`
lists area, box and design airflow for every zone.

### Duct routing

* AHU-1 discharges up through 36x24 riser SA-01, south through the mechanical
  room wall to the east-west main at Y = 47 ft.
* Mains SA-ME / SA-MW (28x16) run east and west, reduce after each interior VAV
  tap, and end in bull-head tees at X = 77 ft and X = 23 ft.
* Ring legs run north and south 23 ft inside the east and west walls, turn the
  corners and stop just past the last north or south box tap, so the ring is
  four dead-ended legs rather than a loop. Every box taps the leg nearest it
  with a short 8x8 to 12x10 branch.
* Office boxes discharge toward the facade into a header on the room centre
  line with a leg each way and one round runout per office. Conference boxes
  discharge into an L-shaped header with two runouts.
* Interior VAVs are unchanged from rev 1: a header spine with two pairs of
  round runouts.

### Checks run on the design

`make_drawings.py` fails if any duct, box or column clashes with another, if a
run end is not on its equipment connector, or if a velocity limit is exceeded.
`verify_ifc.py` validates the IFC4 schema and rebuilds every one of the 472
solids with the ifcopenshell geometry kernel.

## Assumptions and limits

* Single storey slab-on-grade with an exterior wall placeholder (12 in. generic) and
  a roof deck; no doors, windows, lighting or plumbing. The AHU is a box of the
  right footprint with its connections on top; replace it with a manufacturer family.
* Loads are rule-of-thumb (1.0 to 1.5 cfm/sf perimeter by exposure, 0.9 cfm/sf
  interior, 40% glazing assumed). Run a load calculation before sizing equipment for construction.
* Hot-water piping is avoided by using electric reheat in the perimeter boxes;
  swap to hot-water coils if a boiler plant is planned.
* The IFC contains geometry, types, systems and properties but no IfcRelConnectsPorts
  topology; Revit links it as geometry with properties. The native script builds
  the connected duct network, so use that when you need Revit's system browser,
  pressure-loss and sizing tools.
* The Revit script was written against the Revit 2022-2025 API and cannot be
  executed in this environment; the first run in your Revit build may report a
  few fittings that need a routing-preference family loaded.
