#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/cream.json (the Cream theme), after a retro concept cluster (10.jpg): two big cream-faced dials (the
revs in hundreds on the left, the speed on the right), each with a ticked band, a black fill that follows the value, a red zone and numbers turned along
the arc; two small overlapping gauges at the top (coolant, fuel), grey turn arrows, a dark middle panel with the gear selector (P R N D, the current
one boxed in green) and an LCD with the trip and the range. Faces, bezels, ticks and fills are drawn by a shader (shaders.js CREAMDIAL); the numbers are
the bitmap font Liberation Serif turned by the "angle" of a text widget. Photo px -> cluster px: x' = (x - 115) * 1.4, y' = (y - 443) * 1.4.
Edit this and regenerate."""
import json, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'cream.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')


def X(x): return round((x - 115) * 1.4, 1)
def Y(y): return round((y - 443) * 1.4, 1)
def cell(font): return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, x, y, w, font, t, color, align='center', **kw):
    h = cell(font)
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font, 'color': color, 'align': align}
    d.update(kw)
    return d


def icon(i, name, x, y, size, color, **kw):
    d = {'id': i, 'type': 'icon', 'icon': name, 'z': 5, 'x': round(x - size / 2), 'y': round(y - size / 2), 'w': size, 'h': size, 'color': color}
    d.update(kw)
    return d


def lamp_icon(i, lamp, name, x, y, size, lit, dim):
    return {'id': i, 'type': 'lamp', 'lamp': lamp, 'icon': name, 'z': 5, 'x': round(x - size / 2), 'y': round(y - size / 2), 'w': size, 'h': size, 'color': lit, 'dim': dim}


def lamp_text(i, lamp, t, x, y, w, font, lit, dim):
    h = cell(font)
    return {'id': i, 'type': 'lamp', 'lamp': lamp, 'text': t, 'font': font, 'z': 5, 'x': round(x - w / 2), 'y': round(y - h / 2), 'w': w, 'h': h, 'align': 'center', 'color': lit, 'dim': dim}


INK = 'fg'                                  # the theme's dark ink by day, backlit amber at night (hud_themes.js cream.night)
INK_D = 'big'
GREEN = [44, 210, 70, 255]
GHOST = [64, 64, 58, 255]
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 720, 'color': 'bg'}]
START, SWEEP = -113, 226


def dial(i, cx, cy, R, signal, mn, mx, band, minors, every, red, conn):
    r = R + R * 0.075 + 2
    x0, y0 = round(cx - r), round(cy - r)
    h = min(720 - y0, round(2 * r))
    return {'id': i, 'type': 'creamdial', 'class': 'content', 'z': 2, 'x': x0, 'y': y0, 'w': round(2 * r), 'h': h, 'conn': conn, 'signal': signal, 'min': mn, 'max': mx,
            'dial': {'center': [cx, cy], 'radius': R, 'start': START, 'sweep': SWEEP, 'band': band, 'minors': minors, 'majorEvery': every, 'red': red, 'age': 1}}


R = 295                                    # the whole dial (with its bezel) stands inside the 720 px high screen
K = R / 350.0
LC, RC = (360, 720 - R * 1.075 - 6), (1560, 720 - R * 1.075 - 6)


def DY(py): return (Y(py) - Y(790)) * K        # a photo y, as the distance below the dial's centre
W.append(dial('rev_dial', LC[0], LC[1], R, 'rpm', 0, 8000, [0.50, 0.60, 0.545], 16, 2, 0.8125, 1))
W.append(dial('spd_dial', RC[0], RC[1], R, 'speed', 0, {'metric': 240, 'us': 160}, [0.50, 0.60, 0.545], 24, 2, 2, 2))
# ---- the numbers along the arc, turned with it
RN = 0.78 * R


def number(i, c, frac, t, **kw):
    a = START + SWEEP * frac
    x = c[0] + RN * math.sin(math.radians(a))
    y = c[1] - RN * math.cos(math.radians(a))
    return text(i, x, y, 84, 'cr_num', t, INK, 'center', angle=round(a, 1), vcenter=True, **kw) | {'h': 48, 'y': round(y - 24), 'x': round(x - 24), 'w': 48}


for k in range(9):
    W.append(number('rn%d' % k, LC, k / 8, str(k * 10)))
for k in range(13):
    W.append(number('sk%d' % k, RC, k / 12, str(k * 20), toggle='!units=us'))
for k in range(9):
    W.append(number('sm%d' % k, RC, k / 8, str(k * 20), toggle='units=us'))
# ---- inside the dials
for c, name, big, unit, sub in ((LC, 'ENGINE', '{{rpmH}}', 'RPM', 'X100'), (RC, 'SPEED', '{{speed}}', '{{u:speedKph}}', None)):
    n = 'rev' if c is LC else 'spd'
    W.append(text(n + '_name', c[0], c[1] + DY(727), 220, 'cr_mid', name, INK, 'center'))
    W.append(text(n + '_big', c[0], c[1] + DY(812), 260, 'cr_big', big, INK_D, 'center'))
    W.append(text(n + '_unit', c[0], c[1] + DY(901), 160, 'cr_mid', unit, INK, 'center'))
    if sub: W.append(text(n + '_sub', c[0], c[1] + DY(921), 100, 'cr_lab', sub, INK, 'center'))
# ---- the two small gauges at the top: coolant (left), fuel (right)
MR = 100
for i, cx, sig, mn, mx, st, sw, red in (('temp', X(720), 'coolant', 50, 130, 170, -160, 0.82), ('fuel', X(870), 'fuel', 0, 1, 190, 160, 2)):
    d = dial(i + '_gauge', cx, Y(548), MR, sig, mn, mx, [0.60, 0.84, 0.68], 8, 4, red, 3)
    d['dial'].update({'start': st, 'sweep': sw})
    W.append(d)
W.append(icon('therm', 'therm', X(710), Y(551), 42, INK_D))
W.append(icon('pump', 'fuel', X(906), Y(551), 40, INK_D))
for i, x, y, t in (('h', 731, 504, 'H'), ('c', 731, 597, 'C'), ('f', 871, 503, 'F'), ('e', 871, 597, 'E')):
    W.append(text('lbl_' + i, X(x), Y(y), 30, 'cr_lab', t, INK, 'center'))
# ---- the turn arrows
W.append(lamp_icon('turn_l', 'turnL', 'arrowl', X(556), Y(511), 70, [60, 210, 80, 255], [52, 52, 46, 255]))
W.append(lamp_icon('turn_r', 'turnR', 'arrowr', X(1044), Y(511), 70, [60, 210, 80, 255], [52, 52, 46, 255]))
# ---- the middle panel: gear boxes, ghost lamps, the LCD
W.append({'id': 'panel', 'type': 'boxes', 'class': 'content', 'z': 1, 'x': 780, 'y': 296, 'w': 370, 'h': 424, 'color': 'bg', 'conn': 1,
          'boxes': [{'id': 'mid_panel', 'x': round(X(681)), 'y': round(Y(663)), 'w': round(X(925) - X(681)), 'h': round(Y(940) - Y(663)), 'head': 0, 'radius': 10, 'border': 1.5}]})
for i, g in enumerate('PRND'):
    y = Y(692 + 42.3 * i)
    W.append(lamp_icon('gb_' + g, 'g' + g, 'sq', X(799), y, 62, GREEN, [58, 58, 52, 255]))
    W.append(lamp_text('gt_' + g, 'g' + g, g, X(799), y + 1, 40, 'cr_gear', GREEN, [96, 96, 88, 255]))
for i, (nm, x, y) in enumerate((('beam_a', 727, 690), ('beam_b', 727, 735))):
    W.append(lamp_icon(nm, 'lights', 'beam', X(x), Y(y), 44, GHOST, [46, 46, 42, 255]))
for i, (nm, x, y) in enumerate((('fog_a', 873, 690), ('fog_b', 873, 735))):
    W.append(lamp_icon(nm, 'lights', 'beamr', X(x), Y(y), 44, GHOST, [46, 46, 42, 255]))
LCD = {'id': 'lcd', 'type': 'fill', 'class': 'content', 'z': 2, 'x': round(X(687)), 'y': round(Y(866)), 'w': round(X(913) - X(687)), 'h': round(Y(940) - Y(866)), 'color': 'lcd'}
W.append(LCD)
W.append(text('lcd_trip', X(706), Y(910), 60, 'cr_lab', 'TRIP', [40, 40, 34, 255], 'left'))
W.append(text('lcd_odo', X(706), Y(927), 60, 'cr_lab', 'RANGE', [40, 40, 34, 255], 'left'))
W.append(text('lcd_a', X(765), Y(911), 20, 'cr_lab', 'A', [40, 40, 34, 255], 'center'))
W.append(text('lcd_v1', X(900), Y(886), 190, 'cr_lcd', '{{tripDist}}', [34, 34, 28, 255], 'right'))
W.append(text('lcd_v2', X(905), Y(921), 190, 'cr_lcd', '{{range}}', [34, 34, 28, 255], 'right'))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_cover'):
        W.append(w)

LAY = {'schemaVersion': 2, 'name': 'Cream', 'theme': 'cream', 'packWaste': 1.0,
       '_about': "Cream cluster, generated by tools/gen_cream.py (edit that and regenerate), after a retro concept cluster (10.jpg): two big cream-faced dials (the revs in hundreds, the speed) with a ticked band, a black fill that follows the value, a red zone and numbers turned along the arc, two small gauges (coolant, fuel), grey turn arrows, a middle panel with the gear selector (the current gear boxed in green) and an LCD with the trip and the range. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('cream.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
