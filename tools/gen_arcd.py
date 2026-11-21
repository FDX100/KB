#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/arcd.json (the Arc Digital theme), after a photo of a digital sports-car cluster
(13.png): a half-circle bar of thin slats (one every 100 rpm, lit up to the revs: green to 6000, yellow to orange, a red block at the
end) with white tick marks and the numbers 0..9 inside it, a seven-segment speed in a dark window (mph / km/h beside it), a small
window of seven-segment digits under it (here the range and the trip), the coolant bar with C / H on the left and the fuel bar with
E / F on the right, the warning icons (dim, as the unlit ghosts of the real ones), ABS, the two button pills and the small print.
The rev arc and its numbers are the photo scaled 2.3 times and centred, so the arc runs nearly the whole width of the cluster. The rest is laid out afresh with room between the parts: a big speed window under the arc, the small digits under it, the coolant and fuel gauges low on the two sides, the ABS lamp (lights on hard braking, hud.js _lamp) top left. The button pills, the small print and the row of warning lamps of the photo are left out. No Waze window. Edit this and regenerate."""
import json, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'arcd.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')    # its bottom row (strip_*) is the shared one
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')
K = 2.3
Y0 = 40.0


def X(px): return round(960 + K * (px - 504), 1)
def Y(py): return round(Y0 + K * (py - 102), 1)
def cell(font): return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, cx, cy, w, font, t, color='fg', align='center', **kw):
    """A text centred on (cx, cy) (layout px); align left / right measure from cx."""
    h = cell(font)
    x0 = cx - w / 2 if align == 'center' else (cx - w if align == 'right' else cx)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(cy - h / 2), 'w': w, 'h': h, 'text': t, 'font': font, 'color': color, 'align': align}
    d.update(kw)
    return d


def icon(i, name, cx, cy, size, color):
    return {'id': i, 'type': 'icon', 'icon': name, 'z': 5, 'x': round(cx - size / 2), 'y': round(cy - size / 2), 'w': size, 'h': size, 'color': color}


def lamp_icon(i, lamp, name, cx, cy, size, lit, dim):
    return {'id': i, 'type': 'lamp', 'lamp': lamp, 'icon': name, 'z': 5, 'x': round(cx - size / 2), 'y': round(cy - size / 2), 'w': size, 'h': size, 'color': lit, 'dim': dim}


def lamp_text(i, lamp, t, cx, cy, w, font, lit, dim):
    h = cell(font)
    return {'id': i, 'type': 'lamp', 'lamp': lamp, 'text': t, 'font': font, 'z': 5, 'x': round(cx - w / 2), 'y': round(cy - h / 2), 'w': w, 'h': h, 'align': 'center', 'color': lit, 'dim': dim}


def meter(i, x, y, w, h, sig, mn, mx, segs, colors, at, **kw):
    d = {'id': i, 'type': 'meter', 'class': 'content', 'z': 2, 'x': round(x), 'y': round(y), 'w': round(w), 'h': round(h), 'signal': sig, 'min': mn, 'max': mx,
         'segments': segs, 'gap': 4, 'colors': colors, 'at': at}
    d.update(kw)
    return d


def line(i, x, y, w, h, color, z=2):
    return {'id': i, 'type': 'fill', 'class': 'content', 'z': z, 'x': round(x), 'y': round(y), 'w': round(w), 'h': round(h), 'color': color}


WHITE = [236, 238, 240, 255]
DIMTXT = [150, 154, 152, 255]
GHOST = [66, 68, 66, 255]
ORA_L, ORA_D = [255, 156, 30, 255], [104, 66, 16, 255]            # a lamp lit and unlit (a ghost)

W = []
# ---- the panels: the speed window and the small-digits window (one layer; black everywhere else covers BMW's gauges)
SW_X, SW_Y, SW_W, SW_H = 730, 252, 460, 186              # the speed window
OD_X, OD_Y, OD_W, OD_H = 745, 466, 430, 96               # the small-digits window
panels = [
    {'id': 'speed_win', 'x': SW_X, 'y': SW_Y, 'w': SW_W, 'h': SW_H, 'head': 0, 'radius': 18, 'border': 2},
    {'id': 'odo_win', 'x': OD_X, 'y': OD_Y, 'w': OD_W, 'h': OD_H, 'head': 0, 'radius': 14, 'border': 2},
]
W.append({'id': 'frame', 'type': 'boxes', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg', 'boxes': panels})
# ---- the rev arc, its slats, ticks and zones (shaders.js SEGARC)
CX, CY = X(517), Y(632)
W.append({'id': 'tach', 'type': 'segarc', 'class': 'content', 'z': 2, 'x': 230, 'y': 24, 'w': 1540, 'h': 340, 'conn': 1,
          'center': [CX, CY], 'radii': [round(K * 501.5, 1), round(K * 530.5, 1), round(K * 488, 1), round(K * 499, 1)], 'tick': [12, 7, 34],
          'zones': [6.0, 8.1, 9.15, 9.55], 'angles': [-32.5, -28.7, -22.9, -17.1, -11.3, -5.4, 1.0, 9.1, 18.8, 30.4, 43.0]})
# the numbers 0..9 inside the ticks (positions measured in the photo)
NUM = [(265, 219), (294, 204), (335, 187), (381, 173), (426, 162), (473, 156), (525, 155), (590, 160), (665, 178), (754, 213)]
for n, (px, py) in enumerate(NUM):
    W.append(text('n%d' % n, X(px), Y(py), 90, 'x_num', str(n), WHITE, 'center'))
W.append(text('x1000', X(278) + 10, Y(223) + 34, 340, 'x_lab', 'x1000r/min', WHITE, 'left'))
# ---- the speed: unlit ghost 8s under the lit digits, the unit beside it
SYC = SW_Y + SW_H / 2
SXR = SW_X + SW_W - 26                                         # the digits end here
W.append(text('speed_ghost', SXR, SYC, 420, 'x_speed', '888', GHOST, 'right'))
W.append(text('speed', SXR, SYC, 420, 'x_speed', '{{speed}}', WHITE, 'right'))
UX = SW_X + SW_W + 28
W.append(text('mph_on', UX, SYC - 26, 140, 'x_unit', 'mph', WHITE, 'left', toggle='units=us'))
W.append(text('mph_off', UX, SYC - 26, 140, 'x_unit', 'mph', [96, 100, 98, 255], 'left', toggle='!units=us'))
W.append(text('kmh_on', UX, SYC + 28, 150, 'x_unit', 'km/h', WHITE, 'left', toggle='!units=us'))
W.append(text('kmh_off', UX, SYC + 28, 150, 'x_unit', 'km/h', [40, 74, 44, 255], 'left', toggle='units=us'))
# ---- the small digits: the range on the left, the trip on the right
OYC = OD_Y + OD_H / 2 + 12
W.append(text('odo_ghost', OD_X + 250, OYC, 260, 'x_odo', '888888', GHOST, 'right', spacing=-5))
W.append(text('odo', OD_X + 250, OYC, 260, 'x_odo', '{{range}}', WHITE, 'right', spacing=-5))
W.append(text('trip_ghost', OD_X + OD_W - 22, OYC, 180, 'x_odo', '888.8', GHOST, 'right', spacing=-5))
W.append(text('trip', OD_X + OD_W - 22, OYC, 180, 'x_odo', '{{tripDist}}', WHITE, 'right', spacing=-5))
W.append(text('rng_lbl', OD_X + 26, OD_Y + 22, 120, 'x_lab', 'RANGE', DIMTXT, 'left'))
W.append(text('trip_lbl', OD_X + OD_W - 22, OD_Y + 22, 120, 'x_lab', 'TRIP', DIMTXT, 'right'))
# ---- the coolant bar (C .. H) low on the left, the fuel bar (E .. F) low on the right
GY, GW, GH = 548, 330, 32
LX = 190
W.append(icon('therm', 'therm', LX + 16, GY - 52, 50, WHITE))
W.append(text('c_lbl', LX - 46, GY + GH / 2, 60, 'x_cf', 'C', WHITE, 'center'))
W.append(meter('temp', LX, GY, GW, GH, 'coolant', 40, 130, 9, [[206, 208, 206, 255], [150, 24, 20, 255], [150, 24, 20, 255]], [0.72, 1.0]))
W.append(text('h_lbl', LX + GW + 46, GY + GH / 2, 60, 'x_cf', 'H', WHITE, 'center'))
W.append(line('temp_line', LX, GY + GH + 14, GW, 3, WHITE))
RX = 1920 - 190 - GW
W.append(icon('pump', 'fuel', RX + GW - 16, GY - 52, 54, WHITE))
W.append(text('e_lbl', RX - 46, GY + GH / 2, 60, 'x_cf', 'E', WHITE, 'center'))
W.append(meter('fuel', RX, GY, GW, GH, 'fuel', 0, 1, 20, [[210, 40, 30, 255], [206, 208, 206, 255], [206, 208, 206, 255]], [0.06, 1.0], conn=2))
W.append(text('f_lbl', RX + GW + 46, GY + GH / 2, 60, 'x_cf', 'F', WHITE, 'center'))
W.append(line('fuel_line', RX, GY + GH + 14, GW, 3, WHITE))
W.append(line('fuel_tick', RX + GW / 2 - 1.5, GY + GH + 14, 3, 18, WHITE))
# ---- the ABS lamp: a dim ghost until the car brakes hard (hud.js _lamp)
W.append(lamp_text('abs', 'abs', 'ABS', 120, 392, 110, 'x_lab', ORA_L, ORA_D))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_'):
        W.append(w)

L = {'schemaVersion': 2, 'name': 'Arc Digital', 'theme': 'arcd', 'packWaste': 3,
     '_about': "Arc Digital cluster, generated by tools/gen_arcd.py (edit that and regenerate), after a photo of a digital sports-car cluster (13.png), full screen: a half-circle bar of thin slats, one for every 100 rpm, lit up to the revs (green to 6000, yellow to orange, a red block at the end) with white tick marks and the numbers 0 to 9 inside it; under it a big seven-segment speed in a dark window with mph / km/h beside it, and a window of seven-segment digits (the range and the trip); the coolant bar (C to H) low on the left and the fuel bar (E to F) low on the right, and the ABS lamp that lights on hard braking. No map window. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('arcd.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
