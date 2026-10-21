/*
 Builds Office-10k-VAV-Design-Review.docx: a complete, self-contained engineering
 review package generated from design.json and the CSV schedules.
   node build_review_doc.cjs
*/
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel, ImageRun,
  PageBreak, AlignmentType, LevelFormat, ShadingType, PageOrientation, BorderStyle, Footer, Header, PageNumber,
  TableOfContents, VerticalAlign,
} = require("docx");

const HERE = __dirname;
const D = JSON.parse(fs.readFileSync(path.join(HERE, "design.json"), "utf8"));
const T = D.totals;
const csv = (f) => {
  const lines = fs.readFileSync(path.join(HERE, f), "utf8").trim().split(/\r?\n/);
  const parse = (l) => { const out = []; let cur = "", q = false; for (const ch of l) { if (ch === '"') q = !q; else if (ch === "," && !q) { out.push(cur); cur = ""; } else cur += ch; } out.push(cur); return out; };
  const head = parse(lines[0]);
  return { head, rows: lines.slice(1).map(parse) };
};
const zones = csv("schedule_zones.csv"), equip = csv("schedule_equipment.csv"), ducts = csv("schedule_ducts.csv"), terms = csv("schedule_air_terminals.csv");

const FONT = "Calibri";
const LETTER = { width: 12240, height: 15840 };
const fmt = (n) => Number(n).toLocaleString("en-US");

// ---------- helpers ----------
const p = (text, opts = {}) => new Paragraph({ children: [new TextRun({ text, font: FONT, size: opts.size || 22, bold: opts.bold, italics: opts.italics, color: opts.color })], spacing: { after: opts.after == null ? 120 : opts.after }, alignment: opts.align });
const runs = (parts, opts = {}) => new Paragraph({ children: parts.map((t) => typeof t === "string" ? new TextRun({ text: t, font: FONT, size: 22 }) : new TextRun({ font: FONT, size: 22, ...t })), spacing: { after: 120 }, ...opts });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: FONT })], spacing: { before: 360, after: 160 } });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: FONT })], spacing: { before: 240, after: 120 } });
const h3 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text, font: FONT })], spacing: { before: 200, after: 80 } });
const bullet = (text, level = 0) => new Paragraph({ numbering: { reference: "bullets", level }, children: [new TextRun({ text, font: FONT, size: 22 })], spacing: { after: 60 } });
const numbered2 = (text) => numbered(text, "review");
const numbered = (text, ref = "numbers") => new Paragraph({ numbering: { reference: ref, level: 0 }, children: [new TextRun({ text, font: FONT, size: 22 })], spacing: { after: 60 } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

function table(head, rows, widths, opts = {}) {
  const size = opts.size || 18;
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (text, w, isHead, align) => new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: isHead ? { fill: "DCE6F1", type: ShadingType.CLEAR, color: "auto" } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text: String(text), font: FONT, size, bold: isHead })], spacing: { after: 0 } })],
  });
  const numeric = opts.numeric || [];
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false, numeric.includes(i) ? AlignmentType.RIGHT : undefined)) })),
    ],
  });
}
const kv = (rows, w1 = 2800, w2 = 6560) => table(["Item", "Value"], rows, [w1, w2], { size: 20 });

function image(file, widthPx, heightPx, maxWidthIn) {
  const data = fs.readFileSync(path.join(HERE, file));
  const scale = Math.min(1, (maxWidthIn * 96) / (widthPx / 2));
  const w = Math.round((widthPx / 2) * scale), h = Math.round((heightPx / 2) * scale);
  return new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data, transformation: { width: w, height: h } })], spacing: { after: 120 } });
}
const pngSize = (file) => { const b = fs.readFileSync(path.join(HERE, file)); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };

