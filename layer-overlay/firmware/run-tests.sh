#!/bin/sh
# Runs the layer_report host tests inside a QMK or vial-qmk tree.
#   VIAL_QMK  tree to run in (default ~/Documents/git/vial-qmk)
# Needs Homebrew gcc (Apple clang fails on QMK's own test code); set GCC_VER to pick one.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TREE=${VIAL_QMK:-$HOME/Documents/git/vial-qmk}
GCC_VER=${GCC_VER:-$(ls /opt/homebrew/bin/gcc-[0-9]* 2>/dev/null | sed 's/.*gcc-//' | sort -n | tail -1)}
[ -n "$GCC_VER" ] || { echo "Install Homebrew gcc: brew install gcc" >&2; exit 1; }
rm -rf "$TREE/tests/layer_report"
cp -R "$HERE/tests/layer_report" "$TREE/tests/layer_report"
cp "$HERE/layer_report.c" "$HERE/layer_report.h" "$TREE/tests/layer_report/"
cd "$TREE"
trap 'rm -rf "$TREE/tests/layer_report"' EXIT
make test:layer_report CC=/opt/homebrew/bin/gcc-$GCC_VER CXX=/opt/homebrew/bin/g++-$GCC_VER LD=/opt/homebrew/bin/g++-$GCC_VER
