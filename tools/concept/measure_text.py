#!/usr/bin/env python3
"""Finds the white text blobs of the Concept photo (apps/3.jpg) near approximate positions and writes their bounding
boxes (photo px) into tools/concept/text.json; also fits the star lattice's phase."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace import R, G, B, ndi

HERE = os.path.dirname(os.path.abspath(__file__))
white = (np.minimum(np.minimum(R, G), B) > 175)
lab, n = ndi.label(white)


def blob(cx, cy, rx, ry, minarea=25):
    """bbox of the white connected pieces whose centre lies in the window, merged."""
    sub = lab[int(cy - ry):int(cy + ry), int(cx - rx):int(cx + rx)]
    ids = [i for i in np.unique(sub) if i]
    boxes = []
    for i in ids:
        ys, xs = np.nonzero(lab == i)
        if len(xs) < minarea:
            continue
        mx, my = xs.mean(), ys.mean()
        if abs(mx - cx) <= rx and abs(my - cy) <= ry:
            boxes.append((xs.min(), ys.min(), xs.max(), ys.max(), len(xs)))
    if not boxes:
        return None
    a = np.array(boxes)
    return [int(a[:, 0].min()), int(a[:, 1].min()), int(a[:, 2].max()), int(a[:, 3].max())]


GUESS = {
    'speed_0': (462, 712, 14, 14), 'speed_10': (427, 710, 20, 14), 'speed_20': (400, 691, 20, 14), 'speed_30': (381, 662, 20, 14),
    'speed_40': (360, 626, 20, 14), 'speed_50': (339, 591, 20, 14), 'speed_60': (326, 559, 20, 14), 'speed_80': (352, 522, 20, 14),
    'speed_100': (387, 488, 28, 14), 'speed_120': (423, 459, 28, 14), 'speed_140': (466, 432, 28, 14), 'speed_180': (525, 416, 28, 14),
    'speed_220': (592, 409, 28, 14), 'speed_260': (661, 403, 28, 14),
    'rpm_0': (1141, 711, 14, 14), 'rpm_1': (1211, 691, 14, 14), 'rpm_2': (1254, 621, 14, 14), 'rpm_3': (1277, 552, 14, 14),
    'rpm_4': (1241, 495, 14, 14), 'rpm_5': (1165, 435, 14, 14), 'rpm_6': (1081, 416, 14, 14), 'rpm_7': (988, 405, 14, 14),
    'big_40': (575, 557, 40, 34), 'kmh': (640, 573, 26, 12), 'comfort': (985, 572, 48, 14), 'gear_D': (1131, 556, 26, 34),
    'rpm_unit_1': (1106, 700, 26, 9), 'rpm_unit_2': (1106, 716, 26, 9),
}
out = {k: blob(*v) for k, v in GUESS.items()}
for k, v in out.items():
    print(k, v, '' if v is None else ('c=(%.1f,%.1f) h=%d w=%d' % ((v[0] + v[2]) / 2, (v[1] + v[3]) / 2, v[3] - v[1] + 1, v[2] - v[0] + 1)))
json.dump(out, open(os.path.join(HERE, 'text.json'), 'w'), indent=1)
