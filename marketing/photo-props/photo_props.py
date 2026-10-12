#!/usr/bin/env python3
"""
Photo-based props: cut the real thumbs-up and dumbbell photos out of their grey
background, add the JAMIE ATLAS cuff and hand hole, build three skin tones, and
export print PDFs (with vector cut contour), Letter-tiled PDFs, SVG wrappers and previews.

Source photos live in source/. Drop in higher-resolution versions of the same
photos with the same names and re-run for a sharper print.

Run:  python3 marketing/photo-props/photo_props.py
"""
import io
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate import (BLUE, BLUE_DARK, BLUE_LIGHT, WHITE, CUT, FONT_BLACK, FONT_BOLD, DIST, SKIN_TONES)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source")
PPI = 60            # working resolution: pixels per inch of finished prop (photos are ~1200 px, so ~60 ppi at this size)
BORDER_IN = 0.6     # white keyline
CUFF_IN = 8.0       # height of the branded cuff
SLOT_IN = (6.0, 1.5)

PROPS = {
    # name: (source file, finished height in inches of the photo part, cuff anchored at bottom centre)
    "thumbs-up": dict(src="thumbs-up.jpg", height_in=32.0, cuff_cx=0.5),
    "dumbbell": dict(src="dumbbell.jpg", height_in=22.0, cuff_cx=0.40, hull=True),
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- cut-out
def cutout(path, hull_nonskin=False):
    """GrabCut against the plain grey backdrop, seeded with colour distance from the
    backdrop plus local texture (the backdrop is smooth, cast iron and skin are not).
    Returns an RGBA PIL image cropped to the subject."""
    bgr = cv2.imread(path)
    h, w = bgr.shape[:2]
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    # backdrop model from the outer frame band
    band = np.zeros((h, w), bool)
    b = int(min(h, w) * 0.03)
    band[:b, :] = band[-b:, :] = band[:, :b] = band[:, -b:] = True
    # the backdrop darkens toward the floor, so model it as a top-to-bottom gradient
    mu_top = lab[:b, :].reshape(-1, 3).mean(axis=0)
    mu_bot = lab[-b:, :].reshape(-1, 3).mean(axis=0)
    t = (np.arange(h, dtype=np.float32) / max(h - 1, 1))[:, None, None]
    mu = mu_top * (1 - t) + mu_bot * t
    dist = np.linalg.norm(lab - mu, axis=2)
    # local texture: std dev of luminance in a 9 px window
    g = lab[:, :, 0]
    m1 = cv2.blur(g, (9, 9)); m2 = cv2.blur(g * g, (9, 9))
    tex = np.sqrt(np.maximum(m2 - m1 * m1, 0))
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    mask[(dist > 14) | (tex > 7)] = cv2.GC_PR_FGD
    mask[(dist > 30) & (tex > 4)] = cv2.GC_FGD
    mask[(dist < 8) & (tex < 3)] = cv2.GC_BGD
    mask[band & (dist < 22)] = cv2.GC_BGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    if n > 1:
        big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        fg = np.where(labels == big, 255, 0).astype(np.uint8)
    # close notches, padding first so a notch that opens onto the frame edge gets filled too
    pad = 60
    fgp = cv2.copyMakeBorder(fg, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
    fgp = cv2.morphologyEx(fgp, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))
    fg = fgp[pad:-pad, pad:-pad]
    if hull_nonskin:
        # Shadowed iron faces are darker than the backdrop behind them: pull any such pixel
        # that sits next to the subject back into the mask before taking hulls.
        darker = (lab[:, :, 0] < mu[:, :, 0] - 9).astype(np.uint8) * 255
        near = cv2.dilate(fg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71)))
        fg = cv2.bitwise_or(fg, cv2.bitwise_and(darker, near))
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        # Cast-iron hex heads are convex. Fill each big non-skin region with its convex hull so a
        # shadowed bevel face that matches the backdrop colour is not cut away.
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        skin = (((hsv[:, :, 0] < 25) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 60) & (hsv[:, :, 2] > 110)).astype(np.uint8) * 255
        skin = cv2.dilate(skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        iron = cv2.bitwise_and(fg, cv2.bitwise_not(skin))
        iron = cv2.morphologyEx(iron, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(iron, 8)
        for i in range(1, n2):
            if st2[i, cv2.CC_STAT_AREA] > 0.04 * h * w:
                pts = np.column_stack(np.where(lab2 == i))[:, ::-1].astype(np.int32)
                hull = cv2.convexHull(pts)
                cv2.fillConvexPoly(fg, hull, 255)
    contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(fg)
    cv2.drawContours(filled, contours, -1, 255, cv2.FILLED)
    alpha = cv2.GaussianBlur(filled, (5, 5), 0)
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
    rgba[:, :, 3] = alpha
    ys, xs = np.where(alpha > 0)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    return Image.fromarray(rgba[y0:y1 + 1, x0:x1 + 1]), (y1 + 1 >= h - 2)


# ---------------------------------------------------------------- skin tone
def skin_mask(rgba):
    """Soft mask of skin within the subject: warm, moderately saturated pixels."""
    arr = np.array(rgba)
    hsv = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2HSV)
    hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    m = ((hue < 25) | (hue > 170)) & (sat > 35) & (val > 60) & (arr[:, :, 3] > 0)
    m = m.astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m = cv2.GaussianBlur(m, (9, 9), 0)
    return m.astype(np.float32) / 255.0


def retone(rgba, tone):
    """Multiply skin pixels so the average skin colour lands on the tone's base colour. Texture and shading stay."""
    if tone == "light":
        return rgba
    arr = np.array(rgba).astype(np.float32)
    m = skin_mask(rgba)
    skin = arr[:, :, :3][m > 0.9]
    avg = skin.mean(axis=0) if len(skin) else np.array([225, 180, 160])
    photo_targets = {"medium": (188, 136, 104), "deep": (104, 66, 44)}
    target = np.array(photo_targets[tone], np.float32)
    k = target / avg
    # darker tones: keep a little more highlight than a pure multiply so the hand does not go flat
    gamma = 1.0 if tone == "medium" else 0.92
    rgb = arr[:, :, :3] / 255.0
    toned = np.clip((rgb ** gamma) * k, 0, 1) * 255.0
    out = arr.copy()
    out[:, :, :3] = rgb * 255.0 * (1 - m[..., None]) + toned * m[..., None]
    return Image.fromarray(out.astype(np.uint8))


# ---------------------------------------------------------------- compose
def font(path, px):
    return ImageFont.truetype(path, px)


def fit_text(draw, text, path, max_w, start_px):
    px = start_px
    while px > 10:
        f = font(path, px)
        if draw.textlength(text, font=f) <= max_w:
            return f
        px -= 4
    return font(path, 10)


def compose(subject, height_in, cuff_cx=0.5):
    """Place the cut-out over a blue cuff, add keyline + hand hole. Returns (RGB image, alpha mask, finished size in)."""
    ppi = PPI
    scale = height_in * ppi / subject.height
    subj = subject.resize((int(subject.width * scale), int(subject.height * scale)), Image.LANCZOS)
    border = int(BORDER_IN * ppi)
    cuff_h = int(CUFF_IN * ppi)
    cuff_w = min(int(subj.width * 0.9), int(22 * ppi))
    cuff_w = max(cuff_w, int(14 * ppi))
    W = max(subj.width, cuff_w) + 2 * border
    H = subj.height + cuff_h - int(0.6 * ppi) + 2 * border  # cuff overlaps the wrist crop by 0.6 in
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sx = (W - subj.width) // 2
    sy = border
    # cuff
    cx = int(sx + subj.width * cuff_cx - cuff_w / 2)
    cx = max(border, min(cx, W - border - cuff_w))
    cy = sy + subj.height - int(0.6 * ppi)
    tcx = cx + cuff_w / 2
    cuff = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cuff)
    r = int(0.9 * ppi)
    d.rounded_rectangle([cx, cy, cx + cuff_w, cy + cuff_h], radius=r, fill=hex_rgb(BLUE) + (255,))
    d.rounded_rectangle([cx, cy, cx + cuff_w, cy + int(1.1 * ppi)], radius=int(0.5 * ppi), fill=hex_rgb(BLUE_DARK) + (255,))
    # subject sits on top of the cuff so the wrist reads as going into a sleeve
    layer = Image.alpha_composite(cuff, Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    layer.alpha_composite(subj, (sx, sy))
    # but the cuff's lower part is drawn over the wrist crop edge: re-draw cuff below the overlap line
    front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(front)
    d2.rounded_rectangle([cx, cy + int(0.3 * ppi), cx + cuff_w, cy + cuff_h], radius=r, fill=hex_rgb(BLUE) + (255,))
    d2.rounded_rectangle([cx, cy + int(0.3 * ppi), cx + cuff_w, cy + int(1.3 * ppi)], radius=int(0.5 * ppi), fill=hex_rgb(BLUE_DARK) + (255,))
    layer.alpha_composite(front)
    d3 = ImageDraw.Draw(layer)
    f1 = fit_text(d3, "JAMIE ATLAS", FONT_BLACK, cuff_w - int(1.6 * ppi), int(2.6 * ppi))
    tw = d3.textlength("JAMIE ATLAS", font=f1)
    ty = cy + int(1.5 * ppi)
    d3.text((tcx - tw / 2, ty), "JAMIE ATLAS", font=f1, fill=WHITE)
    f2 = font(FONT_BOLD, int(0.85 * ppi))
    tw2 = d3.textlength("@jamieatlasfitness", font=f2)
    d3.text((tcx - tw2 / 2, cy + cuff_h - int(1.45 * ppi)), "@jamieatlasfitness", font=f2, fill=hex_rgb(BLUE_LIGHT))
    # hand hole, between the wordmark and the handle
    sw, sh = int(SLOT_IN[0] * ppi), int(SLOT_IN[1] * ppi)
    st = cy + int(4.6 * ppi)
    slot = (int(tcx - sw / 2), st, int(tcx + sw / 2), st + sh)
    d3.rounded_rectangle(slot, radius=sh // 2, fill=(255, 255, 255, 255))
    # keyline: dilate alpha by the border
    alpha = np.array(layer.split()[3])
    hard = (alpha > 40).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border + 1, 2 * border + 1))
    key = cv2.dilate(hard, k)
    key = cv2.morphologyEx(key, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.2 * ppi) | 1, int(1.2 * ppi) | 1)))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    white.putalpha(Image.fromarray(key))
    out = Image.alpha_composite(white, layer)
    # punch the hand hole out of the alpha too
    a = np.array(out.split()[3]); a[slot[1]:slot[3], slot[0]:slot[2]] = 0
    slot_mask = np.zeros_like(a); cv2.rectangle(slot_mask, (slot[0], slot[1]), (slot[2], slot[3]), 255, -1)
    key[slot_mask > 0] = 0
    return out, key, (W / ppi, H / ppi), slot


