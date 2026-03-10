const std = @import("std");

/// 🫀 Power Organ: 具备 L0 级保护的能源模块
pub const PowerData = struct {
    voltage: f32 = 12.0,

    pub fn scan(self: *PowerData) void {
        std.debug.print("🫀 [POWER] Volt: {d:.1}V\n", .{self.voltage});
    }

    pub fn actuate(self: *PowerData, magnitude: f32) void {
        self.voltage = magnitude * 12.0;
        std.debug.print("⚡ [POWER] Set Output -> {d:.1}V\n", .{self.voltage});
    }
};
