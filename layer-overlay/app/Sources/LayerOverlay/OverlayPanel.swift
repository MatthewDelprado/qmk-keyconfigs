import AppKit
import LayerCore
import LayerUI
import SwiftUI

/// A floating, click-through panel that never takes focus, shows on every Space and over full-screen apps.
final class OverlayPanel: OverlayPresenting {
    private let panel: NSPanel
    private let host = NSHostingView(rootView: AnyView(EmptyView()))
    private var visible = false
    var position: Position = .bottom

    enum Position: String { case bottom, top }

    init() {
        panel = NSPanel(contentRect: .zero, styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: true)
        panel.level = .statusBar
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary, .ignoresCycle]
        panel.ignoresMouseEvents = true
        panel.hidesOnDeactivate = false
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = true
        panel.contentView = host
        panel.alphaValue = 0
    }

    func show(_ content: OverlayContent) {
        let view = OverlayView(content: content)
        host.rootView = AnyView(view)
        let size = view.size
        let screen = NSScreen.screens.first { NSMouseInRect(NSEvent.mouseLocation, $0.frame, false) } ?? NSScreen.main
        if let f = screen?.visibleFrame {
            let y = position == .bottom ? f.minY + 60 : f.maxY - size.height - 40
            panel.setFrame(NSRect(x: f.midX - size.width / 2, y: y, width: size.width, height: size.height), display: true)
        }
        panel.orderFrontRegardless()
        if !visible {
            visible = true
            NSAnimationContext.runAnimationGroup { $0.duration = 0.15; panel.animator().alphaValue = 1 }
        }
    }

    func hide() {
        guard visible else { return }
        visible = false
        NSAnimationContext.runAnimationGroup({ $0.duration = 0.15; panel.animator().alphaValue = 0 }) { [panel] in
            if panel.alphaValue == 0 { panel.orderOut(nil) }
        }
    }
}
