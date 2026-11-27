#!/bin/sh
# Runs the tests. Builds outside the repo: when Documents syncs with iCloud, new folders get Finder
# attributes that code signing rejects ("resource fork, Finder information, or similar detritus").
set -eu
cd "$(dirname "$0")"
exec swift test --scratch-path "${LAYER_OVERLAY_BUILD:-$HOME/Library/Caches/layer-overlay}/build" "$@"
