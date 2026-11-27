#!/bin/sh
# Builds "Layer Overlay.app" into ./build. Needs Xcode or the Swift toolchain (Swift 5.10+), macOS 14+.
#   ./bundle.sh            build only
#   ./bundle.sh --install  also copy it to ~/Applications (needed for "Open at login")
set -eu
cd "$(dirname "$0")"
swift build -c release
BIN=$(swift build -c release --show-bin-path)
APP="build/Layer Overlay.app"
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
