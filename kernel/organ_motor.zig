const std = @import("std");

/// 🦶 Organ: Motor Driver (动力器官/足部驱动)
/// 职责：不仅感应物理状态，还具备自主的行走平滑与避障反射。
/// 遵循原则：身体的平衡由“小脑” (Zig) 负责，不消耗“大脑” (LLM) 资源。

pub const MotorState = struct {
    pos: f32 = 0.0,      // 当前位置
    target: f32 = 0.0,   // 期望位置 (大脑下达)
    load: f32 = 0.0,     // 当前扭矩负载
    feeling: []const u8 = "SMOOTH",
};

pub fn main() !void {
    var limb = MotorState{};
    std.debug.print("\n🦶 ORGAN: MOTOR DRIVER | Locomotion Active\n", .{});

    while (true) {
        // 1. 模拟接收大脑的“期望位置” (Intent Sync)
        // 假设大脑希望我们走到 100.0 的位置
        limb.target = 100.0;

        // 2. 物理平滑 (Locomotion Smoothing) - 避免抖动
        if (limb.pos < limb.target) {
            limb.pos += 1.5; // 模拟平滑加速度
        }

        // 3. 障碍物反射 (The "Knee-Jerk" Reflex)
        // 模拟检测到障碍物，导致电流/负载突增
        limb.load = 0.1; // 正常负载
        if (limb.pos > 50.0 and limb.pos < 55.0) { // 假设此处有个台阶
            limb.load = 0.95; // 踢到东西了！
            
            // L0 级自主反射：立即后退并向大脑汇报“受阻”
            std.debug.print("🚨 [REFLEX] Obstacle detected! Immediate retracting... (Pos: {d:.1})\n", .{limb.pos});
            limb.pos -= 10.0; 
            limb.feeling = "STIFF";
        } else {
            limb.feeling = "SMOOTH";
        }

        // 4. 定期汇报
        std.debug.print("🏃 [LIMB] Pos: {d:.1} | Feeling: {s}\n", .{limb.pos, limb.feeling});

        // 5. 步频：20ms (工业级运动控制频率)
        std.Thread.sleep(20 * std.time.ns_per_ms);
    }
}
