#!/usr/bin/env python3
"""
Break an exercise video into per-exercise clips and re-render each one as a
faceless figure on a blank gym background.

Pipeline (each step can be run on its own):

  download  : fetch a YouTube video with yt-dlp        -> work/source.mp4
  scenes    : ffmpeg scene-change detection            -> work/segments.json
  split     : cut one clip per segment + contact sheet -> work/clips/, work/contact_sheet.jpg
  faceless  : MediaPipe pose -> stylised faceless body -> work/faceless/
  all       : everything above, then work/report.md

Usage:
  python3 breakdown.py all  "https://youtube.com/shorts/VIDEO_ID"  --work work
  python3 breakdown.py all  local_file.mp4 --work work --threshold 0.35

Dependencies: yt-dlp and ffmpeg on PATH, opencv-python-headless, mediapipe, numpy.
The pose model (pose_landmarker_full.task) is downloaded on first use.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_full/float16/latest/pose_landmarker_full.task"
)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def video_info(path: Path) -> tuple[float, float]:
    """(duration_seconds, fps) via OpenCV, so only ffmpeg is needed on PATH."""
    import cv2

    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return (frames / fps if frames > 0 else 0.0), fps


def ffprobe_duration(path: Path) -> float:
    return video_info(path)[0]


def youtube_id(url: str) -> str | None:
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def fmt_ts(t: float) -> str:
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


@dataclass
class Segment:
    index: int
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


# ----------------------------------------------------------------------------
# 1. download
# ----------------------------------------------------------------------------
def step_download(source: str, work: Path) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    dst = work / "source.mp4"
    if Path(source).exists():
        shutil.copy(source, dst)
        return dst
    if dst.exists():
        return dst
    cmd = [
        "yt-dlp", "--no-warnings",
        "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]/b",
        "--merge-output-format", "mp4",
        "-o", str(dst),
        "--print-to-file", "%(title)s\n%(uploader)s\n%(duration)s\n%(description)s",
        str(work / "meta.txt"),
        source,
    ]
    subprocess.run(cmd, check=True)
    return dst


# ----------------------------------------------------------------------------
# 2. scene detection
# ----------------------------------------------------------------------------
def step_scenes(src: Path, work: Path, threshold: float, min_len: float,
                merge_gap: float) -> list[Segment]:
    """Detect hard cuts with ffmpeg's scene score, then tidy the cut list."""
    duration = ffprobe_duration(src)
    proc = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", str(src),
            "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-an", "-f", "null", "-",
        ],
        text=True, capture_output=True,
    )
    cuts = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]

    # Collapse bursts of cuts (flashes, fast transitions) into one cut.
    merged: list[float] = []
    for t in sorted(cuts):
        if merged and t - merged[-1] < merge_gap:
            continue
        merged.append(t)

    bounds = [0.0] + merged + [duration]
    segments: list[Segment] = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a < min_len:
            # Too short to be an exercise: fold into the previous segment.
            if segments:
                segments[-1].end = b
            continue
        segments.append(Segment(len(segments) + 1, round(a, 3), round(b, 3)))

    for i, s in enumerate(segments, 1):
        s.index = i
    (work / "segments.json").write_text(json.dumps(
        {"source": str(src), "duration": duration, "threshold": threshold,
         "raw_cuts": cuts, "segments": [asdict(s) for s in segments]}, indent=2))
    return segments


def load_segments(work: Path) -> list[Segment]:
    data = json.loads((work / "segments.json").read_text())
    return [Segment(**s) for s in data["segments"]]


