#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/arcd.json (the Arc Digital theme), after a photo of a digital sports-car cluster
(13.png): a half-circle bar of thin slats (one every 100 rpm, lit up to the revs: green to 6000, yellow to orange, a red block at the
end) with white tick marks and the numbers 0..9 inside it, a seven-segment speed in a dark window (mph / km/h beside it), a small
window of seven-segment digits under it (here the range and the trip), the coolant bar with C / H on the left and the fuel bar with
E / F on the right, the warning icons (dim, as the unlit ghosts of the real ones), ABS, the two button pills and the small print.
The photo is scaled to the cluster's height (1.528) and centred. No Waze window. Edit this and regenerate."""
import json, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'arcd.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')    # its bottom row (strip_*) is the shared one
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')
K = 660.0 / 432.0


def X(px): return round(960 + K * (px - 504), 1)
def Y(py): return round(K * py, 1)
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


def meter(i, x, y, w, h, sig, mn, mx, segs, colors, at, **kw):
    d = {'id': i, 'type': 'meter', 'class': 'content', 'z': 2, 'x': round(x), 'y': round(y), 'w': round(w), 'h': round(h), 'signal': sig, 'min': mn, 'max': mx,
         'segments': segs, 'gap': 3, 'colors': colors, 'at': at}
    d.update(kw)
    return d


def line(i, x, y, w, h, color, z=2):
    return {'id': i, 'type': 'fill', 'class': 'content', 'z': z, 'x': round(x), 'y': round(y), 'w': round(w), 'h': round(h), 'color': color}


WHITE = [236, 238, 240, 255]
GHOST = [66, 68, 66, 255]
DIM = [150, 154, 152, 255]
RED_D, ORA_D, GRN_D = [168, 30, 24, 255], [176, 104, 20, 255], [34, 128, 52, 255]

