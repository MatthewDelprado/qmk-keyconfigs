#!/bin/sh
# Builds the Corne v4.1 firmware: foostan's factory Vial keymap plus the layer report.
#   VIAL_QMK      vial-qmk checkout (default ~/Documents/git/vial-qmk)
#   KBD_FIRMWARE  foostan/kbd_firmware checkout (default ~/Documents/git/kbd_firmware)
# First time on a new machine:
#   git clone https://github.com/vial-kb/vial-qmk ~/Documents/git/vial-qmk
#   (cd ~/Documents/git/vial-qmk && git checkout dd43959 && make git-submodule)
#   git clone https://github.com/foostan/kbd_firmware ~/Documents/git/kbd_firmware
# Output: corne_v4_1_matt.uf2 next to this script. Flash it to BOTH halves.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SHARED="$HERE/../../layer-overlay/firmware"
V=${VIAL_QMK:-$HOME/Documents/git/vial-qmk}
F=${KBD_FIRMWARE:-$HOME/Documents/git/kbd_firmware}
[ -d "$V/quantum" ] || { echo "No vial-qmk at $V (see the top of this script)" >&2; exit 1; }
[ -d "$F/keyboards/crkbd/qmk/qmk_firmware" ] || { echo "No kbd_firmware at $F (see the top of this script)" >&2; exit 1; }

# foostan's build: his Corne tree goes in as keyboards/tmp/crkbd (rsync keeps the build fast).
mkdir -p "$V/keyboards/tmp/crkbd"
rsync -a --delete --exclude .build --exclude keymaps "$F/keyboards/crkbd/qmk/qmk_firmware/" "$V/keyboards/tmp/crkbd/"
KM="$V/keyboards/tmp/crkbd/keymaps/matt"
rm -rf "$KM"; mkdir -p "$KM"
cp "$HERE"/keymap/* "$KM/"
cp "$SHARED/layer_report.c" "$SHARED/layer_report.h" "$KM/"

cd "$V"
qmk compile -kb tmp/crkbd/rev4_1/standard -km matt
cp .build/tmp_crkbd_rev4_1_standard_matt.uf2 "$HERE/corne_v4_1_matt.uf2" 2>/dev/null || cp tmp_crkbd_rev4_1_standard_matt.uf2 "$HERE/corne_v4_1_matt.uf2"
echo "Built $HERE/corne_v4_1_matt.uf2"
