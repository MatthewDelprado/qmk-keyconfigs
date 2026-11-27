import Foundation

/// The VIA commands the app needs (the same ones qk-alice/tools/dump.cjs uses). 32-byte reports.
/// Read-only: nothing here writes to the keyboard.
public enum VIA {
    public static let reportSize = 32
    public static let chunkSize = 28

    public static func pad(_ b: [UInt8]) -> [UInt8] { b + Array(repeating: 0, count: reportSize - b.count) }
    public static func protocolVersion() -> [UInt8] { pad([0x01]) }
    public static func layerCount() -> [UInt8] { pad([0x11]) }
    public static func getBuffer(offset: Int, size: Int) -> [UInt8] {
        pad([0x12, UInt8(offset >> 8), UInt8(offset & 0xFF), UInt8(size)])
    }

    /// True when `reply` answers `request` (same command byte and, for buffer reads, same offset).
    public static func isReply(_ reply: [UInt8], to request: [UInt8]) -> Bool {
        guard reply.count >= 4, reply[0] == request[0] else { return false }
        if request[0] == 0x12 { return reply[1] == request[1] && reply[2] == request[2] && reply[3] == request[3] }
        return true
    }

    public static func parseProtocolVersion(_ r: [UInt8]) -> Int? {
        guard r.count >= 3, r[0] == 0x01 else { return nil }
        return Int(r[1]) << 8 | Int(r[2])
    }
    public static func parseLayerCount(_ r: [UInt8]) -> Int? {
        guard r.count >= 2, r[0] == 0x11 else { return nil }
        return Int(r[1])
    }

    public static func chunks(total: Int) -> [(offset: Int, size: Int)] {
        stride(from: 0, to: total, by: chunkSize).map { ($0, Swift.min(chunkSize, total - $0)) }
    }
}

/// A keymap read from the board: keycodes per layer, row-major (row * cols + col).
public struct Keymap: Equatable, Sendable {
    public var layers: [[UInt16]]
    public var rows: Int
    public var cols: Int
    public init(layers: [[UInt16]], rows: Int, cols: Int) { self.layers = layers; self.rows = rows; self.cols = cols }

    /// Decodes the dynamic keymap buffer: big-endian UInt16 per key.
    public init(buffer: [UInt8], layers: Int, rows: Int, cols: Int) {
        let per = rows * cols
        self.init(layers: (0..<layers).map { l in
            (0..<per).map { i in
                let o = (l * per + i) * 2
                return UInt16(buffer[o]) << 8 | UInt16(buffer[o + 1])
            }
        }, rows: rows, cols: cols)
    }

    public func code(layer: Int, row: Int, col: Int) -> UInt16 {
        guard layer < layers.count, row < rows, col < cols else { return 0 }
        return layers[layer][row * cols + col]
    }
}

/// Reads a keymap over any request/reply transport. `send` returns the reply or nil on timeout.
public enum KeymapReader {
    public enum ReadError: Error, Equatable { case noReply(command: UInt8), badReply }

    public static func read(rows: Int, cols: Int, send: ([UInt8]) throws -> [UInt8]?) throws -> Keymap {
        guard let r = try send(VIA.layerCount()) else { throw ReadError.noReply(command: 0x11) }
        guard let layers = VIA.parseLayerCount(r), layers > 0 else { throw ReadError.badReply }
        var buf: [UInt8] = []
        for c in VIA.chunks(total: layers * rows * cols * 2) {
            guard let reply = try send(VIA.getBuffer(offset: c.offset, size: c.size)) else { throw ReadError.noReply(command: 0x12) }
            buf += reply[4..<(4 + c.size)]
        }
        return Keymap(buffer: buf, layers: layers, rows: rows, cols: cols)
    }
}
