#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/livehyb.json (the Live Hybrid theme), after a photo of BMW's Live Cockpit
Professional in a plug-in hybrid (2.jpeg): two white outlined chevron scales (the speed 0..330 km/h on the left, the revs 0..8 on the
right) with a red needle at the value, grey panels inside them with the red glow at the foot, the big speed, the drive mode with
ELECTRIC / HYBRID, the power meter with its kW, the electric range, the battery gauge, the fuel gauge, READY, and the dark middle
display where the Waze map opens. The white line art is drawn here from geometry (bake_lines -> hud/art/livehyb.json, shown by the ARTMASK shader); the rest is drawn live. Photo px -> layout px: x' = 960 + (x - 1060) * S, y' = (y - 322) * S.
Edit this and regenerate; do not hand-edit the JSON."""
import json, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'livehyb.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')
S = 1.245


DY = -2.6                                  # the sharp photo (2.jpeg) sits this far above the first one the numbers below were read from


def L(px, py): return (round(960 + (px - 1060) * S, 1), round((py + DY - 322) * S, 1))
def cell(font): return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, p, w, font, t, color='fg', align='center', **kw):
    """A text centred (or, left / right, starting / ending) at photo point p."""
    x, y = L(*p)
    h = cell(font)
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font, 'color': color, 'align': align}
    d.update(kw)
    return d


def icon(i, name, p, size, color, **kw):
    x, y = L(*p)
    d = {'id': i, 'type': 'icon', 'icon': name, 'z': 5, 'x': round(x - size / 2), 'y': round(y - size / 2), 'w': size, 'h': size, 'color': color}
    d.update(kw)
    return d


def circle(a, b, c):
    """The circle through three points: (cx, cy, r)."""
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


def clockwise_deg(center, p):
    """The angle of p round a centre, clockwise from straight up (degrees)."""
    return math.degrees(math.atan2(p[0] - center[0], -(p[1] - center[1]))) % 360


def arc(i, a, b, c, width, track, signal, mn, mx, bottom_first=True, conn=2, z=3, **kw):
    """An arc through three layout points a (where the value is lowest), b, c (highest): lit from a towards c."""
    cx, cy, r = circle(a, b, c)
    ang = lambda p: clockwise_deg((cx, cy), p)
    start, end = ang(a), ang(c)
    sweep = (end - start) % 360
    if sweep > 180: sweep -= 360                    # the short way round
    size = math.ceil(2 * (r + width / 2 + 2))
    d = {'id': i, 'type': 'arc', 'class': 'content', 'z': z, 'x': round(cx - size / 2), 'y': round(cy - size / 2), 'w': size, 'h': size,
         'signal': signal, 'min': mn, 'max': mx, 'width': width, 'trackColor': track, 'start': round(start, 2), 'sweep': round(sweep, 2), 'conn': conn}
    d.update(kw)
    return d


WHITE = [236, 238, 240, 255]
CYAN = [24, 208, 232, 255]
DIM = [150, 154, 158, 255]

# ---- the outlines (photo px, measured off the photo once; every line below is drawn from these numbers)
L_OUT = [(877.8, 337.7), (845.0, 336.6), (769.7, 342.6), (699.8, 354.6), (618.6, 360.7), (576.9, 369.7), (526.5, 394.0), (486.9, 420.0), (452.2, 446.1), (418.3, 475.7), (395.8, 505.2), (368.3, 531.5), (355.3, 563.7), (356.0, 602.5), (367.6, 637.1), (387.8, 675.3), (404.7, 707.4), (430.8, 747.0), (461.9, 786.0), (492.1, 814.8), (523.4, 832.0)]
R_OUT = [(1286.7, 339.1), (1345.0, 341.6), (1430.1, 349.6), (1504.9, 360.1), (1549.9, 368.6), (1594.7, 385.0), (1631.1, 407.9), (1663.9, 433.1), (1699.0, 463.1), (1726.8, 490.9), (1750.8, 522.1), (1768.0, 557.3), (1769.0, 583.2), (1764.1, 606.2), (1751.5, 639.1), (1751.3, 678.3), (1718.3, 703.4), (1693.4, 742.2), (1669.9, 772.9), (1648.3, 795.7), (1627.6, 809.7), (1603.1, 815.8)]


POWER_O = [(1465.5, 474.9), (1482.9, 495.8), (1498.8, 515.9), (1514.0, 533.8), (1525.5, 552.4), (1529.8, 573.1), (1524.6, 594.6), (1514.3, 617.5), (1494.5, 641.8), (1478.8, 673.1)]
B_OUT = [(1792.9, 676.2), (1802.9, 693.7), (1808.6, 714.7), (1809.0, 737.8), (1803.8, 760.7), (1792.5, 781.3), (1779.7, 801.0), (1763.5, 818.5), (1744.6, 831.9), (1722.7, 836.6), (1700.5, 831.7)]
F_O = [(303.4, 677.5), (289.1, 695.3), (285.1, 718.0), (291.3, 740.9), (302.2, 763.2), (316.3, 786.3), (333.5, 809.8), (357.3, 827.3), (388.8, 825.8), (409.7, 844.4), (434.8, 845.6)]
LEFT_BOTTOM = [(522.1, 831.6), (545.2, 835.6), (600.1, 832.6), (700.0, 832.6), (789.9, 831.6), (872.2, 829.6), (893.4, 823.5), (911.4, 809.8), (949.8, 808.6), (996.9, 807.6)]
RIGHT_BOTTOM = [(1177.1, 804.6), (1230.1, 803.6), (1259.7, 804.8), (1278.6, 817.2), (1294.9, 826.8), (1340.3, 830.6), (1450.0, 839.6), (1560.0, 836.6), (1598.6, 821.7)]


def inner(pts, d, toward):
    """The polyline pushed d px towards a point (the inside of the chevron)."""
    out = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = (-ty, tx); ln = math.hypot(*n) or 1
        n = (n[0] / ln, n[1] / ln)
        if (toward[0] - p[0]) * n[0] + (toward[1] - p[1]) * n[1] < 0:
            n = (-n[0], -n[1])
        out.append((p[0] + n[0] * d, p[1] + n[1] * d))
    return out


MID = (1060, 600)
li = inner(L_OUT, 80, MID)
ri = inner(R_OUT, 72, MID)
# the grey panels: the inside of each outline, closed along the middle display's edge
PANEL_L = li[1:] + [(790, 778), (716, 612), (760, 500), (830, 415), (905, 395)]
PANEL_R = ri[1:] + [(1560, 790), (1372, 772), (1385, 690), (1392, 600), (1350, 500), (1300, 425), (1262, 392)]
CENTER = [(800, 354), (1010, 350), (1230, 354), (1413, 470), (1420, 640), (1380, 790), (1060, 836), (790, 800), (739, 640), (745, 470)]


def bake_panels(name):
    """The two grey panels as a soft R8 fill (hud/art/<name>.json, 960 x 330, drawn by ARTMASK): more corners than GPOLY's 8."""
    import base64, zlib
    from PIL import Image, ImageDraw
    k = 4
    im = Image.new('L', (960 * k, 330 * k), 0)
    dr = ImageDraw.Draw(im)
    for pts in (PANEL_L, PANEL_R):
        dr.polygon([(x * 0.5 * k, y * 0.5 * k) for x, y in map(lambda q: L(*q), pts)], fill=255)
    im = im.resize((960, 330), Image.LANCZOS)
    import numpy as np
    yy, xx = np.mgrid[0:330, 0:960].astype(float)
    shade = 0.95 - 0.40 * (yy / 330.0)          # lighter at the top, like the photo's glossy panels
    raw = bytes(np.round(np.asarray(im, dtype=float) * shade).astype(np.uint8).tobytes())
    with open(os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'art', name + '.json'), 'w') as f:
        json.dump({'w': 960, 'h': 330, 'z': base64.b64encode(zlib.compress(raw, 9)).decode()}, f)


