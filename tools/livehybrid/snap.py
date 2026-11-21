#!/usr/bin/env python3
"""Snaps hand-read points of a bright line in the photo (3.jpeg) onto the line itself: each point moves, along the normal of its curve,
to the brightest ridge within +-R px. Used by trace.py."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

IM = Image.open('/home/fd/bmw-lab/3.jpeg').convert('RGB')
A = np.asarray(IM).astype(float)
WHITE = gaussian_filter(np.minimum(np.minimum(A[..., 0], A[..., 1]), A[..., 2]), 1.2)     # white = all three channels high


def snap(points, R=9):
    P = np.array(points, float)
    out = []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]
        t = b - a; n = np.array([-t[1], t[0]]); n /= (np.hypot(*n) or 1)
        best, bv = p, -1
        for s in np.arange(-R, R + 0.1, 0.5):
            q = p + n * s
            x, y = int(round(q[0])), int(round(q[1]))
            if 0 <= x < WHITE.shape[1] and 0 <= y < WHITE.shape[0]:
                v = WHITE[y, x] - 0.6 * abs(s)
                if v > bv: bv, best = v, q
        out.append([round(float(best[0]), 1), round(float(best[1]), 1)])
    return out
