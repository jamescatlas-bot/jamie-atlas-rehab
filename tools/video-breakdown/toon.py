#!/usr/bin/env python3
"""
Rotoscoped cel-shaded cartoon of one person from an exercise clip, placed in a
painted gym room and animated on twos (12 drawings per second).

  python3 toon.py --work work --person right            # all segments
  python3 toon.py --work work --person right --only 1 3 # some segments

Needs work/segments.json and work/pose.json from breakdown.py, and the
source video (work/source.mp4 or --source).

What it does per frame
  1. crops a stable box around the chosen person (union of their pose boxes
     over the clip, so the framing does not jitter),
  2. masks the person with MediaPipe's multiclass segmenter on that crop,
  3. cel-shades the crop: edge-preserving smoothing, a fixed per-clip palette
     (k-means fitted once, so colours do not flicker), soft ink outlines,
  4. composites the drawing onto a painted room (warm wall, tall window with
     sky, wooden floor, light shafts) with a soft ground shadow,
  5. holds each drawing for two frames of a 24 fps output.

It is a filter over real footage, not a generated redraw: the person's own
proportions, hair and clothing colours come through as flat cartoon shapes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from breakdown import (Segment, ensure_seg_model, load_pose, load_segments, run,  # noqa: E402
                       video_info)

# ----------------------------------------------------------------------------
# painted room
# ----------------------------------------------------------------------------
def _noise(h: int, w: int, scale: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, h // scale), max(2, w // scale))).astype(np.float32)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)


def paint_room(w: int, h: int, seed: int = 7) -> np.ndarray:
    """A warm, hand-painted looking gym: plaster wall, tall window with sky and
    clouds, wooden floorboards, soft light shafts. All BGR."""
    img = np.zeros((h, w, 3), np.float32)
    hz = int(h * 0.66)

    # wall: warm plaster with soft brushy variation
    wall_a = np.array([196, 214, 232], np.float32)   # warm cream
    wall_b = np.array([172, 196, 222], np.float32)
    t = np.linspace(0, 1, hz, dtype=np.float32)[:, None, None]
    img[:hz] = wall_a * (1 - t) + wall_b * t
    img[:hz] += (_noise(hz, w, 48, seed) - 0.5)[..., None] * 18
    img[:hz] += (_noise(hz, w, 12, seed + 1) - 0.5)[..., None] * 6

    # floor: wooden boards, warm ochre, perspective seams
    floor_a = np.array([88, 132, 178], np.float32)
    floor_b = np.array([70, 108, 150], np.float32)
    t = np.linspace(0, 1, h - hz, dtype=np.float32)[:, None, None]
    img[hz:] = floor_b * (1 - t) + floor_a * t
    img[hz:] += (_noise(h - hz, w, 6, seed + 2) - 0.5)[..., None] * 10
    vp = (w // 2, int(hz * 0.45))
    for k in range(-9, 10):
        xb = int(w / 2 + k * w * 0.16)
        tt = (hz - h) / (vp[1] - h)
        xh = int(xb + (vp[0] - xb) * tt)
        cv2.line(img, (xb, h), (xh, hz), (60, 92, 128), 2, cv2.LINE_AA)
    cv2.rectangle(img, (0, hz - 10), (w, hz), (120, 150, 176), -1)   # skirting

    # window: tall, on the left third, sky with a few clouds
    wx0, wx1 = int(w * 0.08), int(w * 0.40)
    wy0, wy1 = int(h * 0.10), int(h * 0.56)
    sky_top = np.array([236, 206, 158], np.float32)
    sky_bot = np.array([246, 232, 206], np.float32)
    t = np.linspace(0, 1, wy1 - wy0, dtype=np.float32)[:, None, None]
    img[wy0:wy1, wx0:wx1] = sky_top * (1 - t) + sky_bot * t
    rng = np.random.default_rng(seed + 3)
    for _ in range(4):
        cx = rng.integers(wx0, wx1)
        cy = rng.integers(wy0 + 10, wy0 + (wy1 - wy0) // 2)
        for j in range(5):
            r = int(rng.integers(12, 30))
            cv2.circle(img, (int(cx + rng.integers(-40, 40)), int(cy + rng.integers(-8, 8))), r,
                       (250, 248, 246), -1, cv2.LINE_AA)
    # window frame and mullions
    fr = (150, 176, 200)
    cv2.rectangle(img, (wx0 - 8, wy0 - 8), (wx1 + 8, wy1 + 8), fr, 10)
    cv2.line(img, ((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1), fr, 6)
    cv2.line(img, (wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2), fr, 6)
    cv2.rectangle(img, (wx0 - 14, wy1 + 8), (wx1 + 14, wy1 + 22), (140, 166, 192), -1)  # sill

    # wall bars on the right, a small plant on the sill
    bx0, bx1 = int(w * 0.72), int(w * 0.92)
    for i in range(9):
        y = int(h * 0.12 + i * h * 0.055)
        cv2.line(img, (bx0, y), (bx1, y), (110, 150, 190), 5, cv2.LINE_AA)
    cv2.line(img, (bx0, int(h * 0.10)), (bx0, hz - 10), (100, 140, 180), 7)
    cv2.line(img, (bx1, int(h * 0.10)), (bx1, hz - 10), (100, 140, 180), 7)
    px = wx1 - 30
    cv2.rectangle(img, (px - 14, wy1 - 6), (px + 14, wy1 + 8), (90, 120, 170), -1)
    for a in range(-60, 61, 30):
        cv2.ellipse(img, (px, wy1 - 10), (26, 9), a - 90, 0, 360, (96, 168, 120), -1, cv2.LINE_AA)

    # light shafts from the window across the floor
    shaft = np.zeros((h, w), np.float32)
    pts = np.array([[wx0, wy0], [wx1, wy0], [int(w * 0.95), h], [int(w * 0.45), h]], np.int32)
    cv2.fillConvexPoly(shaft, pts, 1.0)
    shaft = cv2.GaussianBlur(shaft, (0, 0), 40) * 0.16
    img += shaft[..., None] * np.array([200, 235, 255], np.float32)

    # paper grain and a gentle vignette
    img += (_noise(h, w, 2, seed + 4) - 0.5)[..., None] * 8
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    img *= np.clip(1 - 0.16 * np.clip(d - 0.7, 0, 1) / 0.3, 0, 1)[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------
# cel shading
# ----------------------------------------------------------------------------
class CelPalette:
    """k-means palette fitted once per clip so colours stay put between frames."""

    def __init__(self, k: int = 10):
        self.k = k
        self.centers = None

    @staticmethod
    def _lab(bgr_pixels: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(bgr_pixels.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB)
        return lab.reshape(-1, 3).astype(np.float32)

    def fit(self, samples: np.ndarray):
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
        lab = self._lab(samples)
        lab[:, 1:] *= 1.6   # weight chroma so pink, white and skin stay apart
        _, labels, centers = cv2.kmeans(lab, self.k, None, crit, 4, cv2.KMEANS_PP_CENTERS)
        self.centers = centers
        # colour each cluster with the mean of its own source pixels
        self.bgr = np.array([samples[labels.ravel() == k].mean(0) if (labels.ravel() == k).any()
                             else [128, 128, 128] for k in range(self.k)], np.float32)

    def apply(self, img: np.ndarray) -> np.ndarray:
        lab = self._lab(img.reshape(-1, 3))
        lab[:, 1:] *= 1.6
        d = ((lab[:, None, :] - self.centers[None, :, :]) ** 2).sum(-1)
        return self.bgr[d.argmin(1)].reshape(img.shape).astype(np.uint8)


def prepare(bgr: np.ndarray) -> np.ndarray:
    """Edge-preserving smoothing plus a lift in saturation, the way painted cels read."""
    smooth = bgr
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 60, 9)
    hsv = cv2.cvtColor(smooth, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.3 + 10, 0, 255)
    hsv[..., 2] = np.clip(hsv[..., 2] * 1.04 + 4, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def cel_shade(bgr: np.ndarray, palette: CelPalette) -> np.ndarray:
    smooth = prepare(bgr)
    flat = palette.apply(smooth)
    flat = cv2.medianBlur(flat, 7)
    # ink lines only where there is a real colour boundary, soft and dark brown
    grey = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    grey = cv2.GaussianBlur(grey, (0, 0), 1.6)
    edges = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 7)
    edges = cv2.GaussianBlur(edges, (0, 0), 1.0)
    ink = (255 - edges).astype(np.float32) / 255.0 * 0.55
    line_col = np.array([40, 42, 60], np.float32)
    out = flat.astype(np.float32) * (1 - ink[..., None]) + line_col * ink[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------
def person_box(pose: dict, fa: int, fb: int, side: str, src_w: int, src_h: int):
    """Stable crop box for the left/right person over a span, plus that person's
    index (by mean x) per frame."""
    xs0, ys0, xs1, ys1 = [], [], [], []
    picks = []
    for people in pose["frames"][fa:fb]:
        if not people:
            picks.append(None)
            continue
        idx = np.argsort([np.mean([p[0] for p in P["img"]]) for P in people])
        k = int(idx[-1] if side == "right" else idx[0])
        if len(people) == 1 and side == "right" and np.mean([p[0] for p in people[0]["img"]]) < 0.5:
            picks.append(None)
            continue
        picks.append(k)
        A = np.asarray(people[k]["img"], np.float32)
        A = A[A[:, 2] > 0.3]
        if len(A) < 6:
            continue
        xs0.append(np.percentile(A[:, 0], 3)); xs1.append(np.percentile(A[:, 0], 97))
        ys0.append(np.percentile(A[:, 1], 3)); ys1.append(np.percentile(A[:, 1], 97))
    if not xs0:
        return None, picks
    x0, x1 = np.percentile(xs0, 5) * src_w, np.percentile(xs1, 95) * src_w
    y0, y1 = np.percentile(ys0, 5) * src_h, np.percentile(ys1, 95) * src_h
    pad_x, pad_y = (x1 - x0) * 0.35 + 12, (y1 - y0) * 0.18 + 12
    box = (int(max(0, x0 - pad_x)), int(max(0, y0 - pad_y)),
           int(min(src_w, x1 + pad_x)), int(min(src_h, y1 + pad_y)))
    return box, picks


def render(work: Path, src: Path, segments: list[Segment], side: str, out_w: int, out_h: int,
           draw_fps: int = 12, out_fps: int = 24, up: int = 3, export_crops: bool = False):
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    pose = load_pose(work)
    _, fps, src_w, src_h = video_info(src)
    model = ensure_seg_model(Path.home() / ".cache" / "video-breakdown")
    room = paint_room(out_w, out_h)
    out_dir = work / "toon"
    out_dir.mkdir(exist_ok=True)
    floor_y = int(out_h * 0.90)
    results = []

    for s in segments:
        fa, fb = int(s.start * fps), int(s.end * fps)
        box, picks = person_box(pose, fa, fb, side, src_w, src_h)
        if box is None:
            print(f"  #{s.index:02d}: no {side} person found, skipped", file=sys.stderr)
            continue
        bx0, by0, bx1, by1 = box
        cw, ch = (bx1 - bx0) * up, (by1 - by0) * up
        scale = min(out_w * 0.82 / cw, out_h * 0.80 / ch)
        dw, dh = int(cw * scale), int(ch * scale)
        ox, oy = (out_w - dw) // 2, floor_y - dh

        def new_segmenter():
            return vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(model)),
                running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))

        def person_mask(seg, bgr, ts):
            img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
            r = seg.segment_for_video(img, ts)
            m = 1.0 - np.squeeze(r.confidence_masks[0].numpy_view()).astype(np.float32)
            return cv2.resize(m, (bgr.shape[1], bgr.shape[0]))

        # three views of the same body: whole frame, the clip's crop, and a
        # tight per-frame crop; the union survives what any one of them misses
        seg_full, seg_clip, seg_tight = new_segmenter(), new_segmenter(), new_segmenter()
        cap = cv2.VideoCapture(str(src))
        cap.set(cv2.CAP_PROP_POS_FRAMES, fa)
        step = max(1, int(round(fps / draw_fps)))
        hold = max(1, int(round(out_fps / draw_fps)))

        # pass 1: gather crops + masks for the drawn frames
        drawn = []
        prev_mask = None
        for i in range(fa, fb):
            ok, frame = cap.read()
            if not ok:
                break
            if (i - fa) % step:
                continue
            crop = frame[by0:by1, bx0:bx1]
            ts = int((i - fa) * 1000 / fps)
            m = np.maximum(person_mask(seg_full, frame, ts)[by0:by1, bx0:bx1],
                           person_mask(seg_clip, crop, ts))
            joints = None
            k = picks[i - fa] if i - fa < len(picks) else None
            if k is not None and i < len(pose["frames"]) and len(pose["frames"][i]) > k:
                A = np.asarray(pose["frames"][i][k]["img"], np.float32)
                A = A[A[:, 2] > 0.3]
                if len(A) >= 6:
                    joints = np.stack([A[:, 0] * src_w - bx0, A[:, 1] * src_h - by0], 1)
                    jx0, jx1 = np.percentile(A[:, 0], [5, 95]) * src_w
                    jy0, jy1 = np.percentile(A[:, 1], [5, 95]) * src_h
                    side_px = max(jx1 - jx0, jy1 - jy0, 60) * 1.5
                    cx, cy = (jx0 + jx1) / 2, (jy0 + jy1) / 2
                    tx0, ty0 = int(max(0, cx - side_px / 2)), int(max(0, cy - side_px / 2))
                    tx1, ty1 = int(min(src_w, cx + side_px / 2)), int(min(src_h, cy + side_px / 2))
                    if tx1 - tx0 > 16 and ty1 - ty0 > 16:
                        tm = np.zeros((src_h, src_w), np.float32)
                        tm[ty0:ty1, tx0:tx1] = person_mask(seg_tight, frame[ty0:ty1, tx0:tx1], ts)
                        m = np.maximum(m, tm[by0:by1, bx0:bx1])
            if prev_mask is not None:
                m = 0.65 * m + 0.35 * prev_mask
            prev_mask = m
            drawn.append((crop.copy(), m.copy(), joints))
        cap.release()
        for sg in (seg_full, seg_clip, seg_tight):
            sg.close()
        if not drawn:
            continue

        # palette from person pixels across the clip
        samples = []
        for crop, m, _ in drawn[::max(1, len(drawn) // 12)]:
            big = prepare(cv2.resize(crop, (cw, ch), interpolation=cv2.INTER_CUBIC))
            mm = cv2.resize(m, (cw, ch)) > 0.5
            px = big[mm]
            if len(px):
                samples.append(px[np.random.default_rng(0).choice(len(px), min(4000, len(px)), replace=False)])
        pal = CelPalette(14)
        pal.fit(np.concatenate(samples))

        if export_crops:
            crops_dir = work / "crops"
            crops_dir.mkdir(exist_ok=True)
            cw0, ch0 = (bx1 - bx0) - (bx1 - bx0) % 2, (by1 - by0) - (by1 - by0) % 2
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-ss", f"{s.start:.3f}", "-to", f"{s.end:.3f}", "-i", str(src),
                 "-vf", f"crop={cw0}:{ch0}:{bx0}:{by0},scale={cw0 * 2}:{ch0 * 2}:flags=lanczos",
                 "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                 str(crops_dir / f"exercise_{s.index:02d}_{side}.mp4")])
            mid = drawn[len(drawn) // 2][0]
            cv2.imwrite(str(crops_dir / f"exercise_{s.index:02d}_{side}_reference.png"),
                        cv2.resize(mid, (mid.shape[1] * 3, mid.shape[0] * 3), interpolation=cv2.INTER_LANCZOS4))

        raw = out_dir / f"exercise_{s.index:02d}_raw.mp4"
        writer = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"mp4v"), out_fps, (out_w, out_h))
        for crop, m, joints in drawn:
            big = cv2.resize(crop, (cw, ch), interpolation=cv2.INTER_CUBIC)
            toon = cel_shade(big, pal)
            mask = cv2.resize(m, (cw, ch))
            hard = (mask > 0.5).astype(np.uint8)
            n, lab, stats, _ = cv2.connectedComponentsWithStats(hard, 8)
            keep = np.zeros_like(hard)
            owned = set()
            r = 5 * up
            if joints is not None and len(joints):
                for jx, jy in joints * up:
                    xi, yi = int(np.clip(jx, 0, cw - 1)), int(np.clip(jy, 0, ch - 1))
                    patch = lab[max(0, yi - r):yi + r + 1, max(0, xi - r):xi + r + 1]
                    owned.update(int(v) for v in np.unique(patch) if v)
            if n > 1:
                biggest = int(1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]))
                if not owned:
                    owned = {biggest}
                # a sizeable piece that does not hang off the crop's side edges is
                # hers too (a neighbour's arm only ever enters from the side)
                for k in range(1, n):
                    x, wdt, area = stats[k, cv2.CC_STAT_LEFT], stats[k, cv2.CC_STAT_WIDTH], stats[k, cv2.CC_STAT_AREA]
                    touches_side = x <= 2 or x + wdt >= cw - 3
                    if area >= 0.25 * stats[biggest, cv2.CC_STAT_AREA] and not touches_side:
                        owned.add(k)
            for k in owned:
                if stats[k, cv2.CC_STAT_AREA] >= 0.002 * cw * ch:
                    keep[lab == k] = 1
            keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
            # fill enclosed holes (a gap inside the body is never background)
            ff = keep.copy()
            hmask = np.zeros((ch + 2, cw + 2), np.uint8)
            cv2.floodFill(ff, hmask, (0, 0), 1)
            keep = keep | (1 - ff)
            alpha = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.0)
            # outline the whole figure with a soft ink contour, as a cel would be
            contour = cv2.morphologyEx(keep, cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8)).astype(np.float32)
            contour = cv2.GaussianBlur(contour, (0, 0), 1.0) * 0.7
            toon = (toon.astype(np.float32) * (1 - contour[..., None])
                    + np.array([40, 42, 60], np.float32) * contour[..., None]).astype(np.uint8)

            toon_s = cv2.resize(toon, (dw, dh), interpolation=cv2.INTER_AREA)
            a_s = cv2.resize(alpha, (dw, dh), interpolation=cv2.INTER_AREA)[..., None]
            canvas = room.copy().astype(np.float32)
            # ground shadow under the figure's lowest pixels
            ys, xs = np.where(keep > 0)
            if len(ys):
                sh = np.zeros((out_h, out_w), np.float32)
                cx = int(ox + xs.mean() * dw / cw)
                cy = int(oy + ys.max() * dh / ch)
                rx = int(max(30, (xs.max() - xs.min()) * dw / cw * 0.5))
                cv2.ellipse(sh, (cx, cy + 6), (rx, max(8, rx // 5)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
                sh = cv2.GaussianBlur(sh, (0, 0), 14)[..., None] * 0.45
                canvas = canvas * (1 - sh) + np.array([50, 70, 100], np.float32) * sh
            region = canvas[oy:oy + dh, ox:ox + dw]
            canvas[oy:oy + dh, ox:ox + dw] = region * (1 - a_s) + toon_s.astype(np.float32) * a_s
            frame_out = np.clip(canvas, 0, 255).astype(np.uint8)
            for _ in range(hold):
                writer.write(frame_out)
        writer.release()
        final = out_dir / f"exercise_{s.index:02d}_toon.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(final)])
        raw.unlink()
        print(f"  #{s.index:02d} {s.pattern:6s}: {len(drawn)} drawings -> {final.name}", file=sys.stderr)
        results.append(final)
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", type=Path, default=Path("work"))
    ap.add_argument("--source", type=Path, default=None)
    ap.add_argument("--person", choices=["left", "right"], default="right")
    ap.add_argument("--only", type=int, nargs="*", default=None, help="segment numbers to render")
    ap.add_argument("--out-size", default="720x1280")
    ap.add_argument("--draw-fps", type=int, default=12, help="drawings per second (12 = on twos)")
    ap.add_argument("--export-crops", action="store_true",
                    help="also write the person's cropped original clip and a reference still per segment")
    args = ap.parse_args()
    src = args.source or args.work / "source.mp4"
    out_w, out_h = (int(v) for v in args.out_size.lower().split("x"))
    segs = load_segments(args.work)
    if args.only:
        segs = [s for s in segs if s.index in args.only]
    outs = render(args.work, src, segs, args.person, out_w, out_h, args.draw_fps, export_crops=args.export_crops)
    print(f"wrote {len(outs)} cartoon clips to {args.work / 'toon'}")


if __name__ == "__main__":
    main()