bake_panels('livehyb_panel')


def poly(pts, top, bottom, topc, botc, fade=10):
    lp = [L(*p) for p in pts]
    ys = [p[1] for p in lp]
    return {'pts': [[round(x, 1), round(y, 1)] for x, y in lp], 'top': round(min(ys), 1), 'bottom': round(max(ys), 1), 'topColor': topc, 'bottomColor': botc, 'fade': fade}


def thin(pts, n):
    """At most n points of a polyline, evenly picked."""
    if len(pts) <= n: return list(pts)
    return [pts[round(i * (len(pts) - 1) / (n - 1))] for i in range(n)]


def relax(P, times=3):
    """Evens a measured polyline out (the ends stay)."""
    P = [tuple(q) for q in P]
    for _ in range(times):
        P = [P[0]] + [((P[i - 1][0] + 2 * P[i][0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * P[i][1] + P[i + 1][1]) / 4) for i in range(1, len(P) - 1)] + [P[-1]]
    return P


def smooth(pts, n=10, closed=False):
    """A Catmull-Rom curve through the points (n steps between each pair)."""
    P = [tuple(p) for p in pts]
    out = []
    m = len(P)
    for i in range(m if closed else m - 1):
        p0, p1, p2, p3 = (P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]) if closed else (P[max(0, i - 1)], P[i], P[i + 1], P[min(m - 1, i + 2)])
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    if not closed: out.append(P[-1])
    return out


