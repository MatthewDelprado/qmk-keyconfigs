// Write a keymap target over VIA, only the keys that differ: node apply.cjs TARGET.json
// TARGET.json has the same shape as a dump.cjs backup (keymap[layer][row][col]).
const fs = require('fs'); const { open } = require('./via.cjs');
const t = JSON.parse(fs.readFileSync(process.argv[2]));
const { cmd, close } = open();
let n = 0;
try {
  t.keymap.forEach((rows, l) => rows.forEach((cols, r) => cols.forEach((want, c) => {
    if (want == null) return;
    const g = cmd([0x04, l, r, c]); const have = g[4] << 8 | g[5];
    if (have === want) return;
    cmd([0x05, l, r, c, want >> 8, want & 255]);
    const b = cmd([0x04, l, r, c]); const now = b[4] << 8 | b[5];
    if (now !== want) throw new Error(`L${l} r${r} c${c}: wrote 0x${want.toString(16)}, reads 0x${now.toString(16)}`);
    n++;
  })));
  // Macro buffer (optional): rewrite it if it differs, then read it back.
  let m = 'unchanged';
  if (t.macroBufferHex) {
    const want = Buffer.from(t.macroBufferHex, 'hex'), have = [];
    for (let off = 0; off < want.length; off += 28) { const k = Math.min(28, want.length - off); have.push(...cmd([0x0e, off >> 8, off & 255, k]).slice(4, 4 + k)); }
    if (!want.equals(Buffer.from(have))) {
      for (let off = 0; off < want.length; off += 28) { const k = Math.min(28, want.length - off); cmd([0x0f, off >> 8, off & 255, k, ...want.subarray(off, off + k)]); }
      const now = [];
      for (let off = 0; off < want.length; off += 28) { const k = Math.min(28, want.length - off); now.push(...cmd([0x0e, off >> 8, off & 255, k]).slice(4, 4 + k)); }
      if (!want.equals(Buffer.from(now))) throw new Error('macro buffer did not take (is Vial locked?)');
      m = 'rewritten';
    }
  }
  console.log(`wrote ${n} keys, macros ${m}`);
} finally { close(); }
