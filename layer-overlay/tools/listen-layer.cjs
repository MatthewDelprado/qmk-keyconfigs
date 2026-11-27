// Hardware check: print layer reports from the Corne's QMK console interface
// (usage page 0xFF31, usage 0x74) while you hold layer keys. Read-only.
// Run from matt-keyboards/qk-alice/tools so node-hid resolves:
//   cd matt-keyboards/qk-alice/tools && node ../../layer-overlay/tools/listen-layer.cjs [VID PID]
const HID = require(require.resolve('node-hid', { paths: [process.cwd()] }));
const VID = +(process.argv[2] || 0x4653), PID = +(process.argv[3] || 0x0004);

const info = HID.devices().find(d => d.vendorId === VID && d.productId === PID && d.usagePage === 0xff31 && d.usage === 0x74);
if (!info) { console.error('Console interface not found (board unplugged, or firmware built without CONSOLE_ENABLE).'); process.exit(1); }

const dev = new HID.HID(info.path);
let line = '', t0 = Date.now();
dev.on('data', buf => {
  for (const b of buf) {
    if (b === 0) continue;                 // reports are zero-padded to 32 bytes
    if (b === 0x0a) { if (line.startsWith('LAYER ')) console.log(`${((Date.now() - t0) / 1000).toFixed(3)}s  ${line}`); line = ''; }
    else line += String.fromCharCode(b);
  }
});
dev.on('error', e => { console.error(e.message); process.exit(1); });
console.log('Listening. Hold a layer key; expect "LAYER 1 00000002" on press and "LAYER 0 00000000" on release. Ctrl-C to stop.');