def put_art(name, arr):
    import base64, zlib
    h, w = arr.shape
    with open(os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'art', name + '.json'), 'w') as f:
        json.dump({'w': w, 'h': h, 'z': base64.b64encode(zlib.compress(arr.tobytes(), 9)).decode()}, f)


def canvas(w, h, k=4):
    from PIL import Image, ImageDraw
    im = Image.new('L', (w * k, h * k), 0)
    return im, ImageDraw.Draw(im), k


def finish(im, w, h):
    import numpy as np
    from PIL import Image
    return np.asarray(im.resize((w, h), Image.LANCZOS), dtype=np.uint8)



def bake_lines():
    """All the white line art, drawn from geometry (no pixels of the photo): the two chevron outlines with their thin inner lines, the
    tapered leader at every scale mark and the small ticks between, the lines along the bottom, the power meter's, the battery's outlines."""
    import numpy as np
    k = 3
    im, dr, k = canvas(1920, 660, k)
    lead, ldr, _ = canvas(1920, 660, k)

    def lwedge(root, d, length, w0):
        """A leader that fades out towards its tip (slices, bright to faint), on its own picture."""
        (x, y) = L(*root)
        nx, ny = -d[1], d[0]
        n = 10
        for i in range(n):
            a, b = i / n, (i + 1) / n
            wa, wb = w0 * (1 - 0.7 * a), w0 * (1 - 0.7 * b)
            P = [((x + d[0] * length * a + nx * wa / 2) * k, (y + d[1] * length * a + ny * wa / 2) * k), ((x + d[0] * length * b + nx * wb / 2) * k, (y + d[1] * length * b + ny * wb / 2) * k),
                 ((x + d[0] * length * b - nx * wb / 2) * k, (y + d[1] * length * b - ny * wb / 2) * k), ((x + d[0] * length * a - nx * wa / 2) * k, (y + d[1] * length * a - ny * wa / 2) * k)]
            ldr.polygon(P, fill=int(255 * (1 - 0.6 * a)))

    def pl(pts, w):
        pp = [(x * k, y * k) for x, y in (L(*q) for q in pts)]
        dr.line(pp, fill=255, width=max(1, int(w * k)), joint='curve')
        r = w * k / 2
        for x, y in (pp[0], pp[-1]):
            dr.ellipse([x - r, y - r, x + r, y + r], fill=255)

    def wedge(root, d, length, w0, w1=0.4):
        """A tapered leader from root towards the unit direction d."""
        (x, y) = L(*root)
        nx, ny = -d[1], d[0]
        P = [((x + nx * w0 / 2) * k, (y + ny * w0 / 2) * k), ((x + d[0] * length + nx * w1 / 2) * k, (y + d[1] * length + ny * w1 / 2) * k),
             ((x + d[0] * length - nx * w1 / 2) * k, (y + d[1] * length - ny * w1 / 2) * k), ((x - nx * w0 / 2) * k, (y - ny * w0 / 2) * k)]
        dr.polygon(P, fill=255)

    def normal_at(path, p):
        best = min(range(len(path) - 1), key=lambda i: math.hypot((path[i][0] + path[i + 1][0]) / 2 - p[0], (path[i][1] + path[i + 1][1]) / 2 - p[1]))
        a, b = path[best], path[best + 1]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = (-ty, tx); ln = math.hypot(*n) or 1
        n = (n[0] / ln, n[1] / ln)
        return n if (MID[0] - p[0]) * n[0] + (MID[1] - p[1]) * n[1] > 0 else (-n[0], -n[1])

    numbers_l = {i: p for i, (v, p) in enumerate(SPEED)}
    numbers_r = {v: p for v, p in REV}
    for outline, marks, focus, nums in ((L_OUT, SPD_MARKS, (880, 590), numbers_l), (R_OUT, REV_MARKS, (1290, 590), numbers_r)):
        path = smooth(relax(outline, 1), 10)
        pl(path, 4.4)
        pl(inner(path, 8.5, MID)[::2], 1.7)
        pts = [m[1] for m in marks]
        for i, root in enumerate(pts):
            fx, fy = focus[0] - root[0], focus[1] - root[1]
            ln = math.hypot(fx, fy); d = (fx / ln, fy / ln)           # the leaders are rays from a point inside the dial
            num = nums.get(marks[i][0] if focus[0] > 1000 else i)
            reach = (math.hypot(num[0] - root[0], num[1] - root[1]) - 34) if num else 40
            if i > 0:
                lwedge(root, d, max(30, reach) * S, 9.5)
            if i + 1 < len(pts):                                   # the small ticks between two marks, on the outline
                q = ((root[0] + pts[i + 1][0]) / 2, (root[1] + pts[i + 1][1]) / 2)
                q = min(path, key=lambda a: math.hypot(a[0] - q[0], a[1] - q[1]))
                fx, fy = focus[0] - q[0], focus[1] - q[1]; ln = math.hypot(fx, fy)
                wedge(q, (fx / ln, fy / ln), 16, 3.0, 1.4)
    for pts in (LEFT_BOTTOM, RIGHT_BOTTOM):
        sm = smooth(pts, 8)
        pl(sm, 4.0)
        pl([(x, y + 7.5) for x, y in sm], 1.6)
    # the power meter: the edge, the caps, the 0 line
    z = lambda off, pts: [(off[0] + x / 4.0, off[1] + y / 4.0) for x, y in pts]
    pl(smooth([(1428.8, 473.8)] + [(1465, 472.5)] + POWER_O, 8), 3.4)
    pl([(1451, 673.8), (1484, 673.3)], 3.0)
    pl([(1462.5, 643.8), (1500, 643.8)], 2.2)
    pl([(1362, 640)] * 0 + [(1462.5, 643.8), (1470, 643.8)], 2.2)
    # the battery: the outer double line, the tail on the left, the hook at the top
    tail = [(1688, 830.5), (1677.5, 825.5)]
    sm = smooth(B_OUT + tail, 8)
    pl(sm, 3.4)
    pl(smooth(inner(B_OUT[:8], 6, (1730, 760)), 8), 1.4)
    pl([(1776, 675.5), (1788.1, 676.2)], 3.0)
    for pts, width in FUEL_LINES:                                  # the fuel gauge's own lines
        pl(pts, width)
    # the left corner of the screen: the tail of the scale's chevron is part of the outline already
    from PIL import Image, ImageFilter
    lines = im.resize((1920, 660), Image.LANCZOS)
    lead_img = lead.resize((1920, 660), Image.LANCZOS)
    halo = lines.filter(ImageFilter.GaussianBlur(4.0))
    arr = np.maximum.reduce([np.asarray(lines, dtype=float), np.asarray(lead_img, dtype=float) * 0.86, np.minimum(255, np.asarray(halo, dtype=float) * 2.4) * 0.30])
    put_art('livehyb', np.round(np.clip(arr, 0, 255)).astype(np.uint8))

