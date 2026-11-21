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


W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg'}]
HOLE = {'hole': [668, 128, 628, 436], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 56}
# the grey panels (one layer: a polygon each) and, over them, the middle display and the red glows (a second layer)
PANEL = [44, 46, 50, 255]
W.append({'id': 'panels', 'type': 'artmask', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 1, 'art': 'livehyb_panel', 'color': PANEL})
W.append(dict({'id': 'middle', 'type': 'gpoly', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'conn': 2,
               'polys': [poly(CENTER, 0, 0, [10, 12, 16, 1.0], [24, 26, 32, 1.0], 8),
                         poly([(548, 736), (720, 736), (700, 788), (568, 788)], 0, 0, [150, 20, 24, 0.0], [235, 40, 44, 0.85], 26),
                         poly([(1400, 730), (1590, 730), (1560, 794), (1420, 794)], 0, 0, [150, 20, 24, 0.0], [235, 40, 44, 0.85], 26)], 'lines': []}, **HOLE))
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
W.append(arc('power_bar', L(1468, 668), L(1534, 575), L(1447, 478), 36, [92, 96, 104, 255], 'powerPct', 0, 100, conn=2, z=2, color='accent'))
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
W.append(arc('batt_arc', L(1702, 806), L(1802, 758), L(1790, 674), 24, [60, 64, 70, 255], 'hvSoc', 0, 100, conn=2, z=2, color='accent'))
W.append(text('batt_pct', (1748, 758), 90, 'z_unit', '{{hvSoc}}%', WHITE, 'center'))
W.append(text('batt_100', (1766, 682), 50, 'm_tyre', '100', DIM, 'center'))
W.append(text('batt_0', (1698, 797), 30, 'm_tyre', '0', DIM, 'center'))
W.append(icon('batt_icon', 'battery', (1795, 819), 44, WHITE))
W.append(arc('fuel_arc', L(410, 826), L(318, 775), L(345, 700), 24, [60, 64, 70, 255], 'fuel', 0, 1, conn=2, z=2, color='fg'))
W.append(text('fuel_1', (334, 692), 30, 'm_tyre', '1', DIM, 'center'))
W.append(text('fuel_half', (368, 757), 60, 'm_tyre', '1/2', DIM, 'center'))
W.append(text('fuel_0', (418, 802), 30, 'm_tyre', '0', DIM, 'center'))
W.append(icon('pump', 'fuel', (312, 808), 30, DIM))
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
