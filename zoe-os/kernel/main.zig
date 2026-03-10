const std = @import("std");
const fs_organ = @import("organs/fs.zig");
const servo_organ = @import("organs/servo.zig");

pub fn main() !void {
    std.debug.print("\n🐝 ZOE-OS KERNEL | Multi-Organ Support v0.3.0\n", .{});
    
    // 示例：在桌面整理场景下运行
    const f1 = fs_organ.organize_intent("CLEAN_TMP_FILES");
    std.debug.print("📡 [Signal] Digital Feeling: {s}\n", .{@tagName(f1)});

    // 示例：在机器人场景下运行
    const f2 = servo_organ.motor_intent("WAVE_HAND");
    std.debug.print("📡 [Signal] Physical Feeling: {s}\n", .{@tagName(f2)});
}