def bake_centre():
    """The middle display (with and without the Waze window cut out) and the red glows at the feet of the panels, as 960 x 330 fills."""
    import numpy as np
    from PIL import ImageFilter
    pts = [L(*q) for q in smooth(CENTER, 8, True)]
    for name, hole in (('lh_mid', False), ('lh_mid_hole', True)):
        im, dr, k = canvas(480, 165)
        dr.polygon([(x / 4 * k, y / 4 * k) for x, y in pts], fill=255)
        for pp in (PANEL_L, PANEL_R):                                       # the panels are drawn over this: keep their area clear
            dr.polygon([(x / 4 * k, y / 4 * k) for x, y in (L(*q) for q in pp)], fill=0)
        if hole:
            dr.rounded_rectangle([668 / 4 * k, 128 / 4 * k, (668 + 628) / 4 * k, (128 + 436) / 4 * k], radius=56 / 4 * k, fill=0)
        cov = finish(im, 480, 165).astype(float) / 255
        yy, xx = np.mgrid[0:165, 0:480].astype(float)
        glow = np.clip(1 - np.hypot((xx - 240) / 200, (yy - 88) / 90), 0, 1)           # lighter towards the middle, like the photo's display
        put_art(name, np.round(cov * (0.10 + 0.55 * glow) * 255).astype(np.uint8))