# ----------------------------------------------------------------------------
# 3. split + contact sheet
# ----------------------------------------------------------------------------
def step_split(src: Path, work: Path, segments: list[Segment]) -> list[Path]:
    clips_dir = work / "clips"
    clips_dir.mkdir(exist_ok=True)
    clips: list[Path] = []
    for s in segments:
        out = clips_dir / f"exercise_{s.index:02d}.mp4"
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{s.start:.3f}", "-to", f"{s.end:.3f}", "-i", str(src),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-movflags", "+faststart", str(out),
        ])
        clips.append(out)

    # Contact sheet: one mid-segment frame per exercise.
    import cv2
    import numpy as np

    thumbs = []
    cap = cv2.VideoCapture(str(src))
    for s in segments:
        cap.set(cv2.CAP_PROP_POS_MSEC, ((s.start + s.end) / 2) * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        scale = 360 / h
        frame = cv2.resize(frame, (int(w * scale), 360))
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 34), (0, 0, 0), -1)
        cv2.putText(frame, f"#{s.index}  {fmt_ts(s.start)} - {fmt_ts(s.end)}",
                    (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        thumbs.append(frame)
    cap.release()
    if thumbs:
        cols = min(4, len(thumbs))
        rows = math.ceil(len(thumbs) / cols)
        tw = max(t.shape[1] for t in thumbs)
        sheet = np.full((rows * 360, cols * tw, 3), 30, np.uint8)
        for i, t in enumerate(thumbs):
            r, c = divmod(i, cols)
            sheet[r * 360:r * 360 + 360, c * tw:c * tw + t.shape[1]] = t
        cv2.imwrite(str(work / "contact_sheet.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return clips


# ----------------------------------------------------------------------------
# 4. faceless re-render
# ----------------------------------------------------------------------------
# MediaPipe pose landmark indices
NOSE, L_EYE, R_EYE, L_EAR, R_EAR = 0, 2, 5, 7, 8
L_SH, R_SH, L_EL, R_EL, L_WR, R_WR = 11, 12, 13, 14, 15, 16
L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN = 23, 24, 25, 26, 27, 28
L_HEEL, R_HEEL, L_TOE, R_TOE = 29, 30, 31, 32

LIMBS = [
    (L_SH, L_EL), (L_EL, L_WR), (R_SH, R_EL), (R_EL, R_WR),
    (L_HIP, L_KN), (L_KN, L_AN), (R_HIP, R_KN), (R_KN, R_AN),
    (L_AN, L_TOE), (R_AN, R_TOE),
]

# Colours (BGR)
WALL = (232, 228, 222)          # warm off-white wall
FLOOR = (176, 168, 158)         # grey rubber floor
FLOOR_LINE = (150, 142, 132)
BODY = (70, 62, 58)             # near-black charcoal figure
BODY_EDGE = (40, 34, 30)
SHADOW = (160, 152, 142)


def ensure_pose_model(cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    model = cache / "pose_landmarker_full.task"
    if not model.exists():
        print("downloading pose model ...", file=sys.stderr)
        urllib.request.urlretrieve(POSE_MODEL_URL, model)
    return model


def draw_background(w: int, h: int):
    import numpy as np
    import cv2

    img = np.empty((h, w, 3), np.uint8)
    horizon = int(h * 0.72)
    img[:horizon] = WALL
    img[horizon:] = FLOOR
    cv2.line(img, (0, horizon), (w, horizon), FLOOR_LINE, 2, cv2.LINE_AA)
    # soft vignette so it reads as a room, not a flat card
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = np.clip(1 - 0.18 * np.clip(d - 0.6, 0, 1) / 0.4, 0, 1)[..., None]
    return (img * v).astype(np.uint8)


class Smoother:
    """Exponential smoothing on landmark arrays to kill frame-to-frame jitter."""

    def __init__(self, alpha: float = 0.55):
        self.alpha = alpha
        self.prev = None

    def __call__(self, pts):
        if self.prev is None or pts is None:
            self.prev = pts
            return pts
        self.prev = self.alpha * pts + (1 - self.alpha) * self.prev
        return self.prev


def draw_figure(canvas, pts, vis, w: int, h: int):
    """pts: (33, 2) normalised coords, vis: (33,) visibility."""
    import cv2
    import numpy as np

    P = (pts * [w, h]).astype(int)
    ok = vis > 0.4

    # Scale strokes to the body's on-screen size.
    if ok[L_SH] and ok[R_SH] and ok[L_HIP] and ok[R_HIP]:
        torso = np.linalg.norm(((P[L_SH] + P[R_SH]) / 2) - ((P[L_HIP] + P[R_HIP]) / 2))
    else:
        torso = h * 0.25
    limb_w = max(6, int(torso * 0.22))
    head_r = max(8, int(torso * 0.28))

    # Ground shadow under the lowest visible joint
    feet = [P[i] for i in (L_AN, R_AN, L_HEEL, R_HEEL, L_TOE, R_TOE, L_WR, R_WR) if ok[i]]
    if feet:
        cx = int(np.mean([f[0] for f in feet]))
        cy = int(max(f[1] for f in feet)) + limb_w // 2
        cv2.ellipse(canvas, (cx, cy), (int(torso * 0.7), int(limb_w * 0.6)), 0, 0, 360,
                    SHADOW, -1, cv2.LINE_AA)

    def seg(a, b, colour, width):
        if ok[a] and ok[b]:
            cv2.line(canvas, tuple(P[a]), tuple(P[b]), colour, width, cv2.LINE_AA)

    def joint(i, colour, r):
        if ok[i]:
            cv2.circle(canvas, tuple(P[i]), r, colour, -1, cv2.LINE_AA)

    # Outline pass (slightly wider, darker) then fill pass = clean silhouette edge.
    for colour, extra in ((BODY_EDGE, 4), (BODY, 0)):
        lw = limb_w + extra
        # Torso as a filled quad
        if ok[L_SH] and ok[R_SH] and ok[L_HIP] and ok[R_HIP]:
            quad = np.array([P[L_SH], P[R_SH], P[R_HIP], P[L_HIP]], np.int32)
            cv2.fillPoly(canvas, [quad], colour, cv2.LINE_AA)
            cv2.polylines(canvas, [quad], True, colour, lw, cv2.LINE_AA)
        for a, b in LIMBS:
            seg(a, b, colour, lw)
        for i in (L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN):
            joint(i, colour, lw // 2)
        # Neck + plain head disc: no facial features at all.
        if ok[L_SH] and ok[R_SH]:
            neck = ((P[L_SH] + P[R_SH]) / 2).astype(int)
            head_pts = [P[i] for i in (NOSE, L_EYE, R_EYE, L_EAR, R_EAR) if ok[i]]
            if head_pts:
                hc = np.mean(head_pts, axis=0).astype(int)
            else:
                hc = neck - [0, int(head_r * 1.6)]
            cv2.line(canvas, tuple(neck), tuple(hc), colour, lw, cv2.LINE_AA)
            cv2.circle(canvas, tuple(hc), head_r + extra // 2, colour, -1, cv2.LINE_AA)


def step_faceless(work: Path, clips: list[Path], out_h: int = 960) -> list[Path]:
    import cv2
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    model = ensure_pose_model(Path.home() / ".cache" / "video-breakdown")
    out_dir = work / "faceless"
    out_dir.mkdir(exist_ok=True)
    results: list[Path] = []

    for clip in clips:
        cap = cv2.VideoCapture(str(clip))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        src_w, src_h = int(cap.get(3)), int(cap.get(4))
        out_w = int(round(src_w * out_h / src_h / 2) * 2)
        bg = draw_background(out_w, out_h)

        options = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model)),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        landmarker = vision.PoseLandmarker.create_from_options(options)
        smooth = Smoother()

        raw = out_dir / (clip.stem + "_raw.mp4")
        writer = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"mp4v"), fps, (out_w, out_h))
        frame_i, detected = 0, 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            ts_ms = int(frame_i * 1000 / fps)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = landmarker.detect_for_video(mp_img, ts_ms)
            canvas = bg.copy()
            if res.pose_landmarks:
                lm = res.pose_landmarks[0]
                pts = np.array([[p.x, p.y] for p in lm], np.float32)
                vis = np.array([p.visibility for p in lm], np.float32)
                pts = smooth(pts)
                draw_figure(canvas, pts, vis, out_w, out_h)
                detected += 1
            writer.write(canvas)
            frame_i += 1
        writer.release()
        cap.release()
        landmarker.close()

        final = out_dir / (clip.stem + "_faceless.mp4")
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(final),
        ])
        raw.unlink()
        print(f"{clip.name}: pose found on {detected}/{frame_i} frames -> {final.name}",
              file=sys.stderr)
        results.append(final)
    return results


# ----------------------------------------------------------------------------
# 5. report
# ----------------------------------------------------------------------------
def step_report(source: str, work: Path, segments: list[Segment]) -> Path:
    vid = youtube_id(source)
    lines = [f"# Exercise breakdown", "", f"Source: {source}", "",
             f"**{len(segments)} exercises detected** (visual cuts).", "",
             "| # | Start | End | Length | Original clip | Faceless clip | Jump link |",
             "|---|-------|-----|--------|---------------|---------------|-----------|"]
    for s in segments:
        link = f"https://youtube.com/watch?v={vid}&t={int(s.start)}s" if vid else "-"
        lines.append(
            f"| {s.index} | {fmt_ts(s.start)} | {fmt_ts(s.end)} | {s.duration:.1f}s "
            f"| clips/exercise_{s.index:02d}.mp4 | faceless/exercise_{s.index:02d}_faceless.mp4 "
            f"| {link} |")
    lines += ["", "Contact sheet: contact_sheet.jpg", ""]
    out = work / "report.md"
    out.write_text("\n".join(lines))
    return out


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["download", "scenes", "split", "faceless", "all"])
    ap.add_argument("source", help="YouTube URL or local video file")
    ap.add_argument("--work", default="work", type=Path)
    ap.add_argument("--threshold", type=float, default=0.3,
                    help="ffmpeg scene score 0-1; lower = more sensitive (default 0.3)")
    ap.add_argument("--min-len", type=float, default=1.5,
                    help="segments shorter than this (s) are merged into the previous one")
    ap.add_argument("--merge-gap", type=float, default=0.5,
                    help="cuts closer than this (s) count as one cut")
    ap.add_argument("--out-height", type=int, default=960)
    args = ap.parse_args()

    work: Path = args.work
    work.mkdir(parents=True, exist_ok=True)

    if args.step in ("download", "all"):
        src = step_download(args.source, work)
        print(f"source: {src}  ({ffprobe_duration(src):.1f}s)")
    else:
        src = work / "source.mp4" if not Path(args.source).exists() else Path(args.source)

    if args.step in ("scenes", "all"):
        segs = step_scenes(src, work, args.threshold, args.min_len, args.merge_gap)
        print(f"{len(segs)} segments:")
        for s in segs:
            print(f"  #{s.index}  {fmt_ts(s.start)} -> {fmt_ts(s.end)}  ({s.duration:.1f}s)")
    else:
        segs = load_segments(work) if (work / "segments.json").exists() else []

    clips = sorted((work / "clips").glob("exercise_*.mp4"))
    if args.step in ("split", "all"):
        clips = step_split(src, work, segs)
        print(f"wrote {len(clips)} clips + contact_sheet.jpg")

    if args.step in ("faceless", "all"):
        outs = step_faceless(work, clips, args.out_height)
        print(f"wrote {len(outs)} faceless clips")

    if args.step == "all":
        print(f"report: {step_report(args.source, work, segs)}")


if __name__ == "__main__":
    main()
