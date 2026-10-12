#!/usr/bin/env python3
"""
Photo-based props: cut the real thumbs-up and dumbbell photos out of their grey
background, scale both so the fist prints the same width, build three skin tones, and
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
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate import CUT, DIST, SKIN_TONES

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source")
PPI = 150           # pixels per inch in the print files
SEG_PX = 2000       # long side used for segmentation; the mask is then scaled back to full resolution
BORDER_IN = 0.6     # white keyline
LIFE_SIZE_X = 2.0   # every hand prints at this multiple of life size, so the hands match

# crop and erase are in fractions of the source image (x, y from the top-left).
# erase polygons are painted over with the backdrop colour before segmentation, to drop
# objects that are not part of the prop (a second dumbbell, a shoe).
# span_in: what the widest unbroken run of skin on a row measures in real life for that photo.
# Thumbs up is palm-on, so the widest run is wrist to curled fingertips (hand length).
# Dumbbell is a fist seen from the back, so the widest run is across the palm and four fingers.
PROPS = {
    "thumbs-up": dict(src="thumbs-up.jpg", crop=(0.06, 0.0, 1.0, 1.0), span_in=7.5),
    "dumbbell": dict(src="dumbbell.jpg", hull=True, crop=(0.0, 0.0, 1.0, 0.86), span_in=3.8, keep=[
        # the held dumbbell's two hex plates and the hand on the handle; anything outside is dropped
        [(0.145, 0.33), (0.20, 0.245), (0.33, 0.245), (0.37, 0.33), (0.37, 0.60), (0.33, 0.70), (0.19, 0.70), (0.145, 0.60)],
        [(0.70, 0.33), (0.72, 0.245), (0.87, 0.245), (0.905, 0.33), (0.905, 0.60), (0.87, 0.69), (0.72, 0.69), (0.70, 0.60)],
        [(0.36, 0.28), (0.71, 0.28), (0.71, 1.0), (0.36, 1.0)],
    ], erase=[
        # background dumbbell: everything left of the held dumbbell's left head profile
        [(0, 0), (0.20, 0), (0.20, 0.24), (0.145, 0.33), (0.145, 0.60), (0.19, 0.70), (0.21, 0.72), (0.21, 1), (0, 1)],
        # shoe, top right and down the right edge
        [(0.66, 0), (1, 0), (1, 0.75), (0.905, 0.75), (0.905, 0.33), (0.86, 0.245), (0.72, 0.245), (0.66, 0.22)],
    ]),
}


# ---------------------------------------------------------------- cut-out
def prep(bgr, crop=None, erase=None, keep=None):
    """Crop to a fraction box and paint erase polygons with the backdrop colour.
    Returns (image, erase mask) with both cropped the same way."""
    H, W = bgr.shape[:2]
    m = np.zeros((H, W), np.uint8)
    if erase:
        b = int(min(H, W) * 0.03)
        band = np.zeros((H, W), bool)
        band[:b, :] = band[-b:, :] = band[:, :b] = band[:, -b:] = True
        top = np.median(bgr[:b, :].reshape(-1, 3), axis=0)
        bot = np.median(bgr[-b:, :].reshape(-1, 3), axis=0)
        t = (np.arange(H, dtype=np.float32) / max(H - 1, 1))[:, None]
        fill = (top * (1 - t) + bot * t).astype(np.uint8)            # one colour per row
        for poly in erase:
            pts = np.array([(int(x * W), int(y * H)) for x, y in poly], np.int32)
            cv2.fillPoly(m, [pts], 255)
        rows = np.repeat(fill[:, None, :], W, axis=1)
        bgr[m > 0] = rows[m > 0]
    if keep:
        k = np.zeros((H, W), np.uint8)
        for poly in keep:
            pts = np.array([(int(x * W), int(y * H)) for x, y in poly], np.int32)
            cv2.fillPoly(k, [pts], 255)
        d = int(min(H, W) * 0.012) | 1
        k = cv2.dilate(k, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d)))
        m = cv2.bitwise_or(m, cv2.bitwise_not(k))   # outside the keep region counts as erased
    if crop:
        x0, y0, x1, y1 = crop
        bgr = bgr[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
        m = m[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
    return bgr, m


def cutout(path, hull_nonskin=False, crop=None, erase=None, keep=None):
    """GrabCut against a plain backdrop, seeded with colour distance from the backdrop plus
    local texture (the backdrop is smooth, skin and iron are not). Segmentation runs at
    SEG_PX and the mask is scaled back to the full-resolution photo.
    Returns an RGBA PIL image cropped to the subject."""
    full, erased_full = prep(cv2.imread(path), crop, erase, keep)
    FH, FW = full.shape[:2]
    scale = min(1.0, SEG_PX / max(FH, FW))
    bgr = cv2.resize(full, (int(FW * scale), int(FH * scale)), interpolation=cv2.INTER_AREA) if scale < 1 else full.copy()
    h, w = bgr.shape[:2]
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    # backdrop model from the outer frame band
    band = np.zeros((h, w), bool)
    b = int(min(h, w) * 0.03)
    band[:b, :] = band[-b:, :] = band[:, :b] = band[:, -b:] = True
    # the backdrop darkens toward the floor, so model it as a top-to-bottom gradient
    band_bgr = np.median(bgr[band].reshape(-1, 3), axis=0).astype(np.uint8)
    mu_top = lab[:b, :].reshape(-1, 3).mean(axis=0)
    mu_bot = lab[-b:, :].reshape(-1, 3).mean(axis=0)
    t = (np.arange(h, dtype=np.float32) / max(h - 1, 1))[:, None, None]
    mu = mu_top * (1 - t) + mu_bot * t
    dist = np.linalg.norm(lab - mu, axis=2)
    # how noisy is the backdrop itself (marble veins, fabric)? scale every colour threshold by it
    noise = float(np.median(dist[band]))
    tn = max(1.0, noise / 4.0)
    # local texture: std dev of luminance in a 9 px window
    g = lab[:, :, 0]
    m1 = cv2.blur(g, (9, 9)); m2 = cv2.blur(g * g, (9, 9))
    tex = np.sqrt(np.maximum(m2 - m1 * m1, 0))
    bd_sat = cv2.cvtColor(np.uint8([[band_bgr]]), cv2.COLOR_BGR2HSV)[0, 0, 1]
    chroma = bd_sat > 90                       # green screen or similar
    smooth_backdrop = np.median(tex[band]) < 3  # marble and fabric have texture of their own
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    if chroma:
        # key on colour only (a/b channels), ignore brightness so shadows on the screen stay out
        dist_ab = np.linalg.norm(lab[:, :, 1:] - mu[:, :, 1:], axis=2)
        mask[dist_ab > 18] = cv2.GC_PR_FGD
        mask[dist_ab > 40] = cv2.GC_FGD
        mask[dist_ab < 9] = cv2.GC_BGD
    else:
        mask[(dist > 14 * tn) | (smooth_backdrop & (tex > 7))] = cv2.GC_PR_FGD
        mask[(dist > 30 * tn) & (tex > 4)] = cv2.GC_FGD
        mask[(dist < 8 * tn) & ((smooth_backdrop & (tex < 3)) | ~smooth_backdrop)] = cv2.GC_BGD
    mask[band & (dist < 22 * tn)] = cv2.GC_BGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    if n > 1:
        big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        fg = np.where(labels == big, 255, 0).astype(np.uint8)
    # close notches, padding first so a notch that opens onto the frame edge gets filled too.
    # A keyed subject keeps its fine gaps (between fingers); the white keyline fills them later.
    pad = 60
    kc = 9 if chroma else 61
    fgp = cv2.copyMakeBorder(fg, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
    fgp = cv2.morphologyEx(fgp, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kc, kc)))
    fg = fgp[pad:-pad, pad:-pad]
    if hull_nonskin:
        # Shadowed iron faces are darker than the backdrop behind them: pull any such pixel
        # that sits next to the subject back into the mask before taking hulls.
        darker = (lab[:, :, 0] < mu[:, :, 0] - 9 * tn).astype(np.uint8) * 255
        near = cv2.dilate(fg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71)))
        fg = cv2.bitwise_or(fg, cv2.bitwise_and(darker, near))
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        # Cast-iron hex heads are convex. Fill each big non-skin region with its convex hull so a
        # shadowed bevel face that matches the backdrop colour is not cut away.
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        skin = (((hsv[:, :, 0] < 25) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 60) & (hsv[:, :, 2] > 110)).astype(np.uint8) * 255
        skin = cv2.dilate(skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        # only the dark plates: a bright chrome handle would join the two heads into one
        # component whose hull swallows the backdrop between them
        dark = (lab[:, :, 0] < 110).astype(np.uint8) * 255
        iron = cv2.bitwise_and(cv2.bitwise_and(fg, cv2.bitwise_not(skin)), dark)
        iron = cv2.morphologyEx(iron, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(iron, 8)
        for i in range(1, n2):
            if st2[i, cv2.CC_STAT_AREA] > 0.04 * h * w:
                comp = (lab2 == i).astype(np.uint8) * 255
                pts = np.column_stack(np.where(lab2 == i))[:, ::-1].astype(np.int32)
                hullm = np.zeros_like(fg)
                cv2.fillConvexPoly(hullm, cv2.convexHull(pts), 255)
                # the hull may only add a thin rim (a shadowed bevel), never a wedge of backdrop
                rim = cv2.dilate(comp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
                fg = cv2.bitwise_or(fg, cv2.bitwise_and(hullm, rim))
    # nothing inside an erased area is ever part of the prop, hull or not
    if erased_full.any():
        er = cv2.resize(erased_full, (w, h), interpolation=cv2.INTER_NEAREST)
        fg[er > 0] = 0
    if chroma:
        filled = fg  # keep real gaps; no hole filling
    else:
        # drop thin stubs and slivers left at the edges (far thinner than a handle or a finger)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
        contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        filled = np.zeros_like(fg)
        cv2.drawContours(filled, contours, -1, 255, cv2.FILLED)
    # back to full resolution
    mask_full = cv2.resize(filled, (FW, FH), interpolation=cv2.INTER_LINEAR)
    mask_full = (mask_full > 127).astype(np.uint8) * 255
    if chroma:
        # re-key at full resolution inside a band around the edge, for a crisp edge
        lab_f = cv2.cvtColor(full, cv2.COLOR_BGR2LAB).astype(np.float32)
        tf = (np.arange(FH, dtype=np.float32) / max(FH - 1, 1))[:, None, None]
        mu_f = mu_top * (1 - tf) + mu_bot * tf
        dab = np.linalg.norm(lab_f[:, :, 1:] - mu_f[:, :, 1:], axis=2)
        kb = int(FW * 0.01) | 1
        bandm = cv2.dilate(mask_full, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kb, kb))) - cv2.erode(mask_full, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kb, kb)))
        keyed = (dab > 22).astype(np.uint8) * 255
        mask_full = np.where(bandm > 0, keyed, mask_full).astype(np.uint8)
        mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    alpha = cv2.GaussianBlur(mask_full, (7, 7), 0)
    rgba = cv2.cvtColor(full, cv2.COLOR_BGR2RGBA)
    # despill: a strongly coloured backdrop (green screen) tints the edge pixels
    if chroma:
        e = mask_full > 0
        r, g, b = rgba[:, :, 0].astype(np.int32), rgba[:, :, 1].astype(np.int32), rgba[:, :, 2].astype(np.int32)
        lim = (r + b) // 2
        spill = e & (g > lim)
        rgba[:, :, 1][spill] = lim[spill].astype(np.uint8)
    rgba[:, :, 3] = alpha
    ys, xs = np.where(alpha > 0)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    return Image.fromarray(rgba[y0:y1 + 1, x0:x1 + 1]), (y1 + 1 >= FH - 2)


# ---------------------------------------------------------------- skin tone
def skin_mask(rgba):
    """Soft mask of skin within the subject: warm, moderately saturated pixels."""
    arr = np.array(rgba)
    hsv = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2HSV)
    hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    m = ((hue < 25) | (hue > 170)) & (sat > 35) & (val > 60) & (arr[:, :, 3] > 0)
    m = m.astype(np.uint8) * 255
    k = max(9, int(arr.shape[1] * 0.006)) | 1
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k // 2 | 1, k // 2 | 1)))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(m)
    cv2.drawContours(filled, cnts, -1, 255, cv2.FILLED)
    m = cv2.bitwise_and(filled, (arr[:, :, 3] > 0).astype(np.uint8) * 255)
    m = cv2.GaussianBlur(m, (k, k), 0)
    return m.astype(np.float32) / 255.0


def fist_width_px(rgba):
    """Width of the fist across the knuckles: the widest unbroken run of skin on a row."""
    arr = np.array(rgba)
    hsv = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2HSV)
    # stricter than skin_mask: real skin here is bright and clearly warm; metal reflections are not
    m = (((hsv[:, :, 0] < 25) | (hsv[:, :, 0] > 170)) & (hsv[:, :, 1] > 50) & (hsv[:, :, 2] > 70) & (arr[:, :, 3] > 0)).astype(np.uint8)
    k = max(9, int(arr.shape[1] * 0.006)) | 1
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) > 0
    ys = np.where(m.any(axis=1))[0]
    y0, y1 = ys.min(), ys.max()
    runs = []
    for row in range(y0, y1 + 1, max(1, (y1 - y0) // 400)):
        cols = np.where(m[row])[0]
        if len(cols) == 0:
            continue
        breaks = np.where(np.diff(cols) > 1)[0]
        starts = np.r_[0, breaks + 1]; ends = np.r_[breaks, len(cols) - 1]
        runs.append(int((cols[ends] - cols[starts] + 1).max()))
    # the fist is the widest stable part of the hand (wrist and thumb are narrower): take the
    # 97th percentile of the per-row widest run, not a one-row spike
    return int(np.percentile(runs, 97))


def retone(rgba, tone):
    """Multiply skin pixels so the average skin colour lands on the tone's base colour. Texture and shading stay."""
    arr = np.array(rgba).astype(np.float32)
    m = skin_mask(rgba)
    skin = arr[:, :, :3][m > 0.9]
    avg = skin.mean(axis=0) if len(skin) else np.array([225, 180, 160])
    photo_targets = {"light": (226, 182, 160), "medium": (188, 136, 104), "deep": (104, 66, 44)}
    target = np.array(photo_targets[tone], np.float32)
    k = target / avg
    k = k / max(1.0, float(k.max()))   # never brighten past the photo's own highlights (clips to white spots)
    # darker tones: keep a little more highlight than a pure multiply so the hand does not go flat
    gamma = {"light": 1.0, "medium": 1.0, "deep": 0.92}[tone]
    rgb = arr[:, :, :3] / 255.0
    toned = np.clip((rgb ** gamma) * k, 0, 1) * 255.0
    out = arr.copy()
    out[:, :, :3] = rgb * 255.0 * (1 - m[..., None]) + toned * m[..., None]
    return Image.fromarray(out.astype(np.uint8))


