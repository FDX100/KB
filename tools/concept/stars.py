#!/usr/bin/env python3
"""Fits the star lattice of the Concept photo's two panels (apps/3.jpg): for each half the star centres in a clean patch,
the lattice vectors (read off the histogram of their pairwise offsets, printed) and the phase by grid search.
Writes stars_fit.json (photo px): { left|right: { pitch, second, origin } }."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace import R, G, B, ndi
HERE = os.path.dirname(os.path.abspath(__file__))
lum = (R + G + B) / 3
sm = ndi.gaussian_filter(lum, 1.0)
loc = ndi.gaussian_filter(lum, 5.0)
# patch, pitch, second set's offset (from the printed histograms: the strongest offsets are (0, +-py) and (+-px, 0))
SIDES = {'left': ((360, 470, 470, 560), (12.5, 9.8), (6.2, -4.2)), 'right': ((1150, 470, 1250, 560), (12.8, 10.0), (6.6, -4.6))}
out = {}
for name, ((x0, y0, x1, y1), (px, py), (bx, by)) in SIDES.items():
    sub = (sm - loc)[y0:y1, x0:x1]
    pk = np.argwhere((sub == ndi.maximum_filter(sub, size=5)) & (sub > 6))
    cs = []
    for y, x in pk:
        xi, yi = x0 + x, y0 + y
        w = np.clip((sm - loc)[yi - 2:yi + 3, xi - 2:xi + 3], 0, None)
        if w.sum() > 0:
            gy, gx = np.mgrid[-2:3, -2:3]
            cs.append((xi + (w * gx).sum() / w.sum(), yi + (w * gy).sum() / w.sum()))
    cs = np.array(cs)

    def cost(ox, oy):
        tot = 0.0
        for x, y in cs:
            best = 1e9
            for sx, sy in ((0, 0), (bx, by)):
                u = (x - ox - sx) / px; v = (y - oy - sy) / py
                best = min(best, ((u - round(u)) * px) ** 2 + ((v - round(v)) * py) ** 2)
            tot += best
        return tot
    c, ox, oy = min((cost(a, b), a, b) for a in np.arange(0, px, 0.25) for b in np.arange(0, py, 0.25))
    out[name] = {'pitch': [px, py], 'second': [bx, by], 'origin': [float(ox), float(oy)]}
    print(name, 'stars', len(cs), 'origin', (ox, oy), 'rms %.2f' % ((c / len(cs)) ** 0.5))
json.dump(out, open(os.path.join(HERE, 'stars_fit.json'), 'w'), indent=1)
