'use strict';
/**
 * png.js - a small PNG reader and a fitter, for the badge logos a user puts in the app's data folder (logos.js). Only
 * what the car's Node 8 and the zlib in it give: 8 or 16 bits a channel, grey / grey + alpha / RGB / RGBA / palette (1, 2, 4,
 * 8 bits), no interlacing. decode() returns { w, h, rgba } (straight alpha) or throws with the reason.
 *
 * fit(img, bw, bh, align) draws the image scaled down (or up) to fit a bw x bh box, aspect kept, aligned left / center /
 * right, into a new RGBA buffer, the way an image widget wants it. Downscaling averages (premultiplied, so edges keep their
 * colour); upscaling is bilinear.
 */
const zlib = require('zlib');

const SIG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const CHANNELS = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 };

function paeth(a, b, c) {
    const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
    return pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
}

function decode(buf) {
    if (!Buffer.isBuffer(buf) || buf.length < 33 || SIG.some((v, i) => buf[i] !== v)) throw new Error('not a PNG file');
    let off = 8, w = 0, h = 0, depth = 0, type = 0, interlace = 0;
    let palette = null, trns = null;
    const idat = [];
    while (off + 8 <= buf.length) {
        const len = buf.readUInt32BE(off), name = buf.toString('latin1', off + 4, off + 8), body = buf.slice(off + 8, off + 8 + len);
        off += 12 + len;
        if (name === 'IHDR') { w = body.readUInt32BE(0); h = body.readUInt32BE(4); depth = body[8]; type = body[9]; interlace = body[12]; }
        else if (name === 'PLTE') palette = body;
        else if (name === 'tRNS') trns = body;
        else if (name === 'IDAT') idat.push(body);
        else if (name === 'IEND') break;
    }
    if (!w || !h || w > 4096 || h > 4096) throw new Error('bad size ' + w + 'x' + h + ' (4096 at most)');
    if (interlace) throw new Error('interlaced PNG not supported (save it without interlacing)');
    if (!CHANNELS[type] || [1, 2, 4, 8, 16].indexOf(depth) < 0 || (type !== 3 && type !== 0 && depth < 8) || (type === 3 && depth === 16)) throw new Error('unsupported PNG (colour type ' + type + ', ' + depth + ' bit)');
    if (type === 3 && !palette) throw new Error('palette missing');
    const bpp = Math.max(1, (CHANNELS[type] * depth) >> 3);              // bytes a pixel for the filters
    const stride = Math.ceil(w * CHANNELS[type] * depth / 8);
    const raw = zlib.inflateSync(Buffer.concat(idat));
    if (raw.length < (stride + 1) * h) throw new Error('PNG data is short');
    const img = Buffer.alloc(stride * h);
    for (let y = 0; y < h; y++) {
        const f = raw[y * (stride + 1)], src = y * (stride + 1) + 1, dst = y * stride;
        for (let i = 0; i < stride; i++) {
            const x = raw[src + i];
            const a = i >= bpp ? img[dst + i - bpp] : 0, b = y ? img[dst - stride + i] : 0, c = i >= bpp && y ? img[dst - stride + i - bpp] : 0;
            img[dst + i] = (f === 0 ? x : f === 1 ? x + a : f === 2 ? x + b : f === 3 ? x + ((a + b) >> 1) : f === 4 ? x + paeth(a, b, c) : x) & 255;
        }
    }
    const rgba = Buffer.alloc(w * h * 4);
    const sample = (y, idx) => {                                        // sample idx (channel count a pixel) of a row, scaled to 0..255
        const row = y * stride;
        if (depth === 8) return img[row + idx];
        if (depth === 16) return img[row + idx * 2];
        const bit = idx * depth, v = (img[row + (bit >> 3)] >> (8 - depth - (bit & 7))) & ((1 << depth) - 1);
        return type === 3 ? v : Math.round(v * 255 / ((1 << depth) - 1));
    };
    const ch = CHANNELS[type];
    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            const o = (y * w + x) * 4, i = x * ch;
            if (type === 6) { rgba[o] = sample(y, i); rgba[o + 1] = sample(y, i + 1); rgba[o + 2] = sample(y, i + 2); rgba[o + 3] = sample(y, i + 3); }
            else if (type === 2) {
                rgba[o] = sample(y, i); rgba[o + 1] = sample(y, i + 1); rgba[o + 2] = sample(y, i + 2); rgba[o + 3] = 255;
                if (trns && trns.length >= 6 && depth === 8 && rgba[o] === trns[1] && rgba[o + 1] === trns[3] && rgba[o + 2] === trns[5]) rgba[o + 3] = 0;
            } else if (type === 4) { const g = sample(y, i); rgba[o] = rgba[o + 1] = rgba[o + 2] = g; rgba[o + 3] = sample(y, i + 1); }
            else if (type === 0) {
                const g = sample(y, i); rgba[o] = rgba[o + 1] = rgba[o + 2] = g; rgba[o + 3] = 255;
                if (trns && trns.length >= 2 && depth === 8 && g === trns[1]) rgba[o + 3] = 0;
            } else {                                                    // palette
                const p = sample(y, i);
                rgba[o] = palette[p * 3] || 0; rgba[o + 1] = palette[p * 3 + 1] || 0; rgba[o + 2] = palette[p * 3 + 2] || 0;
                rgba[o + 3] = trns && p < trns.length ? trns[p] : 255;
            }
        }
    }
    return { w, h, rgba };
}

