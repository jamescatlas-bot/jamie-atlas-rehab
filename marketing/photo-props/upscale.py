#!/usr/bin/env python3
"""
Upscale a source photo 4x with the EDSR super-resolution model (OpenCV dnn_superres),
cropping to a fraction box first so only the subject is processed.

Usage: python3 marketing/photo-props/upscale.py source/jamie-thumbs-up.jpg source/thumbs-up.jpg 0.28 0.02 0.72 0.98

The 38 MB model is fetched once into .cache/ (ignored by git). Takes a couple of minutes on CPU.
"""
import os
import sys
import urllib.request

import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
MODEL_URL = "https://raw.githubusercontent.com/Saafke/EDSR_Tensorflow/master/models/EDSR_x4.pb"


def model_path():
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "EDSR_x4.pb")
    if not os.path.exists(p) or os.path.getsize(p) < 1_000_000:
        print("fetching EDSR_x4.pb ...")
        urllib.request.urlretrieve(MODEL_URL, p)
    return p


def upscale(src, dst, crop=None):
    img = cv2.imread(src)
    h, w = img.shape[:2]
    if crop:
        x0, y0, x1, y1 = crop
        img = img[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path())
    sr.setModel("edsr", 4)
    out = sr.upsample(img)
    cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"{src} {img.shape[1]}x{img.shape[0]} -> {dst} {out.shape[1]}x{out.shape[0]}")


if __name__ == "__main__":
    a = sys.argv
    crop = tuple(float(v) for v in a[3:7]) if len(a) >= 7 else None
    upscale(a[1], a[2], crop)
