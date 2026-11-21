'use strict';
/**
 * safe_start.js - the first start after an installation draws only the light themes.
 *
 * Alpina, Live Cockpit and Concept are the heaviest themes for the cluster's GPU (large traced shaders); on some cars they
 * blanked the cluster. A fresh install keeps them locked (greyed out, not selectable) for the first start, so the first
 * thing a driver sees cannot be one of them; they unlock at the next start of the app, or the next start of the car
 * (the car was off for a while, then ignition on), whichever comes first. An install that already has saved settings
 * (an update of a car that has been using the app) is not locked at all.
 *
 *   const safe = new SafeStart(ctx.dataDir, ctx.settings.file, log);   // counts this start
 *   safe.isLocked('alpina')   -> true while it is locked
 *   safe.carOn(state) / safe.text()
 * State: <data>/session.json { starts, legacy }. Plain Node 8 (the car's 8.16.2).
 */
const fs = require('fs');
const path = require('path');

const LOCKED = ['alpina', 'live', 'concept'];
const OFF_MIN_MS = 60000;           // the car counts as "off" after this long in a parked / off vehicle state

class SafeStart {
    constructor(dataDir, settingsFile, log) {
        this.log = log;
        this.file = path.join(dataDir || '.', 'session.json');
        let s = null;
        try { s = JSON.parse(fs.readFileSync(this.file, 'utf8')); } catch (e) { /* the first start */ }
        if (!s || typeof s.starts !== 'number') {
            let legacy = false;
            try { legacy = !!settingsFile && fs.existsSync(settingsFile); } catch (e) { legacy = false; }
            s = { starts: 0, legacy };
        }
        this.starts = s.starts + 1;
        this.legacy = s.legacy === true;
        this.offAt = 0;
        this._save();
        this.log.info('start ' + this.starts + (this.legacy ? ' (an install in use: nothing locked)' : this.unlocked() ? ': all themes unlocked' : ': ' + LOCKED.join(', ') + ' locked until the next start'));
    }

    unlocked() { return this.legacy || this.starts >= 2; }

    isLocked(name) { return LOCKED.indexOf(name) >= 0 && !this.unlocked(); }

    /** Which layouts are locked now (for the page). */
    lockedNames() { return this.unlocked() ? [] : LOCKED.slice(); }

    /**
     * The car's vehicle state (vehicle_state.js numbers): parked / off (5 or lower) for a minute and then on (7 and up) is a car
     * start. Returns true when that unlocked the themes.
     */
    carOn(state) {
        if (typeof state !== 'number') return false;
        const now = Date.now();
        if (state <= 5) { if (!this.offAt) this.offAt = now; return false; }
        if (state >= 7 && this.offAt && now - this.offAt >= OFF_MIN_MS) {
            this.offAt = 0;
            if (this.unlocked()) return false;
            this.starts += 1; this._save();
            this.log.info('the car started again: Alpina, Live Cockpit and Concept unlocked');
            return true;
        }
        if (state >= 7) this.offAt = 0;
        return false;
    }

    text() { return this.unlocked() ? '' : 'Alpina, Live Cockpit and Concept unlock the next time the app or the car starts'; }

    _save() { try { fs.writeFileSync(this.file, JSON.stringify({ starts: this.starts, legacy: this.legacy })); } catch (e) { this.log.warn('session save: ' + e.message); } }
}

module.exports = { SafeStart, LOCKED };
