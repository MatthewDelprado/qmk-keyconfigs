# Neo Ergo (Neo Studio, wired)

USB 0x4E45:0x4552 ("NEO ERGO WIRED"), plain VIA (protocol 12, not Vial), 5x15 matrix, 4 layers, rgblight underglow.
Edited live over VIA with the tools in `../qk-alice/tools` (VID=0x4e45 PID=0x4552 ROWS=5 COLS=15); no firmware build.

- `backup/neo-ergo-wired-via-definition.json`: the VIA definition (layout + matrix). Neo Studio doesn't publish it;
  this copy is from github.com/m00nst3r/keyboards-via-files (`neo_ergo_wired.json`), checked against the board's
  USB ids and matrix. Load it in VIA's Design tab to edit the board there.
- Layout options on the board: 41 = split Backspace, 60%-mode Right Shift (1.75u Shift + 1u Fn), 2.25u split spaces,
  1.5u bottom-right pair.
- `backup/neo-ergo-via-backup-2026-11-26.json`: the keymap before the master (picture: `KEYMAP-current.pdf`).
  Put it back with `node ../qk-alice/tools/apply.cjs backup/neo-ergo-via-backup-2026-11-26.json`.
- `neo-ergo-matt-target.json`: the master keymap, built by `tools/build_master.py` (proposal: `PROPOSAL.pdf`).
  On the board since 2026-11-26; current readback in `backup/neo-ergo-via-master-2026-11-27.json` (picture: `KEYMAP.pdf`,
  orange = changed from the old keymap). The 2026-11-26 readback is the first version, before Nav and Fn swapped.

Layers: 0 Base, 1 Nav (hold either Space half), 2 Fn (key right of Right Shift, or the left column's bottom two keys),
3 Lighting (Fn + Space). With one Space half held for Nav, the other half is Backspace on a tap and Fn on a hold.
Nav sits below Fn on purpose: when both are on, the higher layer wins, so holding both halves gives the whole Fn layer.
To repeat Backspace from Nav, tap the other half and then hold it (or hold the Backspace at Nav's top left).
Board-only keys kept from before: the left column (Vol +, Vol −, ⏯ / hold Fn, Fn), ⌃ bottom-left, the right-hand B,
and ← (hold ⌥) / → (hold ⌃) bottom-right. Macro 0 (⌥ + `) is still stored but not on any key.
Dropped from the old Fn layer: F7–F9, F11, F12, PrtSc, Caps. VIA can't set Flow Tap, so the home row mods run on the
firmware's own tapping term.
