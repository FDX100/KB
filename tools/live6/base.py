"""Shared helpers for tools/live6: the native 1920x720 reference (apps/6.png), colour fields, a ridge tracer."""
import math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, '..', '..', 'apps', '6.png')
im = np.asarray(Image.open(IMG).convert('RGB')).astype(float)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
def bil(a, x, y):
    return ndi.map_coordinates(a, [[y], [x]], order=1)[0]
def trace(field, start, direction, steps, step=3, search=3, smooth=0.5, minv=0):
    x, y = start; dx, dy = direction; n = math.hypot(dx, dy); dx /= n; dy /= n
    pts = [(x, y)]
    for i in range(steps):
        px, py = x + dx * step, y + dy * step
        nx, ny = -dy, dx
        best = -1; bo = 0
        for o in np.arange(-search, search + 0.1, 0.5):
            v = bil(field, px + nx * o, py + ny * o)
            if v > best: best = v; bo = o
        if best < minv: break
        px += nx * bo * 0.7; py += ny * bo * 0.7
        ndx, ndy = px - x, py - y; nn = math.hypot(ndx, ndy); ndx /= nn; ndy /= nn
        dx = dx * (1 - smooth) + ndx * smooth; dy = dy * (1 - smooth) + ndy * smooth; nn = math.hypot(dx, dy); dx /= nn; dy /= nn
        x, y = px, py; pts.append((round(float(x), 1), round(float(y), 1)))
    return pts
def dp(pts, eps):
    if len(pts) < 3: return pts
    a = np.array(pts[0]); b = np.array(pts[-1]); d = b - a; L = np.hypot(*d)
    dist = [abs(np.cross(d, np.array(p) - a)) / L if L > 0 else np.hypot(*(np.array(p) - a)) for p in pts[1:-1]]
    i = int(np.argmax(dist))
    if dist[i] > eps:
        l = dp(pts[:i + 2], eps); r = dp(pts[i + 1:], eps); return l[:-1] + r
    return [pts[0], pts[-1]]

def thin(mask):
    """Zhang-Suen thinning."""
    img = mask.copy().astype(np.uint8)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = np.pad(img, 1)
            p2, p3, p4, p5, p6, p7, p8, p9 = (P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:], P[2:, 2:], P[2:, 1:-1], P[2:, :-2], P[1:-1, :-2], P[:-2, :-2])
            Bn = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.uint8) for i in range(8))
            c = ((p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)) if step == 0 else ((p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0))
            rm = (img == 1) & (Bn >= 2) & (Bn <= 6) & (A == 1) & c
            if rm.any():
                img[rm] = 0; changed = True
    return img.astype(bool)

def longest_path(skel):
    """The longest simple path through a thinned line (its graph diameter by two breadth-first passes), as (x, y) points."""
    ys, xs = np.nonzero(skel)
    pts = set(zip(xs.tolist(), ys.tolist()))
    def nb(p):
        return [(p[0] + dx, p[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and (p[0] + dx, p[1] + dy) in pts]
    def bfs(s):
        from collections import deque
        prev = {s: None}; dq = deque([s]); last = s
        while dq:
            u = dq.popleft(); last = u
            for v in nb(u):
                if v not in prev:
                    prev[v] = u; dq.append(v)
        return last, prev
    a, _ = bfs(next(iter(pts)))
    b, prev = bfs(a)
    path = []; u = b
    while u is not None:
        path.append(u); u = prev[u]
    return [(float(x), float(y)) for x, y in path]

def comp(mask, minsize=60):
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return [(lab == i + 1) for i in range(n) if sizes[i] >= minsize]
