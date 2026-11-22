#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/starlight.json (the Starlight theme), after a concept video of a luxury electric car's cluster
(2.mp4): a night sky of stars, a glowing ring in the middle with the speed in a very tall thin face, the revs 0..8 as two rows of numbers that
fan out towards the sides (the outer ones larger and whiter, 8 in red), two thin rails running into the ring, and on each side a curtain of
light with drifting dust whose edge slides outwards along the numbers as the revs climb and turns red towards the redline. Clock
top left, the power and its bar top right, the badge top centre, the gear and drive mode under the ring.
Every shape is drawn by shaders (shaders.js STARS, RINGFX, RAILS, BEAM), no pictures; only the numbers and words are the bitmap fonts. Edit this and regenerate."""
import base64, json, math, os, sys, zlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'starlight.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')
K, Y0 = 0.96, 40.0                                   # the video's 2000 px width onto the cluster's 1920


def C(cx, cy): return (round(cx * K, 1), round((cy - 30) * K + Y0, 1))
def cell(font): return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, p, w, font, t, color, align='center', **kw):
    x, y = p
    h = cell(font)
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font, 'color': color, 'align': align}
    d.update(kw)
    return d


WHITE = [240, 241, 245, 255]
GREY = [168, 174, 188, 255]
DIM = [120, 126, 140, 255]
RED = [236, 62, 52, 255]
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg'}]
# ---- the sky
W.append({'id': 'sky', 'type': 'stars', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 520, 'conn': 1, 'sky': [C(0, 300)[1], C(0, 520)[1], C(0, 31)[1]]})


# ---- the two thin rails into the ring, drawn by the shader (shaders.js RAILS): the outer one turns red towards the edge
SEGS = [[*C(0, 494), *C(600, 401)], [*C(600, 401), *C(822, 401)], [*C(350, 570), *C(606, 481)], [*C(606, 481), *C(822, 403)]]
W.append({'id': 'rails', 'type': 'rails', 'class': 'content', 'z': 2, 'x': 0, 'y': 300, 'w': 1920, 'h': 270, 'conn': 1, 'segs': SEGS, 'red': 150, 'width': 1.6})
# ---- the ring in the middle
RC = C(1000, 340)
RR = 123
RB = 520
W.append({'id': 'ring', 'type': 'ringfx', 'class': 'content', 'z': 2, 'x': 960 - RB // 2, 'y': round(RC[1] - RR - 70), 'w': RB, 'h': RR * 2 + 170, 'conn': 2, 'ring': [960, RC[1], RR, 0.93]})
# ---- the two light curtains (left frame coordinates; the right one is mirrored)
RAIL = C(0, 401)[1]
EDGE_TOP, EDGE_BOT = C(0, 275)[1], 640                      # the curtain's edge ends on the floor rail, which slopes down towards the sides; never below this
FLOOR = [C(606, 481)[0], C(606, 481)[1], C(822, 403)[0], C(822, 403)[1]]
BY0 = round(EDGE_TOP - 18)
BH = 660 - BY0
SCALE_L = [(0, C(732, 0)[0]), (1, C(667, 0)[0]), (2, C(594, 0)[0]), (3, C(516, 0)[0]), (4, C(443, 0)[0]), (5, C(362, 0)[0]), (6, C(272, 0)[0]), (7, C(180, 0)[0]), (8, C(88, 0)[0])]
beam = {'type': 'beam', 'class': 'content', 'z': 3, 'y': BY0, 'w': 800, 'h': BH, 'conn': 2, 'rail': RAIL, 'edge': [EDGE_TOP, EDGE_BOT], 'floor': FLOOR, 'tip': C(822, 0)[0],
        'marks': [[v, x] for v, x in SCALE_L], 'red': [SCALE_L[7][1] + 14, SCALE_L[8][1] - 8]}
W.append(dict(beam, id='beam_l', x=0, mirror=False))
W.append(dict(beam, id='beam_r', x=1120, mirror=True))
# ---- the numbers 0..8 on both sides, positions read off the video (the outer ones bigger and whiter, 8 red)
NUM = [(8, (88, 422), 'sl_n1', RED), (7, (180, 410), 'sl_n1', WHITE), (6, (272, 396), 'sl_n2', WHITE), (5, (362, 384), 'sl_n2', WHITE), (4, (443, 372), 'sl_n3', WHITE),
       (3, (516, 364), 'sl_n3', GREY), (2, (594, 355), 'sl_n4', GREY), (1, (667, 348), 'sl_n4', GREY), (0, (732, 343), 'sl_n4', GREY)]
for v, p, font, col in NUM:
    x, y = C(*p)
    W.append(text('nl%d' % v, (x, y), 70, font, str(v), col, 'center'))
    W.append(text('nr%d' % v, (1920 - x, y), 70, font, str(v), col, 'center'))
# ---- the speed in the ring
W.append(text('speed', (960, RC[1] - 8), 240, 'sl_speed', '{{speed}}', WHITE, 'center'))
W.append(text('speed_u', (960, C(0, 408)[1] + 2), 120, 'sl_unit', '{{u:speed}}', GREY, 'center'))
# ---- the top row: the clock on the left, the power and its bar on the right
TY = 114                                               # inside the visible part of the cluster: the hood curve is ~85 px down at x 200 and x 1700
W.append(text('clock', (268, TY), 190, 'sl_top', '{{time}} {{ampm}}', WHITE, 'left'))
W.append({'id': 'power_icon', 'type': 'icon', 'icon': 'bolt', 'z': 5, 'x': 1428, 'y': TY - 12, 'w': 24, 'h': 24, 'color': WHITE})
W.append(text('power', (1460, TY), 110, 'sl_top', '{{powerKw}} KW', WHITE, 'left'))
W.append({'id': 'power_track', 'type': 'fill', 'class': 'content', 'z': 2, 'x': 1566, 'y': TY - 1, 'w': 140, 'h': 2, 'color': [70, 76, 90, 255]})
W.append({'id': 'power_bar', 'type': 'meter', 'class': 'content', 'z': 3, 'x': 1566, 'y': TY - 2, 'w': 140, 'h': 3, 'signal': 'powerPct', 'min': 0, 'max': 100,
          'segments': 70, 'gap': 0, 'colors': [[240, 241, 245, 255]] * 3, 'at': [1.0, 1.0], 'conn': 2})
# ---- the gear and the drive mode under the ring
W.append(text('gear', (960, RC[1] + RR + 36), 80, 'sl_top', '{{gear}}', WHITE, 'center'))
W.append(text('mode', (960, RC[1] + RR + 66), 240, 'sl_top', '{{mode}}', DIM, 'center'))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_'):
        W.append(w)

LAY = {'schemaVersion': 2, 'name': 'Starlight', 'theme': 'starlight', 'packWaste': 1.5,
       '_about': "Starlight cluster, generated by tools/gen_starlight.py (edit that and regenerate), after a concept video of a luxury electric car's cluster (2.mp4): a night sky of stars, a glowing ring with the speed in a very tall thin face, the revs 0 to 8 as two rows of numbers fanning out to the sides, two rails running into the ring, and on each side a curtain of light with drifting dust whose edge slides outwards along the numbers with the revs and turns red near the redline. Clock top left, power top right, badge top centre. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('starlight.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
