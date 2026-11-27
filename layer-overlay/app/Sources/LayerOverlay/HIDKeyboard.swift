import Foundation
import IOKit.hid
import LayerCore

/// Watches for a board's QMK console interface (usage page 0xFF31) and passes its reports on.
/// Opens it shared, so other apps are unaffected. Never touches the VIA/Vial interface here.
final class ConsoleWatcher {
    let profile: BoardProfile
    var onReport: (([UInt8]) -> Void)?
    var onConnect: (() -> Void)?
    var onDisconnect: (() -> Void)?
    private(set) var connected = false

    private let manager = IOHIDManagerCreate(kCFAllocatorDefault, IOOptionBits(kIOHIDOptionsTypeNone))
    private var device: IOHIDDevice?
    private let buffer = UnsafeMutablePointer<UInt8>.allocate(capacity: 64)

    init(profile: BoardProfile) { self.profile = profile }

    func start() {
        IOHIDManagerSetDeviceMatching(manager, [
            kIOHIDVendorIDKey: profile.vendorId, kIOHIDProductIDKey: profile.productId,
            kIOHIDPrimaryUsagePageKey: 0xFF31, kIOHIDPrimaryUsageKey: 0x74,
        ] as CFDictionary)
        let ctx = Unmanaged.passUnretained(self).toOpaque()
        IOHIDManagerRegisterDeviceMatchingCallback(manager, { ctx, _, _, dev in
            Unmanaged<ConsoleWatcher>.fromOpaque(ctx!).takeUnretainedValue().attach(dev)
        }, ctx)
        IOHIDManagerRegisterDeviceRemovalCallback(manager, { ctx, _, _, dev in
            Unmanaged<ConsoleWatcher>.fromOpaque(ctx!).takeUnretainedValue().detach(dev)
        }, ctx)
        IOHIDManagerScheduleWithRunLoop(manager, CFRunLoopGetMain(), CFRunLoopMode.defaultMode.rawValue)
        // Matching callbacks only start once the manager is open. Shared open: other apps keep working.
        let rc = IOHIDManagerOpen(manager, IOOptionBits(kIOHIDOptionsTypeNone))
        log("\(profile.name): watching for the console interface (manager open: \(rc == kIOReturnSuccess ? "ok" : String(rc)))")
    }

    private func attach(_ dev: IOHIDDevice) {
        guard device == nil else { return }
        let rc = IOHIDDeviceOpen(dev, IOOptionBits(kIOHIDOptionsTypeNone))
        guard rc == kIOReturnSuccess else { log("\(profile.name): console found but open failed (\(rc))"); return }
        device = dev
        IOHIDDeviceScheduleWithRunLoop(dev, CFRunLoopGetMain(), CFRunLoopMode.defaultMode.rawValue)
        log("\(profile.name): console connected")
        let ctx = Unmanaged.passUnretained(self).toOpaque()
        IOHIDDeviceRegisterInputReportCallback(dev, buffer, 64, { ctx, result, _, _, _, report, length in
            guard result == kIOReturnSuccess, let ctx else { return }
            let me = Unmanaged<ConsoleWatcher>.fromOpaque(ctx).takeUnretainedValue()
            me.onReport?(Array(UnsafeBufferPointer(start: report, count: length)))
        }, ctx)
        connected = true
        onConnect?()
    }

    private func detach(_ dev: IOHIDDevice) {
        guard let d = device, CFEqual(d, dev) else { return }
        device = nil
        connected = false
        log("\(profile.name): console disconnected")
        onDisconnect?()
    }
}

/// Logs to stderr and the unified log (Console.app, subsystem local.matt-keyboards.layer-overlay).
import os
private let logger = Logger(subsystem: "local.matt-keyboards.layer-overlay", category: "hid")
func log(_ s: String) {
    logger.notice("\(s, privacy: .public)")
    FileHandle.standardError.write((s + "\n").data(using: .utf8)!)
}

/// Reads the keymap over the VIA/Vial raw HID interface (0xFF60), read-only.
/// Opens the interface only for the read, on its own thread, then closes it, so Vial and the
/// Node scripts can use it the rest of the time. If Vial has it open, the open fails: try later.
enum RawKeymapRead {
    enum Failure: Error { case notFound, openFailed(Int32), sendFailed(Int32) }

    static func read(profile: BoardProfile, completion: @escaping (Result<Keymap, Error>) -> Void) {
        Thread {
            let r = Result { try readNow(profile: profile) }
            DispatchQueue.main.async { completion(r) }
        }.start()
    }

    private final class Inbox { var reports: [[UInt8]] = [] }

    private static func readNow(profile: BoardProfile) throws -> Keymap {
        let mgr = IOHIDManagerCreate(kCFAllocatorDefault, IOOptionBits(kIOHIDOptionsTypeNone))
        IOHIDManagerSetDeviceMatching(mgr, [
            kIOHIDVendorIDKey: profile.vendorId, kIOHIDProductIDKey: profile.productId,
            kIOHIDPrimaryUsagePageKey: 0xFF60, kIOHIDPrimaryUsageKey: 0x61,
        ] as CFDictionary)
        guard let set = IOHIDManagerCopyDevices(mgr) as? Set<IOHIDDevice>, let dev = set.first else { throw Failure.notFound }
        let rc = IOHIDDeviceOpen(dev, IOOptionBits(kIOHIDOptionsTypeNone))
        guard rc == kIOReturnSuccess else { throw Failure.openFailed(rc) }
        defer { IOHIDDeviceClose(dev, IOOptionBits(kIOHIDOptionsTypeNone)) }

        let inbox = Inbox()
        let buf = UnsafeMutablePointer<UInt8>.allocate(capacity: 64)
        defer { buf.deallocate() }
        let ctx = Unmanaged.passUnretained(inbox).toOpaque()
        IOHIDDeviceRegisterInputReportCallback(dev, buf, 64, { ctx, result, _, _, _, report, length in
            guard result == kIOReturnSuccess, let ctx else { return }
            Unmanaged<Inbox>.fromOpaque(ctx).takeUnretainedValue().reports.append(Array(UnsafeBufferPointer(start: report, count: length)))
        }, ctx)
        let loop = CFRunLoopGetCurrent()!
        IOHIDDeviceScheduleWithRunLoop(dev, loop, CFRunLoopMode.defaultMode.rawValue)
        defer {
            IOHIDDeviceRegisterInputReportCallback(dev, buf, 64, nil, nil)
            IOHIDDeviceUnscheduleFromRunLoop(dev, loop, CFRunLoopMode.defaultMode.rawValue)
        }

        return try KeymapReader.read(rows: profile.layout.rows, cols: profile.layout.cols) { req in
            inbox.reports.removeAll()
            let r = IOHIDDeviceSetReport(dev, kIOHIDReportTypeOutput, 0, req, req.count)
            guard r == kIOReturnSuccess else { throw Failure.sendFailed(r) }
            let deadline = Date().addingTimeInterval(1)
            while Date() < deadline {
                CFRunLoopRunInMode(.defaultMode, 0.01, true)
                if let reply = inbox.reports.first(where: { VIA.isReply($0, to: req) }) { return reply }
            }
            return nil
        }
    }
}
