#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/dewdrop.json (the Dewdrop theme), after a concept video of a luxury electric car's cluster (1.mp4):
rings of water drops round a thin speed (the outer ring lights up with the revs), a slanted glass panel on the right, a thin arc round the drops that
fills with the power, the drive mode and gear at the top, the weather and clock top right, the range on the left (where the video shows the next turn,
which the car does not send for Waze), the music that is playing (title, artist, progress) at the lower left, the power in kW and the revs in thousands
on the right. Every shape is drawn by shaders (shaders.js DEWDROPS, SLANT, arc); only text is bitmap. Edit this and regenerate."""
import json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'dewdrop.json')
STRIP = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')


def X(x): return round(960 + (x - 800) * 1.02, 1)           # the video's 1600 px width onto the cluster's 1920 (a little smaller: the hood hides the corners)
def Y(y): return round((y - 118) * 1.15 + 55, 1)            # the video's screen top is at y 118


def cell(font): return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, x, y, w, font, t, color, align='left', **kw):
    h = cell(font)
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font, 'color': color, 'align': align}
    d.update(kw)
    return d


def icon(i, name, x, y, size, color, **kw):
    d = {'id': i, 'type': 'icon', 'icon': name, 'z': 5, 'x': round(x - size / 2), 'y': round(y - size / 2), 'w': size, 'h': size, 'color': color}
    d.update(kw)
    return d


WHITE = [244, 246, 250, 255]
GREY = [128, 134, 148, 255]
DIM = [88, 94, 108, 255]
BLUE = [168, 205, 255, 255]
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg'}]
# ---- the slanted glass panel on the right
W.append({'id': 'glass', 'type': 'slant', 'class': 'content', 'z': 1, 'x': 700, 'y': 0, 'w': 1220, 'h': 660, 'conn': 1,
          'line': [X(685), Y(122), X(1000) + 0.0, Y(440)], 'fill': [0.075, 0.082, 0.1, 0.96], 'edge': [0.55, 1.6]})
# ---- the rings of drops, the thin arc round them (the power)
CX, CY = X(770), Y(415)
W.append({'id': 'drops', 'type': 'dewdrops', 'class': 'content', 'z': 2, 'x': round(CX - 260), 'y': round(CY - 260), 'w': 520, 'h': 520, 'conn': 2, 'rpmMax': 8000, 'fps': 5,
          'drops': {'center': [CX, CY], 'rings': [[218, 26, 15, 8], [170, 21, 23, 8], [126, 15, 25, 5], [236, 44, 4, 3]]}})
R_ARC = 298
AS = round(2 * (R_ARC + 14))
W.append({'id': 'power_arc', 'type': 'arc', 'class': 'content', 'z': 2, 'x': round(CX - AS / 2), 'y': round(CY - AS / 2), 'w': AS, 'h': AS, 'conn': 3, 'signal': 'powerPct', 'min': 0, 'max': 100,
          'width': 3, 'color': BLUE, 'trackColor': [92, 100, 118, 255], 'start': 100, 'sweep': -62})
# ---- the speed
W.append(text('speed', CX, CY - 4, 220, 'bd_speed', '{{speed}}', WHITE, 'center'))
W.append(text('speed_u', CX, CY + 66, 100, 'bd_lab', '{{u:speed}}', GREY, 'center'))
# ---- the top: gear and drive mode, weather and clock
W.append(text('gear', X(777), Y(158), 90, 'bd_gear', '{{gear}}', WHITE, 'center'))
W.append(text('mode', X(948) + 20, Y(165), 200, 'bd_lab', '{{mode}}', GREY, 'left'))
W.append(icon('sun', 'sun', X(1362) - 40, Y(170) + 14, 24, [255, 198, 70, 255]))
W.append(icon('cloud', 'cloud', X(1349) - 40, Y(178) + 14, 34, [214, 222, 236, 255]))
W.append(text('temp', X(1388) - 40, Y(174) + 14, 90, 'bd_sub', '{{ambient}}{{u:temp}}', WHITE, 'left'))
W.append(text('clock', X(1470) - 40, Y(174) + 14, 170, 'bd_sub', '{{time}} {{ampm}}', WHITE, 'left'))
# ---- the left: the range (where the video shows the next turn), the music
W.append(icon('range_icon', 'fuel', X(30), Y(188), 36, WHITE))
W.append(text('range', X(57), Y(190), 200, 'bd_num', '{{range}}{{u:distLc}}', WHITE, 'left'))
W.append(text('range_l', X(57), Y(228), 260, 'bd_sub', 'Range on this tank', DIM, 'left'))
MX, MY = X(62), Y(445)
W.append({'id': 'disc', 'type': 'boxes', 'class': 'content', 'z': 2, 'x': round(MX - 60), 'y': round(MY - 60), 'w': 120, 'h': 120, 'conn': 3, 'color': 'bg',
          'boxes': [{'id': 'disc_b', 'x': round(MX - 52), 'y': round(MY - 52), 'w': 104, 'h': 104, 'head': 0, 'radius': 52, 'border': 1.5}]})
W.append({'id': 'music_ring', 'type': 'arc', 'class': 'content', 'z': 3, 'x': round(MX - 80), 'y': round(MY - 80), 'w': 160, 'h': 160, 'conn': 3, 'signal': 'mediaPct', 'min': 0, 'max': 100,
          'width': 3, 'color': WHITE, 'trackColor': [40, 44, 54, 255], 'start': 0, 'sweep': 359})
W.append(icon('music_note', 'note', MX, MY, 52, WHITE))
W.append(text('title', X(158), Y(430), 330, 'bd_title', '{{mediaTitle}}', WHITE, 'left', showWhen='media'))
W.append(text('artist', X(158), Y(466), 330, 'bd_sub', '{{mediaArtist}}', DIM, 'left', showWhen='media'))
W.append(text('nomusic', X(158), Y(448), 330, 'bd_sub', 'No music playing', DIM, 'left', showWhen='!media'))
# ---- the right: the power and the revs
W.append(text('kw', X(1090), Y(418), 150, 'bd_num', '{{powerKw}}', WHITE, 'left'))
W.append(text('kw_l', X(1090), Y(455), 100, 'bd_lab', 'KW', GREY, 'left'))
W.append(text('rpm', X(1540) + 10, Y(412), 90, 'bd_rpm', '{{rpmK}}', WHITE, 'right'))
W.append(text('rpm_l', X(1560) + 10, Y(472), 140, 'bd_lab', 'XK RPM', GREY, 'right'))
for w in json.load(open(STRIP))['widgets']:
    if str(w['id']).startswith('strip_'):
        W.append(w)

LAY = {'schemaVersion': 2, 'name': 'Dewdrop', 'theme': 'dewdrop', 'packWaste': 3,
       '_about': "Dewdrop cluster, generated by tools/gen_dewdrop.py (edit that and regenerate), after a concept video of a luxury electric car's cluster (1.mp4): rings of water drops round a thin speed whose outer ring lights up with the revs, a slanted glass panel on the right, a thin arc that fills with the power, drive mode and gear at the top, weather and clock top right, the range on the left (the video's next turn: the car does not send turns for Waze), the music that is playing (title, artist, progress) at the lower left, power in kW and the revs in thousands on the right. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
       'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(LAY, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('dewdrop.json:', len(W), 'widgets')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badge_spot; badge_spot.apply(OUT)
