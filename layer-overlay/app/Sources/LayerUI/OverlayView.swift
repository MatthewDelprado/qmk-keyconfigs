import AppKit
import LayerCore
import SwiftUI

/// The overlay: a dark rounded panel with the board drawn key by key (option B: base legends as ghosts).
public struct OverlayView: View {
    public var content: OverlayContent
    public var unit: CGFloat

    public init(content: OverlayContent, unit: CGFloat = 46) { self.content = content; self.unit = unit }

    static let pad: CGFloat = 18
    static let header: CGFloat = 34

    public var boardSize: CGSize {
        CGSize(width: content.bounds.w * unit, height: content.bounds.h * unit)
    }
    public var size: CGSize {
        CGSize(width: boardSize.width + 2 * Self.pad, height: boardSize.height + Self.pad + Self.header)
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Text(content.layerName).font(.system(size: 15, weight: .semibold)).foregroundStyle(.white)
                Text(content.board).font(.system(size: 12)).foregroundStyle(.white.opacity(0.5))
            }
            .frame(height: Self.header, alignment: .center)
            ZStack(alignment: .topLeading) {
                ForEach(Array(content.caps.enumerated()), id: \.offset) { _, cap in
                    CapView(cap: cap, unit: unit)
                        .frame(width: cap.place.w * unit, height: cap.place.h * unit)
                        .rotationEffect(.degrees(cap.place.r),
                                        anchor: UnitPoint(x: (cap.place.rx - cap.place.x) / cap.place.w,
                                                          y: (cap.place.ry - cap.place.y) / cap.place.h))
                        .position(x: (cap.place.x + cap.place.w / 2 - content.bounds.x) * unit,
                                  y: (cap.place.y + cap.place.h / 2 - content.bounds.y) * unit)
                }
            }
            .frame(width: boardSize.width, height: boardSize.height, alignment: .topLeading)
        }
        .padding(.horizontal, Self.pad)
        .padding(.bottom, Self.pad)
        .frame(width: size.width, height: size.height, alignment: .topLeading)
        .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Color(white: 0.11).opacity(0.9)))
        .environment(\.colorScheme, .dark)
    }
}

struct CapView: View {
    var cap: OverlayContent.Cap
    var unit: CGFloat

    var fill: Color {
        switch cap.style {
        case .held: return Color(red: 0.37, green: 0.56, blue: 0.84).opacity(0.35)
        case .empty, .transparent: return .white.opacity(0.04)
        case .mod: return .white.opacity(0.10)
        case .key, .act: return .white.opacity(0.16)
        }
    }
    var faded: Bool { cap.style == .empty || cap.style == .transparent }

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: unit * 0.14, style: .continuous).fill(fill).padding(2)
            if cap.style == .held {   // turns this layer on
                RoundedRectangle(cornerRadius: unit * 0.14, style: .continuous)
                    .strokeBorder(Color(red: 0.45, green: 0.65, blue: 0.95), lineWidth: 2).padding(2)
            }
            if !cap.ghost.isEmpty {
                Text(cap.ghost)
                    .font(.system(size: max(9, unit * 0.2)))
                    .foregroundStyle(.white.opacity(0.42))
                    .lineLimit(1)
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
                    .padding(.leading, unit * 0.13).padding(.top, unit * 0.09)
            }
            VStack(spacing: 1) {
                if !cap.main.isEmpty {
                    Text(cap.main)
                        .font(.system(size: cap.main.count > 3 ? unit * 0.24 : unit * 0.34, weight: .medium))
                        .foregroundStyle(.white.opacity(faded ? 0.35 : 1))
                        .lineLimit(1).minimumScaleFactor(0.5)
                }
                if !cap.hold.isEmpty {
                    Text(cap.hold)
                        .font(.system(size: max(8, unit * 0.17)))
                        .foregroundStyle(.white.opacity(0.6))
                        .lineLimit(1).minimumScaleFactor(0.6)
                }
            }
            .padding(.horizontal, 4)
            .padding(.top, cap.ghost.isEmpty ? 0 : unit * 0.12)
        }
    }
}

/// Renders the overlay to PNG data: used by the tests and by `LayerOverlay --render`.
@MainActor
public func renderPNG(_ content: OverlayContent, unit: CGFloat = 46, scale: CGFloat = 2) -> Data? {
    let view = OverlayView(content: content, unit: unit)
    let r = ImageRenderer(content: view)
    r.scale = scale
    guard let cg = r.cgImage else { return nil }
    return NSBitmapImageRep(cgImage: cg).representation(using: .png, properties: [:])
}