// ---------- data derived for the narrative ----------
const eq = D.equipment;
const ahu = eq.find((e) => e.kind === "AHU");
const louver = eq.find((e) => e.kind === "LOUVER");
const fpb = eq.filter((e) => e.kind === "FPB");
const vav = eq.filter((e) => e.kind === "VAV");
const fpbFan = fpb.reduce((a, e) => a + e.fan_cfm, 0);
const fpbPrim = fpb.reduce((a, e) => a + e.primary_cfm, 0);
const vavPrim = vav.reduce((a, e) => a + e.primary_cfm, 0);
const induced = fpbFan - fpbPrim;
const returnToAhu = ahu.supply_cfm - ahu.outside_air_cfm;
const relief = T.return_grille_cfm - induced - returnToAhu;
const bySystem = {};
for (const r of D.runs) { const k = r.system + "/" + r.pressure_class; bySystem[k] = (bySystem[k] || 0) + r.length_ft; }
const today = new Date().toISOString().slice(0, 10);

const zoneByNum = {}; for (const z of D.zones) zoneByNum[z.number] = z;

// ---------- document ----------
const children = [];
children.push(
  new Paragraph({ spacing: { before: 2400, after: 200 }, children: [new TextRun({ text: "HVAC Design Review Package", font: FONT, size: 56, bold: true })] }),
  p("10,000 sf single-storey office", { size: 32 }),
  p("Central VAV air handler, interior VAV terminals, series fan-powered terminals on the perimeter", { size: 26, color: "444444" }),
  p("Revision 2: perimeter private offices and corner conference rooms, Denver, Colorado exposures", { size: 24, color: "444444", after: 600 }),
  kv([
    ["Document date", today],
    ["Status", "Schematic design for independent engineering review. Not for construction."],
    ["Model files", "Office-10k-VAV-Mechanical.ifc (IFC4, feet), CreateOfficeModel.py (Revit API script), design.json (design data), four CSV schedules, plan.svg, isometric.svg"],
    ["Repository folder", "bim/office-10k-vav on branch ccr-e367aed5-vq3i83 of jamescatlas-bot/jamie-atlas-rehab"],
    ["How it was produced", "The design is defined once in design.py (geometry, zones, airflows). Scripts generate the IFC, the Revit script data, the drawings, the schedules and this document from that one source, so every number here matches the model."],
  ]),
  p("", { after: 200 }),
  p("Purpose of this package", { bold: true, size: 24 }),
  p("Everything that went into the model is written out here so that a mechanical engineer can check the basis, the arithmetic and the layout without opening the model. Section 9 lists the items the author considers most in need of a professional check."),
  pageBreak(),
  h1("Contents"),
  ...["1. Summary", "2. Design basis and assumptions", "3. Thermal zones and spaces", "4. Equipment", "5. Drawings",
      "6. Duct schedule", "7. Air terminal schedule", "8. Checks performed on the model", "9. Items for engineering review",
      "10. Revision history", "11. How the model was built"].map((t) => p(t, { size: 24, after: 100 })),
  pageBreak(),
);

