const std = @import("std");

/// Effector: The Physical Motor Control of Zoe-OS.
/// Designed for low-level GPIO/PWM/Serial communication on devices like Raspberry Pi.

pub const JointState = struct {
    id: u8,
    angle: f32,
    torque: f32,
};

pub fn move_joint(id: u8, angle: f32) !void {
    // 模拟物理驱动：在真正的机器人上，这里是 I2C/Serial 的底层写入
    std.debug.print("🦾 [EFFECTOR] Moving Joint {d} to {d:.2} degrees...\n", .{id, angle});
}

pub fn emergency_stop() void {
    std.debug.print("🚨 [CRITICAL] EMERGENCY STOP TRIGGERED! Cutting power to motors.\n", .{});
}
