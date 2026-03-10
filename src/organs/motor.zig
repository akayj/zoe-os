const std = @import("std");

/// 🦶 Motor Organ: 具备行走本能的动力模块
pub const MotorData = struct {
    pos: f32 = 0.0,
    target: f32 = 0.0,
    
    pub fn scan(self: *MotorData) void {
        std.debug.print("🦶 [MOTOR] Pos: {d:.1}\n", .{self.pos});
    }

    pub fn actuate(self: *MotorData, magnitude: f32) void {
        self.target = magnitude * 100.0;
        // 物理平滑逻辑
        if (self.pos < self.target) self.pos += 1.0;
        std.debug.print("🏃 [MOTOR] Moving -> {d:.1}\n", .{self.pos});
    }
};
