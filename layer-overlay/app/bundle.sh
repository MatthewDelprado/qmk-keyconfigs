#!/bin/sh
# Builds "Layer Overlay.app" into ./build. Needs Xcode or the Swift toolchain (Swift 5.10+), macOS 14+.
#   ./bundle.sh            build only (into ~/Library/Caches/layer-overlay)
#   ./bundle.sh --install  also copy it to ~/Applications (needed for "Open at login")
# Builds outside the repo: when Documents syncs with iCloud, new folders get Finder attributes that
# code signing rejects. Set LAYER_OVERLAY_BUILD to build somewhere else.
set -eu
cd "$(dirname "$0")"
OUT="${LAYER_OVERLAY_BUILD:-$HOME/Library/Caches/layer-overlay}"
swift build -c release --scratch-path "$OUT/build"
BIN=$(swift build -c release --scratch-path "$OUT/build" --show-bin-path)
APP="$OUT/Layer Overlay.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN/LayerOverlay" "$APP/Contents/MacOS/"
cp -R "$BIN/LayerOverlay_LayerCore.bundle" "$APP/Contents/Resources/"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleIdentifier</key><string>local.matt-keyboards.layer-overlay</string>
  <key>CFBundleName</key><string>Layer Overlay</string>
  <key>CFBundleDisplayName</key><string>Layer Overlay</string>
  <key>CFBundleExecutable</key><string>LayerOverlay</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>0.1</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>14.0</string>
  <key>LSUIElement</key><true/>
</dict></plist>
PLIST
# Ad-hoc signature: fine for your own Macs, not for sharing.
codesign --force --deep --sign - --options runtime --timestamp=none "$APP"
codesign --verify --strict "$APP"
echo "Built $APP"
if [ "${1:-}" = "--install" ]; then
    mkdir -p "$HOME/Applications"
    rm -rf "$HOME/Applications/Layer Overlay.app"
    cp -R "$APP" "$HOME/Applications/"
    echo "Installed to ~/Applications/Layer Overlay.app"
fi
