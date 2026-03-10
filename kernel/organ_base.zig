const std = @import("std");

/// 🧬 Spec: Zoe-OS Organ Interface (The VTable Standard)
/// 类似于 Go 的 Interface，定义所有器官必须遵循的物理契约。

pub const OrganInterface = struct {
    ptr: *anyopaque,
    vtable: *const VTable,

    pub const VTable = struct {
        scan: *const fn (ctx: *anyopaque) void,                 // 感官采样
        actuate: *const fn (ctx: *anyopaque, magnitude: f32) void, // 物理执行
        deinit: *const fn (ctx: *anyopaque) void,               // 释放资源
    };

    pub fn scan(self: OrganInterface) void {
        self.vtable.scan(self.ptr);
    }

    pub fn actuate(self: OrganInterface, magnitude: f32) void {
        self.vtable.actuate(self.ptr, magnitude);
    }
};

/// --- 具体实现类 1: PowerOrgan ---
pub const PowerOrgan = struct {
    voltage: f32 = 12.0,

    pub fn init() PowerOrgan { return PowerOrgan{}; }

    pub fn scan(ctx: *anyopaque) void {
        const self: *PowerOrgan = @ptrCast(@alignCast(ctx));
        std.debug.print("🫀 [POWER] Voltage: {d:.1}V\n", .{self.voltage});
    }

    pub fn actuate(ctx: *anyopaque, magnitude: f32) void {
        const self: *PowerOrgan = @ptrCast(@alignCast(ctx));
        self.voltage = magnitude * 12.0;
        std.debug.print("⚡ [POWER] Set Output: {d:.1}V\n", .{self.voltage});
    }

    pub fn organ(self: *PowerOrgan) OrganInterface {
        return .{
            .ptr = self,
            .vtable = &.{
                .scan = scan,
                .actuate = actuate,
                .deinit = struct { fn deinit(_: *anyopaque) void {} }.deinit,
            },
        };
    }
};

/// --- 具体实现类 2: MotorOrgan ---
pub const MotorOrgan = struct {
    pos: f32 = 0.0,

    pub fn init() MotorOrgan { return MotorOrgan{}; }

    pub fn scan(ctx: *anyopaque) void {
        const self: *MotorOrgan = @ptrCast(@alignCast(ctx));
        std.debug.print("🦶 [MOTOR] Position: {d:.1}\n", .{self.pos});
    }

    pub fn actuate(ctx: *anyopaque, magnitude: f32) void {
        const self: *MotorOrgan = @ptrCast(@alignCast(ctx));
        self.pos += magnitude * 10.0;
        std.debug.print("🏃 [MOTOR] Moving to: {d:.1}\n", .{self.pos});
    }

    pub fn organ(self: *MotorOrgan) OrganInterface {
        return .{
            .ptr = self,
            .vtable = &.{
                .scan = scan,
                .actuate = actuate,
                .deinit = struct { fn deinit(_: *anyopaque) void {} }.deinit,
            },
        };
    }
};

pub fn main() !void {
    std.debug.print("\n🧬 ZOE-OS | Polymorphic Organ System Active\n", .{});
    
    var p_orig = PowerOrgan.init();
    var m_orig = MotorOrgan.init();

    const organs = [_]OrganInterface{ p_orig.organ(), m_orig.organ() };

    // 统一循环调用 (The Metabolic Loop)
    for (organs) |o| {
        o.scan();
        o.actuate(0.5);
    }
}
