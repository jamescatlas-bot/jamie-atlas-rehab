#!/usr/bin/env python3
"""
Break an exercise video into per-exercise clips and re-render each one as a
faceless figure on a blank gym background.

Pipeline (each step can be run on its own):

  download  : fetch a YouTube video with yt-dlp            -> work/source.mp4
  pose      : MediaPipe pose landmarks for every frame     -> work/pose.json
  scenes    : cuts + interludes + posture change-points    -> work/segments.json
  split     : cut one clip per segment + contact sheet     -> work/clips/, work/contact_sheet.jpg
  faceless  : stylised faceless body from the pose track   -> work/faceless/
  all       : everything above, then work/report.md

How segmentation works
  1. ffmpeg's scene score finds hard cuts (>= --threshold) and softer jump
     cuts (>= --jump-threshold) in the same framing.
  2. Frames whose colour is far from the video's dominant look (b-roll,
     title cards, a swipe to another video) are marked as interludes and
     dropped.
  3. Inside each remaining shot the tracked body is classified per frame as
     standing / hinge / squat / floor. Runs of the same movement pattern
     become one exercise; short standing gaps between reps are absorbed,
     long standing gaps are treated as rest.
  4. Later segments with the same pattern as an earlier one are flagged as
     repeats (Shorts loop, circuits repeat), so the report can give a count
     of distinct exercises as well as instances.

Usage:
  python3 breakdown.py all "https://youtube.com/shorts/VIDEO_ID" --work work
  python3 breakdown.py all recording.mp4 --work work

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
from dataclasses import dataclass, asdict, field
from pathlib import Path

POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_full/float16/latest/pose_landmarker_full.task"
)

PATTERN_NAMES = {
    "hinge": "Hip hinge (deadlift / swing pattern)",
    "squat": "Squat pattern",
    "floor": "Floor pattern (push-up / plank)",
}


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def video_info(path: Path) -> tuple[float, float, int, int]:
    """(duration_s, fps, width, height) via OpenCV so only ffmpeg is needed on PATH."""
    import cv2

    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (frames / fps if frames > 0 else 0.0), fps, w, h


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
    pattern: str = "unknown"
    label: str = ""
    shot: int = 0
    person: int = 0
    repeat_of: int | None = None

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
        if Path(source).resolve() != dst.resolve():
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
# 2. pose tracking (shared by segmentation and the faceless render)
# ----------------------------------------------------------------------------
def ensure_pose_model(cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    model = cache / "pose_landmarker_full.task"
    if not model.exists():
        print("downloading pose model ...", file=sys.stderr)
        urllib.request.urlretrieve(POSE_MODEL_URL, model)
    return model


def step_pose(src: Path, work: Path, max_people: int = 2) -> dict:
    """Run MediaPipe once over the whole video. Persons are sorted left to right
    per frame so index 0 is always the left-most body."""
    import cv2
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    model = ensure_pose_model(Path.home() / ".cache" / "video-breakdown")
    options = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=max_people,
        min_pose_detection_confidence=0.4,
        min_tracking_confidence=0.4,
    )
    landmarker = vision.PoseLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames: list[list] = []
    sat: list[float] = []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (96, 96))
        sat.append(float(cv2.cvtColor(small, cv2.COLOR_BGR2HSV)[..., 1].mean()))
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        res = landmarker.detect_for_video(img, int(i * 1000 / fps))
        people = []
        for lm, wl in zip(res.pose_landmarks, res.pose_world_landmarks):
            people.append({
                "img": [[round(p.x, 4), round(p.y, 4), round(p.visibility, 3)] for p in lm],
                "world": [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in wl],
            })
        people.sort(key=lambda P: sum(p[0] for p in P["img"]) / 33)
        frames.append(people)
        i += 1
        if i % 300 == 0:
            print(f"  pose: {i} frames", file=sys.stderr)
    cap.release()
    landmarker.close()
    data = {"fps": fps, "frames": frames, "saturation": sat}
    (work / "pose.json").write_text(json.dumps(data))
    return data


def load_pose(work: Path) -> dict:
    return json.loads((work / "pose.json").read_text())


# MediaPipe pose landmark indices
NOSE, L_EYE, R_EYE, L_EAR, R_EAR = 0, 2, 5, 7, 8
L_SH, R_SH, L_EL, R_EL, L_WR, R_WR = 11, 12, 13, 14, 15, 16
L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN = 23, 24, 25, 26, 27, 28
L_HEEL, R_HEEL, L_TOE, R_TOE = 29, 30, 31, 32


def posture_features(P) -> tuple[float, float, float]:
    """(torso angle from vertical in degrees, hip height above ankles in torso
    lengths, average wrist height above hips in torso lengths)."""
    import numpy as np

    P = np.asarray(P)[:, :2]
    sh = (P[L_SH] + P[R_SH]) / 2
    hip = (P[L_HIP] + P[R_HIP]) / 2
    an = (P[L_AN] + P[R_AN]) / 2
    wr = (P[L_WR] + P[R_WR]) / 2
    torso = float(np.linalg.norm(sh - hip)) + 1e-6
    ang = math.degrees(math.atan2(abs(sh[0] - hip[0]), abs(hip[1] - sh[1])))
    return ang, float((an[1] - hip[1]) / torso), float((hip[1] - wr[1]) / torso)


def classify_frame(P) -> str:
    ang, hip_h, _ = posture_features(P)
    if hip_h < 0.55:
        return "floor"
    if ang > 35:
        return "hinge"
    if hip_h < 1.25:
        return "squat"
    return "stand"


# ----------------------------------------------------------------------------
# 3. segmentation
# ----------------------------------------------------------------------------
def scene_scores(src: Path, floor: float = 0.04) -> list[tuple[float, float]]:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(src),
         "-vf", f"select='gte(scene,{floor})',metadata=print:file=-", "-an", "-f", "null", "-"],
        text=True, capture_output=True,
    )
    out, t = [], None
    for line in proc.stdout.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            t = float(m.group(1))
        m = re.search(r"scene_score=([0-9.]+)", line)
        if m and t is not None:
            out.append((t, float(m.group(1))))
    return out


def step_scenes(src: Path, work: Path, pose: dict, threshold: float, jump_threshold: float,
                min_len: float, rest_gap: float, merge_gap: float) -> list[Segment]:
    import numpy as np

    duration, fps, _, _ = video_info(src)
    scores = scene_scores(src)
    cuts = sorted(t for t, s in scores if s >= jump_threshold)
    merged: list[float] = []
    for t in cuts:
        if merged and t - merged[-1] < merge_gap:
            continue
        merged.append(t)

    # Interludes: frames whose saturation is far from the median look.
    sat = np.array(pose["saturation"])
    med = float(np.median(sat))
    mad = float(np.median(np.abs(sat - med))) + 1.0
    off = np.abs(sat - med) > max(6 * mad, 25)
    n = len(sat)

    # Per-frame posture class for the most complete body in the frame.
    frames = pose["frames"]
    # Per-frame posture class. With several people (partner videos) take the
    # most "active" class across bodies, so one badly tracked body can't hide
    # the movement the group is doing.
    rank = {"floor": 0, "hinge": 1, "squat": 2, "stand": 3}
    classes = []
    for people in frames:
        if not people:
            classes.append(None)
            continue
        classes.append(min((classify_frame(P["img"]) for P in people), key=rank.get))

    # Shots = spans between cuts, minus interlude frames.
    bounds = [0.0] + merged + [duration]
    shots: list[tuple[float, float]] = []
    for a, b in zip(bounds, bounds[1:]):
        fa, fb = int(a * fps), min(int(b * fps), n)
        if fb <= fa:
            continue
        if off[fa:fb].mean() > 0.5:
            continue  # this whole shot is b-roll / not the gym
        # trim interlude frames at the edges of the shot
        while fa < fb and off[fa]:
            fa += 1
        while fb > fa and off[fb - 1]:
            fb -= 1
        if fb > fa:
            shots.append((fa / fps, fb / fps))

    # Within each shot: 0.5 s bins, each classified from a 1 s look-ahead so a
    # single rep (which passes through standing at the top) reads as one pattern.
    win, step = 1.0, 0.5
    priority = ["floor", "hinge", "squat"]
    segments: list[Segment] = []
    for shot_i, (a, b) in enumerate(shots, 1):
        bins = []
        t = a
        while t < b:
            fa, fb = int(t * fps), min(int((t + win) * fps), int(b * fps))
            cl = [c for c in classes[fa:fb] if c]
            pat = None
            if cl:
                pat = "stand"
                for p in priority:
                    if cl.count(p) / len(cl) >= 0.2:
                        pat = p
                        break
            bins.append([t, min(t + step, b), pat])
            t += step

        # Runs of consecutive bins with the same pattern.
        runs: list[list] = []
        for bs, be, pat in bins:
            if runs and runs[-1][2] == pat:
                runs[-1][1] = be
            else:
                runs.append([bs, be, pat])

        def is_move(r):
            return r[2] in priority

        def length(j):
            return runs[j][1] - runs[j][0]

        def fold(k, j):
            lo, hi = min(j, k), max(j, k)
            runs[lo][1] = runs[hi][1]
            runs[lo][2] = runs[j][2]
            del runs[hi]

        # 1. Getting down to / up from the floor reads as a hinge or squat, so a
        #    floor run takes its short movement neighbours first.
        changed = True
        while changed:
            changed = False
            for k, r in enumerate(runs):
                if is_move(r) and r[2] != "floor" and length(k) < min_len:
                    nb = [j for j in (k - 1, k + 1) if 0 <= j < len(runs) and runs[j][2] == "floor"]
                    if nb:
                        fold(k, max(nb, key=length))
                        changed = True
                        break
        # 2. Absorb short standing / undetected gaps between two runs of the same
        #    movement (the top of each rep looks like standing).
        changed = True
        while changed:
            changed = False
            for k in range(1, len(runs) - 1):
                if not is_move(runs[k]) and length(k) < rest_gap \
                        and runs[k - 1][2] == runs[k + 1][2] and is_move(runs[k - 1]):
                    runs[k - 1][1] = runs[k + 1][1]
                    del runs[k:k + 2]
                    changed = True
                    break
        # 3. Whatever movement is still too short is treated as rest.
        for r in runs:
            if is_move(r) and r[1] - r[0] < min_len:
                r[2] = "stand"

        for rs, re_, pat in runs:
            if pat not in priority or re_ - rs < min_len:
                continue
            segments.append(Segment(0, round(rs, 2), round(re_, 2), pattern=pat,
                                    label=PATTERN_NAMES.get(pat, pat), shot=shot_i))

    # Number and flag repeats of an earlier pattern.
    first_seen: dict[str, int] = {}
    for i, s in enumerate(segments, 1):
        s.index = i
        if s.pattern in first_seen:
            s.repeat_of = first_seen[s.pattern]
        else:
            first_seen[s.pattern] = i

    (work / "segments.json").write_text(json.dumps({
        "source": str(src), "duration": duration, "threshold": threshold,
        "jump_threshold": jump_threshold, "cuts": merged, "shots": shots,
        "interlude_frames": int(off.sum()),
        "segments": [asdict(s) for s in segments],
    }, indent=2))
    return segments


def load_segments(work: Path) -> list[Segment]:
    data = json.loads((work / "segments.json").read_text())
    return [Segment(**s) for s in data["segments"]]


# ----------------------------------------------------------------------------
# 4. split + contact sheet
# ----------------------------------------------------------------------------
def step_split(src: Path, work: Path, segments: list[Segment]) -> list[Path]:
    import cv2
    import numpy as np

    clips_dir = work / "clips"
    clips_dir.mkdir(exist_ok=True)
    clips: list[Path] = []
    for s in segments:
        out = clips_dir / f"exercise_{s.index:02d}.mp4"
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{s.start:.3f}", "-to", f"{s.end:.3f}", "-i", str(src),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-movflags", "+faststart", str(out),
        ])
        clips.append(out)

    thumbs = []
    cap = cv2.VideoCapture(str(src))
    for s in segments:
        cap.set(cv2.CAP_PROP_POS_MSEC, ((s.start + s.end) / 2) * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        frame = cv2.resize(frame, (int(w * 360 / h), 360))
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 52), (0, 0, 0), -1)
        tag = f"#{s.index}" + (f" (repeat of #{s.repeat_of})" if s.repeat_of else "")
        cv2.putText(frame, f"{tag}  {fmt_ts(s.start)}-{fmt_ts(s.end)}", (8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, s.label[:34], (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (200, 230, 255), 1, cv2.LINE_AA)
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
# 5. faceless re-render
# ----------------------------------------------------------------------------
LIMBS = [
    (L_SH, L_EL), (L_EL, L_WR), (R_SH, R_EL), (R_EL, R_WR),
    (L_HIP, L_KN), (L_KN, L_AN), (R_HIP, R_KN), (R_KN, R_AN),
    (L_AN, L_TOE), (R_AN, R_TOE),
]
WALL = (232, 228, 222)          # BGR: warm off-white wall
FLOOR = (176, 168, 158)         # grey rubber floor
FLOOR_LINE = (150, 142, 132)
BODY = (70, 62, 58)             # charcoal figure
BODY_EDGE = (40, 34, 30)
SHADOW = (160, 152, 142)


def draw_background(w: int, h: int, horizon_frac: float = 0.78):
    import cv2
    import numpy as np

    img = np.empty((h, w, 3), np.uint8)
    horizon = int(h * horizon_frac)
    img[:horizon] = WALL
    img[horizon:] = FLOOR
    cv2.line(img, (0, horizon), (w, horizon), FLOOR_LINE, 2, cv2.LINE_AA)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = np.clip(1 - 0.18 * np.clip(d - 0.6, 0, 1) / 0.4, 0, 1)[..., None]
    return (img * v).astype(np.uint8)


def draw_figure(canvas, P, vis, torso_px: float):
    """P: (33, 2) pixel coords, vis: (33,) visibility, torso_px: shoulder-hip length."""
    import cv2
    import numpy as np

    P = P.astype(int)
    ok = vis > 0.3
    for i in (L_SH, R_SH, L_HIP, R_HIP, NOSE, L_EYE, R_EYE, L_EAR, R_EAR):
        ok[i] = vis[i] > 0.1   # the tracker still places these well when occluded
    limb_w = max(6, int(torso_px * 0.24))
    head_r = max(8, int(torso_px * 0.30))

    feet = [P[i] for i in (L_AN, R_AN, L_HEEL, R_HEEL, L_TOE, R_TOE, L_WR, R_WR) if ok[i]]
    if feet:
        cx = int(np.mean([f[0] for f in feet]))
        cy = int(max(f[1] for f in feet)) + limb_w // 2
        cv2.ellipse(canvas, (cx, cy), (int(torso_px * 0.8), int(limb_w * 0.6)), 0, 0, 360,
                    SHADOW, -1, cv2.LINE_AA)

    for colour, extra in ((BODY_EDGE, 4), (BODY, 0)):
        lw = limb_w + extra
        if ok[L_SH] and ok[R_SH] and ok[L_HIP] and ok[R_HIP]:
            quad = np.array([P[L_SH], P[R_SH], P[R_HIP], P[L_HIP]], np.int32)
            cv2.fillPoly(canvas, [quad], colour, cv2.LINE_AA)
            cv2.polylines(canvas, [quad], True, colour, lw, cv2.LINE_AA)
            mid_sh = ((P[L_SH] + P[R_SH]) / 2).astype(int)
            mid_hip = ((P[L_HIP] + P[R_HIP]) / 2).astype(int)
            cv2.line(canvas, tuple(mid_sh), tuple(mid_hip), colour, int(lw * 1.6), cv2.LINE_AA)
        for a, b in LIMBS:
            if ok[a] and ok[b]:
                cv2.line(canvas, tuple(P[a]), tuple(P[b]), colour, lw, cv2.LINE_AA)
        for i in (L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN):
            if ok[i]:
                cv2.circle(canvas, tuple(P[i]), lw // 2, colour, -1, cv2.LINE_AA)
        if ok[L_SH] and ok[R_SH]:
            neck = ((P[L_SH] + P[R_SH]) / 2).astype(int)
            head_pts = [P[i] for i in (NOSE, L_EYE, R_EYE, L_EAR, R_EAR) if ok[i]]
            hc = np.mean(head_pts, axis=0).astype(int) if head_pts else neck - [0, int(head_r * 1.6)]
            cv2.line(canvas, tuple(neck), tuple(hc), colour, lw, cv2.LINE_AA)
            cv2.circle(canvas, tuple(hc), head_r + extra // 2, colour, -1, cv2.LINE_AA)


def pick_person(frames: list[list], fa: int, fb: int) -> int:
    """Index (left-to-right) of the body that is tallest, most visible and most
    steadily tracked in the span. Jitter (mean joint displacement between
    frames, in body heights) penalises bodies the tracker keeps losing."""
    import numpy as np

    stats: dict[int, dict] = {}
    prev: dict[int, np.ndarray] = {}
    for people in frames[fa:fb]:
        for k, P in enumerate(people):
            A = np.asarray(P["img"])
            h = max(A[:, 1].max() - A[:, 1].min(), 1e-3)
            st = stats.setdefault(k, {"score": [], "jit": []})
            st["score"].append(h * A[:, 2].mean())
            if k in prev:
                st["jit"].append(float(np.abs(A[:, :2] - prev[k]).mean()) / h)
            prev[k] = A[:, :2]
    if not stats:
        return 0

    def rank(k):
        st = stats[k]
        jit = np.mean(st["jit"]) if st["jit"] else 0.0
        return np.mean(st["score"]) * (len(st["score"]) ** 0.5) / (1 + 25 * jit)

    return max(stats, key=rank)


VIEW_FOR_PATTERN = {"hinge": "side", "floor": "side", "squat": "three-quarter"}
VIEW_ANGLE = {"front": 0.0, "three-quarter": 45.0, "side": 90.0}


def step_faceless(work: Path, segments: list[Segment], pose: dict, src: Path,
                  out_w: int = 720, out_h: int = 1280, alpha: float = 0.45,
                  person: int | None = None, view: str = "auto") -> list[Path]:
    """Draw the tracked body from MediaPipe's metric 3D landmarks, rotated to a
    viewpoint that shows the movement (a hinge seen from the front collapses
    into nothing; from the side it is obvious). Feet are pinned to the floor
    line so squats and get-downs keep their vertical travel."""
    import cv2
    import numpy as np

    fps = pose["fps"]
    frames = pose["frames"]
    out_dir = work / "faceless"
    out_dir.mkdir(exist_ok=True)
    horizon = 0.78
    bg = draw_background(out_w, out_h, horizon)
    floor_y = out_h * (horizon + 0.10)
    results: list[Path] = []

    for s in segments:
        fa, fb = int(s.start * fps), min(int(s.end * fps), len(frames))
        who = person if person is not None else pick_person(frames, fa, fb)
        s.person = who
        v = view if view != "auto" else VIEW_FOR_PATTERN.get(s.pattern, "three-quarter")
        ang = math.radians(VIEW_ANGLE[v])
        rot = np.array([[math.cos(ang), 0, math.sin(ang)], [0, 1, 0]], np.float32)  # 3D -> 2D

        # Rotate, smooth, and reject tracker glitches (a jump of > 25 cm per
        # joint per frame is not a human moving).
        track: list = []
        prev = None
        for people in frames[fa:fb]:
            if len(people) > who:
                W = np.asarray(people[who]["world"], np.float32)
                vis = np.asarray(people[who]["img"], np.float32)[:, 2]
                P = W @ rot.T
                if prev is not None and np.abs(P - prev).mean() > 0.25:
                    P = prev
                elif prev is not None:
                    P = alpha * P + (1 - alpha) * prev
                prev = P
                track.append((P, vis))
            else:
                track.append((prev, np.ones(33, np.float32)) if prev is not None else None)
        have = [P for P, _ in (t for t in track if t is not None)]
        if not have:
            continue

        # Fixed scale and horizontal centring per clip; feet on the floor per frame.
        allp = np.concatenate(have)
        span_w = max(np.percentile(allp[:, 0], 98) - np.percentile(allp[:, 0], 2), 0.3)
        span_h = max(max(P[:, 1].max() - P[:, 1].min() for P in have), 0.5)
        scale = min(out_w * 0.80 / span_w, out_h * 0.68 / span_h)
        cx = (np.percentile(allp[:, 0], 98) + np.percentile(allp[:, 0], 2)) / 2

        raw = out_dir / f"exercise_{s.index:02d}_raw.mp4"
        writer = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"mp4v"), fps, (out_w, out_h))
        for item in track:
            canvas = bg.copy()
            if item is not None:
                P, vis = item
                px = np.empty_like(P)
                px[:, 0] = out_w / 2 + (P[:, 0] - cx) * scale
                px[:, 1] = floor_y - (P[:, 1].max() - P[:, 1]) * scale
                torso = np.linalg.norm((px[L_SH] + px[R_SH]) / 2 - (px[L_HIP] + px[R_HIP]) / 2)
                draw_figure(canvas, px, vis, float(max(torso, 0.18 * scale)))
            writer.write(canvas)
        writer.release()

        final = out_dir / f"exercise_{s.index:02d}_faceless.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(final)])
        raw.unlink()
        found = sum(1 for t in track if t is not None)
        print(f"  #{s.index:02d} {s.pattern:6s} person {who} {v:13s}: body on {found}/{len(track)} frames",
              file=sys.stderr)
        results.append(final)
    return results


# ----------------------------------------------------------------------------
# 6. report
# ----------------------------------------------------------------------------
def step_report(source: str, work: Path, segments: list[Segment]) -> Path:
    vid = youtube_id(source)
    distinct = [s for s in segments if s.repeat_of is None]
    lines = ["# Exercise breakdown", "", f"Source: {source}", "",
             f"**{len(distinct)} distinct exercises**, {len(segments)} instances "
             f"(repeats flagged below).", "",
             "| # | Pattern | Start | End | Length | Repeat of | Original clip | Faceless clip | Jump link |",
             "|---|---------|-------|-----|--------|-----------|---------------|---------------|-----------|"]
    for s in segments:
        link = f"https://youtube.com/watch?v={vid}&t={int(s.start)}s" if vid else "-"
        lines.append(
            f"| {s.index} | {s.label} | {fmt_ts(s.start)} | {fmt_ts(s.end)} | {s.duration:.1f}s "
            f"| {('#%d' % s.repeat_of) if s.repeat_of else '-'} "
            f"| clips/exercise_{s.index:02d}.mp4 | faceless/exercise_{s.index:02d}_faceless.mp4 "
            f"| {link} |")
    lines += ["", "Contact sheet: contact_sheet.jpg", ""]
    out = work / "report.md"
    out.write_text("\n".join(lines))
    return out


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["download", "pose", "scenes", "split", "faceless", "all"])
    ap.add_argument("source", help="YouTube URL or local video file")
    ap.add_argument("--work", default="work", type=Path)
    ap.add_argument("--threshold", type=float, default=0.3,
                    help="scene score for a hard cut (default 0.3)")
    ap.add_argument("--jump-threshold", type=float, default=0.1,
                    help="scene score for a jump cut in the same framing (default 0.1)")
    ap.add_argument("--min-len", type=float, default=2.0,
                    help="drop movement segments shorter than this many seconds")
    ap.add_argument("--rest-gap", type=float, default=3.0,
                    help="standing gaps shorter than this between the same movement are absorbed")
    ap.add_argument("--merge-gap", type=float, default=0.5,
                    help="cuts closer than this (s) count as one cut")
    ap.add_argument("--max-people", type=int, default=2)
    ap.add_argument("--out-size", default="720x1280", help="faceless render size WxH")
    ap.add_argument("--person", type=int, default=None,
                    help="which body to render, counted left to right (default: auto)")
    ap.add_argument("--view", default="auto", choices=["auto", "front", "three-quarter", "side"],
                    help="camera angle for the faceless render (auto picks per movement pattern)")
    args = ap.parse_args()

    work: Path = args.work
    work.mkdir(parents=True, exist_ok=True)
    out_w, out_h = (int(v) for v in args.out_size.lower().split("x"))

    if args.step in ("download", "all"):
        src = step_download(args.source, work)
        print(f"source: {src}  ({video_info(src)[0]:.1f}s)")
    else:
        src = Path(args.source) if Path(args.source).exists() else work / "source.mp4"

    pose = None
    if args.step in ("pose", "all") or (args.step in ("scenes", "faceless") and not (work / "pose.json").exists()):
        pose = step_pose(src, work, args.max_people)
        print(f"pose: {len(pose['frames'])} frames tracked")
    elif args.step in ("scenes", "faceless"):
        pose = load_pose(work)

    if args.step in ("scenes", "all"):
        segs = step_scenes(src, work, pose, args.threshold, args.jump_threshold,
                           args.min_len, args.rest_gap, args.merge_gap)
        distinct = sum(1 for s in segs if s.repeat_of is None)
        print(f"{distinct} distinct exercises, {len(segs)} instances:")
        for s in segs:
            rep = f"  (repeat of #{s.repeat_of})" if s.repeat_of else ""
            print(f"  #{s.index:02d}  {fmt_ts(s.start)} -> {fmt_ts(s.end)}  {s.duration:4.1f}s  {s.label}{rep}")
    else:
        segs = load_segments(work) if (work / "segments.json").exists() else []

    if args.step in ("split", "all"):
        clips = step_split(src, work, segs)
        print(f"wrote {len(clips)} clips + contact_sheet.jpg")

    if args.step in ("faceless", "all"):
        outs = step_faceless(work, segs, pose, src, out_w, out_h, person=args.person, view=args.view)
        print(f"wrote {len(outs)} faceless clips")

    if args.step == "all":
        print(f"report: {step_report(args.source, work, segs)}")


if __name__ == "__main__":
    main()
