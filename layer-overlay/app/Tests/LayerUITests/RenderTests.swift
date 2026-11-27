import Foundation
import LayerCore
import LayerUI
import Testing

/// Renders the overlay for each Corne layer to PNG. Set SNAPSHOT_DIR to keep them for a look.
@Suite struct RenderTests {
    static let keymapURL = URL(fileURLWithPath: #filePath)
        .deletingLastPathComponent().deletingLastPathComponent()
        .appendingPathComponent("LayerCoreTests/Fixtures/corne-v4.json")

    func keymap() throws -> Keymap {
        struct F: Decodable { var keymap: [[[UInt16]]] }
        let f = try JSONDecoder().decode(F.self, from: Data(contentsOf: Self.keymapURL))
        return Keymap(layers: f.keymap.map { $0.flatMap { $0 } }, rows: 8, cols: 7)
    }

    @MainActor
    @Test(arguments: [(1, UInt32(0x2)), (2, UInt32(0x6)), (3, UInt32(0x4 | 0x8))])
    func rendersEachLayer(layer: Int, state: UInt32) throws {
        let profile = try #require(BoardProfile.bundled().first { $0.id == "corne-v4" })
        let content = OverlayContent.make(profile: profile, keymap: try keymap(), layer: layer, state: state, ghosts: true)
        let png = try #require(renderPNG(content))
        #expect(png.count > 10_000)
        if let dir = ProcessInfo.processInfo.environment["SNAPSHOT_DIR"] {
            try png.write(to: URL(fileURLWithPath: dir).appendingPathComponent("corne-\(content.layerName.lowercased()).png"))
        }
    }
}