// 1 Summary
children.push(
  h1("1. Summary"),
  p("The building is a 100 ft by 100 ft, 10,000 sf single-storey office with a 9 ft ceiling and a 14 ft roof deck on a 25 ft column grid. The perimeter is fitted out as 15 ft deep private offices, five per facade, with a 20 ft by 20 ft conference room at each corner and a 5 ft corridor behind the rooms. The interior is open office around a 24 ft by 16 ft mechanical room. Plan north is up."),
  p(`A single indoor VAV air handler, AHU-1, rated ${fmt(ahu.supply_cfm)} cfm with ${fmt(ahu.outside_air_cfm)} cfm minimum outside air, serves ${vav.length} interior single-duct VAV terminals and ${fpb.length} series fan-powered terminals on the perimeter through a medium-pressure ring main. Design primary airflow is ${fmt(T.supply_primary_cfm)} cfm (${fmt(vavPrim)} cfm interior, ${fmt(fpbPrim)} cfm perimeter), which with the ${fmt(fpbFan)} cfm of fan air delivered by the perimeter boxes gives ${fmt(T.zone_supply_cfm)} cfm of supply to the rooms through ${T.supply_diffusers} ceiling diffusers. Return is by ceiling plenum through ${T.return_grilles} grilles.`),
  p(`Airflows carry Denver, Colorado exposure factors: relative to a north zone, east 1.25, west 1.35 and south 1.50. Perimeter offices run from 1.0 cfm/sf (north) to 1.5 cfm/sf (south); conference rooms are occupancy-driven at 1.2 cfm/sf times the worse of their two exposures; interior open office is 0.9 cfm/sf.`),
  h2("Key quantities"),
  kv([
    ["Floor area", "10,000 sf (zones sum to 10,000.0 sf exactly)"],
    ["Rooms", `${T.offices} private offices, ${T.conference_rooms} conference rooms, 4 interior open-office zones, 1 mechanical room (29 spaces)`],
    ["AHU-1", `${fmt(ahu.supply_cfm)} cfm supply, ${fmt(ahu.outside_air_cfm)} cfm OA, ${ahu.cooling_tons} tons cooling, ${ahu.heating_mbh} MBH heating, ${ahu.external_sp_in} in. w.g. ESP, ${ahu.fan_hp} hp supply fan`],
    ["Terminal units", `${vav.length} VAV (cooling only) and ${fpb.length} series fan-powered boxes with electric reheat`],
    ["Design primary air", `${fmt(T.supply_primary_cfm)} cfm (diversity ${(T.supply_primary_cfm / ahu.supply_cfm).toFixed(2)} on the AHU rating)`],
    ["Air terminals", `${T.supply_diffusers} supply diffusers 24x24 lay-in, ${T.return_grilles} return grilles 24x24 egg crate, 1 OA louver 36x30`],
    ["Ductwork", `${fmt(T.duct_length_ft)} ft total: ${Object.entries(bySystem).map(([k, v]) => `${k} ${fmt(Math.round(v))} ft`).join(", ")}`],
    ["Duct runs / segments in model", `${D.runs.length} runs, 150 straight segments, 120 fittings`],
  ]),
);

