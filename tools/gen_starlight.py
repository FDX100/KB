#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/starlight.json (the Starlight theme), after a concept video of a luxury electric car's cluster
(2.mp4): a night sky of stars, a glowing ring in the middle with the speed in a very tall thin face, the revs 0..8 as two rows of numbers that
fan out towards the sides (the outer ones larger and whiter, 8 in red), two thin rails running into the ring, and on each side a curtain of
light with drifting dust whose edge slides outwards along the numbers as the revs climb and turns red towards the redline. Weather / clock
top left, the power and its bar top right, the badge top centre, the gear and drive mode under the ring.
Everything is drawn by shaders (shaders.js STARS, RINGFX, BEAM) or baked from geometry here (the two rails). Edit this and regenerate."""
import base64, json, math, os, sys, zlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'starlight.json')
ART = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'art')
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


# ---- the two rails (grey) and the red start of the outer one, baked from geometry
def bake_rails():
    import numpy as np
    from PIL import Image, ImageDraw
    k = 3
    y0, y1 = 300, 570
    grey = Image.new('L', (1920 * k, (y1 - y0) * k), 0)
    red = Image.new('L', (1920 * k, 60 * k), 0)
    dg, dr = ImageDraw.Draw(grey), ImageDraw.Draw(red)
    rails = [([(0, 494), (600, 401), (822, 401)], 150, 1.5), ([(350, 570), (606, 481), (822, 403)], 190, 1.7)]
    ry0 = 440
    for pts, val, wd in rails:
        lp = [C(*q) for q in pts]
        for mirror in (False, True):
            q = [((1920 - x) if mirror else x, y) for x, y in lp]
            dg.line([(x * k, (y - y0) * k) for x, y in q], fill=val, width=int(wd * k), joint='curve')
    # the outer rail turns red towards the edge: fade over 150 px
    lp = [C(*q) for q in rails[0][0]]
    for mirror in (False, True):
        seg = [((1920 - x) if mirror else x, y) for x, y in lp][:2]
        for i in range(60):
            t0, t1 = i / 60, (i + 1) / 60
            x_a, y_a = seg[0][0] + (seg[1][0] - seg[0][0]) * t0 * 0.3, seg[0][1] + (seg[1][1] - seg[0][1]) * t0 * 0.3
            x_b, y_b = seg[0][0] + (seg[1][0] - seg[0][0]) * t1 * 0.3, seg[0][1] + (seg[1][1] - seg[0][1]) * t1 * 0.3
            dr.line([(x_a * k, (y_a - ry0) * k), (x_b * k, (y_b - ry0) * k)], fill=int(255 * (1 - t0)), width=int(2.2 * k))
    for name, im, size in (('sl_rails', grey, (1920, y1 - y0)), ('sl_rails_red', red, (1920, 60))):
        arr = np.asarray(im.resize(size, Image.LANCZOS), dtype=np.uint8)
        with open(os.path.join(ART, name + '.json'), 'w') as f:
            json.dump({'w': size[0], 'h': size[1], 'z': base64.b64encode(zlib.compress(arr.tobytes(), 9)).decode()}, f)
    return y0, ry0


os.makedirs(ART, exist_ok=True)
RY0, REDY0 = bake_rails()
W.append({'id': 'rails', 'type': 'artmask', 'class': 'content', 'z': 2, 'x': 0, 'y': RY0, 'w': 1920, 'h': 270, 'conn': 1, 'art': 'sl_rails', 'color': [176, 190, 220, 255]})
W.append({'id': 'rails_red', 'type': 'artmask', 'class': 'content', 'z': 2, 'x': 0, 'y': REDY0, 'w': 1920, 'h': 60, 'conn': 1, 'art': 'sl_rails_red', 'color': [236, 60, 60, 255]})
# ---- the ring in the middle
RC = C(1000, 340)
RR = 123
W.append({'id': 'ring', 'type': 'ringfx', 'class': 'content', 'z': 2, 'x': 790, 'y': round(RC[1] - RR - 50), 'w': 340, 'h': RR * 2 + 100, 'conn': 2, 'ring': [960, RC[1], RR, 0.93]})
# ---- the two light curtains (left frame coordinates; the right one is mirrored)
RAIL = C(0, 401)[1]
EDGE_TOP, EDGE_BOT = C(0, 275)[1], RAIL + 84               # the curtain's edge ends on the floor rail, but the curtain is never thicker than this
FLOOR = [C(606, 481)[0], C(606, 481)[1], C(822, 403)[0], C(822, 403)[1]]
BY0 = round(EDGE_TOP - 18)
BH = round(EDGE_BOT + 14 - BY0)
SCALE_L = [(0, C(732, 0)[0]), (1, C(667, 0)[0]), (2, C(594, 0)[0]), (3, C(516, 0)[0]), (4, C(443, 0)[0]), (5, C(362, 0)[0]), (6, C(272, 0)[0]), (7, C(180, 0)[0]), (8, C(88, 0)[0])]
beam = {'type': 'beam', 'class': 'content', 'z': 3, 'y': BY0, 'w': 800, 'h': BH, 'conn': 2, 'rail': RAIL, 'edge': [EDGE_TOP, EDGE_BOT], 'floor': FLOOR, 'tip': C(822, 0)[0],
        'marks': [[v, x] for v, x in SCALE_L], 'hotFrom': 6.4}
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
# ---- the top row: the temperature and clock on the left, the power and its bar on the right
TY = C(0, 80)[1]
W.append({'id': 'temp_icon', 'type': 'icon', 'icon': 'therm', 'z': 5, 'x': 30, 'y': round(TY - 14), 'w': 28, 'h': 28, 'color': GREY})
W.append(text('temp', (72, TY), 110, 'sl_top', '{{ambient}}{{u:temp}}', WHITE, 'left'))
W.append(text('clock', (170, TY), 190, 'sl_top', '{{time}} {{ampm}}', WHITE, 'left'))
W.append({'id': 'power_icon', 'type': 'icon', 'icon': 'bolt', 'z': 5, 'x': 1610, 'y': round(TY - 12), 'w': 24, 'h': 24, 'color': WHITE})
W.append(text('power', (1640, TY), 130, 'sl_top', '{{powerKw}} KW', WHITE, 'left'))
W.append({'id': 'power_track', 'type': 'fill', 'class': 'content', 'z': 2, 'x': 1750, 'y': round(TY - 1), 'w': 150, 'h': 2, 'color': [70, 76, 90, 255]})
W.append({'id': 'power_bar', 'type': 'meter', 'class': 'content', 'z': 3, 'x': 1750, 'y': round(TY - 1.5), 'w': 150, 'h': 3, 'signal': 'powerPct', 'min': 0, 'max': 100,
          'segments': 75, 'gap': 0, 'colors': [[240, 241, 245, 255]] * 3, 'at': [1.0, 1.0], 'conn': 2})
# ---- the gear and the drive mode under the ring
W.append(text('gear', (960, RC[1] + RR + 36), 80, 'sl_top', '{{gear}}', WHITE, 'center'))
W.append(text('mode', (960, RC[1] + RR + 66), 240, 'sl_top', '{{mode}}', DIM, 'center'))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_'):
        W.append(w)

LAY = {'schemaVersion': 2, 'name': 'Starlight', 'theme': 'starlight', 'packWaste': 3,
       '_about': "Starlight cluster, generated by tools/gen_starlight.py (edit that and regenerate), after a concept video of a luxury electric car's cluster (2.mp4): a night sky of stars, a glowing ring with the speed in a very tall thin face, the revs 0 to 8 as two rows of numbers fanning out to the sides, two rails running into the ring, and on each side a curtain of light with drifting dust whose edge slides outwards along the numbers with the revs and turns red near the redline. Temperature and clock top left, power top right, badge top centre. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('starlight.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
