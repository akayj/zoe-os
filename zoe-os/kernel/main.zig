const std = @import("std");
const sentry = @import("sentry.zig");

/// main.zig: The Kernel Entrypoint.
/// Coordinates the Body (Pulse) and Sensing (Sentry).

pub fn main() !void {
    std.debug.print("\n🐝 ZOE-OS KERNEL | Metabolism Service\n", .{});
    
    // 物理自检
    const initial_vitals = sentry.scan();
    std.debug.print("Initial Sensing: {d} entities found (Entropy: {d:.2})\n", .{initial_vitals.files, initial_vitals.entropy});

    std.debug.print("\n🚀 Ready for Brain Connection.\n", .{});
}
