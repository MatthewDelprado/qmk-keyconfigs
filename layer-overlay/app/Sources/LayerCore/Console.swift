import Foundation

/// One layer report from the firmware: "LAYER <highest> <state hex>".
public struct LayerEvent: Equatable, Sendable {
    public var highest: UInt8
    public var state: UInt32
    public init(highest: UInt8, state: UInt32) { self.highest = highest; self.state = state }

    /// Parses a console line; anything else (other debug output) gives nil.
    public init?(line: String) {
        let parts = line.split(separator: " ")
        guard parts.count == 3, parts[0] == "LAYER",
              let h = UInt8(parts[1]), let s = UInt32(parts[2], radix: 16) else { return nil }
        self.init(highest: h, state: s)
    }
}

/// Turns QMK console reports (32 bytes, zero padded) into text lines.
public struct ConsoleLineReader: Sendable {
    private var pending: [UInt8] = []
    public static let maxLine = 256
    public init() {}

    public mutating func feed(_ report: [UInt8]) -> [String] {
        var lines: [String] = []
        for b in report where b != 0 {
            if b == 0x0A {
                lines.append(String(decoding: pending, as: UTF8.self).trimmingCharacters(in: .whitespacesAndNewlines))
                pending.removeAll(keepingCapacity: true)
            } else if pending.count < Self.maxLine {
                pending.append(b)
            }
        }
        return lines
    }
}
