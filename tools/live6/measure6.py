#!/usr/bin/env python3
"""Measures the native Live Cockpit render (apps/6.png, 1920x720) into tools/live6/measurements.json (render px):
the outer and inner lines of each gauge (thinned and followed), the band polygons (from their flat colours) and where they
are lit, the bar capsules. Needs numpy, scipy, contourpy, Pillow. Run: python3 tools/live6/measure6.py"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import *
import contourpy
OUTP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measurements.json')

def near(c, tol):
    return np.sqrt(((im - np.array(c)) ** 2).sum(axis=2)) < tol

def line_of(mask, minsize=150, eps=0.9):
    best = max(comp(mask, minsize), key=lambda m: m.sum())
    path = longest_path(thin(best))
    return [(round(x, 1), round(y, 1)) for x, y in dp(path, eps)]

def iso_poly(mask, eps=0.8, opening=0):
    if opening: mask = ndi.binary_opening(mask, iterations=opening)
    m = ndi.binary_fill_holes(max(comp(mask, 100), key=lambda m: m.sum()))
    f = ndi.gaussian_filter(m.astype(float), 0.7)
    cg = contourpy.contour_generator(np.arange(f.shape[1]).astype(float), np.arange(f.shape[0]).astype(float), f)
    best = max(cg.lines(0.5), key=len)
    pts = [(float(x), float(y)) for x, y in best]
    if pts[0] == pts[-1]: pts = pts[:-1]
    a = np.array(pts); far = int(np.argmax(np.hypot(*(a - a[0]).T)))
    p1 = dp(pts[:far + 1], eps); p2 = dp(pts[far:] + [pts[0]], eps)
    return [(round(x, 1), round(y, 1)) for x, y in p1[:-1] + p2[:-1]]

def region(x0, y0, x1, y1):
    m = np.zeros(R.shape, bool); m[y0:y1, x0:x1] = True; return m

out = {}
mL = near((92, 158, 255), 40) & region(0, 0, 800, 720)
mR = near((242, 31, 41), 45) & region(1000, 0, 1920, 720)
out['leftOuter'] = line_of(mL)
comps = sorted(comp(mR, 200), key=lambda m: -m.sum())
out['leftInner'] = line_of(near((48, 109, 237), 22) & region(150, 100, 800, 640), 120)
# bands: the unlit colour, the lit gradient below the cut and the tick notches (closed); the left outline, the right is its mirror
unlitL = near((32, 73, 191), 4)
litL = (B > 150) & (G > 150) & region(250, 486, 480, 610) & ~near((92, 158, 255), 30) & ~near((244, 247, 252), 30) & ~near((120, 170, 245), 20)
bandL = ndi.binary_closing(unlitL | litL, structure=np.ones((3, 3)), iterations=2)
bandL = ndi.binary_fill_holes(bandL)
out['leftBand'] = iso_poly(bandL, 0.9, 1)
for k, v in out.items():
    print(k, len(v), v[:3], '...', v[-2:])
json.dump(out, open(OUTP, 'w'), indent=1)
