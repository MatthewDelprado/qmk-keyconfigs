// Write keycodes over VIA: node set.cjs layer,row,col,0xCODE ...  (then reads each back)
const { open } = require('./via.cjs');
const { cmd, close } = open();
try {
  for (const a of process.argv.slice(2)) {
    const [l, r, c, k] = a.split(',').map(Number);
    cmd([0x05, l, r, c, k >> 8, k & 255]);
    const b = cmd([0x04, l, r, c]);
    console.log(`L${l} r${r} c${c} -> 0x${(b[4] << 8 | b[5]).toString(16)}`);
  }
} finally { close(); }
