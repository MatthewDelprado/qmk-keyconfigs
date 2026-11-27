// swift-tools-version: 5.10
// Layer Overlay: shows the active layer of a QMK keyboard after you hold it for a while.
// Build: ./bundle.sh (needs Xcode or the Swift toolchain, macOS 14+). Test: swift test.
import PackageDescription

let package = Package(
    name: "LayerOverlay",
    platforms: [.macOS(.v14)],
    products: [.executable(name: "LayerOverlay", targets: ["LayerOverlay"])],
    targets: [
        // Pure logic: console parsing, hold timing, VIA protocol, labels, layouts. No AppKit or IOKit.
        .target(name: "LayerCore", resources: [.copy("Resources/boards")]),
        // SwiftUI overlay and PNG rendering.
        .target(name: "LayerUI", dependencies: ["LayerCore"]),
        // The menu-bar app: HID, panel, menu.
        .executableTarget(name: "LayerOverlay", dependencies: ["LayerCore", "LayerUI"],
                          linkerSettings: [.linkedFramework("IOKit"), .linkedFramework("ServiceManagement")]),
        .testTarget(name: "LayerCoreTests", dependencies: ["LayerCore"], resources: [.copy("Fixtures")]),
        .testTarget(name: "LayerUITests", dependencies: ["LayerUI", "LayerCore"]),
    ]
)
