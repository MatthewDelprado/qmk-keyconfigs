# Corne v4.1 firmware: factory Vial + layer report

foostan's factory Vial firmware (`foostan/kbd_firmware`, built in `vial-kb/vial-qmk` at `dd43959`) with one addition:
it reports layer changes on the QMK console for the Layer Overlay app (`../../layer-overlay`). Everything Vial sees is
unchanged: same keyboard ID (`89362ac7fad88945`), same layout file, 6 layers, VialRGB, Tab+Q unlock.

- `keymap/`: foostan's `vial` keymap plus `housekeeping_task_user()` → `layer_report_task()`, and `CONSOLE_ENABLE`.
- `build.sh`: builds `corne_v4_1_matt.uf2` (the top of the script says how to set it up on a new Mac).

## Flashing

**Flashing wipes the keymap, macros and lighting** (Vial resets its storage on any new build). Put them back afterwards.

1. Full backup of each half first, in its bootloader: `picotool save -a backup/corne-<flash id>-full.bin`
   (`brew install picotool`). It copies the firmware and the settings together.
2. Bootloader, half with the USB cable: no button needed. From `qk-alice/tools`:
   `VID=0x4653 PID=0x0004 node ../../layer-overlay/tools/vial-bootloader.cjs $PWD`, then hold Tab + Q for ~8 s
   (let go early and the count restarts). An `RPI-RP2` drive appears; `picotool info -d` shows which chip it is
   (left `E66748911B471522`, right `C4602C925B1D192D`).
3. `cp corne_v4_1_matt.uf2 /Volumes/RPI-RP2/`. The half restarts by itself in about 2 s.
4. Move the cable to the other half. **While the halves run different firmware they don't talk**: each half types only
   its own keys, so Tab + Q can't reach the right half. Use bootmagic instead: hold the key in the Q spot of that half
   (Q on the left, **P** on the right) while plugging the cable in. That also clears the half's settings, which is fine
   here. Flash it the same way.
5. Put the keymap back. Unlock first (`vial-bootloader.cjs $PWD --unlock-only`, hold Tab + Q; this also proves the
   halves talk again), then `VID=0x4653 PID=0x0004 ROWS=8 COLS=7 node apply.cjs ../../corne-v4/corne-v4-matt-target-split-thumbs.json`.
   Dump it to `../backup/` and compare. The macro area is smaller in this build (2,095 bytes, was 2,291); the macros are the same.

Flashed 2026-11-27: both halves, backups in `backup/`, readback in `../backup/corne-v4-vial-split-thumbs-layer-report-2026-11-27.json`.

Going back to stock: foostan's `crkbd_rev4_1_standard_vial.uf2` (in `kbd_firmware`), or `picotool load -x` the backup.

## Checklist with the board

1. Vial ID unchanged: `VID=0x4653 PID=0x0004 node ../../layer-overlay/tools/vial-id.cjs $PWD` (from `qk-alice/tools`).
2. Reports arrive: `node ../../layer-overlay/tools/listen-layer.cjs`, hold a Space thumb → `LAYER 1 00000002`;
   add the other Space → `LAYER 2 00000006`; let go → `LAYER 0 00000000`. Taps print nothing.
3. Typing feels the same with no app listening (the first report with nobody listening can wait up to 0.1 s).
4. Vial still opens, reads and saves; `dump.cjs` still works.
5. The app: hold 2 s → nothing, 3 s → overlay; swap layers while it shows; let go → it fades. It appears over a
   full-screen app and on every Space, clicks go through it, and typing focus never moves.
6. Unplug and replug → the app reconnects and reads the keymap again.
