#!/usr/bin/env python3
"""Measures the Concept cluster photo (apps/3.jpg) into tools/concept/measurements.json (photo px): for each half
the glossy outer line and the little gauge's line (traced), and the amber swooshes' bands in those lines' own
coordinates (arc length s, depth sd; positive inside the gauge). Needs numpy, scipy, contourpy, Pillow.
Run: python3 tools/concept/measure.py"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace import trace, dp, sm, R, G, B, ndi

HERE = os.path.dirname(os.path.abspath(__file__))
CX = 806.0          # the design's centre line


def fixpts(p):
    return [(float(x), float(y)) for x, y in p]


def cumulative(pts):
    c = [0.0]
    for i in range(1, len(pts)):
        c.append(c[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    return c


def near(path, cum, x, y, flip):
    best = 1e9; bs = 0; bsd = 0
    for i in range(len(path) - 1):
        ax, ay = path[i]; bx, by = path[i + 1]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        h = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (L * L)))
        px, py = x - (ax + dx * h), y - (ay + dy * h)
        d = math.hypot(px, py)
        if d < best:
            best = d; bs = cum[i] + h * L; bsd = flip * (dx * py - dy * px) / L
    return bs, bsd


def band_profile(mask, path, cum, flip, step):
    ys, xs = np.nonzero(mask)
    rows = {}
    for x, y in zip(xs, ys):
        s, sd = near(path, cum, float(x), float(y), flip)
        k = int(s // step)
        a, b, n = rows.get(k, (1e9, -1e9, 0))
        rows[k] = (min(a, sd), max(b, sd), n + 1)
    prof = []
    for k in sorted(rows):
        a, b, n = rows[k]
        if n >= 4:
            prof.append((round(k * step + step / 2, 1), round(a, 1), round(b, 1)))
    return prof


def box(x0, y0, x1, y1):
    m = np.zeros(R.shape, bool); m[y0:y1, x0:x1] = True; return m


def biggest(m):
    m = ndi.binary_closing(m, iterations=2)
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    return ndi.binary_fill_holes(lab == int(np.argmax(sizes)) + 1)


base = ((R > 120) & ((R - B) > 45) & (G > 55))
base = ndi.binary_opening(base, iterations=1)

# ---- left half: paths run bottom end -> top end with the gauge on their right-hand side (flip +1)
up = trace((350, 461), (1, -0.75), 90, step=4, search=6, minv=55)
down = trace((350, 461), (-0.75, 1), 160, step=4, search=6, minv=55)
outer_l = fixpts(dp(down[::-1] + up[1:], 0.9))
fu = trace((228, 636), (0.35, 1), 60, step=4, search=5, minv=60)
fd = trace((228, 636), (-0.2, -1), 4, step=4, search=5, minv=60)
fb = trace(fu[-1], (1, 0.0), 14, step=4, search=4, minv=45)
mini_l = fixpts(dp(fd[::-1] + fu[1:] + fb[1:], 0.8))[::-1]
mini_l.insert(0, (378.0, 749.0))          # the line runs on along the bottom to here (too faint to trace)
# ---- right half: traced top -> bottom, then reversed so every path runs bottom -> top; the gauge is on the left (flip -1)
ru = trace((1300, 494), (-1, -0.7), 120, step=4, search=6, minv=55)
rd = trace((1300, 494), (0.6, 1), 200, step=4, search=6, minv=55)
outer_r = fixpts(dp(ru[::-1] + rd[1:], 0.9))[::-1]
cu = trace((1385, 640), (-0.45, 1), 40, step=4, search=5, minv=60)
cd = trace((1385, 640), (0.35, -1), 8, step=4, search=5, minv=60)
cb = trace(cu[-1], (-1, 0.0), 14, step=4, search=4, minv=45)
mini_r = fixpts(dp(cd[::-1] + cu[1:] + cb[1:], 0.8))[::-1]

cum_ol, cum_ml, cum_or, cum_mr = cumulative(outer_l), cumulative(mini_l), cumulative(outer_r), cumulative(mini_r)
sw_l = biggest(base & box(330, 630, 480, 740))
sw_r = biggest(base & box(1130, 560, 1310, 740))
fu_sw = biggest(base & box(235, 630, 352, 745))
co_sw = biggest(base & box(1265, 685, 1350, 745))
out = {
    'cx': CX,
    'left': {'outer': outer_l, 'outerCum': cum_ol, 'mini': mini_l, 'miniCum': cum_ml,
             'swoosh': band_profile(sw_l, outer_l, cum_ol, 1, 12.0), 'miniBand': band_profile(fu_sw, mini_l, cum_ml, 1, 8.0)},
    'right': {'outer': outer_r, 'outerCum': cum_or, 'mini': mini_r, 'miniCum': cum_mr,
              'swoosh': band_profile(sw_r, outer_r, cum_or, -1, 12.0), 'miniBand': band_profile(co_sw, mini_r, cum_mr, -1, 8.0)},
}
json.dump(out, open(os.path.join(HERE, 'measurements.json'), 'w'), indent=1)
for side in ('left', 'right'):
    d = out[side]
    print(side, 'outer', len(d['outer']), 'mini', len(d['mini']), 'swoosh', d['swoosh'][:2], '...', d['swoosh'][-1], 'miniBand', d['miniBand'][:1], '...', d['miniBand'][-1])
print('right outer', [(round(x), round(y)) for x, y in outer_r][:4], '...', [(round(x), round(y)) for x, y in outer_r][-3:])
print('right mini', [(round(x), round(y)) for x, y in mini_r])
