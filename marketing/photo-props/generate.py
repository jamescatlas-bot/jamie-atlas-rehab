#!/usr/bin/env python3
"""
Generate the oversized photo props for the Jamie Atlas studio.

Outputs (all under dist/):
  svg/          master vector files (art + CutContour layer)
  print/        full-size PDFs for a sign / print shop
  home-print/   the same props tiled onto US Letter pages for a home printer
  preview/      PNG previews

Units inside the SVGs are 1/100 inch, so a 28 x 36 in prop has viewBox 0 0 2800 3600.

Run:  python3 marketing/photo-props/generate.py
"""
import io
import math
import os
import sys

import cairosvg
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

# Brand (from src/styles/global.css + public/favicon.svg)
BLUE = "#0079C2"
BLUE_DARK = "#005C94"
BLUE_LIGHT = "#7CC4F0"
ORANGE = "#F5921E"
ORANGE_DARK = "#C9700F"
INK = "#172230"
STEEL = "#3D4B58"
STEEL_LIGHT = "#5B6B7A"
WHITE = "#FFFFFF"
CUT = "#FF00FF"  # CutContour spot colour, hairline

BORDER = 60   # white keyline around the art, 0.6 in
OUTLINE = 36  # dark outline, 0.36 in

SKIN_TONES = {
    "light":  dict(base="#F2C4A2", shade="#DDA07D", line="#A86A48", nail="#FBE3D1"),
    "medium": dict(base="#C8895A", shade="#A96C40", line="#6E4226", nail="#E6B892"),
    "deep":   dict(base="#6F4328", shade="#55301A", line="#2E180C", nail="#9A6A4A"),
}


# ---------------------------------------------------------------- helpers
_fonts = {}

def _font(path):
    if path not in _fonts:
        f = TTFont(path)
        _fonts[path] = (f, f.getGlyphSet(), f["cmap"].getBestCmap(), f["head"].unitsPerEm)
    return _fonts[path]


def text_path(text, size, font=FONT_BLACK, tracking=0.0):
    """Return (path_d, width) for text as outlines. size = cap-to-descender em size in units."""
    f, gs, cmap, upm = _font(font)
    scale = size / upm
    parts = []
    x = 0.0
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            gname = ".notdef"
        glyph = gs[gname]
        pen = SVGPathPen(gs)
        glyph.draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path transform="translate({x:.1f},0) scale({scale:.5f},{-scale:.5f})" d="{d}"/>')
        x += glyph.width * scale + tracking * size
    width = x - tracking * size
    return "".join(parts), width


def text_group(text, size, cx, baseline_y, fill, font=FONT_BLACK, tracking=0.0, anchor="middle", max_width=None):
    d, w = text_path(text, size, font, tracking)
    if max_width and w > max_width:
        size = size * max_width / w
        d, w = text_path(text, size, font, tracking)
    x0 = cx - w / 2 if anchor == "middle" else cx
    return f'<g fill="{fill}" transform="translate({x0:.1f},{baseline_y:.1f})">{d}</g>'


def rrect_poly(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return box(x + r, y + r, x + w - r, y + h - r).buffer(r, quad_segs=24)


def ellipse_poly(cx, cy, rx, ry, n=96):
    return Polygon([(cx + rx * math.cos(t), cy + ry * math.sin(t))
                    for t in (2 * math.pi * i / n for i in range(n))])


def _bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


def bezier_poly(start, segs):
    """segs: list of (c1, c2, end) cubic segments from start, closed."""
    pts = [start]
    cur = start
    for c1, c2, end in segs:
        pts += _bez(cur, c1, c2, end)[1:]
        cur = end
    return Polygon(pts)


def bezier_d(start, segs):
    d = f"M {start[0]:.0f} {start[1]:.0f} "
    for c1, c2, end in segs:
        d += f"C {c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {end[0]:.0f} {end[1]:.0f} "
    return d + "Z"


def poly_d(geom):
    """shapely (Multi)Polygon -> SVG path d (exterior + holes)."""
    polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            d.append("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z")
    return " ".join(d)


def svg_doc(w_in, h_in, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_in}in" height="{h_in}in" '
            f'viewBox="0 0 {w_in*100:.0f} {h_in*100:.0f}">\n<title>{title}</title>\n{body}\n</svg>\n')


def cut_layer(cut_geoms, slots):
    """CutContour: magenta hairline (0.25pt). Slots are interior cuts (hand holes)."""
    parts = [f'<path d="{poly_d(g)}" fill="none" stroke="{CUT}" stroke-width="0.35"/>' for g in cut_geoms]
    for (x, y, w, h, r) in slots:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{CUT}" stroke-width="0.35"/>')
    return '<g id="CutContour" inkscape:label="CutContour">' + "".join(parts) + "</g>"


