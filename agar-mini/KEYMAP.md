# KBDfans Agar Mini BLE: master keymap (ZMK Studio)

The Agar Mini runs ZMK, not QMK. The keymap lives on the board and is edited live through ZMK Studio (zmk.studio in Chrome, over USB). Nothing here is compiled.

- `KEYMAP.pdf` / `KEYMAP.html`: printable sheet. Page 1 is the current layout, page 2 the layout before 2026-11-22.
- `agar-mini-matt-v3.json`: full dump of the board as it is now (`agar-mini-matt-2026-11-22.json` is the earlier version with right Space = Fn).
- `agar-mini-matt-target.json`: the master layout for layers 0–4, as `[behaviorId, param1, param2]` per key.
- `backup/`: the board as it was before, raw (`.json`), readable (`.txt`), and as a restore target.

## Layers

| ZMK layer | Name | Reached by |
|---|---|---|
| 0 | Base | always on |
| 1 | unused | a leftover Fn copy |
| 2 | Nav | hold either Space; the other Space taps Bksp and holds Fn. Del is on the Bksp key, = beside it; both Shifts stay Shift |
| 3 | Fn (symbols, arrows, media) | hold the 1u Fn key right of Right Shift, or hold both Spaces |
| 4 | System (USB, Bluetooth 1–3, media) | Fn + either Space; stock apart from BT 3 on L, with the arrows, Bksp, Home and End cleared |

Nav sits below Fn on purpose (target changed 2026-11-27; before, Fn was layer 1 and Nav layer 3): when both are on, the higher
layer wins, so holding one Space for Nav and then the other for Fn gives the whole Fn layer. `KEYMAP.pdf` shows the board as it
was last read; rebuild it after writing the target.

Media on Fn: Enter ⏯, Bksp ⏭, Right Shift Vol+, right ⌃ Vol−, right ⌘ Mute. ? is Fn + comma.

Brackets on Fn: [ ] on R U, { } on D K, ( ) on F J. $ is Fn + S and / is Fn + the key after P. (The master puts [ ] on S L; the Agar differs because its Fn arrows take L.)

## Tools (`tools/`)

Talk to the board over ZMK Studio's serial RPC; close zmk.studio first, since only one app can hold the port.

```bash
cd ~/Documents/git/matt-keyboards/agar-mini/tools && ./setup.sh   # once: installs + patches the client
node dump.mjs out.json && python3 decode.py out.json                 # read the board
node apply.mjs ../agar-mini-matt-target.json                         # write only the keys that differ, then save
python3 gen_print.py NOW.json ../backup/agar-mini-zmk-backup-2026-11-22.json ../KEYMAP.html
```

The board must be unlocked in ZMK Studio for writes.

## Restore the old layout

1. In zmk.studio, **Restore Stock Settings**. This brings back the keys only firmware can set (mouse keys on layer 1, striped keys on layer 4).
2. Close zmk.studio, then `node apply.mjs ../backup/agar-mini-restore-target.json`.
