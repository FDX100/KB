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
W.append(text('speed_u', X(850), Y(470), 120, 'rd_unit', '{{u:speed}}', DIM, 'left'))
W.append({'id': 'line_l', 'type': 'fill', 'class': 'content', 'z': 3, 'x': round(X(268)), 'y': round(Y(412)), 'w': round(X(328) - X(268)), 'h': 1, 'color': [60, 150, 90, 255]})
W.append({'id': 'line_r', 'type': 'fill', 'class': 'content', 'z': 3, 'x': round(X(696)), 'y': round(Y(412)), 'w': round(X(752) - X(696)), 'h': 1, 'color': [60, 150, 90, 255]})
# ---- the small print under the arc
W.append(text('range', X(152), Y(263), 220, 'rd_small', '{{range}} {{u:distLc}}', DIM, 'center'))
W.append(text('clock', X(873), Y(263), 220, 'rd_small', '{{time}} {{ampm}}', DIM, 'center'))
# ---- the neon headlamps, drawn in the photo's pixels (the left one, the right one mirrored) at 1.3 times
HL = [  # [x0, y0, x1, y1, width, brightness]: the lens' top edge, its bottom edge, the reflector, the lower light
    (66, 384, 96, 377, 2.4, 1.0), (96, 377, 140, 378, 2.4, 1.0), (140, 378, 180, 390, 2.4, 1.0), (180, 390, 214, 408, 2.4, 1.0),
    (66, 398, 110, 406, 2.0, 0.85), (110, 406, 170, 410, 2.0, 0.85), (170, 410, 214, 414, 2.0, 0.85),
    (146, 398, 170, 396, 1.6, 0.75), (170, 396, 192, 402, 1.6, 0.75),
    (78, 438, 78, 466, 5.0, 1.0), (78, 466, 86, 484, 5.0, 1.0), (86, 484, 100, 494, 5.0, 1.0), (100, 494, 122, 498, 5.0, 1.0),
]
LS, LW, LH = 1.3, 320, 270
for side in ('l', 'r'):
    cx = X(140) if side == 'l' else 1920 - X(140)
    cy = Y(440)
    x0, y0 = round(cx - LW / 2), round(cy - LH / 2)

    def pt(px, py):
        qx = (px - 140) if side == 'l' else -(px - 140)
        return round(cx + qx * LS, 1), round(cy + (py - 440) * LS, 1)
    segs = []
    for (ax, ay, bx, by, wd, br) in HL:
        (a, b), (c, d) = pt(ax, ay), pt(bx, by)
        segs.append([a, b, c, d, round(wd * 1.45, 1), br])
    ring = list(pt(124, 400)) + [round(10 * LS, 1), 1.8]
    W.append({'id': 'lamp_' + side, 'type': 'neonlamp', 'class': 'content', 'z': 1, 'x': x0, 'y': y0, 'w': LW, 'h': LH, 'conn': 3, 'segs': segs, 'ring': ring})
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
