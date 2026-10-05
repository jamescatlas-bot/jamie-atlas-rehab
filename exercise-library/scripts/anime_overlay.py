"""Hand-drawn anime overlay on one person in a video, leaving everything else untouched.

    python anime_overlay.py INPUT.mp4 OUTPUT.mp4 [--start=S --end=S --frames=N]

How it works, per frame:
  1. A person-segmentation model (U2-Net human, from rembg) finds every person.
  2. The person wearing the most pink is kept (in the test clip: the woman in pink leggings);
     her outline is smoothed over time so it doesn't flicker.
  3. AnimeGANv3 "Hayao" (trained on Miyazaki film stills) repaints the frame in that style.
  4. Only her pixels are taken from the repainted frame and blended onto the original.

Models (downloaded once into MODELS): AnimeGANv3_Hayao_36.onnx and u2net_human_seg.onnx.
AnimeGANv3 is licensed for non-commercial use only; ask its author before using results commercially.
"""
import pathlib
import subprocess
import sys

import cv2
import imageio_ffmpeg
import numpy as np
import onnxruntime as ort

MODELS = pathlib.Path(__file__).resolve().parents[1] / 'assets' / 'models'
FF = imageio_ffmpeg.get_ffmpeg_exe()
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = dict(a[2:].split('=') for a in sys.argv[1:] if a.startswith('--') and '=' in a)
SRC, DST = args[0], args[1]
SCALE = 2                      # work at twice the source size for cleaner line work

seg = ort.InferenceSession(str(MODELS / 'u2net_human_seg.onnx'))
gan = ort.InferenceSession(str(MODELS / 'AnimeGANv3_Hayao_36.onnx'))


def people_mask(rgb):
    x = cv2.resize(rgb, (320, 320), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    out = seg.run(None, {seg.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    out = (out - out.min()) / (out.max() - out.min() + 1e-6)
    return cv2.resize(out, (rgb.shape[1], rgb.shape[0]))


def pink(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return ((h > 140) | (h < 8)) & (s > 50) & (v > 90)


def her_mask(rgb, prev):
    m = people_mask(rgb)
    binm = (m > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(binm, 8)
    pk = pink(rgb)
    best, score = 0, 0
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 400:
            continue
        sc = (pk & (lab == i)).sum()
        if prev is not None:
            sc += 0.3 * ((prev > 0.5) & (lab == i)).sum()
        if sc > score:
            best, score = i, sc
    if best == 0 or score < 150:
        return np.zeros_like(m)
    keep = (lab == best).astype(np.float32)
    keep = cv2.dilate(keep, np.ones((5, 5), np.uint8))
    return np.clip(m * keep * 1.4, 0, 1)


def anime(rgb):
    h, w = rgb.shape[:2]
    H8, W8 = (h // 8) * 8, (w // 8) * 8
    x = cv2.resize(rgb, (W8, H8), interpolation=cv2.INTER_AREA).astype(np.float32) / 127.5 - 1
    y = gan.run(None, {gan.get_inputs()[0].name: x[None]})[0][0]
    y = ((y + 1) * 127.5).clip(0, 255).astype(np.uint8)
    return cv2.resize(y, (w, h), interpolation=cv2.INTER_CUBIC)


def main():
    probe = subprocess.run([FF, '-i', SRC], capture_output=True, text=True).stderr
    import re
    w, h = map(int, re.search(r'Video:.*? (\d{2,5})x(\d{2,5})', probe).groups())
    fps = float(re.search(r'([\d.]+) fps', probe).group(1))
    trim = []
    if 'start' in opt:
        trim += ['-ss', opt['start']]
    if 'end' in opt:
        trim += ['-to', opt['end']]
    reader = subprocess.Popen([FF, '-loglevel', 'error', *trim, '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                              stdout=subprocess.PIPE)
    W, H = w * SCALE, h * SCALE
    W -= W % 2; H -= H % 2
    writer = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                               '-r', str(fps), '-i', '-', *trim, '-i', SRC, '-map', '0:v', '-map', '1:a?', '-shortest',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', '-c:a', 'aac', '-movflags', '+faststart', DST],
                              stdin=subprocess.PIPE)
    prev, k, limit = None, 0, int(opt.get('frames', 10**9))
    while k < limit:
        buf = reader.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        big = cv2.resize(frame, (W, H), interpolation=cv2.INTER_LANCZOS4)
        m = her_mask(big, prev)
        if prev is not None and m.any():
            m = 0.65 * m + 0.35 * prev            # steadier outline
        prev = m
        if m.max() > 0.05:
            soft = cv2.GaussianBlur(m, (0, 0), 2.0)[..., None]
            out = (anime(big) * soft + big * (1 - soft)).astype(np.uint8)
        else:
            out = big
        writer.stdin.write(out.tobytes())
        k += 1
        if k % 30 == 0:
            print('frame', k, flush=True)
    writer.stdin.close(); writer.wait(); reader.kill()
    print('wrote', DST, k, 'frames')


if __name__ == '__main__':
    main()
