const std = @import("std");

/// Muscle: 抽象肌肉层。
/// 这里的职责是把底层的电信号（GPIO/PWM）封装成生理本能。
/// 大脑永远看不到具体的 Pin 脚或电压。

pub const Sensation = enum {
    smooth,      // 流畅
    stiff,       // 僵硬（受阻）
    collided,    // 碰撞
    overheated,  // 过热
};

pub fn move_to_intent(intent: []const u8) Sensation {
    // 模拟底层闭环控制：
    // 大脑说“抓取”，肌肉层自己去算角度、避障、控制力度。
    std.debug.print("🦾 [Muscle] Executing intent: {s}...\n", .{intent});
    
    // 模拟遇到阻力：
    return .stiff; 
}

pub fn get_feeling() Sensation {
    // 向大脑汇报的只有“感觉”，没有数据。
    return .smooth;
}
