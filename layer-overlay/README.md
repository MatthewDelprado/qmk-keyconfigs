# Layer Overlay

Hold a layer on a QMK keyboard for a few seconds (3 by default) and a Mac overlay shows that layer's keys,
with the base layer's legends as small ghosts in each corner. Let go and it fades out.

Two parts:

- **Firmware** (`firmware/`): `layer_report.c` sends one line on the QMK console whenever the layer changes,
  `LAYER <highest> <state hex>`, e.g. `LAYER 2 00000006`. The console is its own USB interface (usage page 0xFF31),
  so Vial, VIA and the Node scripts in `qk-alice/tools` never see it. Works on any QMK board, Vial or VIA.
- **Mac app** (`app/`): a menu-bar app. It listens on the console, and reads the keymap once over the VIA/Vial
  interface when the board connects (opening it only for the read, so Vial keeps working). Labels and key positions
  come from the board itself and its layout file, so edits in Vial show up after "Reload keymap" or a replug.

## Firmware: adding it to a keymap

1. Copy `firmware/layer_report.c` and `layer_report.h` into the keymap folder (the board's `build.sh` can do it).
2. `rules.mk`: `CONSOLE_ENABLE = yes` and `SRC += layer_report.c`.
3. `keymap.c`: `#include "layer_report.h"` and call `layer_report_task()` from `housekeeping_task_user()`.

Tests run in QMK's own host test framework: `firmware/run-tests.sh` (needs Homebrew gcc; uses `~/Documents/git/vial-qmk`
or `VIAL_QMK`). To watch a real board: `cd ../qk-alice/tools && node ../../layer-overlay/tools/listen-layer.cjs`.

Boards using it: Corne v4 (`../corne-v4/firmware/build.sh`).

## Mac app

```sh
cd app
./test.sh                # the tests: console parsing, hold timing, VIA reads, labels, layout, overlay renders
./bundle.sh --install    # builds "Layer Overlay.app" and copies it to ~/Applications
```

Needs Xcode (or the Swift 5.10+ toolchain) and macOS 14+. Both scripts build in `~/Library/Caches/layer-overlay`,
outside the repo, because iCloud-synced folders get Finder attributes that code signing rejects; plain `swift test`
in the repo can fail with "resource fork, Finder information, or similar detritus". Nothing in it is tied to one Mac, so it builds the same
anywhere the repo is cloned. It's ad-hoc signed, which is fine for your own Macs.

Menu: which boards are connected, which layers get the overlay, the hold delay (1–5 s), ghosts on/off, top or bottom of the screen, a preview of each
layer, reload keymap, open at login.

Command line, for testing without the menu:

- `LayerOverlay --listen corne-v4 [seconds]` connects to the board's console the same way the app does and prints what arrives.
- `LayerOverlay --dump-keymap corne-v4` reads the keymap from the board (read-only) and prints JSON.
- `LayerOverlay --render corne-v4 2 out.png keymap.json` draws the overlay for a layer to a PNG.
- `SNAPSHOT_DIR=/some/dir ./test.sh` keeps the rendered overlays from the tests.

### Adding a board

Put two files in `app/Sources/LayerCore/Resources/boards/`:

- `<id>.layout.json`: the board's VIA or Vial definition (the JSON with `matrix` and `layouts.keymap`).
- `<id>.profile.json`: name, USB vendor and product IDs, the layout file name, and names for layers and macros
  (see `corne-v4.profile.json`). Use `layoutOptions` if the board has layout choices in VIA.

Then flash the board with `layer_report.c` in its keymap.

## Testing

- **Firmware**: 5 host tests. A held layer-tap reports the layer, then base on release; a tap reports nothing;
  stacked layers report the highest one plus the full state; a held layer sends once.
- **App**: labels and key positions are checked against `corne-v4/tools/gen_print.py` (the code behind the printed
  keymaps) on every key of the real keymap. Fixtures: `app/Tests/LayerCoreTests/Fixtures/make_fixtures.py`.
  The hold timing is tested with times passed in (2.9 s shows nothing, 3.0 s shows it), and the controller is tested
  end to end with console bytes in and overlay calls out. A pretend board answers the VIA keymap reads.
- **By hand, with the board**: see the checklist in `../corne-v4/firmware/README.md`. The USB side of the app has no
  unit tests (a fake USB device needs an Apple entitlement), so `--listen` and the log are how to check it:
  `log stream --predicate 'subsystem == "local.matt-keyboards.layer-overlay"'`.

## Tools (`tools/`, run from `qk-alice/tools` so node-hid loads)

- `listen-layer.cjs`: prints the layer messages from the console.
- `vial-id.cjs`: prints the Vial protocol and keyboard ID (read-only).
- `vial-bootloader.cjs $PWD [--unlock-only]`: unlocks Vial (hold the unlock keys, Tab + Q on the Corne) and jumps to
  the bootloader, so no button is needed. `--unlock-only` just unlocks, e.g. before `apply.cjs` writes macros.
- `matrix-watch.cjs $PWD`: prints raw switch presses (needs Vial unlocked). Tells a dead switch from a firmware fault.