def slot_art(slots):
    return "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{WHITE}"/>'
                   for (x, y, w, h, r) in slots)


# ---------------------------------------------------------------- thumbs up
THUMB_W, THUMB_H = 28, 36  # inches, finished size incl. white keyline


def thumbs_up(tone_name):
    t = SKIN_TONES[tone_name]
    W, H = THUMB_W * 100, THUMB_H * 100

    # Fist block
    fist = rrect_poly(560, 1420, 1720, 1420, 380)
    # Four curled fingers along the right edge
    fingers = []
    fy = 1480
    for i in range(4):
        fingers.append(rrect_poly(1780, fy, 660, 330, 165))
        fy += 345
    # Thumb (cubic path), leaning a little to the right
    thumb_start = (640, 1760)
    thumb_segs = [
        ((600, 1300), (700, 760), (880, 430)),     # left edge up
        ((980, 250), (1300, 230), (1400, 440)),    # rounded tip
        ((1500, 640), (1460, 1040), (1380, 1320)), # right edge down
        ((1330, 1500), (1310, 1650), (1320, 1760)),
    ]
    thumb = bezier_poly(thumb_start, thumb_segs)
    # Cuff / sleeve in brand blue
    cuff = rrect_poly(520, 2760, 1760, 700, 110)
    # Hem band on top of cuff
    hem = rrect_poly(520, 2760, 1760, 160, 60)

    silhouette = unary_union([fist, *fingers, thumb, cuff])
    outline = silhouette.buffer(OUTLINE, quad_segs=16)
    keyline = outline.buffer(BORDER, quad_segs=16)

    slots = [(1100, 3150, 600, 150, 60)]  # hand hole in the cuff

    def rr(x, y, w, h, r, fill):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'

    body = []
    body.append(f'<path d="{poly_d(keyline)}" fill="{WHITE}"/>')
    body.append(f'<path d="{poly_d(outline)}" fill="{t["line"]}"/>')
    # fills
    body.append(rr(560, 1420, 1720, 1420, 380, t["base"]))
    body.append(f'<path d="{bezier_d(thumb_start, thumb_segs)}" fill="{t["base"]}"/>')
    fy = 1480
    for i in range(4):
        body.append(rr(1780, fy, 660, 330, 165, t["base"]))
        # crease shadow under each finger
        body.append(f'<path d="M 1900 {fy+330} Q 2110 {fy+395} 2400 {fy+300}" fill="none" '
                    f'stroke="{t["shade"]}" stroke-width="34" stroke-linecap="round"/>')
        fy += 345
    # thumb-side shading and crease where thumb meets the fist
    body.append(f'<path d="M 1330 1760 C 1250 1620 1270 1420 1370 1330" fill="none" '
                f'stroke="{t["shade"]}" stroke-width="34" stroke-linecap="round"/>')
    body.append(f'<path d="M 760 1560 C 720 1200 780 820 920 560" fill="none" '
                f'stroke="{t["shade"]}" stroke-width="30" stroke-linecap="round" opacity="0.7"/>')
    # thumbnail
    body.append(f'<ellipse cx="1200" cy="560" rx="120" ry="180" transform="rotate(14 1200 560)" fill="{t["nail"]}"/>')
    # palm highlight
    body.append(f'<ellipse cx="1050" cy="2250" rx="230" ry="300" fill="{WHITE}" opacity="0.12"/>')
    # cuff
    body.append(f'<path d="{poly_d(cuff)}" fill="{BLUE}"/>')
    body.append(f'<path d="{poly_d(hem)}" fill="{BLUE_DARK}"/>')
    body.append(text_group("JAMIE ATLAS", 300, 1400, 3085, WHITE, tracking=0.03, max_width=1520))
    body.append(slot_art(slots))
    body.append(text_group("@jamieatlasfitness", 95, 1400, 3400, BLUE_LIGHT, font=FONT_BOLD))
    art = '<g id="Artwork">' + "".join(body) + "</g>"
    svg = svg_doc(THUMB_W, THUMB_H, art + "\n" + cut_layer([keyline], slots), f"Thumbs up ({tone_name} skin tone)")
    svg = svg.replace("<svg ", '<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" ', 1)
    return svg


# ---------------------------------------------------------------- dumbbell
DB_W, DB_H = 48, 22  # inches


