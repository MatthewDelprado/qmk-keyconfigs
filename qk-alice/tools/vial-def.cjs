// Read a Vial board's compressed keyboard definition: node vial-def.cjs OUT.xz
const fs = require('fs'); const { open } = require('./via.cjs');
const { cmd, close } = open();
try {
  const pv = cmd([0x01]); console.log('VIA protocol', pv[1] << 8 | pv[2]);
  const id = cmd([0xfe, 0x00]);
  const vp = Buffer.from(id).readUInt32LE(0);
  console.log('Vial protocol', vp, 'uid', Buffer.from(id.slice(4, 12)).toString('hex'));
  const sz = Buffer.from(cmd([0xfe, 0x01])).readUInt32LE(0); console.log('definition bytes', sz);
  const out = [];
  for (let blk = 0; out.length < sz; blk++) { const r = cmd([0xfe, 0x02, blk & 255, blk >> 8]); out.push(...r.slice(0, 32)); }
  fs.writeFileSync(process.argv[2], Buffer.from(out.slice(0, sz)));
  console.log('layers', cmd([0x11])[1]);
} finally { close(); }