def contour_path_in(mask, ppi, simplify_px=2.0):
    """Outer contour(s) of the cut as SVG path data in 1/100 in units."""
    contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    parts = []
    for c in contours:
        c = cv2.approxPolyDP(c, simplify_px, True)
        if len(c) < 3:
            continue
        pts = [(p[0][0] * 100 / ppi, p[0][1] * 100 / ppi) for p in c]
        parts.append("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z")
    return " ".join(parts), contours


# ---------------------------------------------------------------- export
def export(name, rgba, key, size_in, slot):
    w_in, h_in = size_in
    for sub in ("svg", "print", "home-print", "preview"):
        os.makedirs(os.path.join(DIST, sub), exist_ok=True)
    # flatten on white for print + preview
    flat = Image.new("RGB", rgba.size, (255, 255, 255))
    flat.paste(rgba, mask=rgba.split()[3])
    prev = rgba.copy(); prev.thumbnail((1400, 1400), Image.LANCZOS)
    prev.save(os.path.join(DIST, "preview", f"{name}.png"), optimize=True)

    cut_d, contours = contour_path_in(key, PPI)
    # SVG wrapper: embedded photo + vector CutContour
    buf = io.BytesIO(); rgba.save(buf, "PNG"); import base64
    b64 = base64.b64encode(buf.getvalue()).decode()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{w_in:.2f}in" height="{h_in:.2f}in" viewBox="0 0 {w_in*100:.0f} {h_in*100:.0f}">\n'
           f'<title>{name}</title>\n<g id="Artwork"><image width="{w_in*100:.0f}" height="{h_in*100:.0f}" '
           f'xlink:href="data:image/png;base64,{b64}"/></g>\n'
           f'<g id="CutContour"><path d="{cut_d}" fill="none" stroke="{CUT}" stroke-width="0.35"/></g>\n</svg>\n')
    with open(os.path.join(DIST, "svg", f"{name}.svg"), "w") as f:
        f.write(svg)

    # Print PDF: true size, photo + magenta hairline contour
    pdf = os.path.join(DIST, "print", f"{name}-print.pdf")
    c = rl_canvas.Canvas(pdf, pagesize=(w_in * inch, h_in * inch))
    c.setTitle(f"{name} print, {w_in:.1f} x {h_in:.1f} in, cut on magenta")
    jb = io.BytesIO(); flat.save(jb, "JPEG", quality=92); jb.seek(0)
    c.drawImage(ImageReader(jb), 0, 0, w_in * inch, h_in * inch)
    c.setStrokeColorRGB(1, 0, 1); c.setLineWidth(0.25)
    for cnt in contours:
        cnt = cv2.approxPolyDP(cnt, 2.0, True)
        p = c.beginPath()
        pts = [(pt[0][0] / PPI * inch, (h_in - pt[0][1] / PPI) * inch) for pt in cnt]
        p.moveTo(*pts[0])
        for x, y in pts[1:]:
            p.lineTo(x, y)
        p.close(); c.drawPath(p, stroke=1, fill=0)
    c.showPage(); c.save()

    # Tiled Letter PDF
    from generate import tile_letter
    cols, rows = tile_letter_img(name, flat, w_in, h_in, os.path.join(DIST, "home-print", f"{name}-tiled-letter.pdf"))
    print(f"{name}: {w_in:.1f} x {h_in:.1f} in, tiled {cols}x{rows} = {cols*rows} Letter pages")
    return w_in, h_in, cols * rows


