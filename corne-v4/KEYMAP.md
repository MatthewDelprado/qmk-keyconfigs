# Corne v4 (foostan, v4.1, Vial)

USB 0x4653:0x0004, Vial protocol 6 (modern QMK keycodes), 8x7 matrix, 6 layers, VialRGB.
Edited live over VIA with the tools in `../qk-alice/tools` (VID=0x4653 PID=0x0004 ROWS=8 COLS=7); no firmware build.

- `backup/corne-v4-vial-backup-2026-11-25.json`: the factory keymap as it arrived (picture: `KEYMAP-current.pdf`).
  Put it back with `node ../qk-alice/tools/apply.cjs backup/corne-v4-vial-backup-2026-11-25.json`.
- `corne-v4-matt-target.json`: the master keymap, built by `tools/build_master.py` (picture: `PROPOSAL.pdf`).
  On the board since 2026-11-25 for testing; readback in `backup/corne-v4-vial-master-2026-11-25.json`.

Hyper on G and H as well as Esc and Enter (master rule, 2026-11-25).
Layers: 0 Base, 1 Fn (right middle thumb), 2 Nav (either inner thumb, the other is Backspace), 3 Lighting (Fn + inner thumb).
Layers 4 and 5 are the factory ones and nothing reaches them.
Home row mods run on Vial's tapping term (200 ms); this firmware has no Flow Tap.
