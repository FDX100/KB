'use strict';
/**
 * ckb.js - Sorani (Central Kurdish) text for the app's own pages (page.js): the shaping of Arabic-script letters into their joined forms,
 * the right-to-left order of a line with Latin runs in it, Arabic-Indic digits, and the catalog of the page's English strings.
 *
 *   ckb.translate('Settings')        -> the Sorani string (numbers kept: '65 L' -> '٦٥ لیتر'), or null when there is no entry
 *   ckb.visual('ڕێکخستن')             -> the string as code points of the arabic atlases (kit/runtime/fonts/arabic*.json) in left-to-right
 *                                       drawing order; the kit's canvas draws it as it is (fonts.js picks the family)
 *
 * The letter forms come from shared/ckb_table.js (made by tools/ckb/bake_arabic.py with the atlases); the catalog is shared/ckb_catalog.js
 * (made from tools/ckb/catalog.json by tools/ckb/make_catalog.py). Plain Node 8.
 */
const T = require('./ckb_table');
let CAT = {};
try { CAT = require('./ckb_catalog'); } catch (e) { CAT = {}; }

const JOIN = T.join, FORMS = T.forms, LIG = T.lig;
const isArabicLetter = (cp) => JOIN[cp] !== undefined;
const isDigit = (cp) => (cp >= 48 && cp <= 57) || (cp >= 0x660 && cp <= 0x669);
const isAlef = (cp) => cp === 0x627 || cp === 0x622 || cp === 0x623 || cp === 0x625;
const isMark = (cp) => (cp >= 0x64b && cp <= 0x65f) || cp === 0x670;

/** Latin digits to Arabic-Indic ones (the digits Sorani is written with). */
function indic(s) { return String(s).replace(/[0-9]/g, (d) => String.fromCharCode(0x660 + d.charCodeAt(0) - 48)); }

/** Shapes the Arabic-script letters of a string into their contextual forms (logical order kept); other characters pass through. */
function shape(s) {
    const cps = Array.from(s).map((c) => c.codePointAt(0)).filter((c) => !isMark(c));
    const out = [];
    for (let i = 0; i < cps.length; i++) {
        const c = cps[i];
        if (!isArabicLetter(c)) { out.push(c); continue; }
        const prev = cps[i - 1], next = cps[i + 1];
        const joinPrev = prev !== undefined && JOIN[prev] === 'D';
        if (c === 0x644 && next !== undefined && isAlef(next) && LIG[next]) {        // lam + alef
            out.push(LIG[next][joinPrev ? 1 : 0]); i++; continue;
        }
        const f = FORMS[c];
        const joinNext = JOIN[c] === 'D' && next !== undefined && JOIN[next] !== undefined;
        let k = 0;
        if (JOIN[c] === 'D') k = joinPrev && joinNext ? 2 : joinNext ? 1 : joinPrev ? 3 : 0;
        else k = joinPrev ? 3 : 0;
        out.push(f[k] || f[0]);
    }
    return out;
}

/** Orders a shaped code point list for drawing left to right in a right-to-left paragraph (Latin letters and digits stay left to right as runs). */
function reorder(cps) {
    const isL = (c) => (c >= 65 && c <= 90) || (c >= 97 && c <= 122) || isDigit(c);
    const isR = (c) => c >= 0xe000 || (c >= 0x600 && c <= 0x6ff && !isDigit(c));
    const cls = cps.map((c) => (isL(c) ? 'L' : isR(c) ? 'R' : 'N'));
    for (let i = 0; i < cls.length; i++) {                      // a neutral between two Latin / digit characters is part of that run
        if (cls[i] !== 'N') continue;
        let a = i - 1, b = i + 1;
        while (a >= 0 && cls[a] === 'N') a--;
        while (b < cls.length && cls[b] === 'N') b++;
        const v = (a >= 0 && b < cls.length && cls[a] === 'L' && cls[b] === 'L') ? 'L' : 'R';
        for (let k = a + 1; k < b; k++) cls[k] = v;
    }
    const runs = [];
    cps.forEach((c, i) => {
        const last = runs[runs.length - 1];
        if (last && last.d === cls[i]) last.v.push(c); else runs.push({ d: cls[i], v: [c] });
    });
    const MIRROR = { 40: 41, 41: 40, 91: 93, 93: 91, 123: 125, 125: 123, 60: 62, 62: 60 };
    const res = [];
    for (let r = runs.length - 1; r >= 0; r--) {                // the runs right to left; an R run is reversed, an L run keeps its order
        const run = runs[r];
        if (run.d === 'R') for (let k = run.v.length - 1; k >= 0; k--) res.push(MIRROR[run.v[k]] || run.v[k]);
        else run.v.forEach((c) => res.push(c));
    }
    return res;
}

/** A Sorani string as drawable text: shaped and in visual order. */
function visual(s) { return String.fromCodePoint.apply(null, reorder(shape(s))); }

/** Looks up an English string; numbers inside it are carried over (as Arabic-Indic digits). Returns null for none. */
function translate(en) {
    const s = String(en);
    if (CAT[s] !== undefined) return indic(CAT[s]);
    const nums = [];
    const key = s.replace(/\d[\d,.]*\d|\d/g, (m) => { nums.push(m); return '{n}'; });
    if (!nums.length || CAT[key] === undefined) return null;
    let i = 0;
    return indic(CAT[key].replace(/\{n\}/g, () => nums[i++] || ''));
}

function has(s) { return /[؀-ۿ]/.test(s); }

module.exports = { translate, visual, shape, reorder, indic, has };
