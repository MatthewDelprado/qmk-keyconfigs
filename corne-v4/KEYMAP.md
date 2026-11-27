# Corne v4 (foostan, v4.1, Vial)

USB 0x4653:0x0004, Vial protocol 6 (modern QMK keycodes), 8x7 matrix, 6 layers, VialRGB.
Edited live over VIA with the tools in `../qk-alice/tools` (VID=0x4653 PID=0x0004 ROWS=8 COLS=7).
Since 2026-11-27 it runs our own build of the factory Vial firmware with a layer report for the Layer Overlay app
(`firmware/`, `../layer-overlay`); factory backups of both halves are in `firmware/backup/`.

- `backup/corne-v4-vial-backup-2026-11-25.json`: the factory keymap as it arrived (picture: `KEYMAP-current.pdf`).
  Put it back with `node ../qk-alice/tools/apply.cjs backup/corne-v4-vial-backup-2026-11-25.json`.
- `corne-v4-matt-target-standard-thumbs.json`: the master keymap with standard thumbs (⌥ ⌘ Space/Nav | Space/Nav Fn ⌘),
  closest to the other boards. Built by `tools/build_master.py BACKUP OUT standard` (picture: `PROPOSAL.pdf`);
  readback in `backup/corne-v4-vial-master-2026-11-25.json`.
- `corne-v4-matt-target-split-thumbs.json`: the same keymap with split thumbs, on the board for a trial since 2026-11-25:
  ⌘⌘, Space/Nav, Backspace | Enter (hold Fn), Space/Nav, ⇧⇧. The outer thumbs are Vial macros 0 and 1, which tap left ⌘ or left ⇧
  twice for double-tap hotkeys. Built with `... split` (picture: `KEYMAP-split-thumbs.pdf`); readback in
  `backup/corne-v4-vial-split-thumbs-2026-11-27.json` (the 2026-11-25 one is from before the Nav/Fn swap). Writing macros needs Vial unlocked (hold Tab + Q when asked).
- Switch between them with `node ../qk-alice/tools/apply.cjs <target>`; it also rewrites the macro buffer.

Hyper on G and H as well as Esc and Enter (master rule, 2026-11-25).
Layers: 0 Base, 1 Nav (hold a Space thumb), 2 Fn, 3 Lighting (from Fn). Standard thumbs: Fn is the right middle thumb, Nav either inner thumb.
With one Space thumb held for Nav, the other Space thumb is Backspace on a tap and Fn on a hold. Nav sits below Fn on purpose:
the higher layer wins, so holding both Space thumbs gives the whole Fn layer. (Fn and Nav swapped numbers on 2026-11-27; the
2026-11-25 readbacks in `backup/` are from before the swap.)
Split thumbs: Fn is held on the Enter thumb, Nav on either middle thumb, Lighting is Fn + the Backspace thumb. (The left inner thumb was Delete until 2026-11-27, when it was changed to Backspace in Vial.)
Layers 4 and 5 are the factory ones and nothing reaches them.
Home row mods run on Vial's tapping term (200 ms); this firmware has no Flow Tap.
