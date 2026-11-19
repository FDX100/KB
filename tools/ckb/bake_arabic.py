#!/usr/bin/env python3
"""Bakes the Arabic-script glyph atlases for the app's Sorani (Central Kurdish) page text.

The kit's canvas draws text from pre-baked glyph atlases (kit/runtime/fonts/*.json) one code point at a time, with no shaping. Arabic script
needs the letter forms (isolated, initial, medial, final), so every form of every letter is rendered here (HarfBuzz through Pillow's raqm
layout, Noto Sans Arabic) and stored under a private-use code point; shared/ckb.js shapes a string into those code points and puts them in
visual (right-to-left) order. Output:

    kit/runtime/fonts/arabic.json, arabicbold.json   the atlases (regular 500, bold 700), Arabic letters + Arabic-Indic digits + Latin from Barlow
    shared/ckb_table.js                               the shaping table: joining types, the form code points, the lam-alef ligatures

    python3 tools/ckb/bake_arabic.py        (needs Pillow with raqm)
"""
import base64, json, os, zlib
from PIL import Image, ImageDraw, ImageFont, features

assert features.check('raqm'), 'Pillow needs raqm (HarfBuzz) for Arabic shaping'
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'tools', 'fonts-src')
NOTO = os.path.join(SRC, 'NotoSansArabic[wdth,wght].ttf')
SIZES = [16, 22, 30, 42, 56]
ZWJ = '‍'
# letters of the Sorani alphabet and the Arabic ones its text uses (the letter, its joining type: D dual, R right-joining only)
LETTERS = {
    'D': 'بپتثجچحخسشصضطظعغفڤقکگلڵمنھهیێيكئ',
    'R': 'اآأإدذرڕزژوۆۇؤەةۋ',
}
ALEF = 'اآأإ'
DIGITS_AR = '٠١٢٣٤٥٦٧٨٩'
PUNCT_AR = '،؟؛'
LATIN = [chr(c) for c in range(32, 127)] + ['·', '°', '–', '—', '…', '×']
PUA = 0xE000


def noto(size, weight):
    f = ImageFont.truetype(NOTO, size, layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_axes([weight, 100])
    return f


def latin(size, bold):
    return ImageFont.truetype(os.path.join(SRC, 'BarlowCondensed-Bold.ttf' if bold else 'Barlow-Medium.ttf'), size)


def render(font, text, rtl=True):
    """A glyph run drawn at the origin (left edge, baseline): the bitmap crop, its offset from the origin, the advance."""
    kw = dict(direction='rtl', language='ckb') if rtl else {}
    adv = font.getlength(text, **kw)
    bb = font.getbbox(text, anchor='ls', **kw)
    w, h = max(1, bb[2] - bb[0]), max(1, bb[3] - bb[1])
    img = Image.new('L', (w + 8, h + 8), 0)
    ImageDraw.Draw(img).text((4 - bb[0], 4 - bb[1]), text, font=font, fill=255, anchor='ls', **kw)
    box = img.getbbox()
    if not box:
        return None, 0, 0, adv
    return img.crop(box), bb[0] + box[0] - 4, bb[1] + box[1] - 4, adv


def contexts(ch, kind):
    """The strings whose rendering gives each form of a letter: isolated, initial, medial, final."""
    if kind == 'D':
        return [ch, ch + ZWJ, ZWJ + ch + ZWJ, ZWJ + ch]
    return [ch, None, None, ZWJ + ch]


def bake(weight, bold):
    table = {'join': {}, 'forms': {}, 'lig': {}}
    forms_text = {}
    nxt = PUA
    for kind, chars in LETTERS.items():
        for ch in chars:
            table['join'][ord(ch)] = kind
            ctx = contexts(ch, kind)
            codes = []
            for form in ctx:
                if form is None:
                    codes.append(0); continue
                forms_text[nxt] = form; codes.append(nxt); nxt += 1
            table['forms'][ord(ch)] = codes
    for al in ALEF:                                   # lam + alef ligatures: isolated and final
        a, b = 'ل' + al, ZWJ + 'ل' + al
        forms_text[nxt] = a; forms_text[nxt + 1] = b
        table['lig'][ord(al)] = [nxt, nxt + 1]; nxt += 2
    out = {'family': 'arabicbold' if bold else 'arabic', 'source': 'NotoSansArabic + Barlow (SIL OFL 1.1)', 'sizes': []}
    for size in SIZES:
        nf, lf = noto(size, weight), latin(size, bold)
        asc, desc = nf.getmetrics()
        glyphs = {}
        items = []
        for cp, text in forms_text.items():
            items.append((cp, *render(nf, text)))
        for ch in DIGITS_AR + PUNCT_AR:
            im, ox, oy, adv = render(nf, ch, rtl=False)
            items.append((ord(ch), im, ox, oy, adv))
        for ch in LATIN:
            if ch == ' ':
                items.append((32, None, 0, 0, size * 0.28)); continue
            im, ox, oy, adv = render(lf, ch, rtl=False)
            items.append((ord(ch), im, ox, oy, adv))
        # pack the bitmaps into rows of an atlas 1024 wide
        x = y = rowh = 0
        placed = []
        for cp, im, ox, oy, adv in items:
            if im is None:
                glyphs[cp] = [0, 0, 0, 0, 0, 0, round(adv, 2)]; continue
            w, h = im.size
            if x + w + 1 > 1024:
                x, y, rowh = 0, y + rowh + 1, 0
            placed.append((cp, im, x, y, ox, oy, adv)); x += w + 1; rowh = max(rowh, h)
        H = y + rowh + 1
        atlas = Image.new('L', (1024, H), 0)
        for cp, im, gx, gy, ox, oy, adv in placed:
            atlas.paste(im, (gx, gy))
            glyphs[cp] = [gx, gy, im.size[0], im.size[1], ox, oy, round(adv, 2)]
        out['sizes'].append({'size': size, 'ascent': asc, 'descent': desc, 'atlasW': 1024, 'atlasH': H,
                             'glyphs': {str(k): v for k, v in glyphs.items()},
                             'alpha': base64.b64encode(zlib.compress(atlas.tobytes(), 9)).decode()})
    return out, table


def main():
    fonts_dir = os.path.join(ROOT, 'kit', 'runtime', 'fonts')
    for weight, bold in ((500, False), (700, True)):
        out, table = bake(weight, bold)
        name = out['family']
        with open(os.path.join(fonts_dir, name + '.json'), 'w') as f:
            json.dump(out, f, separators=(',', ':'))
        print(name, [(s['size'], s['atlasH']) for s in out['sizes']], len(out['sizes'][0]['glyphs']), 'glyphs')
    with open(os.path.join(ROOT, 'shared', 'ckb_table.js'), 'w') as f:
        f.write("'use strict';\n// Generated by tools/ckb/bake_arabic.py: the Arabic-script shaping table for shared/ckb.js (join: D dual / R right-joining;\n"
                "// forms: [isolated, initial, medial, final] code points in the arabic atlases; lig: lam + alef ligature [isolated, final]).\n"
                'module.exports = ' + json.dumps(table, separators=(',', ':')) + ';\n')
    print('table:', len(table['forms']), 'letters,', len(table['lig']), 'ligatures')


if __name__ == '__main__':
    main()