def bake_glows():
    """The red glows at the feet of the panels, with the photo's fine grid, as one full-size R8 strip across the screen; returns its box."""
    import numpy as np
    (ax, ay), (bx, by) = L(548, 730), L(1590, 794)
    ax, ay, bx, by = int(ax), int(ay), int(bx) + 1, int(by) + 1
    w, h = bx - ax, by - ay
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    a = np.zeros((h, w))
    for x0, x1, y0, y1 in ((548, 720, 736, 788), (1400, 1590, 726, 794)):
        (lx, ly), (rx, ry) = L(x0, y0), L(x1, y1)
        lx, ly, rx, ry = lx - ax, ly - ay, rx - ax, ry - ay
        u = np.clip((yy - ly) / max(1, ry - ly), 0, 1)
        inside = (xx >= lx) & (xx <= rx) & (yy >= ly) & (yy <= ry)
        edge = np.clip(np.minimum(xx - lx, rx - xx) / 40.0, 0, 1) ** 1.5
        a = np.maximum(a, np.where(inside, u ** 0.9 * edge, 0))
    grid = 1.0 - 0.42 * (((xx % 5) < 1.3) | ((yy % 5) < 1.3))
    put_art('lh_glow', np.round(np.clip(a * grid, 0, 1) * 255).astype(np.uint8))
    return {'glow': (ax, ay, w, h)}


def gauge_masks():
    """The three gauge shapes of the photo (the power meter's chevron band, the battery's bowl, the fuel gauge's bent band), each baked as a
    coverage picture and a 'how far along' picture (hud/art/lh_<name>.json and lh_<name>_t.json, half size) for the GAUGEMASK shader, with
    smooth edges: the outer curves are the measured numbers above, set a little inside the white lines."""
    import numpy as np
    z = lambda off, pts: [(off[0] + x / 4.0, off[1] + y / 4.0) for x, y in pts]       # a zoomed crop's coordinates -> photo px
    power_o = smooth(POWER_O, 8)
    power_i = smooth(z((1360, 440), [(440, 330), (520, 410), (572, 490), (580, 560), (555, 640), (500, 720), (440, 800), (395, 935)]), 8)
    power = [(1360 + 275 / 4, 440 + 135 / 4)] + power_o + [(1360 + 395 / 4, 440 + 935 / 4)] + power_i[::-1] + [(1360 + 440 / 4, 440 + 330 / 4)]
    # the battery: the outer white curve inset by a few px, the bowl on the left, the thin band up to 100
    b_out = B_OUT
    b_ins = [(x - 4 * (x - 1740) / math.hypot(x - 1740, y - 800), y - 4 * (y - 800) / math.hypot(x - 1740, y - 800)) for x, y in b_out]
    band_in = inner(b_out[:6], 10, (1700, 760))
    batt = smooth(b_ins, 8) + smooth(z((1640, 660), [(250, 672), (262, 600), (300, 510), (350, 450), (420, 428)]), 8) + smooth(band_in[::-1], 6)[::-1][::-1]
    # the fuel gauge: the band between its outer white line and the thin inner one
    FX = 17                                                                           # the photo's gauge reaches past the screen's edge: moved in
    f_o = [(x + FX, y) for x, y in F_O]
    f_i = inner(f_o, 13, (467, 660))
    f_c = inner(f_o, 3.5, (467, 660))
    fuel = smooth(f_c, 8) + smooth(f_i, 8)[::-1]
    fuel_path = z((260 + FX, 650), [(700, 715), (600, 722), (520, 700), (440, 650), (370, 580), (300, 500), (235, 400), (195, 300), (190, 200), (240, 150)])

    def by_y(table):
        ys = [a for a, _ in table]; vs = [b for _, b in table]
        return lambda y: np.interp(y, ys[::-1], vs[::-1])

    def along(path):
        seg = np.array(path); d = np.hypot(*(seg[1:] - seg[:-1]).T); cum = np.concatenate([[0], np.cumsum(d)]) / d.sum()
        def f(x, y):
            best = np.full(x.shape, 1e9); val = np.zeros(x.shape)
            for i in range(len(seg) - 1):
                a, b = seg[i], seg[i + 1]; ab = b - a
                u = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / (ab @ ab), 0, 1)
                dist = np.hypot(x - (a[0] + u * ab[0]), y - (a[1] + u * ab[1]))
                m = dist < best; best = np.where(m, dist, best); val = np.where(m, cum[i] + u * (cum[i + 1] - cum[i]), val)
            return val
        return f
    out = {}
    for name, poly, par in (('power', power, lambda x, y: by_y([(666.25, 0), (473.75, 1)])(y)),
                            ('batt', batt, lambda x, y: by_y([(827.5, 0), (767.5, 0.53), (681.25, 1)])(y)),
                            ('fuel', fuel, along(fuel_path))):
        lp = [L(*q) for q in poly]
        x0 = max(0, int(min(q[0] for q in lp)) - 4); x1 = int(max(q[0] for q in lp)) + 5
        y0 = max(0, int(min(q[1] for q in lp)) - 4); y1 = int(max(q[1] for q in lp)) + 5
        w, h = x1 - x0, y1 - y0
        im, dr, k = canvas(w, h, 4)
        dr.polygon([((x - x0) * k, (y - y0) * k) for x, y in lp], fill=255)
        cov = finish(im, w, h)                                                           # full size: the edges stay crisp
        gx, gy = np.meshgrid(np.arange(w) + 0.5 + x0, np.arange(h) + 0.5 + y0)
        px = 1060 + (gx - 960) / S; py = 322 + gy / S - DY
        t = np.clip(par(px, py), 0, 1)
        put_art('lh_' + name, cov)
        put_art('lh_' + name + '_t', np.round(t * 255).astype(np.uint8))
        out[name] = (x0, y0, w, h)
    # the fuel gauge's own white lines: the outer double line and the thin inner one (drawn into the main line art)
    global FUEL_LINES
    FUEL_LINES = [(smooth(f_o, 8), 2.8), (smooth(inner(f_o, 3.8, (467, 660)), 8), 1.7), (smooth(f_i, 8), 1.7)]
    return out