// 2 Design basis
children.push(
  h1("2. Design basis and assumptions"),
  p("Every assumption used to generate the model is listed here. Items marked (check) are rule-of-thumb values that should be replaced by calculation before the design is used for anything beyond planning."),
  h2("2.1 Site and climate"),
  kv([
    ["Location", "Denver, Colorado, ASHRAE climate zone 5B (high altitude, strong solar, dry). (check: altitude correction to fan and coil capacities is not applied)"],
    ["Orientation", "Plan up is true north. Facades are named N, E, S, W accordingly."],
    ["Exposure factors (cooling airflow multiplier vs north)", "North 1.00, East 1.25, West 1.35, South 1.50 (check: derived from typical peak solar gain ratios for 5B, not from a load calculation)"],
    ["Glazing", "40% window-to-wall assumed on all facades, not modeled geometrically (check)"],
  ]),
  h2("2.2 Building"),
  kv([
    ["Footprint", "100 ft x 100 ft, origin at the south-west corner, X east, Y north"],
    ["Levels", "Level 1 at 0 ft, Roof at 14 ft. Slab on grade 6 in. (top at 0), roof deck 6 in. (bottom at 14 ft)"],
    ["Ceiling", "2x4 lay-in acoustical ceiling at 9 ft 0 in. everywhere except the mechanical room; plenum from 9 ft to 14 ft"],
    ["Structure", "25 ft x 25 ft grid, grids A to E (X = 0, 25, 50, 75, 100) and 1 to 5 (Y = 0, 25, 50, 75, 100); 25 columns 12 in. x 12 in. placeholder"],
    ["Exterior walls", "12 in. placeholder, full height 14 ft, centred 6 in. inside the building line"],
    ["Interior partitions", "6 in. placeholder; mechanical room walls full height to the roof deck; office and conference partitions to the 9 ft ceiling (plenum continuous above them)"],
    ["Mechanical room M-101", "X 38 to 62 ft, Y 54 to 70 ft (24 ft x 16 ft, 384 sf), no ceiling"],
    ["Perimeter rooms", "15 ft deep from the exterior face. Offices 12 ft wide (180 sf) with left edges at 20, 32, 44, 56 and 68 ft along each facade. Conference rooms 20 ft x 20 ft (400 sf) at each corner"],
    ["Corridor", "5 ft wide behind the rooms (depth 15 to 20 ft), open to the interior office, counted with the adjacent interior zone"],
    ["Not modeled", "Doors, windows, lighting, plumbing, fire protection, electrical, structure beyond placeholder columns, roof drains, equipment pads, hangers, insulation, flex duct"],
  ]),
  h2("2.3 Airflow basis"),
  kv([
    ["Perimeter office supply (fan air)", "Floor area x exposure factor x 1.0 cfm/sf: north 180, east 225, west 245, south 270 cfm per 180 sf office (check)"],
    ["Conference room supply", "400 sf x 1.2 cfm/sf (occupancy and equipment) x the larger exposure factor of the two facades: NE 600, NW 650, SE 720, SW 720 cfm (check: based on about 12 to 16 occupants)"],
    ["Interior open office", "0.90 cfm/sf: NW and NE 1,008 sf at 905 cfm, SW and SE 1,200 sf at 1,080 cfm"],
    ["Series fan-powered box ratio", `Fan airflow = 1.5 x design primary airflow. Primary = fan / 1.5 rounded to 5 cfm. Induced plenum air = ${fmt(induced)} cfm in total (check: ratio, and whether parallel boxes would be preferred)`],
    ["Minimum airflow", "30% of design primary for every box (check against ASHRAE 62.1 zone minimums and 90.1 reheat limits)"],
    ["Electric reheat", "25 Btuh/sf of zone area, rounded up to whole kW (3,412 Btuh/kW). (check: Denver heating load with 40% glazing; also confirms whether hot-water reheat is preferred)"],
    ["Outside air", `${fmt(ahu.outside_air_cfm)} cfm, about 18% of supply. Basis: ASHRAE 62.1 office rates, 5 cfm/person + 0.06 cfm/sf, for roughly 20 office occupants, 48 conference seats and 40 open-office occupants, divided by a system ventilation efficiency of about 0.75, then rounded up (check: run the 62.1 multiple-zone calculation with the actual occupancy)`],
    ["AHU rating", `${fmt(ahu.supply_cfm)} cfm against ${fmt(T.supply_primary_cfm)} cfm block primary air (diversity 0.88). ${ahu.cooling_tons} tons is about 400 cfm/ton on the rated airflow (check: block cooling load calculation)`],
    ["Return air", `${fmt(returnToAhu)} cfm to the AHU (supply minus OA). Rooms return ${fmt(T.return_grille_cfm)} cfm to the plenum; ${fmt(induced)} cfm is re-induced by the fan-powered boxes and about ${fmt(relief)} cfm is available for relief, toilet exhaust and exfiltration (check: relief and building pressurization are not modeled)`],
  ]),
  h2("2.4 Duct design basis"),
  kv([
    ["Pressure classes", "Medium pressure (2 in. w.g. class) from the AHU through the ring main to the terminal inlets. Low pressure (1 in. w.g. class) downstream of every terminal, and for the return and outside-air ducts"],
    ["Sizing method", "Velocity limited, rectangular sizes chosen from a standard list in 2 in. steps: medium pressure at or below 1,500 fpm, low pressure at or below 900 fpm. Ring legs are held at a 12x10 minimum. Round runouts at or below 800 fpm. Sizes reduce 2 ft after each tap where the remaining airflow allows a smaller duct (check: equal-friction or static-regain check, and acoustic check of the 1,400 to 1,500 fpm mains)"],
    ["Duct elevation", "All horizontal ductwork at 11 ft 6 in. centreline (bottom of the largest 36x24 duct at 10 ft 6 in., 1 ft 6 in. above the ceiling). Runouts drop vertically to the diffuser necks at 9 ft 6 in."],
    ["Fittings", "Elbows at every direction change, transitions at size changes, bull-head tees where mains split, takeoffs for branch taps. In the IFC these are placeholder blocks; in Revit they come from the duct type's routing preferences"],
    ["Terminal inlets", "Round, sized for at or below 2,000 fpm at design primary air: 6 to 10 in. for the perimeter boxes, 10 in. for the VAVs"],
    ["Diffusers", "24x24 lay-in, one per office, two per conference room, four per interior VAV. Neck sized at or below 800 fpm: 6 in. up to 155 cfm, 8 in. up to 280 cfm, 10 in. up to 435 cfm"],
    ["Return grilles", "24x24 egg crate in the ceiling, one per office, two per conference room, eight in the open office. Each grille is assigned its room's supply airflow (check: door undercuts or transfer grilles are not needed because every room has its own plenum return)"],
    ["Flexible duct", "Not modeled. Runouts are drawn as rigid round duct from the header to the diffuser neck"],
    ["Materials", "Not specified. Assume galvanized steel, SMACNA construction, externally insulated supply"],
  ]),
);

