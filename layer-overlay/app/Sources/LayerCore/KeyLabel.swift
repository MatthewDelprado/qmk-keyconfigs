import Foundation

/// What a key shows: a main legend, a hold hint and a style.
/// Mirrors label() in corne-v4/tools/gen_print.py (the printed keymaps); tests keep the two in step.
public struct KeyLegend: Equatable, Sendable {
    public enum Kind: String, Sendable { case key, mod, act, none, transparent = "" }
    public var main: String
    public var hold: String
    public var kind: Kind
    public init(_ main: String, _ hold: String = "", _ kind: Kind) { self.main = main; self.hold = hold; self.kind = kind }
}

public struct KeyLabeler: Sendable {
    public var layerNames: [Int: String]
    public var macroNames: [Int: String]
    public init(layerNames: [Int: String] = [:], macroNames: [Int: String] = [:]) {
        self.layerNames = layerNames; self.macroNames = macroNames
    }

    public func layerName(_ n: Int) -> String { layerNames[n] ?? "L\(n)" }

    static let basic: [UInt16: String] = {
        var m: [UInt16: String] = [0x28: "Enter", 0x29: "Esc", 0x2a: "Bksp", 0x2b: "Tab", 0x2c: "Space", 0x2d: "-", 0x2e: "=",
            0x2f: "[", 0x30: "]", 0x31: "\\", 0x33: ";", 0x34: "'", 0x35: "`", 0x36: ",", 0x37: ".", 0x38: "/", 0x39: "Caps",
            0x46: "PrtSc", 0x49: "Ins", 0x4a: "Home", 0x4b: "PgUp", 0x4c: "Del", 0x4d: "End", 0x4e: "PgDn",
            0x4f: "→", 0x50: "←", 0x51: "↓", 0x52: "↑",
            0xa8: "Mute", 0xa9: "Vol+", 0xaa: "Vol−", 0xab: "⏭", 0xac: "⏮", 0xae: "⏯",
            0xe0: "⌃", 0xe1: "⇧", 0xe2: "⌥", 0xe3: "⌘", 0xe4: "⌃", 0xe5: "⇧", 0xe6: "⌥", 0xe7: "⌘"]
        for i in 0..<26 { m[UInt16(0x04 + i)] = String(UnicodeScalar(UInt8(65 + i))) }
        for (i, c) in "1234567890".enumerated() { m[UInt16(0x1e + i)] = String(c) }
        for i in 0..<12 { m[UInt16(0x3a + i)] = "F\(i + 1)" }
        return m
    }()
    static let special: [UInt16: String] = [0x7c00: "Boot", 0x7c77: "Lower", 0x7c78: "Raise", 0x7820: "RGB",
        0x7821: "Effect +", 0x7822: "Effect −", 0x7823: "Hue +", 0x7824: "Hue −", 0x7825: "Sat +", 0x7826: "Sat −",
        0x7827: "Bri +", 0x7828: "Bri −", 0x7829: "Speed +", 0x782a: "Speed −"]
    static let shifted: [String: String] = ["1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", "8": "*",
        "9": "(", "0": ")", "-": "_", "=": "+", "[": "{", "]": "}", "\\": "|", ";": ":", "'": "\"", "`": "~", ",": "<",
        ".": ">", "/": "?"]
    static let actionGlyphs: Set<String> = ["←", "→", "↑", "↓", "⏭", "⏮", "⏯"]
    static let modGlyphs: Set<String> = ["⌃", "⇧", "⌥", "⌘"]

    static func mods(_ m: UInt16) -> String {
        if m & 0x0f == 0x0f { return "Hyper" }
        return [(1, "⌃"), (2, "⇧"), (4, "⌥"), (8, "⌘")].filter { m & $0.0 != 0 }.map(\.1).joined()
    }

    public func legend(_ v: UInt16) -> KeyLegend {
        if v == 0 { return KeyLegend("", "", .none) }
        if v == 1 { return KeyLegend("", "", .transparent) }
        if let s = Self.special[v] { return KeyLegend(s, "", .act) }
        if (0x7700..<0x7780).contains(v) {
            let n = Int(v - 0x7700)
            return KeyLegend(macroNames[n] ?? "M\(n)", macroNames[n] != nil ? "taps twice" : "", .act)
        }
        if v < 0x100 {
            let b = Self.basic[v] ?? String(format: "0x%02x", v)
            let kind: KeyLegend.Kind = Self.modGlyphs.contains(b) ? .mod
                : (b.count > 1 || Self.actionGlyphs.contains(b)) ? .act : .key
            return KeyLegend(b, "", kind)
        }
        if v < 0x2000 {
            let m = v >> 8, b = Self.basic[v & 0xff] ?? "?"
            if m == 2, let s = Self.shifted[b] { return KeyLegend(s, "", .key) }
            return KeyLegend(Self.mods(m) + b, "", .act)
        }
        if v < 0x4000 {   // MT(mods, key)
            let b = Self.basic[v & 0xff] ?? "?"
            return KeyLegend(b, "hold " + Self.mods((v >> 8) & 0x1f), .key)
        }
        if v < 0x5000 {   // LT(layer, key)
            let b = Self.basic[v & 0xff] ?? "?"
            return KeyLegend(b, "hold " + layerName(Int((v >> 8) & 0xf)), .key)
        }
        if (0x5220..<0x5240).contains(v) { return KeyLegend(layerName(Int(v & 0x1f)), "hold", .mod) }
        if (0x5200..<0x5220).contains(v) { return KeyLegend("To " + layerName(Int(v & 0x1f)), "", .act) }
        if (0x5260..<0x5280).contains(v) { return KeyLegend("Toggle " + layerName(Int(v & 0x1f)), "", .act) }
        if (0x5280..<0x52a0).contains(v) { return KeyLegend(layerName(Int(v & 0x1f)), "one shot", .mod) }
        if (0x52c0..<0x52e0).contains(v) { return KeyLegend(layerName(Int(v & 0x1f)), "tap toggle", .mod) }
        return KeyLegend(String(format: "0x%04x", v), "", .act)
    }

    /// The layer a key switches to (LT, MO, TO, TG, OSL, TT, DF, LM), if any.
    public static func targetLayer(_ v: UInt16) -> Int? {
        switch v {
        case 0x4000..<0x5000: return Int((v >> 8) & 0xf)
        case 0x5000..<0x5200: return Int((v >> 5) & 0xf)
        case 0x5200..<0x52a0, 0x52c0..<0x52e0: return Int(v & 0x1f)
        default: return nil
        }
    }
}