def dumbbell():
    W, H = DB_W * 100, DB_H * 100
    cy = H / 2

    bar = rrect_poly(1120, cy - 350, 2560, 700, 70)
    collars = [rrect_poly(1000, cy - 440, 170, 880, 50), rrect_poly(3630, cy - 440, 170, 880, 50)]
    inner = [rrect_poly(690, cy - 720, 330, 1440, 110), rrect_poly(3780, cy - 720, 330, 1440, 110)]
    outer = [rrect_poly(240, cy - 880, 470, 1760, 150), rrect_poly(4090, cy - 880, 470, 1760, 150)]
    silhouette = unary_union([bar, *collars, *inner, *outer])
    outline = silhouette.buffer(OUTLINE, quad_segs=16)
    keyline = outline.buffer(BORDER, quad_segs=16)

    slots = [(405, cy + 40, 140, 520, 60), (4255, cy + 40, 140, 520, 60)]  # hand holes in outer plates

    def rr(x, y, w, h, r, fill, extra=""):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" {extra}/>'

    body = []
    body.append(f'<path d="{poly_d(keyline)}" fill="{WHITE}"/>')
    body.append(f'<path d="{poly_d(outline)}" fill="{INK}"/>')
    # plates
    for (x, w) in [(240, 470), (4090, 470)]:
        body.append(rr(x, cy - 880, w, 1760, 150, BLUE))
        body.append(rr(x + 70, cy - 810, w - 140, 1620, 100, BLUE_DARK))
        body.append(rr(x + 110, cy - 770, 60, 1540, 30, BLUE_LIGHT, 'opacity="0.55"'))
        # JA roundel, same mark as the site favicon
        rx = x + w / 2
        body.append(rr(rx - 170, cy - 640, 340, 340, 76, WHITE))
        body.append(text_group("JA", 220, rx, cy - 390, BLUE, tracking=0.04))
    for (x, w) in [(690, 330), (3780, 330)]:
        body.append(rr(x, cy - 720, w, 1440, 110, BLUE))
        body.append(rr(x + 60, cy - 660, w - 120, 1320, 70, BLUE_DARK))
        body.append(rr(x + 90, cy - 630, 50, 1260, 25, BLUE_LIGHT, 'opacity="0.55"'))
    # collars
    for x in (1000, 3630):
        body.append(rr(x, cy - 440, 170, 880, 50, ORANGE))
        body.append(rr(x + 55, cy - 380, 60, 760, 30, ORANGE_DARK))
    # bar with knurl
    body.append(rr(1120, cy - 350, 2560, 700, 70, STEEL))
    body.append(rr(1180, cy - 290, 2440, 90, 45, STEEL_LIGHT, 'opacity="0.8"'))
    knurl = []
    for kx in range(1240, 3600, 60):
        knurl.append(f'<line x1="{kx}" y1="{cy-140}" x2="{kx+40}" y2="{cy+300}" stroke="{INK}" stroke-width="10" opacity="0.25"/>')
    body.append("".join(knurl))
    body.append(text_group("JAMIE ATLAS", 330, W / 2, cy + 110, WHITE, tracking=0.04))
    body.append(text_group("@jamieatlasfitness", 100, W / 2, cy + 265, ORANGE, font=FONT_BOLD))
    body.append(slot_art(slots))
    art = '<g id="Artwork">' + "".join(body) + "</g>"
    svg = svg_doc(DB_W, DB_H, art + "\n" + cut_layer([keyline], slots), "Dumbbell")
    svg = svg.replace("<svg ", '<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" ', 1)
    return svg


# ---------------------------------------------------------------- export
def strip_cut(svg):
    i = svg.find('<g id="CutContour"')
    j = svg.find("</g>", i) + 4
    return svg[:i] + svg[j:]


