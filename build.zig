const std = @import("std");

/// 🛠️ Zoe-OS Build System
/// 职责：管理模块化编译，支持一键构建与测试。
pub fn build(b: *std.Build) void {
    // 1. 定义编译目标 (Standard target options)
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // 2. 创建主可执行文件 zoe-kernel
    const exe = b.addExecutable(.{
        .name = "zoe-kernel",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    // 3. 安装可执行文件 (zig build)
    b.installArtifact(exe);

    // 4. 定义运行子命令 (zig build run)
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    if (b.args) |args| {
        run_cmd.addArgs(args);
    }
    const run_step = b.step("run", "Run the Zoe-OS Kernel");
    run_step.dependOn(&run_cmd.step);

    // 5. 定义测试子命令 (zig build test)
    const exe_unit_tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    const run_exe_unit_tests = b.addRunArtifact(exe_unit_tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_exe_unit_tests.step);
}
