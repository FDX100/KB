"""Polar measurements of the E46 photo (apps/11.jpg) round a dial's hub: the red scale line's radius against the angle."""
import sys, math, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
im = np.asarray(Image.open(os.path.join(HERE, '..', '..', 'apps', '11.jpg')).convert('RGB')).astype(float)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
red = (R > 120) & (R - G > 50) & (R - B > 40)
dark = (R + G + B) < 150
def hub(cx, cy, r0=60):
    """Refine the hub's centre: the centroid of the dark disc near (cx, cy)."""
    m = dark.copy(); box = np.zeros_like(m); box[int(cy - r0):int(cy + r0), int(cx - r0):int(cx + r0)] = True
    lab, n = ndi.label(m & box); 
    sizes = ndi.sum(m & box, lab, range(1, n + 1)); k = int(np.argmax(sizes)) + 1
    ys, xs = np.nonzero(lab == k); return xs.mean(), ys.mean(), math.sqrt(len(xs) / math.pi)
def profile(cx, cy, rmin, rmax, step=0.5):
    out = []
    for a in np.arange(0, 360, step):
        t = math.radians(a)
        best = None
        for r in np.arange(rmax, rmin, -0.5):
            x, y = cx + r * math.sin(t), cy - r * math.cos(t)
            if 0 <= int(y) < red.shape[0] and 0 <= int(x) < red.shape[1] and red[int(y), int(x)]:
                best = r; break
        out.append((float(a), best))
    return out
if __name__ == '__main__':
    for name, (cx, cy) in {'spd': (413, 767), 'rev': (822, 767)}.items():
        hx, hy, hr = hub(cx, cy)
        print(name, 'hub', round(hx, 1), round(hy, 1), 'r', round(hr, 1))
