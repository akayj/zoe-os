const std = @import("std");
const net = std.net;
const fs = std.fs;

pub fn main() !void {
    const socket_path = "/tmp/zoe.sock";
    
    // 1. 清理旧 Socket
    fs.cwd().deleteFile(socket_path) catch {};

    // 2. 物理层监听初始化 (Reflex Arc)
    var server = try net.Address.initUnix(socket_path);
    var listener = try server.listen(.{ .kernel_backlog = 128 });
    defer listener.deinit();

    std.debug.print("\n🐝 ZOE-OS KERNEL v0.2.0 | Body Engaged\n", .{});
    std.debug.print("Pulse Bus Active on {s}\n", .{socket_path});

    while (true) {
        var conn = try listener.accept();
        defer conn.stream.close();

        // 核心心跳信号 (Metabolic Heartbeat)
        const msg = "{\"signal\": \"BEAT\", \"entropy\": 0.42}\n";
        _ = try conn.stream.write(msg);
        
        // 0.15.2 兼容版 Sleep (5秒)
        std.Thread.sleep(5 * std.time.ns_per_s);
    }
}
