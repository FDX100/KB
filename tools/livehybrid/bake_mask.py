#!/usr/bin/env python3
"""Bakes the white line art of the hybrid Live Cockpit photo (3.jpeg) into the R8 mask the theme draws: the outlines of the two
chevrons with their ticks and leader lines, the power meter's outline, the battery and fuel brackets, the lines under the middle.
The photo's white pixels (all three channels high) are kept, the numbers, texts and icons (boxes listed below: the theme draws
those itself, live) and the map's road lines in the middle are blanked, and the picture is placed on the cluster's 1920 x 660
(photo px -> layout px: x' = 960 + (x - 1060) * S, y' = (y - 322) * S). Writes hud/art/livehyb.json { w, h, z } (z: base64 of the
deflated R8 rows) and a preview PNG next to it in tools/livehybrid/."""
import base64, json, os, sys, zlib
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
PHOTO = '/home/fd/bmw-lab/3.jpeg'
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'art', 'livehyb.json')
S = 1.245
CX_PHOTO, X0, Y0 = 1060.0, 960.0, 322.0
W, H = 1920, 660

# boxes (photo px x0, y0, x1, y1) blanked: numbers, texts, icons, the map's road lines
BOXES = []
def num(cx, cy, w=52, h=30): BOXES.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
for cx, cy, wide in [(875, 380, 1), (802, 384, 1), (730, 387, 1), (655, 400, 1), (588, 422, 1), (536, 464, 1), (476, 514, 1), (437, 582, 1),
                     (466, 654, 0), (514, 726, 0), (570, 784, 0), (657, 782, 0)]:
    num(cx, cy, 86 if wide else 62, 34)
for cx, cy in [(1287, 385), (1390, 390), (1485, 407), (1575, 440), (1647, 500), (1687, 575), (1655, 665), (1600, 752)]:
    num(cx, cy, 52, 46)
BOXES += [
    (606, 500, 890, 576),          # the mode icon and ELECTRIC / INDIVIDUAL
    (732, 596, 884, 666),          # the speed and km/h
    (640, 806, 714, 830), (698, 776, 784, 850),          # km/h, and the speed-limit sign's white disc (the line under it is put back below)
    (312, 668, 362, 716), (330, 726, 404, 776), (392, 760, 440, 810), (268, 780, 328, 830),   # the fuel gauge's 1, 1/2, 0 and pump
    (1384, 452, 1438, 490), (1428, 512, 1480, 552), (1446, 576, 1500, 614), (1414, 642, 1452, 682),   # the power meter's 60, 40, 20, 0
    (1388, 544, 1458, 618), (1526, 616, 1614, 668),         # 1.5 kW, Ø9.3
    (1340, 686, 1530, 726),        # the electric range
    (1460, 752, 1560, 794), (1384, 784, 1524, 818),     # READY, 1/min x1000
    (1730, 656, 1802, 702), (1708, 734, 1790, 786), (1680, 774, 1726, 818), (1796, 776, 1836, 818), (1778, 796, 1840, 842),   # the battery: 100, 53 %, 0, %, icon
    (1040, 372, 1130, 402),        # the M logo
    (848, 418, 1362, 792),         # the middle: the map's road lines
    (1190, 836, 1860, 900), (270, 848, 1190, 900),          # the bottom row
]
# the left part of the middle line (the marker and the line) is part of the design: its box is not blanked beyond x 848


def build():
    im = np.asarray(Image.open(PHOTO).convert('RGB')).astype(float)
    mn = np.minimum(np.minimum(im[..., 0], im[..., 1]), im[..., 2])          # white: all channels high
    mx = np.maximum(np.maximum(im[..., 0], im[..., 1]), im[..., 2])
    white = np.where(mx - mn < 70, mn, 0)                                      # not coloured light
    white = gaussian_filter(white, 0.8)
    m = np.clip((white - 135.0) / 80.0, 0, 1)
    for x0, y0, x1, y1 in BOXES:
        m[int(max(0, y0)):int(y1), int(max(0, x0)):int(x1)] = 0
    # the fuel gauge at the bottom left (drawn live instead): everything left of the chevron's outline there
    pm = Image.new('L', (m.shape[1], m.shape[0]), 0)
    ImageDraw.Draw(pm).polygon([(255, 652), (386, 684), (420, 744), (446, 788), (472, 846), (255, 846)], fill=255)
    m[np.asarray(pm) > 0] = 0
    m[:318, :] = 0; m[:, :268] = 0; m[:, 1850:] = 0                             # outside the cluster
    img = Image.fromarray((m * 255).astype(np.uint8), 'L')
    ImageDraw.Draw(img).line([(690, 835.5), (792, 835.5)], fill=235, width=4)      # the bottom line, which the sign covers in the photo
    # photo -> layout (an affine: scale S, shift)
    a = 1.0 / S
    coeffs = (a, 0, CX_PHOTO - X0 * a, 0, a, Y0)                              # output (x', y') -> photo (x, y)
    out = img.transform((W, H), Image.AFFINE, coeffs, resample=Image.BICUBIC)
    return out


if __name__ == '__main__':
    out = build()
    arr = np.asarray(out)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'w': W, 'h': H, 'z': base64.b64encode(zlib.compress(arr.tobytes(), 9)).decode()}, open(OUT, 'w'))
    out.save(os.path.join(HERE, 'livehyb_mask.png'))
    print('livehyb art:', os.path.getsize(OUT) // 1024, 'KB')
