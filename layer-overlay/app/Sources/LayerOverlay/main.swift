import AppKit
import LayerCore
import LayerUI
import ServiceManagement

// `LayerOverlay --render <board-id> <layer> <out.png> [keymap.json]` renders an overlay without the keyboard.
if CommandLine.arguments.count >= 5, CommandLine.arguments[1] == "--render" {
    let a = CommandLine.arguments
    guard let p = BoardProfile.bundled().first(where: { $0.id == a[2] }), let layer = Int(a[3]) else {
        FileHandle.standardError.write("unknown board or layer\n".data(using: .utf8)!); exit(1)
    }
    struct F: Decodable { var keymap: [[[UInt16]]] }
    let f = try JSONDecoder().decode(F.self, from: Data(contentsOf: URL(fileURLWithPath: a.count > 5 ? a[5] : a[4] + ".json")))
    let km = Keymap(layers: f.keymap.map { $0.flatMap { $0 } }, rows: p.layout.rows, cols: p.layout.cols)
    let c = OverlayContent.make(profile: p, keymap: km, layer: layer, state: UInt32(1 << layer) | 2, ghosts: true)
    let png = MainActor.assumeIsolated { renderPNG(c) }
    try png!.write(to: URL(fileURLWithPath: a[4]))
    exit(0)
}

// `LayerOverlay --dump-keymap <board-id>` reads the keymap from the board (read-only) and prints it as JSON.
if CommandLine.arguments.count >= 3, CommandLine.arguments[1] == "--dump-keymap" {
    guard let p = BoardProfile.bundled().first(where: { $0.id == CommandLine.arguments[2] }) else { exit(1) }
    RawKeymapRead.read(profile: p) { r in
        switch r {
        case .success(let km):
            let layers = km.layers.map { l in (0..<km.rows).map { Array(l[($0 * km.cols)..<(($0 + 1) * km.cols)]) } }
            print(String(data: try! JSONEncoder().encode(["keymap": layers]), encoding: .utf8)!)
            exit(0)
        case .failure(let e):
            FileHandle.standardError.write("\(e)\n".data(using: .utf8)!); exit(2)
        }
    }
    RunLoop.main.run()
}

// `LayerOverlay --listen <board-id> [seconds]` prints console lines and layer events, for checking the HID path.
var listenWatcher: ConsoleWatcher?
if CommandLine.arguments.count >= 3, CommandLine.arguments[1] == "--listen" {
    guard let p = BoardProfile.bundled().first(where: { $0.id == CommandLine.arguments[2] }) else { exit(1) }
    let secs = Double(CommandLine.arguments.count > 3 ? CommandLine.arguments[3] : "30") ?? 30
    var reader = ConsoleLineReader()
    let w = ConsoleWatcher(profile: p)
    w.onReport = { bytes in
        for line in reader.feed(bytes) { print(line, LayerEvent(line: line).map { "→ layer \($0.highest)" } ?? ""); fflush(stdout) }
    }
    w.start()
    listenWatcher = w
    DispatchQueue.main.asyncAfter(deadline: .now() + secs) { exit(w.connected ? 0 : 3) }
    RunLoop.main.run()
}

final class App: NSObject, NSApplicationDelegate, NSMenuDelegate {
    let defaults = UserDefaults.standard
    let panel = OverlayPanel()
    var boards: [(controller: OverlayController, watcher: ConsoleWatcher)] = []
    var statusItem: NSStatusItem!
    var timer: DispatchSourceTimer?
    var keymapNote: [String: String] = [:]

    var delay: Double { defaults.object(forKey: "holdDelay") as? Double ?? 3.0 }
    var ghosts: Bool { defaults.object(forKey: "ghosts") as? Bool ?? true }
    /// Per board: layers that don't get the overlay (menu: "Show overlay for").
    func quietLayers(_ board: String) -> Set<Int> { Set(defaults.array(forKey: "quietLayers.\(board)") as? [Int] ?? []) }

    func applicationDidFinishLaunching(_ n: Notification) {
        panel.position = OverlayPanel.Position(rawValue: defaults.string(forKey: "position") ?? "") ?? .bottom
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem.button?.image = NSImage(systemSymbolName: "keyboard", accessibilityDescription: "Layer Overlay")
        let menu = NSMenu()
        menu.delegate = self
        statusItem.menu = menu

        for p in BoardProfile.bundled() {
            let c = OverlayController(profile: p, delay: delay)
            c.presenter = panel
            c.ghosts = ghosts
            c.quietLayers = quietLayers(p.id)
            let w = ConsoleWatcher(profile: p)
            w.onReport = { [weak self, weak c] bytes in
                c?.consoleReport(bytes, at: ProcessInfo.processInfo.systemUptime)
                self?.schedule()
            }
            w.onConnect = { [weak self, weak c] in if let c { self?.loadKeymap(c) } }
            w.onDisconnect = { [weak c] in c?.reset() }
            w.start()
            boards.append((c, w))
        }
    }

    /// One timer for all boards, set to the earliest deadline.
    func schedule() {
        timer?.cancel()
        guard let next = boards.compactMap({ $0.controller.nextDeadline }).min() else { return }
        let t = DispatchSource.makeTimerSource(queue: .main)
        t.schedule(deadline: .now() + max(0, next - ProcessInfo.processInfo.systemUptime))
        t.setEventHandler { [weak self] in
            guard let self else { return }
            let now = ProcessInfo.processInfo.systemUptime
            boards.forEach { $0.controller.tick(at: now) }
            schedule()
        }
        t.resume()
        timer = t
    }

