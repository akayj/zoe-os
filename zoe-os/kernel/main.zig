const std = @import("std");
const sentry = @import("sentry.zig");
const effector = @import("effector.zig");

pub fn main() !void {
    std.debug.print("\n🐝 ZOE-OS KERNEL | Embodied Mode Engaged\n", .{});
    
    // 物理层测试：驱动一个模拟关节
    try effector.move_joint(1, 45.0);
    
    std.debug.print("\n🚀 Ready to drive physical robot.\n", .{});
}