def gauges():
    box = GAUGE_BOXES
    spec = (('power', 'powerPct', 0, 100, 'accent', [96, 98, 106, 255]), ('batt', 'hvSoc', 0, 100, 'accent', [58, 62, 68, 255]),
            ('fuel', 'fuel', 0, 1, [236, 238, 240, 255], [74, 76, 80, 255]))
    return [{'id': n + '_gauge', 'type': 'gaugemask', 'class': 'content', 'z': 2, 'x': box[n][0], 'y': box[n][1], 'w': box[n][2], 'h': box[n][3], 'conn': 2,
             'art': 'lh_' + n, 'art2': 'lh_' + n + '_t', 'signal': sg, 'min': mn, 'max': mx, 'color': col, 'trackColor': trk} for n, sg, mn, mx, col, trk in spec] 


W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg'}]
HOLE = {'hole': [668, 128, 628, 436], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 56}
# the grey panels (one layer: a polygon each) and, over them, the middle display and the red glows (a second layer)
PANEL = [64, 67, 74, 255]
FUEL_LINES = []
GAUGE_BOXES = gauge_masks()
bake_centre()
GLOWS = bake_glows()
W.append({'id': 'middle', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 1, 'art': 'lh_mid', 'color': [74, 82, 94, 255], 'toggle': '!mapUp'})
W.append({'id': 'middle_map', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 1, 'art': 'lh_mid_hole', 'color': [74, 82, 94, 255], 'toggle': 'mapUp'})
W.append({'id': 'panels', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 1, 'art': 'livehyb_panel', 'color': PANEL})
for gid, (gx, gy, gw, gh) in GLOWS.items():
    W.append({'id': gid, 'type': 'artmask', 'class': 'content', 'z': 1, 'x': gx, 'y': gy, 'w': gw, 'h': gh, 'conn': 2, 'art': 'lh_' + gid, 'color': [238, 36, 40, 255]})
