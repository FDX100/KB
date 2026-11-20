'use strict';
/**
 * cluster-reset.js - restart the instrument cluster (KOMBI) the way BimmerCode and E-Sys do after coding: UDS ECUReset
 * (service 0x11, hardReset 0x01) to the cluster's control unit, 0x60, over the head unit's own diagnostic link (diag.js).
 *
 * It sends nothing else: one address (0x60), one service (0x11 01), and when the cluster says that service is not
 * available in its current session (7F 11 7E / 7F), the extended session (10 03) first, as the coding tools do. No
 * coding, no writes. The cluster is dark for several seconds while it starts again.
 *
 *   const r = await resetCluster(ctx.signals, log);
 *   r.sent     the request left the head unit
 *   r.answer   'accepted' (51 01), 'no answer' (it may already be restarting) or the refusal's text
 */
const { Diag, hex, NRC, replyTo } = require('./diag');

const KOMBI = 0x60;

async function resetCluster(signals, log) {
    const diag = new Diag(signals, log);
    await diag.init();
    if (!diag.p) throw new Error(diag.error || 'no diagnostic link');
    const ask = (sid, data) => diag.physical(KOMBI, sid, data, 3000, replyTo(sid, data));
    let uds = await ask(0x11, [0x01]);
    if (uds && uds[0] === 0x7F && (uds[2] === 0x7E || uds[2] === 0x7F)) {
        log.info('cluster reset: not in this session, asking for the extended session first');
        await ask(0x10, [0x03]);
        uds = await ask(0x11, [0x01]);
    }
    if (!uds) return { sent: true, answer: 'no answer' };
    if (uds[0] === 0x51) return { sent: true, answer: 'accepted' };
    if (uds[0] === 0x7F) return { sent: true, answer: 'refused: ' + (NRC[uds[2]] || '0x' + hex(uds[2])) };
    return { sent: true, answer: 'unexpected reply ' + uds.map((b) => hex(b)).join(' ') };
}

module.exports = { resetCluster, KOMBI };
