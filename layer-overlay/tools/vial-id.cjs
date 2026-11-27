// Read-only: Vial "get keyboard id" (0xFE 0x00). Usage, from qk-alice/tools: VID=0x4653 PID=0x0004 node ../../layer-overlay/tools/vial-id.cjs $PWD
process.chdir(process.argv[2]);
const { open } = require(process.argv[2] + '/via.cjs');
const { cmd, close } = open();
try {
  const r = cmd([0xFE, 0x00]);
  const proto = r[0] | r[1] << 8 | r[2] << 16 | r[3] << 24;
  console.log('vial protocol', proto, 'uid', Buffer.from(r.slice(4, 12)).toString('hex'));
} finally { close(); }