# the white line art baked from the photo
W.append({'id': 'art', 'type': 'artmask', 'class': 'content', 'z': 2, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 3, 'art': 'livehyb', 'color': WHITE})
# ---- the scale numbers
SPEED = [(0, (658, 781)), (30, (573, 782)), (60, (514, 726)), (90, (467, 652)), (120, (440, 580)), (150, (478, 512)), (180, (538, 462)), (210, (590, 421)), (240, (658, 400)), (270, (734, 386)), (300, (807, 382)), (330, (879, 378))]
for k, (v, p) in enumerate(SPEED):
    W.append(text('sk%d' % v, p, 100, 'h_scale', str(v), WHITE, 'center', toggle='!units=us'))
    W.append(text('sm%d' % (k * 20), p, 100, 'h_scale', str(k * 20), WHITE, 'center', toggle='units=us'))
REV = [(1, (1600, 749)), (2, (1654, 665)), (3, (1690, 574)), (4, (1648, 498)), (5, (1575, 440)), (6, (1486, 404)), (7, (1392, 386)), (8, (1290, 382))]
for v, p in REV:
    W.append(text('rv%d' % v, p, 60, 'h_scale', str(v), WHITE, 'center'))
# ---- the needles: where each scale's ticks meet its outline (photo px)
SPD_MARKS = [(0, (523.4, 832.0)), (1, (502.3, 820.4)), (2, (438.1, 756.1)), (3, (390.5, 680.4)), (4, (355.7, 587.6)), (5, (395.2, 505.8)), (6, (452.1, 446.2)), (7, (525.9, 394.4)), (8, (618.2, 360.8)), (9, (699.6, 354.6)), (10, (789.6, 341.0)), (11, (877.3, 337.7))]
REV_MARKS = [(0, (1603.1, 815.8)), (1, (1649.6, 794.3)), (2, (1717.3, 704.9)), (3, (1768.9, 583.6)), (4, (1698.6, 462.7)), (5, (1630.8, 407.7)), (6, (1550.4, 368.8)), (7, (1430.6, 349.7)), (8, (1345.4, 341.6))]
bake_lines()
W.append({'id': 'spd_needle', 'type': 'pneedle', 'class': 'content', 'z': 3, 'x': 0, 'y': 0, 'w': 960, 'h': 660, 'conn': 3, 'signal': 'speed',
          'marks': [[30 * i, *L(*p)] for i, p in SPD_MARKS], 'marksUs': [[20 * i, *L(*p)] for i, p in SPD_MARKS], 'length': 78, 'width': 3.4, 'glow': 12, 'color': 'hot'})
W.append({'id': 'rev_needle', 'type': 'pneedle', 'class': 'content', 'z': 3, 'x': 960, 'y': 0, 'w': 960, 'h': 660, 'conn': 3, 'signal': 'rpm',
          'marks': [[v, *L(*p)] for v, p in REV_MARKS], 'length': 78, 'width': 3.4, 'glow': 12, 'color': 'hot'})
# ---- the mode, the speed
W.append(text('evmode', (765, 526), 340, 'h_mode', '{{evmode}}', CYAN, 'center'))
W.append(text('mode', (668, 553), 260, 'h_mode2', '{{mode}}', WHITE, 'left'))
W.append(icon('drive_icon', 'gauge', (636, 546), 46, WHITE))
W.append(text('speed', (770, 632), 220, 'm_speed', '{{speed}}', WHITE, 'center'))
W.append(text('speed_u', (818, 608), 100, 'h_unit', '{{u:speedLc}}', WHITE, 'left'))
# ---- the power meter and the electric range
W.extend(gauges())
for v, p in ((60, (1409, 471)), (40, (1454, 533)), (20, (1475, 595)), (0, (1432, 660))):
    W.append(text('pk%d' % v, p, 50, 'h_tick', str(v), DIM, 'center'))
