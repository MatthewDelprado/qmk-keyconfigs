import Foundation

/// What the overlay draws: one entry per key, already labelled.
public struct OverlayContent: Equatable, Sendable {
    public enum Style: String, Sendable { case key, mod, act, empty, transparent, held }
    public struct Cap: Equatable, Sendable {
        public var place: KeyPlace
        public var main: String
        public var hold: String
        public var ghost: String
        public var style: Style
    }
    public var board: String
    public var layer: Int
    public var layerName: String
    public var caps: [Cap]
    public var bounds: (x: Double, y: Double, w: Double, h: Double)

    public static func == (a: Self, b: Self) -> Bool {
        a.board == b.board && a.layer == b.layer && a.layerName == b.layerName && a.caps == b.caps
    }

    /// Labels `layer` of `keymap`. Keys that turn this layer on (on any active layer below it) are marked held.
    /// Ghosts are the base layer's legends, for learning where things are.
    public static func make(profile: BoardProfile, keymap: Keymap, layer: Int, state: UInt32, ghosts: Bool) -> OverlayContent {
        let lab = profile.labeler
        let below = (0..<layer).filter { $0 == 0 || state & (1 << UInt32($0)) != 0 }
        let caps = profile.layout.keys.map { k -> Cap in
            let code = keymap.code(layer: layer, row: k.row, col: k.col)
            let lg = lab.legend(code)
            let base = lab.legend(keymap.code(layer: 0, row: k.row, col: k.col))
            let turnsOn = below.contains { KeyLabeler.targetLayer(keymap.code(layer: $0, row: k.row, col: k.col)) == layer }
            let style: Style = turnsOn ? .held : {
                switch lg.kind {
                case .none: return .empty
                case .transparent: return .transparent
                case .mod: return .mod
                case .act: return .act
                case .key: return .key
                }
            }()
            let ghost = ghosts && layer != 0 && base.main != lg.main ? base.main : ""
            // We can't tell which of several such keys is down, so each keeps its own legend.
            return Cap(place: k, main: turnsOn && lg.main.isEmpty ? lab.layerName(layer) : lg.main,
                       hold: lg.hold, ghost: ghost, style: style)
        }
        return OverlayContent(board: profile.name, layer: layer, layerName: lab.layerName(layer), caps: caps,
                              bounds: profile.layout.bounds)
    }
}

public protocol OverlayPresenting: AnyObject {
    func show(_ content: OverlayContent)
    func hide()
}

/// Glue: console reports in, overlay show/hide out. Main thread only. Times are seconds on a monotonic clock.
public final class OverlayController {
    public let profile: BoardProfile
    public weak var presenter: OverlayPresenting?
    public var keymap: Keymap? { didSet { refresh() } }
    public var ghosts = true { didSet { refresh() } }
    /// Layers that never get the overlay. Holding one counts as being on Base: nothing shows, and
    /// moving into it from a shown layer hides the overlay.
    public var quietLayers: Set<Int> = [] {
        didSet { if let s = timer.shown, quietLayers.contains(Int(s)), let out = timer.layerChanged(0, at: 0) { apply(out) } }
    }
    public var delay: Double {
        get { timer.delay }
        set { timer.delay = newValue }
    }
    public private(set) var last = LayerEvent(highest: 0, state: 0)
    private var timer: HoldTimer
    private var reader = ConsoleLineReader()

    public init(profile: BoardProfile, delay: Double = 3.0) {
        self.profile = profile
        self.timer = HoldTimer(delay: delay)
    }

    public var shownLayer: UInt8? { timer.shown }
    public var nextDeadline: Double? { timer.nextDeadline }

    /// One input report from the console interface.
    public func consoleReport(_ bytes: [UInt8], at t: Double) {
        for line in reader.feed(bytes) {
            if let e = LayerEvent(line: line) { handle(e, at: t) }
        }
    }

    public func handle(_ e: LayerEvent, at t: Double) {
        let before = last
        last = e
        let layer = quietLayers.contains(Int(e.highest)) ? 0 : e.highest
        if let out = timer.layerChanged(layer, at: t) { apply(out) }
        else if timer.shown == e.highest, before != e { refresh() }   // same layer, different stack: redraw
    }

    public func tick(at t: Double) {
        if let out = timer.tick(at: t) { apply(out) }
    }

    /// Keyboard went away: hide and forget the held layer.
    public func reset() {
        if let out = timer.layerChanged(0, at: 0) { apply(out) }
        last = LayerEvent(highest: 0, state: 0)
        reader = ConsoleLineReader()
    }

    public func content(layer: Int, state: UInt32) -> OverlayContent? {
        guard let km = keymap, layer < km.layers.count else { return nil }
        return OverlayContent.make(profile: profile, keymap: km, layer: layer, state: state, ghosts: ghosts)
    }

    private func apply(_ out: HoldTimer.Output) {
        switch out {
        case .show(let l):
            if let c = content(layer: Int(l), state: last.state) { presenter?.show(c) }
        case .hide:
            presenter?.hide()
        }
    }

    private func refresh() {
        guard let l = timer.shown, let c = content(layer: Int(l), state: last.state) else { return }
        presenter?.show(c)
    }
}
