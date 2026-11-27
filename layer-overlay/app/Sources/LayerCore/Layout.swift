import Foundation

/// One key's place, in key units, as KLE gives it: a w×h box at (x, y) turned r degrees about (rx, ry).
public struct KeyPlace: Equatable, Sendable {
    public var x, y, w, h, r, rx, ry: Double
    public var row, col: Int
    public init(x: Double, y: Double, w: Double, h: Double, r: Double, rx: Double, ry: Double, row: Int, col: Int) {
        self.x = x; self.y = y; self.w = w; self.h = h; self.r = r; self.rx = rx; self.ry = ry; self.row = row; self.col = col
    }

    public var corners: [(Double, Double)] {
        let a = r * .pi / 180
        return [(x, y), (x + w, y), (x, y + h), (x + w, y + h)].map { px, py in
            let dx = px - rx, dy = py - ry
            return (rx + dx * cos(a) - dy * sin(a), ry + dx * sin(a) + dy * cos(a))
        }
    }
}

/// A board's key positions, from the layout in its VIA or Vial definition (KLE format).
public struct Layout: Equatable, Sendable {
    public var keys: [KeyPlace]
    public var rows: Int
    public var cols: Int

    public enum ParseError: Error { case badJSON, noKeymap }

    /// `options[group]` picks a layout option per group (default 0), as in VIA's layout settings.
    public init(definition data: Data, options: [Int: Int] = [:]) throws {
        guard let root = try JSONSerialization.jsonObject(with: data) as? [String: Any] else { throw ParseError.badJSON }
        guard let layouts = root["layouts"] as? [String: Any], let kle = layouts["keymap"] as? [[Any]] else { throw ParseError.noKeymap }
        let matrix = root["matrix"] as? [String: Any]
        rows = matrix?["rows"] as? Int ?? 0
        cols = matrix?["cols"] as? Int ?? 0
        keys = Self.parse(kle, options: options)
    }

    public init(keys: [KeyPlace], rows: Int, cols: Int) { self.keys = keys; self.rows = rows; self.cols = cols }

    /// Port of the KLE walk in corne-v4/tools/gen_print.py.
    static func parse(_ kle: [[Any]], options: [Int: Int]) -> [KeyPlace] {
        var out: [KeyPlace] = []
        var x = 0.0, y = 0.0, r = 0.0, rx = 0.0, ry = 0.0, w = 1.0, h = 1.0
        func num(_ v: Any?) -> Double? { (v as? NSNumber)?.doubleValue }
        for row in kle {
            for item in row {
                if let d = item as? [String: Any] {
                    if let v = num(d["r"]) { r = v }
                    if let v = num(d["rx"]) { rx = v; x = v; y = ry }
                    if let v = num(d["ry"]) { ry = v; x = rx; y = v }
                    x += num(d["x"]) ?? 0; y += num(d["y"]) ?? 0
                    w = num(d["w"]) ?? w; h = num(d["h"]) ?? h
                    continue
                }
                guard let s = item as? String else { continue }
                let parts = s.components(separatedBy: "\n")
                var include = true
                if parts.count > 3, !parts[3].isEmpty {
                    let o = parts[3].split(separator: ",").compactMap { Int($0) }
                    if o.count == 2 { include = (options[o[0]] ?? 0) == o[1] }
                }
                let rc = parts[0].split(separator: ",").compactMap { Int($0) }
                if include, rc.count == 2 {
                    out.append(KeyPlace(x: x, y: y, w: w, h: h, r: r, rx: rx, ry: ry, row: rc[0], col: rc[1]))
                }
                x += w; w = 1; h = 1
            }
            y += 1; x = rx
        }
        return out
    }

    /// Bounding box of all keys, rotation included: (minX, minY, width, height).
    public var bounds: (x: Double, y: Double, w: Double, h: Double) {
        let pts = keys.flatMap(\.corners)
        guard let x0 = pts.map(\.0).min(), let y0 = pts.map(\.1).min(),
              let x1 = pts.map(\.0).max(), let y1 = pts.map(\.1).max() else { return (0, 0, 0, 0) }
        return (x0, y0, x1 - x0, y1 - y0)
    }
}