// 3 Zones
const zoneRows = zones.rows.map((r) => [r[0], r[1], r[2], r[3], fmt(r[4]), fmt(r[5]), r[6]]);
children.push(
  h1("3. Thermal zones and spaces"),
  p("Zones are numbered clockwise from the north-west corner. Each perimeter zone is one room; interior zones are the open office quadrants including the corridor behind the perimeter rooms. The supply column is the air delivered to the room (fan air for fan-powered zones)."),
  table(zones.head, zoneRows, [900, 2600, 1300, 1300, 1050, 1300, 910], { size: 18, numeric: [4, 5, 6] }),
  p("", { after: 120 }),
  p("Zone boundaries (plan coordinates in feet, X east, Y north):", { bold: true }),
  table(["Zone", "Polygon vertices (X, Y)"], D.zones.map((z) => [z.number, z.polygon.map((q) => `(${q[0]}, ${q[1]})`).join("  ")]), [1100, 8260], { size: 16 }),
);

// 4 Equipment
const eqRows = equip.rows.map((r) => r.slice(0, 12));
children.push(
  h1("4. Equipment"),
  h2("4.1 Equipment schedule"),
  table(equip.head.slice(0, 12), eqRows, [900, 700, 1100, 800, 700, 700, 600, 600, 760, 760, 800, 940], { size: 16, numeric: [3, 4, 5, 6, 7, 8, 9, 10] }),
  p("", { after: 80 }),
  h2("4.2 Equipment descriptions"),
  ...eq.map((e) => runs([{ text: e.tag + ": ", bold: true }, `${e.description || e.kind}. Location (${e.centre[0]}, ${e.centre[1]}, ${e.centre[2]}) ft, footprint ${e.length} x ${e.width} ft, height ${e.height} ft, flow direction (${e.flow_dir[0]}, ${e.flow_dir[1]}), rotation ${e.rotation_deg} deg. Inlet at (${e.inlet.join(", ")}), outlet at (${e.outlet.join(", ")}).` + (e.exposure ? ` Exposure ${e.exposure}.` : "") + (e.zone ? ` Serves zone(s) ${e.zone}.` : "")])),
  h2("4.3 Notes on the equipment"),
  bullet(`AHU-1 is a placeholder box of the right footprint (16 x 6 x 7 ft) with the return (48x28 at X = 45), outside air (22x14 at X = 58) and supply (36x24 at X = 54) connections all on top at 7 ft. A real unit will have end connections and needs the mechanical room layout, service clearance and a condensate drain checked.`),
  bullet("Fan-powered boxes are 5 x 3.5 x 1.5 ft placeholders mounted in the corridor ceiling with the primary inlet facing the ring main and the discharge toward the facade. The plenum induction inlet is on the side; no induction duct is drawn."),
  bullet("VAV boxes are 3 x 2 x 1.25 ft placeholders in the open office ceiling."),
  bullet("Electric reheat sizes are rounded up to whole kW from 25 Btuh/sf; the 3-office south boxes come to 4 kW, the conference boxes 3 kW."),
);