def tile_letter_img(name, im, w_in, h_in, out_pdf, dpi=150):
    """Same tiling as generate.tile_letter, from a PIL image instead of an SVG."""
    im = im.resize((int(w_in * dpi), int(h_in * dpi)), Image.LANCZOS)
    margin, overlap = 0.5, 0.5
    tile_w, tile_h = 8.5 - 2 * margin, 11 - 2 * margin
    step_w, step_h = tile_w - overlap, tile_h - overlap
    cols = math.ceil((w_in - overlap) / step_w)
    rows = math.ceil((h_in - overlap) / step_h)
    c = rl_canvas.Canvas(out_pdf, pagesize=letter)
    c.setTitle(f"{name} - tiled for US Letter")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, 10.2 * inch, f"{name}: home-print assembly map")
    c.setFont("Helvetica", 10.5)
    lines = [
        f"Finished size {w_in:.1f} x {h_in:.1f} in. {cols} columns x {rows} rows = {cols*rows} Letter pages.",
        "Print at 100% / Actual size (turn OFF 'fit to page'). Portrait. Card stock or 28 lb paper hides the seams better.",
        "Each page overlaps its neighbour by 0.5 in. Trim the RIGHT and BOTTOM edges of each page on the dashed line,",
        "then lay it over the next page so the picture lines up. Tape the back. Glue the whole sheet to foam board,",
        "then cut along the outside of the white border and cut out the hand hole.",
        "Page labels run A1, A2 ... across the top row, then B1, B2 ... for the next row down.",
    ]
    y = 9.8 * inch
    for ln in lines:
        c.drawString(0.75 * inch, y, ln); y -= 15
    scale = min(7.0 * inch / (w_in * inch), 5.5 * inch / (h_in * inch))
    mx, my = 0.75 * inch, 1.0 * inch
    mw, mh = w_in * inch * scale, h_in * inch * scale
    tb = io.BytesIO(); im.resize((max(1, int(mw)), max(1, int(mh)))).save(tb, "PNG"); tb.seek(0)
    c.drawImage(ImageReader(tb), mx, my, mw, mh)
    c.setStrokeColorRGB(1, 0, 1); c.setLineWidth(0.5); c.setFont("Helvetica-Bold", 9)
    for r in range(rows):
        for col in range(cols):
            x0, y0 = col * step_w, r * step_h
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


