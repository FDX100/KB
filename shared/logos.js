'use strict';
/**
 * logos.js - the badge logos (Badge tab, the "badgemark" widget): PNG files the OWNER puts in the app's data folder,
 * <data>/logos/. The app ships no BMW, M, i or ALPINA artwork (trademarks; this repository is public), so the pictures are
 * yours: the logos you have the right to use on your own car, in any size (transparent PNG, 4096 px at most).
 *
 * For a model the first file that exists wins:
 *   1. the model's own, its name in lower case with dashes: "M340i" -> m340i.png, "X3 M40i" -> x3-m40i.png, "i4 eDrive40" -> i4-edrive40.png
 *   2. its family: alpina.png (ALPINA models), i.png (i4, i5, i7, iX and their M versions), m.png (M models and M Performance:
 *      M135i, M340i, X3 M40i, XM ...), bmw.png (every other)
 * No file: the badge is the model's name as text, in the theme's own font. scripts/logos.sh puts files on the car.
 * Plain Node 8 (the car's 8.16.2).
 */
const fs = require('fs');
const path = require('path');
const png = require('./png');
const badges = require('./badges');

const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

/** The file names (without .png) to try for a model, most specific first. */
function names(model) {
    if (!model || model === 'none') return [];
    const series = badges.seriesOf(model);
    const family = series === 'ALPINA' ? 'alpina' : (series === 'i' || /^i[0-9X]/.test(model)) ? 'i' : (series === 'M' || /(^|\s)M\d|^XM$/.test(model)) ? 'm' : 'bmw';
    return [slug(model), family];
}

class Logos {
    constructor(dataDir, log) {
        this.dir = path.join(dataDir || '.', 'logos');
        this.log = log;
        this.cache = {};                 // name -> { mtime, img | null (unreadable), why }
        this.scanAt = 0; this.files = [];
    }

    /** The PNG files in the folder (names without .png), rescanned at most every 3 s. */
    list() {
        const now = Date.now();
        if (now - this.scanAt < 3000) return this.files;
        this.scanAt = now;
        try { this.files = fs.readdirSync(this.dir).filter((n) => /\.png$/i.test(n)).map((n) => n.slice(0, -4).toLowerCase()); } catch (e) { this.files = []; }
        return this.files;
    }

    /** The logo for a model: { name, mtime, img: { w, h, rgba } }, or null (none there, or unreadable). */
    find(model) {
        const have = this.list();
        for (const n of names(model)) {
            if (have.indexOf(n) < 0) continue;
            const file = path.join(this.dir, n + '.png');
            let mtime = 0;
            try { mtime = fs.statSync(file).mtime.getTime(); } catch (e) { continue; }
            let c = this.cache[n];
            if (!c || c.mtime !== mtime) {
                c = this.cache[n] = { mtime, img: null, why: '' };
                try { c.img = png.decode(fs.readFileSync(file)); this.log.info('logo ' + n + '.png: ' + c.img.w + 'x' + c.img.h); }
                catch (e) { c.why = e.message; this.log.warn('logo ' + n + '.png: ' + e.message); }
            }
            if (c.img) return { name: n, mtime, img: c.img };
        }
        return null;
    }

    /** For the page: what it will show for this model, and why when it is not a logo. */
    describe(model) {
        if (!model || model === 'none') return { text: 'No badge' };
        const l = this.find(model);
        if (l) return { text: 'Logo: ' + l.name + '.png (' + l.img.w + 'x' + l.img.h + ')', logo: l };
        const tried = names(model).map((n) => n + '.png').join(' or ');
        return { text: 'No logo file (' + tried + '): shown as text' };
    }
}

module.exports = { Logos, names, slug };