// 5 Drawings
const [pw, ph] = pngSize("plan.png");
const [iw, ih] = pngSize("isometric.png");
children.push(
  h1("5. Drawings"),
  h2("5.1 Ceiling plan at 9 ft, looking up"),
  image("plan.png", pw, ph, 6.5),
  p("Blue: supply air. Red: return. Green: outside air. Orange: VAV boxes. Magenta: fan-powered boxes. Squares with an X are supply diffusers, squares with a bar are return grilles. Zone numbers and airflows are printed in each room.", { size: 18, italics: true }),
  h2("5.2 Axonometric of the IFC model"),
  image("isometric.png", iw, ih, 6.5),
  p("Roof, north wall and east wall removed. Partitions stop at the 9 ft ceiling; ductwork runs in the plenum above.", { size: 18, italics: true }),
);

// 6 Duct schedule (landscape section)
const ductRows = D.runs.map((r) => {
  const pts = r.points;
  return [r.id, r.system, r.pressure_class, r.name, r.shape === "round" ? `${r.diameter_in} in. dia` : `${r.width_in}x${r.height_in}`, fmt(r.cfm),
    fmt(Math.round(r.cfm / (r.shape === "round" ? Math.PI * Math.pow(r.diameter_in / 24, 2) : r.width_in * r.height_in / 144))), r.length_ft.toFixed(1),
    r.tap_on || "", r.from_ || "", r.to || "", pts.map((q) => `(${q[0]}, ${q[1]}, ${q[2]})`).join(" > ")];
});
const landscapeChildren = [
  h1("6. Duct schedule"),
  p("Every run in the model. A run is a constant-size polyline; its interior vertices are elbows. 'Taps on' names the run a branch takes off from; 'From' and 'To' name equipment or terminals at the run ends. CAP marks a dead end. Points are centreline coordinates in feet (X, Y, Z), listed in the direction of airflow for supply and toward the AHU for return and outside air.", { size: 20 }),
  table(["Run", "Sys", "Class", "Description", "Size", "cfm", "fpm", "Len ft", "Taps on", "From", "To", "Centreline points (X, Y, Z) ft"],
    ductRows, [900, 450, 650, 2100, 850, 600, 600, 600, 900, 850, 700, 4300], { size: 14, numeric: [5, 6, 7] }),
  p("", { after: 120 }),
  h1("7. Air terminal schedule"),
  p("Supply diffusers (SD) and return grilles (RG), all 24x24 lay-in at the 9 ft ceiling. 'Served by' is the terminal box for diffusers; return grilles return to the plenum.", { size: 20 }),
  table(["Tag", "Type", "Room", "Served by", "cfm", "Face in.", "Neck in.", "X ft", "Y ft", "Ceiling ft"],
    D.terminals.map((t) => [t.tag, t.kind === "supply_diffuser" ? "Supply diffuser" : "Return grille", t.room || "", t.served_by, fmt(t.cfm), t.face_in, t.neck_in || "", t.x, t.y, t.z]),
    [900, 1500, 900, 1200, 800, 900, 900, 900, 900, 1000], { size: 15, numeric: [4, 5, 6, 7, 8, 9] }),
];

