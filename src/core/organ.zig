const std = @import("std");

/// 🧬 Spec: Zoe-OS Organ (Comptime Specialization)
/// 遵循 Zig 哲学：使用 comptime 实现静态多态，消除虚表开销。
/// 数据导向设计：器官仅作为逻辑容器，由主循环在编译期特化。

pub fn Organ(comptime T: type) type {
    return struct {
        data: T,

        pub fn init(initial_data: T) @This() {
            return .{ .data = initial_data };
        }

        /// 编译期内联特化：主循环直接调用具体实现的 scan/actuate
        pub inline fn metabolicLoop(self: *@This(), magnitude: f32) void {
            // 在编译期检查 T 是否有对应的接口函数
            if (@hasDecl(T, "scan")) {
                self.data.scan();
            }
            if (@hasDecl(T, "actuate")) {
                self.data.actuate(magnitude);
            }
        }
    };
}

/// --- 具体实现类: Motor (数据导向) ---
pub const MotorData = struct {
    pos: f32 = 0.0,
    
    pub fn scan(self: *MotorData) void {
        std.debug.print("🦶 [MOTOR] Pos: {d:.1}\n", .{self.pos});
    }

    pub fn actuate(self: *MotorData, magnitude: f32) void {
        self.pos += magnitude * 10.0;
        std.debug.print("🏃 [MOTOR] Moving -> {d:.1}\n", .{self.pos});
    }
};

/// --- 具体实现类: Power (数据导向) ---
pub const PowerData = struct {
    voltage: f32 = 12.0,

    pub fn scan(self: *PowerData) void {
        std.debug.print("🫀 [POWER] Volt: {d:.1}V\n", .{self.voltage});
    }

    pub fn actuate(self: *PowerData, magnitude: f32) void {
        self.voltage = magnitude * 12.0;
        std.debug.print("⚡ [POWER] Output -> {d:.1}V\n", .{self.voltage});
    }
};

pub fn main() !void {
    std.debug.print("\n🧬 ZOE-OS | Comptime Specialized Organs Active\n", .{});
    
    // 编译期静态特化
    var motor = Organ(MotorData).init(.{});
    var power = Organ(PowerData).init(.{});

    // 零开销调用：这些调用在汇编级别是直接内联的，没有虚表跳转
    motor.metabolicLoop(0.8);
    power.metabolicLoop(0.5);
}
