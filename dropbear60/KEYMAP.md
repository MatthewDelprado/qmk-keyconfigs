# Dropbear 60 (solder PCB)

Runs QMK's `kkatano/bakeneko60` definition (atmega32u4, atmel-dfu). The board shipped with
Bakeneko 60 firmware using USB ID `0x6A6A:0xCBDC`; `config.h` keeps that vendor ID so VIA
still matches `firmware/dropbear60-solder-via-v2.json` (load it in VIA → Settings → Design).

Layout: tsangan bottom row, split backspace, split right shift.

## Layers

The master keymap (same as the Rama Works Kara), flashed 2026-11-25. Printout: `KEYMAP.pdf`
(regenerate with `python3 tools/gen_print.py backup/<dump>.json KEYMAP.html`).

- **0 Base**: home row mods (A ⇧, S ⌃, D ⌥, F ⌘ / J ⌘, K ⌥, L ⌃, ; ⇧), Hyper on Caps-position Esc, Enter, G and H,
  Space = hold Nav, key right of RShift = Fn. HHKB bottom row: ⌥ ⌘ Space ⌘ ⌃.
- **1 Fn**: symbols on the letter rows with mirrored brackets, HHKB arrows on [ ; ' /, media on F7–F12, ⏭ on Bksp, ⏯ on Enter, and in the corner (Right Shift Vol +, right ⌘ Mute, ⌃ Vol −), ? on comma, Ins/Del.
- **2 Nav** (hold Space): Backspace on Esc, arrows, Home/End, PgUp/PgDn, ⌘H on Tab; numpad on the right, . on right ⌘. Both Shifts stay Shift.
- **3**: spare (no lighting on this board).

Backups in `backup/`: the live VIA keymap before the master (`dropbear-via-backup-2026-11-24.json`), the old
`keymap.c`, and the board read back after flashing (`dropbear-via-master-2026-11-25.json`). The old firmware is
`firmware/kkatano_bakeneko60_matt.pre-master-2026-11-24.hex`. `qk-alice/tools/dump.cjs` reads the board over VIA:
`VID=0x6A6A PID=0xCBDC ROWS=5 COLS=15 node dump.cjs out.json`.

## Tap-hold tuning

- `FLOW_TAP_TERM 150` — a home row mod pressed within 150 ms of the previous key is always
  a tap. Fixes K+Space firing Option+Space while typing. Tap-hold otherwise uses QMK defaults
  (200 ms tapping term, no Permissive Hold / Hold On Other Key Press — don't add those here,
  they make home row mods misfire on rolls).

## Flashing

1. Hold the top-left key (Esc) while plugging in to enter the bootloader.
2. `qmk flash -kb kkatano/bakeneko60 -km matt` (uses dfu-programmer).

Flashing a new build resets VIA's stored keymap to the layers in `keymap.c`. To switch to the
non-home-row layout afterwards, load the saved layout JSON in VIA → Save + Load.

`firmware/pre-flash_board_keymap_dump.json` is the raw keymap read off the board before the
first custom flash (VIA protocol 9, pre-2023 keycode numbering).