# ---------------------------------------------------------------- compose
def compose(subject, span_px, span_in):
    """Scale the cut-out so the measured span prints at LIFE_SIZE_X times its real size, add the keyline.
    Returns (RGBA image, cut mask, finished size in inches)."""
    ppi = PPI
    scale = span_in * LIFE_SIZE_X * ppi / span_px
    subj = subject.resize((int(subject.width * scale), int(subject.height * scale)), Image.LANCZOS)
    border = int(BORDER_IN * ppi)
    W, H = subj.width + 2 * border, subj.height + 2 * border
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(subj, (border, border))
    alpha = np.array(layer.split()[3])
    hard = (alpha > 40).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border + 1, 2 * border + 1))
    key = cv2.dilate(hard, k)
    key = cv2.morphologyEx(key, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.2 * ppi) | 1, int(1.2 * ppi) | 1)))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    white.putalpha(Image.fromarray(key))
    out = Image.alpha_composite(white, layer)
    return out, key, (W / ppi, H / ppi)


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
def export(name, rgba, key, size_in):
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
    import base64
    buf = io.BytesIO(); flat.save(buf, "JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{w_in:.2f}in" height="{h_in:.2f}in" viewBox="0 0 {w_in*100:.0f} {h_in*100:.0f}">\n'
           f'<title>{name}</title>\n<g id="Artwork"><image width="{w_in*100:.0f}" height="{h_in*100:.0f}" '
           f'xlink:href="data:image/jpeg;base64,{b64}"/></g>\n'
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
        "then cut along the outside of the white border.",
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
    only = sys.argv[1:]
    for base, spec in PROPS.items():
        if only and base not in only:
            continue
        subject, _ = cutout(os.path.join(SRC, spec["src"]), hull_nonskin=spec.get("hull", False),
                            crop=spec.get("crop"), erase=spec.get("erase"), keep=spec.get("keep"))
        subject.save(os.path.join(DIST, "cutouts", f"{base}-cutout.png"))
        chk = Image.new("RGB", subject.size, (255, 255, 255)); chk.paste(subject, mask=subject.split()[3])
        chk.save(os.path.join(DIST, "cutouts", f"{base}-cutout-check.jpg"), quality=85)
        span = fist_width_px(subject)
        print(f"{base}: widest skin run {span} px = {spec['span_in']} in real -> prints {spec['span_in'] * LIFE_SIZE_X:.0f} in")
        for tone in SKIN_TONES:
            name = f"photo-{base}-{tone}"
            rgba, key, size_in = compose(retone(subject, tone), span, spec["span_in"])
            results[name] = export(name, rgba, key, size_in)
    if only:
        print("done (subset, montages skipped)"); sys.exit(0)
    montage(["photo-dumbbell-light", "photo-dumbbell-medium", "photo-dumbbell-deep"], "all-dumbbells.png")
    montage(["photo-thumbs-up-light", "photo-thumbs-up-medium", "photo-thumbs-up-deep"], "all-thumbs.png")
    montage(["photo-dumbbell-medium", "photo-thumbs-up-light", "photo-thumbs-up-medium", "photo-thumbs-up-deep"], "all-photo-props.png")
    print("done")
