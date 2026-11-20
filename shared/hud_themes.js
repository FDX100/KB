'use strict';
/**
 * HUD colour themes. Layouts name colour *roles* ("fg", "dim", "arc", ...) and
 * the active theme fills them in, so every layout works in every theme.
 *
 * HUD rule (Nov 7 2026, from road photos: greys were hard to see even at night): the HUD is a projector, so a dim or
 * see-through colour comes out faint on the glass. Every HUD role is opaque and no lit colour is darker than
 * about 70 % brightness; only "track" (the unlit part of a bar) stays partly see-through, at 96..110 of 255.
 *
 * Colours are [r, g, b, a] 0-255. On the HUD, black is see-through glass, so a
 * theme only ever adds light. Dark blue is the weakest colour on a HUD in sun;
 * M's mid blue is kept brighter than the paint-chip M blue for that reason.
 *
 * bar: the shift bar's three zones. lowColor up to midAt, midColor up to the
 * red zone, highColor from there. midAt: 'shift' = where the shift zone starts
 * (redline - 1500), or a fraction of the bar (M climbs light blue -> blue at 50%).
 */
const THEMES = {
    classic: {
        name: 'Classic',
        fg: [243, 246, 250, 255], dim: [200, 208, 220, 255], track: [243, 246, 250, 96], arc: [243, 246, 250, 255],
        glow: 0.35, stripe: false,
        bar: { low: [243, 246, 250], mid: [255, 154, 60], high: [255, 75, 62], midAt: 'shift' },
        rev: { from: [185, 192, 204], to: [243, 246, 250] },
    },
    m: {
        name: 'M',
        fg: [243, 246, 250, 255], dim: [170, 205, 255, 255], track: [80, 150, 255, 110], arc: [79, 180, 255, 255],
        glow: 0.4, stripe: true,
        bar: { low: [79, 180, 255], mid: [51, 102, 255], high: [232, 38, 45], midAt: 0.5 },
        rev: { from: [51, 102, 255], to: [110, 170, 255] },
    },
    night: {
        name: 'Night',
        fg: [255, 179, 71, 255], dim: [235, 165, 70, 255], track: [255, 179, 71, 96], arc: [255, 179, 71, 255],
        glow: 0.3, stripe: false,
        bar: { low: [255, 179, 71], mid: [255, 179, 71], high: [255, 75, 62], midAt: 'shift' },
        rev: { from: [205, 135, 55], to: [255, 179, 71] },
    },
    // Hybrid (layout hybrid.json): Minimal for plug-in hybrids, the battery charge in electric blue.
    hybrid: {
        name: 'Hybrid',
        fg: [240, 243, 248, 255], dim: [128, 134, 146, 255], track: [44, 48, 56, 255], arc: [96, 190, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [240, 243, 248], mid: [240, 243, 248], high: [255, 42, 42], midAt: 'shift' },
        rev: { from: [240, 243, 248], to: [240, 243, 248] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [70, 74, 82, 255], head: [226, 228, 232, 255],
        ink: [12, 12, 14, 255], accent: [240, 243, 248, 255], well: [0, 0, 0, 255],
    },
    // Alpina (layout alpina.json): black with Alpina blue panels, cool white scales, a red needle.
    alpina: {
        name: 'Alpina',
        fg: [236, 242, 255, 255], dim: [140, 165, 215, 255], track: [40, 60, 120, 255], arc: [70, 150, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [70, 150, 255], mid: [70, 150, 255], high: [255, 42, 42], midAt: 'shift' },
        rev: { from: [70, 150, 255], to: [70, 150, 255] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [225, 236, 255, 255], head: [180, 205, 255, 255],
        ink: [12, 12, 14, 255], accent: [70, 150, 255, 255], well: [0, 0, 0, 255],
    },
    // Concept (layout concept.json): black, glossy blue lines, amber swooshes, white numbers.
    concept: {
        name: 'Concept',
        fg: [244, 247, 252, 255], dim: [120, 150, 190, 255], track: [40, 60, 100, 255], arc: [255, 178, 40, 255],
        glow: 0, stripe: false,
        bar: { low: [255, 178, 40], mid: [255, 178, 40], high: [255, 42, 42], midAt: 'shift' },
        rev: { from: [255, 178, 40], to: [255, 178, 40] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [200, 225, 255, 255], head: [190, 215, 255, 255],
        ink: [12, 12, 14, 255], accent: [255, 178, 40, 255], well: [0, 0, 0, 255],
    },
    // Live Cockpit (layout live.json): white numbers, a blue half and a red half.
    live: {
        name: 'Live Cockpit',
        fg: [244, 247, 252, 255], dim: [150, 160, 180, 255], track: [40, 50, 80, 255], arc: [0, 178, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [0, 178, 255], mid: [0, 178, 255], high: [255, 0, 57], midAt: 'shift' },
        rev: { from: [255, 0, 57], to: [255, 0, 57] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [0, 178, 255, 255], head: [0, 178, 255, 255],
        ink: [12, 12, 14, 255], accent: [255, 96, 120, 255], accent2: [64, 170, 255, 255], amber: [255, 170, 0, 255], well: [0, 0, 0, 255],
        lblue: [120, 170, 245, 255], pink: [236, 140, 140, 255], red: [242, 31, 41, 255], lgrey: [150, 170, 205, 255],
    },
    // Eco (layout eco.json): deep blue black, cyan rings, a green eco accent, amber then red as the load rises.
    eco: {
        name: 'Eco',
        fg: [242, 248, 255, 255], dim: [110, 150, 200, 255], track: [30, 60, 120, 120], arc: [64, 190, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [64, 190, 255], mid: [255, 170, 40], high: [255, 60, 60], midAt: 'shift' },
        rev: { from: [64, 190, 255], to: [64, 190, 255] },
        bg: [2, 7, 18, 255], panel: [2, 7, 18, 255], line: [64, 190, 255, 255], head: [120, 200, 255, 255],
        ink: [12, 12, 14, 255], accent: [64, 190, 255, 255], well: [2, 7, 18, 255],
        cy: [48, 160, 255, 255], green: [70, 225, 150, 255], amber: [255, 170, 40, 255],
    },
    // Classic (layout classic.json): the analog cluster at night: red-orange on black.
    classic: {
        name: 'Classic',
        fg: [255, 240, 232, 255], dim: [190, 110, 90, 255], track: [70, 20, 14, 255], arc: [255, 72, 34, 255],
        glow: 0, stripe: false,
        bar: { low: [255, 72, 34], mid: [255, 72, 34], high: [255, 28, 18], midAt: 'shift' },
        rev: { from: [255, 72, 34], to: [255, 72, 34] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [255, 72, 34, 255], head: [255, 120, 80, 255],
        ink: [12, 12, 14, 255], accent: [255, 72, 34, 255], well: [0, 0, 0, 255],
    },
    // Night Drive (layout night.json): near black, warm white text, dim amber.
    night_drive: {
        name: 'Night Drive',
        fg: [232, 218, 196, 255], dim: [150, 126, 98, 255], track: [40, 32, 24, 255], arc: [236, 148, 52, 255],
        glow: 0, stripe: false,
        bar: { low: [236, 148, 52], mid: [236, 148, 52], high: [200, 70, 44], midAt: 'shift' },
        rev: { from: [236, 148, 52], to: [236, 148, 52] },
        bg: [2, 2, 3, 255], panel: [2, 2, 3, 255], line: [150, 112, 70, 255], head: [200, 160, 110, 255],
        ink: [12, 12, 14, 255], accent: [226, 150, 66, 255], well: [2, 2, 3, 255],
    },
    // M Digital (layout mdigital.json): white on black with M orange bands.
    mdigital: {
        name: 'M Digital',
        fg: [244, 246, 248, 255], dim: [150, 150, 156, 255], track: [50, 50, 56, 255], arc: [255, 112, 40, 255],
        glow: 0, stripe: false,
        bar: { low: [255, 112, 40], mid: [255, 112, 40], high: [255, 30, 20], midAt: 'shift' },
        rev: { from: [255, 112, 40], to: [255, 112, 40] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [244, 246, 248, 255], head: [255, 140, 80, 255],
        ink: [12, 12, 14, 255], accent: [255, 112, 40, 255], well: [0, 0, 0, 255],
    },
    // Blue Dials (layout bluedials.json): white on a vivid blue, red needles.
    bluedials: {
        name: 'Blue Dials',
        fg: [245, 246, 252, 255], dim: [150, 170, 230, 255], track: [30, 50, 140, 255], arc: [86, 156, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [86, 156, 255], mid: [86, 156, 255], high: [255, 40, 60], midAt: 'shift' },
        rev: { from: [86, 156, 255], to: [86, 156, 255] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [86, 156, 255, 255], head: [150, 190, 255, 255],
        ink: [12, 12, 14, 255], accent: [86, 156, 255, 255], well: [0, 0, 0, 255],
    },
    // ePower (layout epower.json): the plug-in hybrid cluster: grey-white on navy, blue eDrive accents, a red-orange needle.
    epower: {
        name: 'ePower',
        fg: [236, 240, 248, 255], dim: [150, 158, 176, 255], track: [30, 40, 70, 255], arc: [64, 150, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [64, 150, 255], mid: [64, 150, 255], high: [255, 88, 44], midAt: 'shift' },
        rev: { from: [64, 150, 255], to: [64, 150, 255] },
        bg: [1, 3, 10, 255], panel: [1, 3, 10, 255], line: [206, 212, 228, 255], head: [150, 190, 255, 255],
        ink: [12, 12, 14, 255], accent: [64, 150, 255, 255], well: [1, 3, 10, 255],
    },
    // Digital Rain (layout rain.json): phosphor green on black.
    rain: {
        name: 'Digital Rain',
        fg: [140, 255, 170, 255], dim: [0, 150, 64, 255], track: [0, 60, 24, 255], arc: [0, 235, 80, 255],
        glow: 0, stripe: false,
        bar: { low: [0, 235, 80], mid: [140, 255, 170], high: [255, 60, 60], midAt: 'shift' },
        rev: { from: [0, 235, 80], to: [0, 235, 80] },
        bg: [0, 5, 1, 255], panel: [0, 5, 1, 255], line: [0, 235, 80, 255], head: [140, 255, 170, 255],
        ink: [0, 10, 2, 255], accent: [0, 235, 80, 255], well: [0, 5, 1, 255], amber: [255, 190, 30, 255],
    },
    // Neon City (layout neon.json): Cyberpunk yellow, cyan and magenta on near black.
    neon: {
        name: 'Neon City',
        fg: [252, 238, 10, 255], dim: [150, 140, 40, 255], track: [36, 10, 52, 255], arc: [20, 242, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [252, 238, 10], mid: [255, 128, 12], high: [255, 30, 150], midAt: 'shift' },
        rev: { from: [252, 238, 10], to: [255, 30, 150] },
        bg: [4, 1, 10, 255], panel: [4, 1, 10, 255], line: [20, 242, 255, 255], head: [20, 242, 255, 255],
        ink: [10, 2, 18, 255], accent: [20, 242, 255, 255], well: [4, 1, 10, 255],
    },
    // Glass (layout glass.json): white numerals on dark navy, steel-blue glass and a blue needle.
    glass: {
        name: 'Glass',
        fg: [244, 247, 252, 255], dim: [150, 170, 205, 255], track: [30, 50, 100, 255], arc: [60, 130, 255, 255],
        glow: 0, stripe: false,
        bar: { low: [60, 130, 255], mid: [60, 130, 255], high: [255, 90, 60], midAt: 'shift' },
        rev: { from: [60, 130, 255], to: [60, 130, 255] },
        bg: [3, 6, 18, 255], panel: [3, 6, 18, 255], line: [200, 215, 240, 255], head: [150, 190, 255, 255],
        ink: [10, 12, 24, 255], accent: [60, 190, 255, 255], well: [3, 6, 18, 255], amber: [255, 170, 20, 255],
    },
    // E46 (layout e46.json): the white-faced analog cluster: red numbers and notches, black ink, an orange LCD.
    e46: {
        name: 'E46 M3',
        fg: [236, 236, 232, 255], dim: [120, 120, 124, 255], track: [60, 60, 64, 255], arc: [226, 40, 30, 255],
        glow: 0, stripe: false,
        bar: { low: [226, 40, 30], mid: [248, 150, 30], high: [226, 40, 30], midAt: 'shift' },
        rev: { from: [226, 40, 30], to: [226, 40, 30] },
        bg: [6, 6, 8, 255], panel: [6, 6, 8, 255], line: [226, 40, 30, 255], head: [226, 40, 30, 255],
        ink: [20, 20, 22, 255], accent: [226, 40, 30, 255], well: [6, 6, 8, 255],
        redn: [176, 40, 34, 255], inkb: [34, 32, 32, 255], lcdink: [110, 34, 10, 255],
    },
    // Apex (layout apex.json): two big dials, white speed and orange revs, on black.
    apex: {
        name: 'Apex',
        fg: [244, 246, 250, 255], dim: [132, 138, 150, 255], track: [255, 255, 255, 26], arc: [255, 106, 26, 255],
        glow: 0, stripe: false,
        bar: { low: [244, 246, 250], mid: [255, 106, 26], high: [255, 42, 42], midAt: 'shift' },
        rev: { from: [244, 246, 250], to: [255, 106, 26] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [150, 156, 168, 255], head: [255, 106, 26, 255],
        ink: [12, 12, 14, 255], accent: [255, 106, 26, 255], well: [0, 0, 0, 255],
    },
    // E-Race (layout erace.json): a race dash for hybrids and EVs, black with an electric lime accent, a green for regen.
    erace: {
        name: 'E-Race',
        fg: [244, 246, 250, 255], dim: [128, 138, 132, 255], track: [255, 255, 255, 24], arc: [168, 255, 40, 255],
        glow: 0, stripe: false,
        bar: { low: [168, 255, 40], mid: [255, 190, 30], high: [255, 42, 42], midAt: 'shift' },
        rev: { from: [168, 255, 40], to: [255, 42, 42] },
        bg: [0, 0, 0, 255], panel: [0, 0, 0, 255], line: [96, 108, 100, 255], head: [168, 255, 40, 255],
        ink: [10, 14, 10, 255], accent: [168, 255, 40, 255], well: [0, 0, 0, 255], green: [40, 220, 130, 255],
    },
};
// every theme: the shift-point red, used by "hot" (the gear and SHIFT at the shift point, the rev bar past it)
Object.keys(THEMES).forEach((k) => { THEMES[k].hot = [255, 42, 42, 255]; });

// Redline layout (after cauliflowermossgrape's Redline app): rev bar segments ramp rev.from -> rev.to up to
// the shift point; the shift lights run green -> yellow -> red in every theme; grade badges by verdict.
const LIGHTS = { green: [47, 210, 122], yellow: [255, 194, 26], red: [255, 42, 42], blue: [40, 110, 255] };
const VERDICT = {
    'SPOT ON': [47, 210, 122, 255], EARLY: [255, 194, 26, 255], LATE: [255, 138, 26, 255],
    LIMITER: [255, 42, 42, 255], 'COLD REV': [61, 139, 255, 255], COLD: [61, 139, 255, 255],
};

// The M tricolour stripe: light blue, dark blue, red (brightened for the HUD).
const M_STRIPE = [[79, 180, 255, 255], [47, 91, 216, 255], [232, 38, 45, 255]];

/** A colour from a role name ("fg") or a literal [r,g,b,a]. */
function color(theme, c) {
    if (Array.isArray(c)) return c;
    return theme[c] || theme.fg;
}

module.exports = { THEMES, M_STRIPE, LIGHTS, VERDICT, color };
