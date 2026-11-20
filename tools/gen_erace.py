#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/erace.json (the E-Race theme): a race dash for plug-in and mild hybrids and EVs.
Built like the GT3 theme (framed boxes, a bar along the top, a huge gear), which is known to run on a car, with e-drive readouts:
a power bar and a regen bar across the top, boxes for the speed, the battery, the drive mode, the power, the regen and the range,
and the gear in the middle. While the Waze map shows, the middle box gives way to a map window. Edit this and regenerate."""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'erace.json')
MIN = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'apex.json')     # its bottom row (strip_*) is the shared one


def text(i, x, y, w, h, t, font, color=None, align=None, **kw):
    d = {'id': i, 'type': 'text', 'z': 5, 'x': x, 'y': y, 'w': w, 'h': h, 'text': t, 'font': font}
    if color: d['color'] = color
    if align: d['align'] = align
    d.update(kw)
    return d


def meter(i, x, y, w, h, sig, mn, mx, segs, colors, at, **kw):
    d = {'id': i, 'type': 'meter', 'class': 'content', 'z': 2, 'x': x, 'y': y, 'w': w, 'h': h, 'signal': sig, 'min': mn, 'max': mx,
         'segments': segs, 'gap': 3, 'colors': colors, 'at': at}
    d.update(kw)
    return d


LX, RX, BW = 120, 1520, 280              # the side boxes
boxes = [
    {'id': 'speed_box', 'x': LX, 'y': 206, 'w': BW, 'h': 190, 'head': 36, 'radius': 4},
    {'id': 'soc_box', 'x': LX, 'y': 410, 'w': BW, 'h': 116, 'head': 36, 'radius': 4},
    {'id': 'mode_box', 'x': LX, 'y': 540, 'w': BW, 'h': 116, 'head': 36, 'radius': 4},
    {'id': 'pow_box', 'x': RX, 'y': 206, 'w': BW, 'h': 190, 'head': 36, 'radius': 4, 'headColor': 'accent'},
    {'id': 'regen_box', 'x': RX, 'y': 410, 'w': BW, 'h': 116, 'head': 36, 'radius': 4},
    {'id': 'range_box', 'x': RX, 'y': 540, 'w': BW, 'h': 116, 'head': 36, 'radius': 4},
    {'id': 'gear_box', 'x': 540, 'y': 206, 'w': 840, 'h': 450, 'head': 36, 'radius': 4, 'toggle': '!mapUp'},
]
W = [
    {'id': 'frame', 'type': 'boxes', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
     'hole': [424, 130, 1072, 470], 'holeWhen': 'mapUp', 'holeInset': 6, 'holeRadius': 28, 'boxes': boxes},
    # across the top: the electric power (lime, amber near the limit, red at it) and, under it, the regen
    meter('power_bar', 440, 56, 1040, 34, 'powerPct', 0, 100, 52, ['accent', 'fg', 'hot'], [0.62, 0.88]),
    meter('regen_bar', 440, 104, 1040, 14, 'recup', 0, 100, 52, ['green', 'green', 'green'], [1, 1], conn=2),
    text('power_label', 300, 58, 120, 27, 'POWER', 'head', 'dim', 'right'),
    text('regen_label', 300, 100, 120, 27, 'REGEN', 'head', 'dim', 'right'),
    text('power_pct', 1490, 76, 110, 36, '{{powerPct}}%', 'head', 'fg', 'left'),
    text('regen_pct', 1490, 114, 110, 36, '{{recup}}%', 'head', 'green', 'left'),
    # left boxes: speed, battery, drive mode
    text('speed_head', 136, 211, 250, 27, '{{slotHead:1}} {{slotUnit:1}}', 'head', 'ink'),
    text('speed', 128, 258, 206, 93, '{{slot:1}}', 'big', align='right', slot='1', fit=['value', 'small']),
    text('speed_unit', 340, 312, 60, 37, '{{slotUnit:1}}', 'unit', 'dim', fit=['head']),
    text('soc_head', 136, 415, 250, 27, '{{slotHead:2}} {{slotUnit:2}}', 'head', 'ink'),
    text('soc', 132, 448, 256, 70, '{{slot:2}}', 'value', slot='2', fit=['small']),
    text('mode_head', 136, 545, 250, 27, 'DRIVE MODE', 'head', 'ink'),
    text('mode', 132, 579, 256, 70, '{{mode}}', 'value', align='center'),
    # right boxes: power, regen, range
    text('pow_head', 1536, 211, 250, 27, '{{slotHead:3}} {{slotUnit:3}}', 'head', 'ink'),
    text('pow', 1528, 258, 206, 93, '{{slot:3}}', 'big', align='right', slot='3', fit=['value', 'small']),
    text('pow_unit', 1740, 312, 60, 37, '{{slotUnit:3}}', 'unit', 'dim', fit=['head']),
    text('regen_head', 1536, 415, 250, 27, '{{slotHead:4}} {{slotUnit:4}}', 'head', 'ink'),
    text('regen', 1532, 448, 256, 70, '{{slot:4}}', 'value', slot='4', fit=['small']),
    text('range_head', 1536, 545, 250, 27, '{{slotHead:5}} {{slotUnit:5}}', 'head', 'ink'),
    text('range', 1532, 579, 256, 70, '{{slot:5}}', 'value', slot='5', fit=['small']),
    # the middle box: the gear, the mode, the two temperatures
    text('gear_head', 556, 211, 300, 27, 'GEAR', 'head', 'ink', toggle='!mapUp'),
    text('gear_mode', 1066, 211, 300, 27, '{{mode}}', 'head', 'ink', 'right', toggle='!mapUp'),
    text('gear', 760, 282, 400, 244, '{{gearnum}}', 'gear', align='center', hotWhen='now', toggle='!mapUp'),
    text('water_label', 592, 606, 140, 27, '{{slotHeadU:6}}', 'head', 'dim', 'right', toggle='!mapUp'),
    text('water', 742, 595, 140, 45, '{{slot:6}}{{slotSuffix:6}}', 'small', slot='6', fit=['unit'], toggle='!mapUp'),
    text('oil_label', 1086, 606, 140, 27, '{{slotHeadU:7}}', 'head', 'dim', 'right', toggle='!mapUp'),
    text('oil', 1230, 595, 134, 45, '{{slot:7}}{{slotSuffix:7}}', 'small', 'fg', 'right', slot='7', fit=['unit'], toggle='!mapUp'),
    # with the map: the battery as a thin bar under it
    text('mbatt_label', 800, 604, 140, 27, 'BATTERY', 'head', 'dim', 'left', toggle='mapUp'),
    meter('mbatt', 934, 630, 186, 4, 'hvSoc', 0, 100, 40, ['hot', 'accent', 'accent'], [0.15, 1], gap=0, toggle='mapUp'),
    text('badge', 136, 150, 270, 34, '{{badge}}', 'badge', 'dim'),
    # the bottom row (clock, range, outside temperature) as Minimal draws it
]
for w in json.load(open(MIN))['widgets']:
    if w['id'].startswith('strip_'):
        W.append(w)

L = {'schemaVersion': 2, 'name': 'E-Race', 'packWaste': 3, 'theme': 'erace',
     'slots': [{'id': '1', 'where': 'left box, top', 'default': 'speed'}, {'id': '2', 'where': 'left box, middle', 'default': 'hvSoc'},
               {'id': '3', 'where': 'right box, top', 'default': 'powerPct'}, {'id': '4', 'where': 'right box, middle', 'default': 'recup'},
               {'id': '5', 'where': 'right box, bottom', 'default': 'range'}, {'id': '6', 'where': 'centre, left', 'default': 'coolant'},
               {'id': '7', 'where': 'centre, right', 'default': 'oil'}],
     '_about': "E-Race cluster, generated by tools/gen_erace.py (edit that and regenerate): a race dash for plug-in and mild hybrids and EVs, built like the GT3 theme (framed boxes, a bar along the top, a huge gear in the middle). A power bar (lime, amber, red) and a regen bar (green, an estimate) run across the top; the boxes show the speed, the battery, the drive mode, the power %, the regen % and the range. While the Waze map shows inside the theme the middle box gives way to a map window and the battery shows as a thin bar under it. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('erace.json:', len(W), 'widgets')
