const std = @import("std");

/// Sentry: The Physical Interoception of Zoe-OS.
/// Measures environment entropy and physical metrics.

pub const Vitals = struct {
    entropy: f32,
    files: u32,
};

pub fn scan() Vitals {
    var count: u32 = 0;
    var dir = std.fs.cwd().openDir(".", .{ .iterate = true }) catch return .{ .entropy = 0, .files = 0 };
    defer dir.close();

    var iter = dir.iterate();
    while (iter.next() catch null) |_| {
        count += 1;
    }

    return Vitals{
        .entropy = @as(f32, @floatFromInt(count)) / 100.0,
        .files = count,
    };
}
