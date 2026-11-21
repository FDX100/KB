#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/livehyb.json (the Live Hybrid theme), after a photo of BMW's Live Cockpit
Professional in a plug-in hybrid (3.jpeg): two white outlined chevron scales (the speed 0..330 km/h on the left, the revs 0..8 on the
right) with a red needle at the value, grey panels inside them with the red glow at the foot, the big speed, the drive mode with
ELECTRIC / HYBRID, the power meter with its kW, the electric range, the battery gauge, the fuel gauge, READY, and the dark middle
display where the Waze map opens. The white lines are baked from the photo (tools/livehybrid/bake_mask.py -> hud/art/livehyb.json,
drawn by the ARTMASK shader); the rest is drawn live. Photo px -> layout px: x' = 960 + (x - 1060) * S, y' = (y - 322) * S.
Edit this and regenerate; do not hand-edit the JSON."""
import json, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'livehyb.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')
S = 1.245


def L(px, py): return (round(960 + (px - 1060) * S, 1), round((py - 322) * S, 1))
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

# ---- the outlines (photo px, snapped onto the photo's lines by tools/livehybrid/snap.py)
L_OUT = [[876.8, 343.0], [845.0, 339.0], [770.2, 344.0], [700.5, 358.0], [619.0, 362.1], [578.4, 371.3], [528.4, 394.9], [488.9, 420.3], [455.0, 447.0], [420.0, 475.0],
         [394.3, 501.3], [370.0, 530.0], [355.8, 561.2], [355.0, 600.0], [360.0, 637.0], [380.6, 677.3], [403.9, 705.4], [429.2, 745.6], [460.0, 785.0], [490.0, 815.0], [521.7, 832.5]]
R_OUT = [[1286.7, 343.0], [1344.8, 343.0], [1429.6, 351.0], [1504.2, 361.9], [1548.9, 369.9], [1593.4, 385.1], [1629.4, 407.8], [1662.3, 432.4], [1697.3, 462.3], [1725.0, 490.0],
         [1750.0, 520.0], [1767.0, 555.0], [1769.0, 580.6], [1765.1, 603.8], [1756.4, 637.3], [1753.1, 676.6], [1723.5, 705.4], [1695.8, 741.4], [1672.2, 772.2], [1650.0, 795.0],
         [1629.3, 810.7], [1604.1, 817.1]]


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
li = inner(L_OUT, 15, MID)
ri = inner(R_OUT, 15, MID)
# the grey panels: the inside of each outline, closed along the middle display's edge
PANEL_L = li[1:] + [(790, 778), (716, 612), (760, 500), (830, 415), (905, 395)]
PANEL_R = ri[1:] + [(1560, 790), (1372, 772), (1385, 690), (1392, 600), (1350, 500), (1300, 425), (1262, 392)]
CENTER = [(905, 414), (1250, 404), (1330, 418), (1390, 560), (1384, 650), (1318, 774), (900, 780), (796, 660)]


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
    raw = bytes(im.getdata())
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


def bake_centre():
    """The middle display (with and without the Waze window cut out) and the red glows at the feet of the panels, as 960 x 330 fills."""
    import numpy as np
    from PIL import ImageFilter
    pts = [L(*q) for q in smooth(CENTER, 8, True)]
    for name, hole in (('lh_mid', False), ('lh_mid_hole', True)):
        im, dr, k = canvas(960, 330)
        dr.polygon([(x / 2 * k, y / 2 * k) for x, y in pts], fill=255)
        if hole:
            dr.rounded_rectangle([668 / 2 * k, 128 / 2 * k, (668 + 628) / 2 * k, (128 + 436) / 2 * k], radius=56 / 2 * k, fill=0)
        put_art(name, finish(im, 960, 330))
    g = np.zeros((330, 960), float)
    for x0, x1, y0, y1, ins in ((548, 720, 736, 788, 18), (1400, 1590, 730, 794, 20)):
        (ax, ay), (bx, by) = L(x0, y0), L(x1, y1)
        ax, ay, bx, by = ax / 2, ay / 2, bx / 2, by / 2
        for yy in range(int(ay), int(by) + 1):
            for xx in range(int(ax), int(bx) + 1):
                u = (yy - ay) / max(1, by - ay)                                  # glow is strongest at the foot
                edge = min(1.0, min(xx - ax, bx - xx) / 14.0) if True else 1
                g[yy, xx] = max(g[yy, xx], 0.9 * (u ** 1.4) * max(0, edge))
    put_art('lh_glow', np.round(g * 255).astype(np.uint8))


def gauge_masks():
    """The three gauge shapes of the photo (the power meter's chevron band, the battery's bowl, the fuel gauge's bent band), each baked as a
    coverage picture and a 'how far along' picture (hud/art/lh_<name>.json and lh_<name>_t.json, half size) for the GAUGEMASK shader, with
    smooth edges: the outer curves are snapped onto the photo's white lines, then set a little inside them."""
    import numpy as np
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'livehybrid'))
    import snap
    z = lambda off, pts: [(off[0] + x / 4.0, off[1] + y / 4.0) for x, y in pts]       # a zoomed crop's coordinates -> photo px
    def relax(P, times=3):                                                             # the ridge snapping is noisy: even the points out
        P = [tuple(q) for q in P]
        for _ in range(times):
            P = [P[0]] + [((P[i - 1][0] + 2 * P[i][0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * P[i][1] + P[i + 1][1]) / 4) for i in range(1, len(P) - 1)] + [P[-1]]
        return P
    snapped = lambda off, pts, R=6: relax(snap.snap(z(off, pts), R))
    power_o = smooth(snapped((1360, 440), [(420, 130), (500, 215), (560, 300), (620, 370), (665, 440), (688, 520), (675, 600), (640, 690), (580, 790), (500, 935)], 7), 8)
    power_i = smooth(z((1360, 440), [(440, 330), (520, 410), (572, 490), (580, 560), (555, 640), (500, 720), (440, 800), (395, 935)]), 8)
    power = [(1360 + 275 / 4, 440 + 135 / 4)] + power_o + [(1360 + 395 / 4, 440 + 935 / 4)] + power_i[::-1] + [(1360 + 440 / 4, 440 + 330 / 4)]
    # the battery: the outer white curve inset by a few px, the bowl on the left, the thin band up to 100
    b_out = snapped((1640, 660), [(590, 68), (650, 112), (684, 200), (690, 300), (676, 400), (640, 490), (585, 570), (505, 640), (420, 692), (330, 722), (240, 706)], 7)
    b_ins = [(x - 4 * (x - 1740) / math.hypot(x - 1740, y - 800), y - 4 * (y - 800) / math.hypot(x - 1740, y - 800)) for x, y in b_out]
    band_in = inner(b_out[:6], 10, (1700, 760))
    batt = smooth(b_ins, 8) + smooth(z((1640, 660), [(250, 672), (262, 600), (300, 510), (350, 450), (420, 428)]), 8) + smooth(band_in[::-1], 6)[::-1][::-1]
    # the fuel gauge: the band between its outer white line and the thin inner one
    FX = 17                                                                           # the photo's gauge reaches past the screen's edge: moved in
    f_o = [(x + FX, y) for x, y in snapped((260, 650), [(172, 92), (100, 160), (78, 260), (98, 360), (140, 450), (210, 540), (300, 620), (400, 690), (500, 745), (600, 775), (700, 768)], 6)]
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
        px = 1060 + (gx - 960) / S; py = 322 + gy / S
        t = np.clip(par(px, py), 0, 1)
        put_art('lh_' + name, cov)
        put_art('lh_' + name + '_t', np.round(t * 255).astype(np.uint8))
        out[name] = (x0, y0, w, h)
    # the fuel gauge's own white lines (the photo's are blanked out of the baked art): the outer double line and the thin inner one
    lp = lambda pts: [L(*q) for q in pts]
    x0, y0, w, h = out['fuel']
    im, dr, k = canvas(w, h, 4)
    for pts, width in ((smooth(f_o, 8), 2.6), (smooth(inner(f_o, 3.8, (467, 660)), 8), 1.6), (smooth(f_i, 8), 1.6)):
        dr.line([((x - x0) * k, (y - y0) * k) for x, y in lp(pts)], fill=255, width=int(width * k), joint='curve')
    put_art('lh_fuel_lines', finish(im, w, h))
    return out


def gauges():
    box = gauge_masks()
    spec = (('power', 'powerPct', 0, 100, 'accent', [84, 86, 92, 255]), ('batt', 'hvSoc', 0, 100, 'accent', [58, 62, 68, 255]),
            ('fuel', 'fuel', 0, 1, [236, 238, 240, 255], [74, 76, 80, 255]))
    return [{'id': n + '_gauge', 'type': 'gaugemask', 'class': 'content', 'z': 2, 'x': box[n][0], 'y': box[n][1], 'w': box[n][2], 'h': box[n][3], 'conn': 2,
             'art': 'lh_' + n, 'art2': 'lh_' + n + '_t', 'signal': sg, 'min': mn, 'max': mx, 'color': col, 'trackColor': trk} for n, sg, mn, mx, col, trk in spec] + [
        {'id': 'fuel_lines', 'type': 'artmask', 'class': 'content', 'z': 3, 'x': box['fuel'][0], 'y': box['fuel'][1], 'w': box['fuel'][2], 'h': box['fuel'][3], 'conn': 2, 'art': 'lh_fuel_lines', 'color': WHITE}]


W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg'}]
HOLE = {'hole': [668, 128, 628, 436], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 56}
# the grey panels (one layer: a polygon each) and, over them, the middle display and the red glows (a second layer)
PANEL = [44, 46, 50, 255]
W.append({'id': 'panels', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 1, 'art': 'livehyb_panel', 'color': PANEL})
bake_centre()
W.append({'id': 'middle', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 2, 'art': 'lh_mid', 'color': [16, 18, 24, 255], 'toggle': '!mapUp'})
W.append({'id': 'middle_map', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 2, 'art': 'lh_mid_hole', 'color': [16, 18, 24, 255], 'toggle': 'mapUp'})
W.append({'id': 'glow', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 2, 'art': 'lh_glow', 'color': [236, 40, 44, 255]})
# the white line art baked from the photo
W.append({'id': 'art', 'type': 'artmask', 'class': 'content', 'z': 2, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 3, 'art': 'livehyb', 'color': WHITE})
# ---- the scale numbers
SPEED = [(0, (657, 782)), (30, (570, 784)), (60, (514, 726)), (90, (466, 654)), (120, (437, 582)), (150, (476, 514)), (180, (536, 464)),
         (210, (588, 422)), (240, (655, 400)), (270, (730, 387)), (300, (802, 384)), (330, (875, 380))]
for k, (v, p) in enumerate(SPEED):
    W.append(text('sk%d' % v, p, 100, 'z_num', str(v), WHITE, 'center', toggle='!units=us'))
    W.append(text('sm%d' % (k * 20), p, 100, 'z_num', str(k * 20), WHITE, 'center', toggle='units=us'))
REV = [(1, (1600, 752)), (2, (1655, 665)), (3, (1687, 575)), (4, (1647, 500)), (5, (1575, 440)), (6, (1485, 407)), (7, (1390, 390)), (8, (1287, 385))]
for v, p in REV:
    W.append(text('rv%d' % v, p, 60, 'z_num', str(v), WHITE, 'center'))
# ---- the needles: where each scale's ticks meet its outline (photo px)
SPD_MARKS = [(0, (598, 837)), (1, (500, 822)), (2, (440, 752)), (3, (392, 677)), (4, (355, 585)), (5, (394, 502)), (6, (455, 447)), (7, (528, 395)), (8, (619, 362)),
             (9, (700, 358)), (10, (790, 343)), (11, (877, 343))]
REV_MARKS = [(0, (1550, 825)), (1, (1652, 794)), (2, (1723, 706)), (3, (1769, 581)), (4, (1697, 462)), (5, (1629, 408)), (6, (1549, 370)), (7, (1430, 351)), (8, (1345, 343))]
W.append({'id': 'spd_needle', 'type': 'pneedle', 'class': 'content', 'z': 3, 'x': 0, 'y': 0, 'w': 960, 'h': 660, 'conn': 3, 'signal': 'speed',
          'marks': [[30 * i, *L(*p)] for i, p in SPD_MARKS], 'marksUs': [[20 * i, *L(*p)] for i, p in SPD_MARKS], 'length': 78, 'width': 3.4, 'glow': 12, 'color': 'hot'})
W.append({'id': 'rev_needle', 'type': 'pneedle', 'class': 'content', 'z': 3, 'x': 960, 'y': 0, 'w': 960, 'h': 660, 'conn': 3, 'signal': 'rpm',
          'marks': [[v, *L(*p)] for v, p in REV_MARKS], 'length': 78, 'width': 3.4, 'glow': 12, 'color': 'hot'})
# ---- the mode, the speed
W.append(text('evmode', (765, 526), 340, 'h_mode', '{{evmode}}', CYAN, 'center'))
W.append(text('mode', (668, 553), 260, 'z_unit', '{{mode}}', WHITE, 'left'))
W.append(icon('drive_icon', 'gauge', (636, 546), 46, WHITE))
W.append(text('speed', (770, 632), 220, 'm_speed', '{{speed}}', WHITE, 'center'))
W.append(text('speed_u', (818, 608), 100, 'h_small', '{{u:speedLc}}', WHITE, 'left'))
# ---- the power meter and the electric range
W.extend(gauges())
for v, p in ((60, (1409, 471)), (40, (1454, 533)), (20, (1475, 595)), (0, (1432, 660))):
    W.append(text('pk%d' % v, p, 50, 'm_tyre', str(v), DIM, 'center'))
W.append(text('power', (1415, 565), 110, 'm_mid', '{{powerKw}}', WHITE, 'center'))
W.append(text('power_u', (1415, 597), 60, 'h_small', 'kW', DIM, 'center'))
W.append(text('avg', (1562, 642), 130, 'h_small', 'Ø{{avgSpeed}}', DIM, 'center'))
W.append(icon('evcar', 'evcar', (1381, 706), 70, CYAN))
W.append(text('evrange', (1428, 706), 130, 'm_mid', '{{evRange}}', CYAN, 'left'))
W.append(text('evrange_u', (1520, 712), 60, 'h_small', '{{u:distLc}}', CYAN, 'left'))
# ---- READY, the revs label, the battery and fuel gauges
W.append(text('ready', (1504, 771), 170, 'z_unit', '{{ready}}', WHITE, 'center'))
W.append(text('revs_lbl', (1450, 803), 190, 'h_small', '1/min x1000', DIM, 'center'))
W.append(text('batt_pct', (1748, 758), 90, 'z_unit', '{{hvSoc}}%', WHITE, 'center'))
W.append(text('batt_100', (1750, 680), 80, 'm_tyre', '100', DIM, 'center'))
W.append(text('batt_0', (1698, 797), 30, 'm_tyre', '0', DIM, 'center'))
W.append(icon('batt_icon', 'battery', (1795, 819), 44, WHITE))
W.append(text('fuel_1', (351, 692), 30, 'm_tyre', '1', DIM, 'center'))
W.append(text('fuel_half', (385, 757), 70, 'z_unit', '1/2', DIM, 'center'))
W.append(text('fuel_0', (435, 802), 30, 'm_tyre', '0', DIM, 'center'))
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
       '_about': "Live Hybrid cluster, generated by tools/gen_livehybrid.py (edit that and regenerate), after a photo of BMW's Live Cockpit Professional in a plug-in hybrid (3.jpeg): white outlined chevron scales (the speed 0 to 330 km/h on the left, the revs 0 to 8 on the right) with a red needle at the value, grey panels with the red glow at their foot, the big speed, the drive mode under ELECTRIC / HYBRID, the power meter with its kW, the electric range, the battery and fuel gauges, READY, and the dark middle display, where the Waze map opens while 'Show Waze map inside the theme' is on. The line art is baked from the photo (hud/art/livehyb.json). Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('livehyb.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
