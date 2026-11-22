#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/radar.json (the Radar theme), after a green concept cluster (11.jpeg): a radar-sweep rev gauge in the middle
(a white ring 0..7 with the numbers 0..10 (x1000) in italics, a grey band, a dark disc with a green sweep that runs from the needle back round to the 0, a halftone
behind the needle, the thin white needle, a load arc beyond the 7), the gear in a big slanted numeral on the left, the speed on the right, a thin neon arc across
the top, a neon headlamp on each side, the range and the time. Everything but the text is drawn by shaders (shaders.js RADAR, NEONARC, NEONLAMP). Photo px ->
cluster px: x' = 960 + (x - 512) * 1.45, y' = (y - 62) + 40 (the photo is 4:3, the cluster is wider, so the sides are spread out). Edit this and regenerate."""
import json, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'radar.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')


def X(x): return round(960 + (x - 512) * 1.45, 1)
def Y(y): return round((y - 62) + 40, 1)
def cell(font): return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, x, y, w, font, t, color, align='center', **kw):
    h = cell(font)
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font, 'color': color, 'align': align}
    d.update(kw)
    return d


WHITE = [244, 247, 244, 255]
DIM = [120, 136, 124, 255]
GREEN = [98, 224, 120, 255]
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 720, 'color': 'bg'}]
# ---- the neon arc across the top (an ellipse through the photo's (20, 300), (512, 62), (1000, 300))
EC = (960, 663)
W.append({'id': 'top_arc', 'type': 'neonarc', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 360, 'conn': 1,
          'ellipse': {'center': [EC[0], EC[1]], 'axes': [907, 623], 'half': 720, 'core': 0.9}})
# ---- the radar gauge
GC = (960, Y(412))
GR = 241
SZ = 600
W.append({'id': 'radar', 'type': 'radar', 'class': 'content', 'z': 2, 'x': round(GC[0] - SZ / 2), 'y': round(GC[1] - SZ / 2), 'w': SZ, 'h': SZ, 'conn': 2, 'rpmMax': 10000,
          'radar': {'center': [GC[0], GC[1]], 'radius': GR}})
for k in range(11):
    a = math.radians(-145 + 29 * k)
    W.append(text('n%d' % k, GC[0] + 0.9 * GR * math.sin(a), GC[1] - 0.9 * GR * math.cos(a), 56, 'rd_num', str(k), WHITE, 'center'))
for t, dx, dy in (('N', 0, -84), ('W', -88, 0), ('E', 88, 0), ('S', 0, 84)):
    W.append(text('c_' + t, GC[0] + dx, GC[1] + dy, 30, 'rd_small', t, DIM, 'center'))
W.append(text('rpm_x', GC[0], GC[1] + 183, 140, 'rd_small', 'x1000', WHITE, 'center'))
W.append(text('rpm_l', GC[0], GC[1] + 203, 140, 'rd_small', 'RPM', WHITE, 'center'))
# ---- the gear (left) and the speed (right), with the thin lines that join them to the gauge
W.append(text('gear', X(275), Y(455), 130, 'rd_big', '{{gearN}}', WHITE, 'center'))
W.append(text('speed', X(775), Y(455), 300, 'rd_big', '{{speed}}', WHITE, 'center'))
W.append(text('speed_u', X(850) - 14, Y(470) + 4, 90, 'rd_unit', '{{u:speed}}', DIM, 'left'))
W.append({'id': 'line_l', 'type': 'fill', 'class': 'content', 'z': 3, 'x': round(X(268)), 'y': round(Y(412)), 'w': round(X(328) - X(268)), 'h': 1, 'color': [60, 150, 90, 255]})
W.append({'id': 'line_r', 'type': 'fill', 'class': 'content', 'z': 3, 'x': round(X(696)), 'y': round(Y(412)), 'w': round(X(752) - X(696)), 'h': 1, 'color': [60, 150, 90, 255]})
# ---- the small print under the arc
W.append(text('range', X(152), Y(263), 220, 'rd_small', '{{range}} {{u:distLc}}', DIM, 'center'))
W.append(text('clock', X(873), Y(263), 220, 'rd_small', '{{time}} {{ampm}}', DIM, 'center'))
# ---- the BMW headlamps, drawn as neon lines in the photo's pixels (zoomed crop coordinates: x' = 50 + zx / 5, y' = 360 + zy / 5; the left lamp, the right one mirrored)
def Z(zx, zy): return (50 + zx / 5.0, 360 + zy / 5.0)


def smooth(zs, n):
    """A Catmull-Rom curve through the points, n steps a span (zoomed crop coordinates)."""
    out = []
    for i in range(len(zs) - 1):
        p0, p1, p2, p3 = zs[max(0, i - 1)], zs[i], zs[i + 1], zs[min(len(zs) - 1, i + 2)]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(zs[-1])
    return out


DRL = smooth([(88, 125), (95, 200), (118, 262), (200, 277), (400, 283), (620, 282), (740, 272), (800, 238)], 2)                 # 15 vertices
U_LIGHT = smooth([(440, 180), (462, 225), (500, 245), (650, 248), (682, 215)], 2)                                                  # 9 vertices
TOP_EDGE = smooth([(65, 110), (450, 140), (850, 255)], 2)                                                                          # 5 vertices
BOT_EDGE = smooth([(70, 292), (450, 302), (845, 262)], 2)                                                                          # 5 vertices
BODY = [(65, 110), (380, 122), (700, 175), (850, 255), (780, 285), (420, 298), (80, 295), (62, 200)]
BAR = smooth([(140, 405), (150, 480), (175, 580), (230, 650), (310, 695), (410, 725)], 3)                                          # 16 vertices
LOW_OUT1 = [(125, 400), (640, 470), (720, 540)]
LOW_OUT2 = [(410, 728), (640, 640)]
RINGS = [(368, 200, 9.4, 103.6, 1.0), (368, 200, 5.4, 2.0, 0.9), (205, 190, 7.2, 1.2, 0.35), (560, 190, 6.0, 1.2, 0.35)]
LS = 1.75
for side in ('l', 'r'):
    cx = X(140) - 60 if side == 'l' else 1920 - X(140) + 60
    cy = Y(440)

    def pt(zx, zy):
        px, py = Z(zx, zy)
        qx = (px - 140) if side == 'l' else -(px - 140)
        return cx + qx * LS, cy + (py - 440) * LS

    def chain(zs, w, b):
        return [[round(pt(*q)[0], 1), round(pt(*q)[1], 1), round(w * 1.25, 1), b] for q in zs]

    def layer(nm, z, chains, rings, fill, haze):
        pts = [(v[0], v[1]) for ch in chains for v in ch] + [(r[0], r[1]) for r in rings] + list(fill)
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        pad = 46
        x0, y0 = round(min(xs) - pad), round(min(ys) - pad)
        d = {'id': 'lamp_%s_%s' % (nm, side), 'type': 'neonlamp', 'class': 'content', 'z': z, 'x': x0, 'y': y0, 'w': round(max(xs) - min(xs) + 2 * pad), 'h': round(max(ys) - min(ys) + 2 * pad),
             'conn': 3, 'chains': chains, 'rings': rings, 'fill': [list(q) for q in fill], 'haze': haze}
        return d
    rg = []
    for (zx, zy, r, wd, br) in RINGS:
        x, y = pt(zx, zy)
        rg.append([round(x, 1), round(y, 1), round(r * LS, 1), wd, br])
    body = [[round(pt(*q)[0], 1), round(pt(*q)[1], 1)] for q in BODY]
    W.append(layer('body', 1, [chain(U_LIGHT, 3.4, 1.0)], rg, body, 0.9))
    W.append(layer('drl', 2, [chain(DRL, 4.2, 1.0), chain([(82, 160), (90, 232)], 4.0, -0.95), chain(TOP_EDGE, 1.6, 0.5), chain(BOT_EDGE, 1.6, 0.5)], [], [], 0))
    W.append(layer('low', 1, [chain(BAR, 5.2, 1.0), chain(LOW_OUT1, 1.1, 0.3), chain(LOW_OUT2, 1.1, 0.3)], [], [], 0))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_cover'):
        W.append(w)

LAY = {'schemaVersion': 2, 'name': 'Radar', 'theme': 'radar', 'packWaste': 3,
       '_about': "Radar cluster, generated by tools/gen_radar.py (edit that and regenerate), after a green concept cluster (11.jpeg): a radar-sweep rev gauge (white ring 0 to 7, italic numbers 0 to 10, a green sweep from the needle back round to the 0, a halftone behind the needle, a load arc beyond the 7), the gear and the speed in big slanted numerals, a thin neon arc across the top, a neon headlamp on each side, the range and the time. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('radar.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
