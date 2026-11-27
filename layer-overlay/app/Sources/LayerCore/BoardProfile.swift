import Foundation

/// A keyboard the app knows: USB IDs, layout file and the names to show for layers and macros.
/// Profiles live in Resources/boards/<id>.profile.json next to <id>.layout.json (the VIA or Vial definition).
public struct BoardProfile: Sendable {
    public var id: String
    public var name: String
    public var vendorId: Int
    public var productId: Int
    public var layout: Layout
    public var labeler: KeyLabeler

    public init(id: String, name: String, vendorId: Int, productId: Int, layout: Layout, labeler: KeyLabeler) {
        self.id = id; self.name = name; self.vendorId = vendorId; self.productId = productId
        self.layout = layout; self.labeler = labeler
    }

    struct File: Decodable {
        var name: String
        var vendorId: String
        var productId: String
        var layout: String
        var layoutOptions: [String: Int]?
        var layerNames: [String: String]?
        var macroNames: [String: String]?
    }

    public static func load(id: String, from dir: URL) throws -> BoardProfile {
        let f = try JSONDecoder().decode(File.self, from: Data(contentsOf: dir.appendingPathComponent("\(id).profile.json")))
        func hex(_ s: String) -> Int { Int(s.replacingOccurrences(of: "0x", with: ""), radix: 16) ?? 0 }
        func ints<V>(_ d: [String: V]?) -> [Int: V] {
            Dictionary(uniqueKeysWithValues: (d ?? [:]).compactMap { k, v in Int(k).map { ($0, v) } })
        }
        let layout = try Layout(definition: Data(contentsOf: dir.appendingPathComponent(f.layout)), options: ints(f.layoutOptions))
        return BoardProfile(id: id, name: f.name, vendorId: hex(f.vendorId), productId: hex(f.productId), layout: layout,
                            labeler: KeyLabeler(layerNames: ints(f.layerNames), macroNames: ints(f.macroNames)))
    }

    /// Every profile bundled with the app.
    public static func bundled() -> [BoardProfile] {
        guard let dir = Bundle.module.url(forResource: "boards", withExtension: nil),
              let files = try? FileManager.default.contentsOfDirectory(atPath: dir.path) else { return [] }
        return files.filter { $0.hasSuffix(".profile.json") }.sorted()
            .compactMap { try? load(id: String($0.dropLast(".profile.json".count)), from: dir) }
    }
}
