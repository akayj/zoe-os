const std = @import("std");
pub const Feeling = enum { smooth, stiff, jitter };

pub fn motor_intent(intent: []const u8) Feeling {
    std.debug.print("🦾 [Organ:Servo] Handling physical intent: {s}\n", .{intent});
    // 逻辑：发送 PWM 信号
    return .smooth;
}
