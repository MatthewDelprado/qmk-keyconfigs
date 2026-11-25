// Minimal VIA / Vial raw-HID client for the QK Alice (USB 0x4F57:0x4110).
// Every request is a 32-byte report; the board echoes the command byte back.
const HID = require('node-hid');

const VID = +(process.env.VID || 0x4f57), PID = +(process.env.PID || 0x4110);

function open() {
  const info = HID.devices().find(d => d.vendorId === VID && d.productId === PID && d.usagePage === 0xff60 && d.usage === 0x61);
  if (!info) throw new Error('Raw HID interface not found. Is the board plugged in by USB?');
  const dev = new HID.HID(info.path);
  function cmd(bytes, timeout = 1000) {
    const buf = new Array(32).fill(0);
    bytes.forEach((b, i) => (buf[i] = b));
    dev.write([0x00, ...buf]);
    const r = dev.readTimeout(timeout);
    if (!r || !r.length) throw new Error('no reply to command 0x' + bytes[0].toString(16));
    return r;
  }
  return { cmd, close: () => dev.close() };
}

module.exports = { open };