// 8 Checks, 9 review items, 10 revisions, 11 method
const portrait2 = [
  h1("8. Checks performed on the model"),
  p("The following automated checks ran on the final design and passed. They are geometric and arithmetic checks, not an engineering review."),
  numbered("Clash check: every straight duct segment, terminal box, air handler and column is represented by a bounding box; no two overlap except where runs legitimately meet at a node or tap. Interior walls are not included in the check (ducts pass through partitions above the ceiling)."),
  numbered("Connectivity check: every run that names a piece of equipment starts or ends exactly on that equipment's inlet or outlet connector."),
  numbered(`Velocity check: no medium-pressure run exceeds 2,000 fpm and no low-pressure run exceeds 1,200 fpm. Actual maxima: ${fmt(Math.max(...D.runs.filter((r) => r.pressure_class === "medium").map((r) => Math.round(r.cfm / (r.shape === "round" ? Math.PI * Math.pow(r.diameter_in / 24, 2) : r.width_in * r.height_in / 144)))))} fpm medium pressure (SA-01 riser), ${fmt(Math.max(...D.runs.filter((r) => r.pressure_class === "low").map((r) => Math.round(r.cfm / (r.shape === "round" ? Math.PI * Math.pow(r.diameter_in / 24, 2) : r.width_in * r.height_in / 144)))))} fpm low pressure.`),
  numbered("Area check: the 29 space polygons sum to 10,000.0 sf with no gaps or overlaps by construction."),
  numbered("Airflow accounting: diffuser airflows equal the zone supply airflows within rounding; box primary air equals the sum of the taps on each trunk; trunk sizes are recomputed from the remaining airflow after every tap."),
  numbered("IFC validation: the IFC4 file passes the ifcopenshell schema validator with no errors, and every one of the 472 solids rebuilds in the geometry kernel."),
  numbered("Terminal spacing: no two air terminals are within 2 ft of each other."),
  h2("8.1 What was not checked"),
  bullet("Cooling and heating loads, psychrometrics, altitude corrections, coil selections."),
  bullet("Duct pressure drop, fan static pressure, static regain, acoustics, or the ASHRAE 62.1 multiple-zone outside air calculation."),
  bullet("Code compliance (IMC, IECC/90.1, 62.1, NFPA 90A), smoke dampers at the mechanical room, fire dampers, plenum-rated materials."),
  bullet("Structural coordination (duct hangers, roof openings), beam depths (none modeled), and the 1 ft 6 in. clearance assumed between the ceiling and the bottom of the largest duct."),
  bullet("Revit execution: the Revit API script was written against the 2022 to 2025 API but has not been run in Revit; the IFC was generated and verified in Python."),
  h1("9. Items for engineering review"),
  p("These are the points where a professional judgement or calculation should replace the author's assumption."),
  numbered2("Exposure factors (S 1.50, W 1.35, E 1.25) and the 1.0 cfm/sf north office baseline. A room-by-room load calculation for Denver with the actual glazing will set the real airflows. Conference rooms in particular may need more than 1.2 cfm/sf before the exposure factor, or CO2 demand control."),
  numbered2("Series versus parallel fan-powered boxes, and the 1.5 fan-to-primary ratio. Parallel boxes with a lower fan airflow may be preferred for energy; series boxes were chosen for constant room airflow and better winter mixing on the perimeter."),
  numbered2("Electric reheat at 25 Btuh/sf. Confirm the perimeter heating load (Denver 99% design about 0 deg F; 40% glazing) and whether the owner prefers hot water. Check 90.1 reheat and fan-power limits."),
  numbered2(`Outside air: ${fmt(ahu.outside_air_cfm)} cfm was estimated from 62.1 rates and a 0.75 system efficiency. The multiple-zone calculation with the actual critical zone (likely a south conference room at minimum airflow) should be run, and demand-control ventilation considered. Relief and building pressurization are not addressed.`),
  numbered2(`AHU rating: ${fmt(ahu.supply_cfm)} cfm, ${ahu.cooling_tons} tons, ${ahu.heating_mbh} MBH, ${ahu.external_sp_in} in. w.g. ESP are placeholders. The block load, altitude correction (about 0.82 air density at 5,280 ft) and the actual duct pressure drop will set these. The 36x24 riser at about 1,470 fpm and 28x16 mains at about 1,420 fpm are at the high end for a medium-pressure office system; a static-regain sizing and an acoustic check at the first boxes are recommended.`),
  numbered2("Ring main concept: four dead-ended legs fed from the east and west mains rather than a closed loop. A closed loop would give pressure equalization; the dead ends simplify balancing and the Revit system definition."),
  numbered2("Mechanical room: 24 x 16 ft with a 16 x 6 ft unit and all three risers on top of the unit. A real unit of this size (10,000 cfm) is about 20 ft long with end connections; check the room, door, service access and acoustic separation from the adjacent open office."),
  numbered2("Return path: every perimeter room has its own ceiling return grille so partitions to the ceiling do not block return. If partitions go to the deck for acoustics, transfer ducts are needed. The plenum must be rated for return air."),
  numbered2("The middle office of each three-office group has its diffuser 3 ft off the room centre line to clear the header tee. Confirm throw and coverage, or move the box."),
  numbered2("Outside-air louver L-1 sits above the ceiling in the north wall of North Office 4 (X 58 ft). Check that it clears the window head and is acceptable on that elevation, and that the OA duct can be insulated and sloped."),
  numbered2("Interior VAV minimums (30%) and whether the interior zones need any heating (none provided)."),
  h1("10. Revision history"),
  table(["Rev", "Change"], [
    ["1", "Open-plan office, 8 perimeter fan-powered boxes in 20 ft deep perimeter zones (two per facade), 4 interior VAVs, AHU 8,500 cfm, uniform 1.0 to 1.25 cfm/sf, 48 diffusers, 16 return grilles."],
    ["2", "Perimeter rezoned to 20 private offices and 4 corner conference rooms with a 5 ft corridor; plan north fixed as up; Denver exposure factors applied (S 1.50, W 1.35, E 1.25); 12 perimeter fan-powered boxes (one per conference room, one per 2 to 3 offices); AHU 10,000 cfm with 1,800 cfm OA; ducts resized automatically from airflow along a ring main; OA louver moved from X 47.5 to X 58 to clear the north discharge legs; return duct 48x28; 44 diffusers and 36 return grilles; 44 walls."],
  ], [700, 8660], { size: 18 }),
  h1("11. How the model was built"),
  p("design.py holds the building, the zones, the equipment, the duct network and the sizing rules in one Python module. From it:"),
  bullet("build_ifc.py writes the IFC4 model with ifcopenshell. Every element is a swept solid placed in feet, typed (duct sizes, box types, wall types) and grouped into Supply Air, Return Air and Outside Air distribution systems, with an HVAC_Design property set on every element (airflow, size, velocity, pressure class, zone)."),
  bullet("CreateOfficeModel.py reads design.json inside Revit and creates native levels, grids, walls, floor, roof, ceilings, spaces with separation lines, ducts with fittings (elbows, transitions, tees, crosses, takeoffs from the duct type's routing preferences), equipment and air terminals, using library families when found and DirectShape placeholders otherwise."),
  bullet("make_drawings.py runs the clash, connectivity and velocity checks and writes the schedules and the plan."),
  bullet("render_iso.py draws the axonometric from the IFC geometry, and build_review_doc.cjs writes this document from the same data."),
  p("Coordinates: all values in this package are in feet with the origin at the outside south-west corner of the building, X to the east, Y to the north, Z up from Level 1."),
];

const sectionProps = (landscape) => ({
  page: { size: landscape ? { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE } : LETTER, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } },
});
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "10,000 sf Office HVAC Design Review, Rev 2  |  Page ", font: FONT, size: 16, color: "666666" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "666666" })] })] });

const doc = new Document({
  creator: "design.py / build_review_doc.js",
  title: "10,000 sf Office HVAC Design Review Package, Rev 2",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: FONT, color: "1F3864" }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: FONT, color: "2E74B5" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 23, bold: true, font: FONT }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
      { reference: "review", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
    ],
  },
  sections: [
    { properties: sectionProps(false), footers: { default: footer }, children },
    { properties: sectionProps(true), footers: { default: footer }, children: landscapeChildren },
    { properties: sectionProps(false), footers: { default: footer }, children: portrait2 },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(HERE, "Office-10k-VAV-Design-Review.docx");
  fs.writeFileSync(out, buf);
  console.log("wrote", out, Math.round(buf.length / 1024), "KB");
});
