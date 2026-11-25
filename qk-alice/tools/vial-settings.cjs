// List the Vial QMK settings a board supports and read each value (read-only).
const { open } = require('./via.cjs'); const { cmd, close } = open();
try {
  const ids = []; let start = 0;
  for (;;) {
    const r = cmd([0xfe, 0x09, start & 255, start >> 8]); let done = false;
    for (let i = 0; i < 32; i += 2) { const q = r[i] | r[i + 1] << 8; if (q === 0xffff) { done = true; break; } ids.push(q); }
    if (done || !ids.length) break; start = ids[ids.length - 1];
  }
  for (const q of ids) { const r = cmd([0xfe, 0x0a, q & 255, q >> 8]); console.log(q, 'status', r[0], 'value', r[1] | r[2] << 8 | r[3] << 16 | r[4] << 24); }
} finally { close(); }