W = []
# ---- the panels: the speed window, the small-digits window, the button pills (one layer; black everywhere else covers BMW's gauges)
panels = [
    {'id': 'speed_win', 'x': X(432), 'y': Y(178), 'w': round(K * 176), 'h': round(K * 69), 'head': 0, 'radius': 10, 'border': 1},
    {'id': 'odo_win', 'x': X(432), 'y': Y(253), 'w': round(K * 180), 'h': round(K * 39), 'head': 0, 'radius': 9, 'border': 1},
    {'id': 'pill_l', 'x': X(72), 'y': Y(298), 'w': round(K * 105), 'h': round(K * 44), 'head': 0, 'radius': 34, 'border': 1},
    {'id': 'pill_r', 'x': X(870), 'y': Y(303), 'w': round(K * 100), 'h': round(K * 44), 'head': 0, 'radius': 34, 'border': 1},
]
W.append({'id': 'frame', 'type': 'boxes', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg', 'boxes': panels})
# ---- the rev arc, its slats, ticks and zones (shaders.js SEGARC)
CX, CY = X(517), Y(632)
W.append({'id': 'tach', 'type': 'segarc', 'class': 'content', 'z': 2, 'x': 470, 'y': 135, 'w': 1020, 'h': 320, 'conn': 1,
          'center': [CX, CY], 'radii': [round(K * 501.5, 1), round(K * 530.5, 1), round(K * 488, 1), round(K * 499, 1)], 'tick': [8, 4.5, 22],
          'zones': [6.0, 8.1, 9.15, 9.55], 'angles': [-32.5, -28.7, -22.9, -17.1, -11.3, -5.4, 1.0, 9.1, 18.8, 30.4, 43.0]})
# the numbers 0..9 inside the ticks (positions measured in the photo)
NUM = [(265, 219), (294, 204), (335, 187), (381, 173), (426, 162), (473, 156), (525, 155), (590, 160), (665, 178), (754, 213)]
for n, (px, py) in enumerate(NUM):
    W.append(text('n%d' % n, X(px), Y(py), 60, 'x_num', str(n), WHITE, 'center'))
W.append(text('x1000', X(278), Y(223), 230, 'x_lab', 'x1000r/min', WHITE, 'left'))
# ---- the speed: unlit ghost 8s under the lit digits, the unit beside it
SX = X(595)
W.append(text('speed_ghost', SX, Y(213), 250, 'x_speed', '888', GHOST, 'right'))
W.append(text('speed', SX, Y(213), 250, 'x_speed', '{{speed}}', WHITE, 'right'))
W.append(text('mph_on', X(618), Y(225), 80, 'e_unit', 'mph', WHITE, 'left', toggle='units=us'))
W.append(text('mph_off', X(618), Y(225), 80, 'e_unit', 'mph', [96, 100, 98, 255], 'left', toggle='!units=us'))
W.append(text('kmh_on', X(618), Y(244), 90, 'e_unit', 'km/h', WHITE, 'left', toggle='!units=us'))
W.append(text('kmh_off', X(618), Y(244), 90, 'e_unit', 'km/h', [40, 74, 44, 255], 'left', toggle='units=us'))
# ---- the small digits: the range and the trip
W.append(text('odo_ghost', X(526), Y(276), 190, 'x_odo', '888888', GHOST, 'right', spacing=-3))
W.append(text('odo', X(526), Y(276), 190, 'x_odo', '{{range}}', WHITE, 'right', spacing=-3))
W.append(text('trip_ghost', X(608), Y(276), 130, 'x_odo', '888.8', GHOST, 'right', spacing=-3))
W.append(text('trip', X(608), Y(276), 130, 'x_odo', '{{tripDist}}', WHITE, 'right', spacing=-3))
W.append(text('trip_lbl', X(608), Y(262), 130, 'x_lab', 'TRIP', WHITE, 'right'))
# ---- the coolant bar (C .. H) on the left, the fuel bar (E .. F) on the right
W.append(icon('therm', 'therm', X(207), Y(215), 30, WHITE))
W.append(text('c_lbl', X(170), Y(236), 40, 'x_cf', 'C', WHITE, 'center'))
W.append(text('h_lbl', X(318), Y(237), 40, 'x_cf', 'H', WHITE, 'center'))
W.append(meter('temp', X(185), Y(232), K * 115, K * 11, 'coolant', 40, 130, 8, [[206, 208, 206, 255], [150, 24, 20, 255], [150, 24, 20, 255]], [0.72, 1.0]))
W.append(line('temp_line', X(185), Y(250), K * 115, 2, WHITE))
W.append(icon('pump', 'fuel', X(843), Y(221), 32, WHITE))
W.append(text('e_lbl', X(727), Y(242), 40, 'x_cf', 'E', WHITE, 'center'))
W.append(text('f_lbl', X(870), Y(242), 40, 'x_cf', 'F', WHITE, 'center'))
W.append(meter('fuel', X(750), Y(235), K * 107, K * 12, 'fuel', 0, 1, 20, [[210, 40, 30, 255], [206, 208, 206, 255], [206, 208, 206, 255]], [0.06, 1.0], conn=2))
W.append(line('fuel_line', X(750), Y(252), K * 107, 2, WHITE))
W.append(line('fuel_tick', X(803) - 1, Y(252), 2, K * 7, WHITE))
# ---- ABS, the warning icons (dim, like the unlit ghosts), the buttons, the small print
W.append(text('abs', X(167), Y(275), 70, 'x_lab', 'ABS', ORA_D, 'center'))
W.append(text('brake', X(211), Y(328), 90, 'x_lab', 'BRAKE', RED_D, 'center'))
W.append(icon('battery', 'battery', X(264), Y(328), 40, RED_D))
W.append(icon('oil', 'oilcan', X(318), Y(328), 40, RED_D))
W.append(icon('engine', 'engine', X(371), Y(328), 42, ORA_D))
W.append(icon('key', 'key', X(417), Y(328), 40, GRN_D))
W.append(text('maint1', X(468), Y(323), 100, 'x_lab', 'MAINT', ORA_D, 'center'))
W.append(text('maint2', X(468), Y(334), 100, 'x_lab', "REQ'D", ORA_D, 'center'))
W.append(text('eps', X(572), Y(330), 70, 'x_lab', 'EPS', ORA_D, 'center'))
W.append(text('minus', X(91), Y(318), 40, 'x_lab', '-', DIM, 'center'))
W.append(text('plus', X(147), Y(318), 40, 'x_lab', '+', DIM, 'center'))
W.append(text('sel', X(892), Y(325), 70, 'x_lab', 'SEL', DIM, 'center'))
W.append(text('trip_btn', X(947), Y(325), 70, 'x_lab', 'TRIP', DIM, 'center'))
W.append(text('push', X(190), Y(355), 200, 'x_lab', 'PUSH CANCEL', DIM, 'left'))
W.append(text('mphkmh', X(793), Y(360), 110, 'x_lab', 'mph-km/h', [100, 104, 102, 255], 'left'))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_'):
        W.append(w)

L = {'schemaVersion': 2, 'name': 'Arc Digital', 'theme': 'arcd', 'packWaste': 3,
     '_about': "Arc Digital cluster, generated by tools/gen_arcd.py (edit that and regenerate), after a photo of a digital sports-car cluster (13.png): a half-circle bar of thin slats, one for every 100 rpm, lit up to the revs (green to 6000, yellow to orange, a red block at the end) with white tick marks and the numbers 0 to 9 inside it, a seven-segment speed in a dark window with mph / km/h beside it, a small window of seven-segment digits under it (the range and the trip), the coolant bar (C to H) on the left and the fuel bar (E to F) on the right, the warning icons as dim ghosts, ABS, the two button pills and the small print. No map window. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('arcd.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
