// Puts a Vial board into its bootloader with no buttons: unlocks Vial (hold the unlock keys,
// Tab + Q on the Corne, for about 5 s), then sends VIA's bootloader jump (0x0B).
// Reconnects if the board drops off USB for a moment. Gives up after 300 s.
// From qk-alice/tools: VID=0x4653 PID=0x0004 node ../../layer-overlay/tools/vial-bootloader.cjs $PWD [--unlock-only]
// --unlock-only leaves the board unlocked (until it restarts), e.g. so apply.cjs can write macros.
const { open } = require(process.argv[2] + '/via.cjs');
const sleep = ms => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
const t0 = Date.now();
let dev = null, started = false, last = -1;
function call(bytes) {
  for (;;) {
    if (Date.now() - t0 > 300000) { console.log('Gave up after 300 s.'); process.exit(1); }
    try {
      if (!dev) { dev = open(); if (started) { dev.cmd([0xfe, 0x06]); console.log('reconnected, unlock restarted'); } }
      return dev.cmd(bytes);
    } catch (e) {
      console.log('board not answering (' + e.message.split(':').pop().trim() + '), retrying');
      try { dev && dev.close(); } catch (_) {}
      dev = null; sleep(500);
    }
  }
}
let s = call([0xfe, 0x05]);
if (!s[0]) {
  call([0xfe, 0x06]); started = true;
  console.log('Hold the unlock keys (Tab + Q) now...');
  while (!s[0]) {
    sleep(100);
    s = call([0xfe, 0x07]);
    if (s[2] !== last && s[2] % 10 === 0) { console.log('  counter', s[2]); last = s[2]; }
  }
}
if (process.argv[3] === '--unlock-only') { console.log('Unlocked.'); try { dev.close(); } catch (e) {} process.exit(0); }
console.log('Unlocked. Jumping to the bootloader.');
try { dev.cmd([0x0b]); } catch (e) { /* it leaves USB straight after replying */ }
try { dev.close(); } catch (e) {}
console.log('Sent.');
