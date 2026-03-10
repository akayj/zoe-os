const std = @import("std");
const effector = @import("effector.zig");

pub fn main() !void {
    std.debug.print("\n🐝 ZOE-OS KERNEL | Interoception Active\n", .{});
    
    // 大脑发来一个意图
    const feeling = effector.move_to_intent("GRAB_COFFEE");
    
    // 内核只向大脑反馈“感觉”
    std.debug.print("📡 [Signal] Feeling: {s}\n", .{@tagName(feeling)});
}