/** The image scaled into a bw x bh RGBA buffer (aspect kept, aligned); the picture's own size when it is smaller is NOT kept: it scales up to fit. */
function fit(img, bw, bh, align) {
    const out = Buffer.alloc(bw * bh * 4);
    const k = Math.min(bw / img.w, bh / img.h);
    const dw = Math.max(1, Math.round(img.w * k)), dh = Math.max(1, Math.round(img.h * k));
    const ox = align === 'left' ? 0 : align === 'right' ? bw - dw : Math.floor((bw - dw) / 2), oy = Math.floor((bh - dh) / 2);
    const sx = img.w / dw, sy = img.h / dh, src = img.rgba;
    for (let y = 0; y < dh; y++) {
        const y0 = y * sy, y1 = (y + 1) * sy;
        for (let x = 0; x < dw; x++) {
            let r = 0, g = 0, b = 0, a = 0, wsum = 0;
            if (k < 1) {                                                // downscale: the average over the source box, premultiplied
                const x0 = x * sx, x1 = (x + 1) * sx;
                for (let yy = Math.floor(y0); yy < Math.min(img.h, Math.ceil(y1)); yy++) {
                    const wy = Math.min(yy + 1, y1) - Math.max(yy, y0);
                    for (let xx = Math.floor(x0); xx < Math.min(img.w, Math.ceil(x1)); xx++) {
                        const wgt = wy * (Math.min(xx + 1, x1) - Math.max(xx, x0)), si = (yy * img.w + xx) * 4, sa = src[si + 3] / 255;
                        r += src[si] * sa * wgt; g += src[si + 1] * sa * wgt; b += src[si + 2] * sa * wgt; a += sa * wgt; wsum += wgt;
                    }
                }
            } else {                                                    // upscale: bilinear
                const fx = Math.min(img.w - 1, Math.max(0, (x + 0.5) * sx - 0.5)), fy = Math.min(img.h - 1, Math.max(0, (y + 0.5) * sy - 0.5));
                const x0 = Math.floor(fx), y0i = Math.floor(fy), x1 = Math.min(img.w - 1, x0 + 1), y1i = Math.min(img.h - 1, y0i + 1), tx = fx - x0, ty = fy - y0i;
                [[x0, y0i, (1 - tx) * (1 - ty)], [x1, y0i, tx * (1 - ty)], [x0, y1i, (1 - tx) * ty], [x1, y1i, tx * ty]].forEach((p) => {
                    const si = (p[1] * img.w + p[0]) * 4, sa = src[si + 3] / 255;
                    r += src[si] * sa * p[2]; g += src[si + 1] * sa * p[2]; b += src[si + 2] * sa * p[2]; a += sa * p[2]; wsum += p[2];
                });
            }
            const o = ((oy + y) * bw + ox + x) * 4;
            if (a > 0 && wsum > 0) { out[o] = Math.round(r / a); out[o + 1] = Math.round(g / a); out[o + 2] = Math.round(b / a); out[o + 3] = Math.round(255 * a / wsum); }
        }
    }
    return out;
}

module.exports = { decode, fit };