W.append(text('power', (1415, 565), 110, 'h_kw', '{{powerKw}}', WHITE, 'center'))
W.append(text('power_u', (1415, 597), 60, 'h_small', 'kW', DIM, 'center'))
W.append(text('avg', (1562, 642), 130, 'h_small', 'Ø{{avgSpeed}}', DIM, 'center'))
W.append(icon('evcar', 'evcar', (1381, 706), 70, CYAN))
W.append(text('evrange', (1428, 706), 130, 'h_kw', '{{evRange}}', CYAN, 'left'))
W.append(text('evrange_u', (1520, 712), 60, 'h_small', '{{u:distLc}}', CYAN, 'left'))
# ---- READY, the revs label, the battery and fuel gauges
W.append(text('ready', (1504, 771), 170, 'z_unit', '{{ready}}', WHITE, 'center'))
W.append(text('revs_lbl', (1450, 803), 190, 'h_small', '1/min x1000', DIM, 'center'))
W.append(text('batt_pct', (1748, 758), 90, 'z_unit', '{{hvSoc}}%', WHITE, 'center'))
W.append(text('batt_100', (1750, 680), 80, 'h_tick', '100', DIM, 'center'))
W.append(text('batt_0', (1698, 797), 30, 'h_tick', '0', DIM, 'center'))
W.append(icon('batt_icon', 'battery', (1795, 819), 44, WHITE))
W.append(text('fuel_1', (351, 692), 30, 'h_tick', '1', DIM, 'center'))
W.append(text('fuel_half', (385, 757), 70, 'h_tick', '1/2', DIM, 'center'))
W.append(text('fuel_0', (435, 802), 30, 'h_tick', '0', DIM, 'center'))
W.append(icon('pump', 'fuel', (329, 808), 30, DIM))
# ---- the bottom row: the range and the time on the left, the temperature and the electric range on the right
W.append({'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'})
W.append({'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'})
W.append({'id': 'strip_icon', 'type': 'icon', 'icon': 'fuel', 'z': 3, 'x': 168, 'y': 673, 'w': 34, 'h': 34, 'color': WHITE, 'stripRow': 'l'})
W.append({'id': 'strip_range', 'type': 'text', 'z': 3, 'x': 212, 'y': 672, 'w': 110, 'h': 37, 'text': '{{range}}', 'font': 'e_unit', 'color': 'fg', 'align': 'right', 'stripRow': 'l'})
W.append({'id': 'strip_range_u', 'type': 'text', 'z': 3, 'x': 330, 'y': 678, 'w': 60, 'h': 27, 'text': '{{u:dist}}', 'font': 'e_head', 'color': 'dim', 'align': 'left', 'stripRow': 'l'})
W.append({'id': 'strip_time', 'type': 'text', 'z': 3, 'x': 420, 'y': 672, 'w': 120, 'h': 37, 'text': '{{time}}', 'font': 'e_unit', 'color': 'fg', 'align': 'right', 'stripRow': 'l'})
W.append({'id': 'strip_ampm', 'type': 'text', 'z': 3, 'x': 546, 'y': 678, 'w': 60, 'h': 27, 'text': '{{ampm}}', 'font': 'e_head', 'color': 'dim', 'align': 'left', 'stripRow': 'l'})
W.append({'id': 'strip_out', 'type': 'text', 'z': 3, 'x': 1520, 'y': 672, 'w': 150, 'h': 37, 'text': '{{ambient}}', 'font': 'e_unit', 'color': 'fg', 'align': 'right', 'stripRow': 'r'})
W.append({'id': 'strip_out_u', 'type': 'text', 'z': 3, 'x': 1678, 'y': 678, 'w': 50, 'h': 27, 'text': '{{u:temp}}', 'font': 'e_head', 'color': 'dim', 'align': 'left', 'stripRow': 'r'})
W.append({'id': 'strip_ev', 'type': 'text', 'z': 3, 'x': 1752, 'y': 672, 'w': 100, 'h': 37, 'text': '{{evRange}}', 'font': 'e_unit', 'color': CYAN, 'align': 'right', 'stripRow': 'r'})
W.append({'id': 'strip_ev_u', 'type': 'text', 'z': 3, 'x': 1858, 'y': 678, 'w': 50, 'h': 27, 'text': '{{u:dist}}', 'font': 'e_head', 'color': CYAN, 'align': 'left', 'stripRow': 'r'})

LAY = {'schemaVersion': 2, 'name': 'Live Hybrid', 'theme': 'livehyb', 'packWaste': 3, 'mapLive': False,
       '_about': "Live Hybrid cluster, generated by tools/gen_livehybrid.py (edit that and regenerate), after a photo of BMW's Live Cockpit Professional in a plug-in hybrid (2.jpeg): white outlined chevron scales (the speed 0 to 330 km/h on the left, the revs 0 to 8 on the right) with a red needle at the value, grey panels with the red glow at their foot, the big speed, the drive mode under ELECTRIC / HYBRID, the power meter with its kW, the electric range, the battery and fuel gauges, READY, and the dark middle display, where the Waze map opens while 'Show Waze map inside the theme' is on. The line art is drawn from geometry by the generator (hud/art/livehyb.json). Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('livehyb.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
