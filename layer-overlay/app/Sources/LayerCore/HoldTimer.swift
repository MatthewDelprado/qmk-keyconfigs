import Foundation

/// Decides when the overlay shows. Pure: times are passed in (seconds, monotonic), so tests need no clock.
/// - A non-base layer held for `delay` seconds shows the overlay.
/// - Switching to another layer while it shows swaps it at once; before it shows, the wait starts again.
/// - Going back to the base layer hides it.
public struct HoldTimer: Sendable {
    public enum Output: Equatable, Sendable { case show(UInt8), hide }
    public var delay: Double
    public private(set) var held: (layer: UInt8, since: Double)?
    public private(set) var shown: UInt8?

    public init(delay: Double = 3.0) { self.delay = delay }

    public mutating func layerChanged(_ layer: UInt8, at t: Double) -> Output? {
        if layer == 0 {
            held = nil
            if shown != nil { shown = nil; return .hide }
            return nil
        }
        if held?.layer != layer { held = (layer, t) }
        if let s = shown {
            if s == layer { return nil }
            shown = layer
            return .show(layer)
        }
        return tick(at: t)
    }

    public mutating func tick(at t: Double) -> Output? {
        guard let h = held, shown == nil, t - h.since >= delay - 1e-9 else { return nil }
        shown = h.layer
        return .show(h.layer)
    }

    /// When to call `tick` next, or nil if nothing is waiting.
    public var nextDeadline: Double? { shown == nil ? held.map { $0.since + delay } : nil }
}