def tile_letter(name, svg_art_only, w_in, h_in, out_pdf, dpi=150):
    """Tile the prop across US Letter pages with 0.5 in overlap, crop marks and labels."""
    png = cairosvg.svg2png(bytestring=svg_art_only.encode(), output_width=int(w_in * dpi), output_height=int(h_in * dpi),
                           background_color="white")
    im = Image.open(io.BytesIO(png)).convert("RGB")
    margin, overlap = 0.5, 0.5
    tile_w, tile_h = 8.5 - 2 * margin, 11 - 2 * margin   # printable 7.5 x 10
    step_w, step_h = tile_w - overlap, tile_h - overlap   # 7.0 x 9.5
    cols = math.ceil((w_in - overlap) / step_w)
    rows = math.ceil((h_in - overlap) / step_h)
    c = rl_canvas.Canvas(out_pdf, pagesize=letter)
    c.setTitle(f"{name} - tiled for US Letter")

    # Assembly map page
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, 10.2 * inch, f"{name}: home-print assembly map")
    c.setFont("Helvetica", 10.5)
    lines = [
        f"Finished size {w_in} x {h_in} in. {cols} columns x {rows} rows = {cols*rows} Letter pages.",
        "Print at 100% / Actual size (turn OFF 'fit to page'). Portrait. Plain paper is fine; 28 lb or card stock holds up better.",
        "Each page overlaps its neighbour by 0.5 in. Trim the RIGHT and BOTTOM edges of each page on the dashed line,",
        "then lay it over the next page so the crop marks line up. Tape the back. Glue the whole sheet to foam board,",
        "then cut along the outside of the white border and cut out the hand hole.",
        "Page labels run A1, A2 ... across the top row, then B1, B2 ... for the next row down.",
    ]
    y = 9.8 * inch
    for ln in lines:
        c.drawString(0.75 * inch, y, ln)
        y -= 15
    # map thumbnail
    map_w = 7.0 * inch
    scale = min(map_w / (w_in * inch), 5.5 * inch / (h_in * inch))
    mx, my = 0.75 * inch, 1.0 * inch
    mw, mh = w_in * inch * scale, h_in * inch * scale
    thumb = im.resize((int(mw / inch * 72), int(mh / inch * 72)))
    tb = io.BytesIO(); thumb.save(tb, "PNG"); tb.seek(0)
    from reportlab.lib.utils import ImageReader
    c.drawImage(ImageReader(tb), mx, my, mw, mh)
    c.setStrokeColorRGB(1, 0, 1); c.setLineWidth(0.5)
    c.setFont("Helvetica-Bold", 9)
    for r in range(rows):
        for col in range(cols):
            x0 = col * step_w; y0 = r * step_h
            c.rect(mx + x0 * inch * scale, my + mh - (y0 + tile_h) * inch * scale, tile_w * inch * scale, tile_h * inch * scale)
            c.setFillColorRGB(1, 0, 1)
            c.drawString(mx + (x0 + 0.15) * inch * scale, my + mh - (y0 + 0.5) * inch * scale, f"{chr(65+r)}{col+1}")
    c.showPage()

    px = dpi
    for r in range(rows):
        for col in range(cols):
            x0, y0 = col * step_w, r * step_h
            crop = im.crop((int(x0 * px), int(y0 * px), int(min(x0 + tile_w, w_in) * px), int(min(y0 + tile_h, h_in) * px)))
            cw, ch = crop.size[0] / px, crop.size[1] / px
            buf = io.BytesIO(); crop.save(buf, "JPEG", quality=88); buf.seek(0)
            c.drawImage(ImageReader(buf), margin * inch, (11 - margin - ch) * inch, cw * inch, ch * inch)
            # crop / overlap guides
            c.setStrokeColorRGB(0.6, 0.6, 0.6); c.setLineWidth(0.4); c.setDash(4, 3)
            if col < cols - 1:
                xo = (margin + tile_w - overlap) * inch
                c.line(xo, (11 - margin) * inch, xo, (11 - margin - ch) * inch)
            if r < rows - 1:
                yo = (11 - margin - tile_h + overlap) * inch
                c.line(margin * inch, yo, (margin + cw) * inch, yo)
            c.setDash()
            c.setFillColorRGB(0.35, 0.35, 0.35); c.setFont("Helvetica-Bold", 9)
            c.drawString(margin * inch, 0.22 * inch, f"{name}  |  tile {chr(65+r)}{col+1} of {chr(64+rows)}{cols}  |  print at 100%, do not scale")
            c.showPage()
    c.save()
    return cols, rows


def export(name, svg, w_in, h_in):
    for sub in ("svg", "print", "home-print", "preview"):
        os.makedirs(os.path.join(DIST, sub), exist_ok=True)
    with open(os.path.join(DIST, "svg", f"{name}.svg"), "w") as f:
        f.write(svg)
    # Full-size print PDF: artwork + CutContour hairline, true size
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=os.path.join(DIST, "print", f"{name}-print.pdf"))
    art_only = strip_cut(svg)
    cairosvg.svg2png(bytestring=art_only.encode(), write_to=os.path.join(DIST, "preview", f"{name}.png"),
                     output_width=1400, output_height=int(1400 * h_in / w_in))
    cols, rows = tile_letter(name, art_only, w_in, h_in, os.path.join(DIST, "home-print", f"{name}-tiled-letter.pdf"))
    print(f"{name}: {w_in}x{h_in} in, tiled {cols}x{rows} = {cols*rows} Letter pages")


def montage():
    names = ["dumbbell", "thumbs-up-light", "thumbs-up-medium", "thumbs-up-deep"]
    ims = [Image.open(os.path.join(DIST, "preview", f"{n}.png")).convert("RGBA") for n in names]
    H = 900
    scaled = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    pad = 40
    W = sum(s.width for s in scaled) + pad * (len(scaled) + 1)
    out = Image.new("RGBA", (W, H + 2 * pad), (236, 246, 253, 255))
    x = pad
    for s in scaled:
        out.alpha_composite(s, (x, pad)); x += s.width + pad
    out.convert("RGB").save(os.path.join(DIST, "preview", "all-props.png"), optimize=True)


if __name__ == "__main__":
    export("dumbbell", dumbbell(), DB_W, DB_H)
    for tone in SKIN_TONES:
        export(f"thumbs-up-{tone}", thumbs_up(tone), THUMB_W, THUMB_H)
    montage()
    print("done ->", DIST)
