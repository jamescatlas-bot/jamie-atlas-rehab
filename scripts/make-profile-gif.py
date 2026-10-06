"""Build the Jamie Atlas animated profile GIF from public/logo-white.png.

Usage: python3 scripts/make-profile-gif.py public/logo-white.png public/jamie-atlas-profile.gif 250
"""
import math, sys
from PIL import Image, ImageDraw

SRC = sys.argv[1]; OUT = sys.argv[2]
SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 250
SS = 3                       # supersample for smooth edges
S = SIZE * SS
BLUE = (0, 121, 194, 255)
FPS = 20

src = Image.open(SRC).convert("RGBA")
mark = src.crop((186, 0, 260, 124))        # figure mark
name = src.crop((0, 128, 560, 182))        # JAMIE ATLAS
tag  = src.crop((40, 190, 522, 212))       # LOVE YOUR BODY

def fit(im, w):
    r = w / im.width
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

# Layout inside the circle-safe area (Gmail crops the square to a circle)
mark_h = int(S * 0.40)
mark_s = mark.resize((int(mark.width * mark_h / mark.height), mark_h), Image.LANCZOS)
name_s = fit(name, int(S * 0.66))
tag_s  = fit(tag,  int(S * 0.46))

mark_y_final = int(S * 0.13)
name_y = int(S * 0.60)
tag_y  = name_y + name_s.height + int(S * 0.035)

def ease_out_back(t, s=1.4):
    t -= 1
    return 1 + t * t * ((s + 1) * t + s)

def ease_out(t):
    return 1 - (1 - t) ** 3

def with_alpha(im, a):
    if a >= 1: return im
    im = im.copy()
    al = im.getchannel("A").point(lambda v: int(v * a))
    im.putalpha(al)
    return im

def frame(t):
    """t in seconds. Returns an RGBA frame at full supersampled size."""
    img = Image.new("RGBA", (S, S), BLUE)
    d = ImageDraw.Draw(img)

    # 0.0-0.7s: mark drops in from above with a little overshoot
    if t < 0.7:
        p = ease_out_back(min(1, t / 0.7))
        my = int(-mark_s.height + (mark_y_final + mark_s.height) * p)
    else:
        # gentle idle "breath": 2px bob at 1 cycle / 2.4s
        my = mark_y_final + int(math.sin((t - 0.7) * 2 * math.pi / 2.4) * S * 0.008)
    mx = (S - mark_s.width) // 2
    img.alpha_composite(mark_s, (mx, my))

    # 0.5-0.9s: soft ring pulse behind the mark (landing ripple)
    if 0.5 <= t < 1.1:
        p = (t - 0.5) / 0.6
        r = int(S * (0.22 + 0.22 * ease_out(p)))
        cx, cy = S // 2, mark_y_final + mark_s.height // 2
        ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rd.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, int(140 * (1 - p))), width=int(S * 0.012))
        img.alpha_composite(ring)

    # 0.6-1.2s: name slides up + fades in
    if t >= 0.6:
        p = ease_out(min(1, (t - 0.6) / 0.6))
        ny = name_y + int(S * 0.06 * (1 - p))
        img.alpha_composite(with_alpha(name_s, p), ((S - name_s.width) // 2, ny))

    # 1.0-1.6s: tagline fades in
    if t >= 1.0:
        p = ease_out(min(1, (t - 1.0) / 0.6))
        img.alpha_composite(with_alpha(tag_s, p), ((S - tag_s.width) // 2, tag_y))

    return img

DURATION = 4.2   # seconds per loop (intro ~1.6s, then hold with the breathing mark)
n = int(DURATION * FPS)
frames = []
for i in range(n):
    t = i / FPS
    f = frame(t).resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    frames.append(f)

# Quantize with a shared palette so colours don't flicker between frames
pal = frames[-1].quantize(colors=64, method=Image.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
q[0].save(OUT, save_all=True, append_images=q[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print("wrote", OUT, SIZE, "x", SIZE, n, "frames")
