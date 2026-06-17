#!/usr/bin/env python3
"""Generate the CIT pinwheel-bloom mark as a clean SVG path.

Refines the hand-drawn flower into a rotationally consistent set of curved
petals (a pinwheel) rendered as a single stroked path. Output is centered in
a 100x100 viewBox so it scales cleanly from favicon to nav size.
"""
import math

CX, CY = 50.0, 50.0
R = 40.0          # petal length from center
N = 8             # number of petals
GLOBAL_DEG = -8   # whole-mark tilt so it reads hand-placed, not stamped

# One petal in local coords: base at origin, tip pointing up (-y).
# Asymmetric control points make the petal sweep to one side -> pinwheel.
LOCAL = [
    ("M", 0.00, 0.00),
    ("C", 0.42, -0.28, 0.34, -0.82, 0.06, -1.00),  # right edge out to tip
    ("C", -0.20, -0.80, -0.12, -0.30, 0.00, 0.00),  # left edge back to base
    ("Z",),
]


def rot(x, y, deg):
    a = math.radians(deg)
    return (x * math.cos(a) - y * math.sin(a),
            x * math.sin(a) + y * math.cos(a))


def fmt(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def petal_path(deg):
    out = []
    for seg in LOCAL:
        cmd = seg[0]
        if cmd == "Z":
            out.append("Z")
            continue
        coords = seg[1:]
        pts = []
        for i in range(0, len(coords), 2):
            lx, ly = coords[i] * R, coords[i + 1] * R
            rx, ry = rot(lx, ly, deg)
            pts.append(f"{fmt(CX + rx)} {fmt(CY + ry)}")
        out.append(cmd + " " + " ".join(pts))
    return " ".join(out)


d = " ".join(petal_path(GLOBAL_DEG + i * (360.0 / N)) for i in range(N))

svg = f'''<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Columbus Technology Institute">
  <path d="{d}" stroke="currentColor" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>
</svg>
'''

print(svg)