    func loadKeymap(_ c: OverlayController, attempt: Int = 0) {
        keymapNote[c.profile.id] = "reading keymap…"
        RawKeymapRead.read(profile: c.profile) { [weak self] r in
            guard let self else { return }
            switch r {
            case .success(let km):
                c.keymap = km
                keymapNote[c.profile.id] = "\(km.layers.count) layers"
                log("\(c.profile.name): keymap read, \(km.layers.count) layers")
            case .failure(let e):
                keymapNote[c.profile.id] = "keymap not read (\(e)); retrying"
                log("\(c.profile.name): keymap not read (\(e)), attempt \(attempt + 1)")
                if attempt < 20 {   // Vial may have it: try again in 15 s
                    DispatchQueue.main.asyncAfter(deadline: .now() + 15) { self.loadKeymap(c, attempt: attempt + 1) }
                }
            }
        }
    }

    // MARK: menu

    func menuNeedsUpdate(_ menu: NSMenu) {
        menu.removeAllItems()
        for (c, w) in boards {
            let note = w.connected ? (keymapNote[c.profile.id] ?? "connected") : "not connected"
            menu.addItem(NSMenuItem(title: "\(c.profile.name): \(note)", action: nil, keyEquivalent: ""))
        }
        menu.addItem(.separator())

        let delayMenu = NSMenu()
        for s in [1.0, 2.0, 3.0, 4.0, 5.0] {
            let i = NSMenuItem(title: "\(Int(s)) s", action: #selector(setDelay(_:)), keyEquivalent: "")
            i.target = self; i.tag = Int(s); i.state = delay == s ? .on : .off
            delayMenu.addItem(i)
        }
        let d = NSMenuItem(title: "Show after holding", action: nil, keyEquivalent: ""); d.submenu = delayMenu
        menu.addItem(d)
        for (bi, (c, _)) in boards.enumerated() {
            let layers = c.keymap.map { 1..<$0.layers.count } ?? 1..<(max(2, (c.profile.labeler.layerNames.keys.max() ?? 1) + 1))
            let sub = NSMenu()
            for l in layers {
                let i = NSMenuItem(title: c.profile.labeler.layerName(l), action: #selector(toggleLayer(_:)), keyEquivalent: "")
                i.target = self; i.tag = bi * 100 + l
                i.state = c.quietLayers.contains(l) ? .off : .on
                sub.addItem(i)
            }
            let title = boards.count > 1 ? "Show overlay for (\(c.profile.name))" : "Show overlay for"
            let item = NSMenuItem(title: title, action: nil, keyEquivalent: ""); item.submenu = sub
            menu.addItem(item)
        }
        add(menu, "Base-key ghosts", #selector(toggleGhosts), on: ghosts)
        add(menu, "Show at top of screen", #selector(togglePosition), on: panel.position == .top)

        let preview = NSMenu()
        for (bi, (c, _)) in boards.enumerated() {
            guard let km = c.keymap else { continue }
            for l in 1..<km.layers.count {
                let i = NSMenuItem(title: "\(c.profile.name): \(c.profile.labeler.layerName(l))", action: #selector(previewLayer(_:)), keyEquivalent: "")
                i.target = self; i.tag = bi * 100 + l
                preview.addItem(i)
            }
        }
        let pv = NSMenuItem(title: "Preview a layer", action: nil, keyEquivalent: ""); pv.submenu = preview
        pv.isEnabled = !preview.items.isEmpty
        menu.addItem(pv)
        add(menu, "Reload keymap", #selector(reloadKeymaps))
        menu.addItem(.separator())
        add(menu, "Open at login", #selector(toggleLogin), on: SMAppService.mainApp.status == .enabled)
        menu.addItem(NSMenuItem(title: "Quit Layer Overlay", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
    }

    func add(_ m: NSMenu, _ title: String, _ sel: Selector, on: Bool? = nil) {
        let i = NSMenuItem(title: title, action: sel, keyEquivalent: "")
        i.target = self
        if let on { i.state = on ? .on : .off }
        m.addItem(i)
    }

    @objc func setDelay(_ i: NSMenuItem) {
        defaults.set(Double(i.tag), forKey: "holdDelay")
        boards.forEach { $0.controller.delay = Double(i.tag) }
    }
    @objc func toggleLayer(_ i: NSMenuItem) {
        let c = boards[i.tag / 100].controller, l = i.tag % 100
        var q = c.quietLayers
        if q.contains(l) { q.remove(l) } else { q.insert(l) }
        c.quietLayers = q
        defaults.set(q.sorted(), forKey: "quietLayers.\(c.profile.id)")
    }
    @objc func toggleGhosts() {
        defaults.set(!ghosts, forKey: "ghosts")
        boards.forEach { $0.controller.ghosts = ghosts }
    }
    @objc func togglePosition() {
        panel.position = panel.position == .top ? .bottom : .top
        defaults.set(panel.position.rawValue, forKey: "position")
    }
    @objc func previewLayer(_ i: NSMenuItem) {
        let c = boards[i.tag / 100].controller, l = i.tag % 100
        if let content = c.content(layer: l, state: UInt32(1 << l)) {
            panel.show(content)
            DispatchQueue.main.asyncAfter(deadline: .now() + 3) { [weak self] in
                if c.shownLayer == nil { self?.panel.hide() }
            }
        }
    }
    @objc func reloadKeymaps() { boards.filter { $0.watcher.connected }.forEach { loadKeymap($0.controller) } }
    @objc func toggleLogin() {
        do {
            if SMAppService.mainApp.status == .enabled { try SMAppService.mainApp.unregister() }
            else { try SMAppService.mainApp.register() }
        } catch {
            let a = NSAlert(); a.messageText = "Couldn't change Open at login"; a.informativeText = "\(error.localizedDescription)\nMove the app to Applications and try again."
            a.runModal()
        }
    }
}

let app = NSApplication.shared
let delegate = App()
app.delegate = delegate
app.setActivationPolicy(.accessory)
app.run()
