#!/usr/bin/env python3
"""Process the user's hand-drawn logo PNG into a site-ready asset.

Does NOT redraw anything: crops tight to the existing line art (which also
removes the bottom-right 'ChatGPT' watermark), then makes the white background
transparent so the original drawing sits cleanly on the cream site bg.
"""
import sys
from PIL import Image

SRC = "/Users/henrymarkwardt/Downloads/ChatGPT Image Jun 17, 2026, 09_29_14 AM.png"
OUT = "assets/logo.png"
FAVICON = "favicon.png"

img = Image.open(SRC).convert("RGBA")
gray = img.convert("L")

# 1) Bounding box of the dark line art (watermark is light gray -> excluded).
mask = gray.point(lambda p: 255 if p < 140 else 0)
bbox = mask.getbbox()
if not bbox:
    sys.exit("no dark content found")

# Pad ~4% so the mark isn't cropped flush to the strokes.
pad = int(0.04 * max(bbox[2] - bbox[0], bbox[3] - bbox[1]))
x0 = max(0, bbox[0] - pad)
y0 = max(0, bbox[1] - pad)
x1 = min(img.width, bbox[2] + pad)
y1 = min(img.height, bbox[3] + pad)
crop = img.crop((x0, y0, x1, y1))

# 2) White background -> transparent. Alpha from darkness (smooth edges):
#    luminance <= 150 fully opaque, >= 240 fully clear, smooth between.
cg = crop.convert("L")
px = crop.load()
lp = cg.load()
LO, HI = 150, 240
for y in range(crop.height):
    for x in range(crop.width):
        lum = lp[x, y]
        if lum <= LO:
            a = 255
        elif lum >= HI:
            a = 0
        else:
            a = int(255 * (HI - lum) / (HI - LO))
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, a)

crop.save(OUT)
crop.resize((128, 128), Image.LANCZOS).save(FAVICON)
print(f"wrote {OUT} ({crop.width}x{crop.height}) and {FAVICON} (128x128)")