def montage(names, out):
    ims = [Image.open(os.path.join(DIST, "preview", f"{n}.png")).convert("RGBA") for n in names]
    H = 900
    scaled = [im.resize((int(im.width * H / im.height), H), Image.LANCZOS) for im in ims]
    pad = 40
    W = sum(s.width for s in scaled) + pad * (len(scaled) + 1)
    bg = Image.new("RGBA", (W, H + 2 * pad), (236, 246, 253, 255))
    x = pad
    for s in scaled:
        bg.alpha_composite(s, (x, pad)); x += s.width + pad
    bg.convert("RGB").save(os.path.join(DIST, "preview", out), optimize=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(DIST, "cutouts"), exist_ok=True)
    results = {}
    for base, spec in PROPS.items():
        subject, _ = cutout(os.path.join(SRC, spec["src"]), hull_nonskin=spec.get("hull", False))
        subject.save(os.path.join(DIST, "cutouts", f"{base}-cutout.png"))
        chk = Image.new("RGB", subject.size, (255, 255, 255)); chk.paste(subject, mask=subject.split()[3])
        chk.save(os.path.join(DIST, "cutouts", f"{base}-cutout-check.jpg"), quality=85)
        tones = SKIN_TONES.keys() if base == "thumbs-up" else ["light"]
        for tone in tones:
            name = f"photo-{base}-{tone}" if base == "thumbs-up" else f"photo-{base}"
            rgba, key, size_in, slot = compose(retone(subject, tone), spec["height_in"], spec["cuff_cx"])
            results[name] = export(name, rgba, key, size_in, slot)
    montage(["photo-dumbbell", "photo-thumbs-up-light", "photo-thumbs-up-medium", "photo-thumbs-up-deep"], "all-photo-props.png")
    print("done")
