// Back up the QK Alice's VIA state: node dump.cjs OUT.json
// Saves every layer (5 x 16 matrix), the macro buffer and the layout options.
const fs = require('fs');
const { open } = require('./via.cjs');
const ROWS = +(process.env.ROWS || 5), COLS = +(process.env.COLS || 16);

const out = process.argv[2];
if (!out) { console.error('usage: node dump.cjs OUT.json'); process.exit(1); }
const { cmd, close } = open();
try {
  const pv = cmd([0x01]);
  const layers = cmd([0x11])[1];
  const lo = cmd([0x02, 0x02]);
  const layoutOptions = (lo[2] << 24 | lo[3] << 16 | lo[4] << 8 | lo[5]) >>> 0;

  // Keymap: read the whole dynamic keymap buffer, 28 bytes at a time.
  const size = layers * ROWS * COLS * 2, buf = [];
  for (let off = 0; off < size; off += 28) {
    const n = Math.min(28, size - off);
    const r = cmd([0x12, off >> 8, off & 255, n]);
    buf.push(...r.slice(4, 4 + n));
  }
  const keymap = [];
  for (let l = 0; l < layers; l++) {
    const rows = [];
    for (let r = 0; r < ROWS; r++) {
      const row = [];
      for (let c = 0; c < COLS; c++) {
        const i = ((l * ROWS + r) * COLS + c) * 2;
        row.push(buf[i] << 8 | buf[i + 1]);
      }
      rows.push(row);
    }
    keymap.push(rows);
  }

  // Macros: raw buffer (NUL-separated, with QMK's SS_ escape bytes).
  const macroCount = cmd([0x0c])[1];
  const ms = cmd([0x0d]); const macroSize = ms[1] << 8 | ms[2];
  const macro = [];
  for (let off = 0; off < macroSize; off += 28) {
    const n = Math.min(28, macroSize - off);
    const r = cmd([0x0e, off >> 8, off & 255, n]);
    macro.push(...r.slice(4, 4 + n));
  }

  const data = {
    board: process.env.BOARD || 'QK ALICE', usb: process.env.VID ? process.env.VID + ':' + process.env.PID : '0x4F57:0x4110', savedAt: new Date().toISOString(),
    viaProtocol: pv[1] << 8 | pv[2], layers, rows: ROWS, cols: COLS, layoutOptions,
    keymap, macroCount, macroBufferHex: Buffer.from(macro).toString('hex'),
  };
  fs.writeFileSync(out, JSON.stringify(data, null, 1));
  console.log(`saved ${layers} layers, ${macroCount} macros (${macroSize} bytes), layout options ${layoutOptions} -> ${out}`);
} finally { close(); }
