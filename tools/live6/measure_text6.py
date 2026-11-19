#!/usr/bin/env python3
"""Finds the text blobs of the native render (apps/6.png): bounding boxes (render px) -> tools/live6/text.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import *
def near(c, tol): return np.sqrt(((im - np.array(c)) ** 2).sum(axis=2)) < tol
WHITE = near((244, 247, 252), 12); BLUE = near((120, 170, 245), 12); PINK = near((236, 140, 140), 12); LGREY = near((150, 170, 205), 14)
lab_cache = {}
def blobs(mask, key, cx, cy, rx, ry, minarea=12):
    if key not in lab_cache: lab_cache[key] = ndi.label(mask, structure=np.ones((3, 3)))
    lab, n = lab_cache[key]
    sub = lab[int(cy - ry):int(cy + ry), int(cx - rx):int(cx + rx)]
    boxes = []
    for i in np.unique(sub):
        if not i: continue
        ys, xs = np.nonzero(lab == i)
        if len(xs) < minarea: continue
        if abs(xs.mean() - cx) <= rx and abs(ys.mean() - cy) <= ry:
            boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    if not boxes: return None
    a = np.array(boxes)
    return [int(a[:, 0].min()), int(a[:, 1].min()), int(a[:, 2].max()), int(a[:, 3].max())]
G = {}
for v, (x, y) in {'200': (193, 153), '160': (163, 209), '120': (133, 263), '100': (118, 319), '80': (160, 373), '60': (202, 429), '20': (286, 540), '0': (343, 594)}.items():
    G['L' + v] = (BLUE, 'b', x, y, 60, 18)
G['L40'] = (WHITE, 'w', 244, 484, 40, 18)
for v, (x, y) in {'7': (1696, 153), '6': (1733, 216), '5': (1766, 279), '3': (1720, 405), '2': (1672, 468), '1': (1624, 531), '0': (1576, 594)}.items():
    G['R' + v] = (PINK, 'p', x, y, 20, 18)
G['R4'] = (WHITE, 'w', 1762, 342, 20, 18)
G.update({'mph_top': (BLUE, 'b', 378, 100, 40, 14), 'rpm_top': (None, 'r', 1543, 100, 80, 14), 'mph_mid': (BLUE, 'b', 960, 318, 40, 14),
          'big': (WHITE, 'w', 957, 215, 150, 60), 'gear': (WHITE, 'w', 893, 395, 40, 35),
          'fuel1': (WHITE, 'w', 344, 360, 14, 14), 'fuel0': (WHITE, 'w', 481, 544, 14, 14), 'oil300': (WHITE, 'w', 1545, 360, 40, 14), 'oil120': (WHITE, 'w', 1408, 544, 40, 14),
          'psi_val': (WHITE, 'w', 795, 639, 50, 16), 'psi_unit': (WHITE, 'w', 863, 640, 20, 12), 'temp_val': (WHITE, 'w', 1072, 639, 50, 16),
          'time': (WHITE, 'w', 208, 690, 60, 16), 'ampm': (LGREY, 'g', 290, 692, 20, 12), 'odo': (WHITE, 'w', 965, 690, 50, 16), 'mi': (LGREY, 'g', 1009, 691, 20, 12),
          'out': (WHITE, 'w', 1715, 690, 50, 16), 'degf': (LGREY, 'g', 1772, 688, 22, 12)})
out = {}
for k, (mask, key, cx, cy, rx, ry) in G.items():
    if mask is None: mask = near((242, 31, 41), 40); key = 'r'
    out[k] = blobs(mask, key, cx, cy, rx, ry)
    v = out[k]
    print('%-9s' % k, v, '' if v is None else 'c=(%.1f,%.1f) h=%d w=%d' % ((v[0] + v[2]) / 2, (v[1] + v[3]) / 2, v[3] - v[1] + 1, v[2] - v[0] + 1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'text.json'), 'w'), indent=1)
