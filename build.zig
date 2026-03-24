const std = @import("std");

/// 🛠️ Zoe-OS Build System
/// 职责：管理模块化编译，支持一键构建与测试。
pub fn build(b: *std.Build) void {
    // 1. 定义编译目标 (Standard target options)
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // 2. 创建主可执行文件 zoe-kernel (简版反射总线)
    const exe = b.addExecutable(.{
        .name = "zoe-kernel",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    // 3. 安装可执行文件 (zig build)
    b.installArtifact(exe);

    // 4. 创建完整 Signal Bus 内核 (pulse.zig)
    const pulse_exe = b.addExecutable(.{
        .name = "zoe-pulse",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/core/pulse.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    b.installArtifact(pulse_exe);

    // 5. 定义运行子命令 (zig build run)
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    if (b.args) |args| {
        run_cmd.addArgs(args);
    }
    const run_step = b.step("run", "Run the Zoe-OS Kernel (simple reflex bus)");
    run_step.dependOn(&run_cmd.step);

    // 6. 定义 pulse 运行子命令 (zig build run-pulse)
    const run_pulse_cmd = b.addRunArtifact(pulse_exe);
    run_pulse_cmd.step.dependOn(b.getInstallStep());
    const run_pulse_step = b.step("run-pulse", "Run the Zoe-OS Signal Bus Kernel");
    run_pulse_step.dependOn(&run_pulse_cmd.step);

    // 7. 定义测试子命令
    const exe_unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_exe_unit_tests = b.addRunArtifact(exe_unit_tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_exe_unit_tests.step);
}
