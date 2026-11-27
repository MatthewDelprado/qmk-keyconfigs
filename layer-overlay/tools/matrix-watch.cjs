// Prints raw switch presses (row,col) as the board sees them, before the keymap: a hardware check.
// Needs Vial unlocked (vial-bootloader.cjs --unlock-only). Read-only. Stops after SECS (default 60).
// From qk-alice/tools: VID=0x4653 PID=0x0004 ROWS=8 COLS=7 node ../../layer-overlay/tools/matrix-watch.cjs $PWD
const { open } = require(process.argv[2] + '/via.cjs');
const ROWS = +(process.env.ROWS || 8), COLS = +(process.env.COLS || 7), SECS = +(process.env.SECS || 60);
const sleep = ms => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
const { cmd, close } = open();
const per = Math.floor(COLS / 8) + 1;   // bytes per row, big-endian
let prev = '', t0 = Date.now();
try {
  console.log('watching the matrix for', SECS, 's');
  while (Date.now() - t0 < SECS * 1000) {
    const r = cmd([0x02, 0x03]);
    if (r[0] !== 0x02) { console.log('locked or unsupported (reply', r[0], ')'); break; }
    const down = [];
    for (let row = 0; row < ROWS; row++) {
      let v = 0;
      for (let b = 0; b < per; b++) v = v << 8 | r[2 + row * per + b];
      for (let c = 0; c < COLS; c++) if (v & (1 << c)) down.push(`${row},${c}`);
    }
    const s = down.join(' ');
    if (s !== prev) { console.log(((Date.now() - t0) / 1000).toFixed(2) + 's  down: ' + (s || '-')); prev = s; }
    sleep(20);
  }
} finally { close(); }
