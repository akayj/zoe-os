//! Zoe-OS Kernel - Signal Bus
//!
//! 核心功能:
//! - 维护 zoe.sock 语义总线
//! - 器官注册与管理
//! - 意图路由与转发
//! - 心跳监控

const std = @import("std");
const net = std.net;
const fs = std.fs;
const json = std.json;
const time = std.time;

// ============ 常量定义 ============

const SOCKET_PATH = "/tmp/zoe.sock";
const HEARTBEAT_INTERVAL = 5 * time.ns_per_s; // 5秒
const HEARTBEAT_TIMEOUT = 15 * time.ns_per_s; // 15秒超时
const MAX_ORGANS = 64;
const BUFFER_SIZE = 4096;

// ============ Signal 类型 ============

const SignalType = enum(u8) {
    REGISTER = 1,
    INTENT = 2,
    FEELING = 3,
    BEAT = 4,
    ACK = 5,
    ERROR = 6,
};

const Signal = struct {
    type: SignalType,
    organ_id: ?[]const u8 = null,
    capability: ?[]const u8 = null,
    target: ?[]const u8 = null,
    action: ?[]const u8 = null,
    params: ?json.Value = null,
    content: ?json.Value = null,
    status: ?[]const u8 = null,
    message: ?[]const u8 = null,
};

// ============ 器官注册表 ============

const Organ = struct {
    id: []const u8,
    capability: []const u8,
    stream: net.Stream,
    last_heartbeat: i64,
    is_active: bool,
};

const OrganRegistry = struct {
    organs: [MAX_ORGANS]?Organ,
    count: usize,
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) OrganRegistry {
        var registry: OrganRegistry = undefined;
        registry.count = 0;
        registry.allocator = allocator;
        for (&registry.organs) |*slot| {
            slot.* = null;
        }
        return registry;
    }

    fn register(self: *OrganRegistry, id: []const u8, capability: []const u8, stream: net.Stream) bool {
        if (self.count >= MAX_ORGANS) return false;

        // 检查是否已注册
        for (self.organs[0..self.count]) |*slot| {
            if (slot.*) |*organ| {
                if (std.mem.eql(u8, organ.id, id)) {
                    // 更新已存在的器官
                    organ.stream = stream;
                    organ.last_heartbeat = time.timestamp();
                    organ.is_active = true;
                    return true;
                }
            }
        }

        // 添加新器官
        self.organs[self.count] = Organ{
            .id = id,
            .capability = capability,
            .stream = stream,
            .last_heartbeat = time.timestamp(),
            .is_active = true,
        };
        self.count += 1;
        return true;
    }

    fn find(self: *OrganRegistry, id: []const u8) ?*Organ {
        for (self.organs[0..self.count]) |*slot| {
            if (slot.*) |*organ| {
                if (std.mem.eql(u8, organ.id, id)) {
                    return organ;
                }
            }
        }
        return null;
    }

    fn findByCapability(self: *OrganRegistry, capability: []const u8) ?*Organ {
        for (self.organs[0..self.count]) |*slot| {
            if (slot.*) |*organ| {
                if (std.mem.eql(u8, organ.capability, capability) and organ.is_active) {
                    return organ;
                }
            }
        }
        return null;
    }

    fn updateHeartbeat(self: *OrganRegistry, id: []const u8) void {
        if (self.find(id)) |organ| {
            organ.last_heartbeat = time.timestamp();
            organ.is_active = true;
        }
    }

    fn checkTimeouts(self: *OrganRegistry) void {
        const now = time.timestamp();
        for (self.organs[0..self.count]) |*slot| {
            if (slot.*) |*organ| {
                if (now - organ.last_heartbeat > HEARTBEAT_TIMEOUT / time.ns_per_s) {
                    organ.is_active = false;
                    std.debug.print("[Kernel] Organ {s} timeout, marked inactive\n", .{organ.id});
                }
            }
        }
    }
};

// ============ 主函数 ============

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var registry = OrganRegistry.init(allocator);

    // 1. 清理旧 Socket
    fs.cwd().deleteFile(SOCKET_PATH) catch {};

    // 2. 初始化 Unix Socket 服务器
    var server = try net.Address.initUnix(SOCKET_PATH);
    var listener = try server.listen(.{ .kernel_backlog = 128 });
    defer listener.deinit();

    std.debug.print("\n🐝 ZOE-OS KERNEL v0.3.0 | Signal Bus Active\n", .{});
    std.debug.print("Pulse Bus: {s}\n", .{SOCKET_PATH});
    std.debug.print("Waiting for organs to register...\n\n", .{});

    // 3. 主循环
    while (true) {
        // 接受新连接
        var conn = try listener.accept();

        // 读取信号
        var buffer: [BUFFER_SIZE]u8 = undefined;
        const bytes_read = conn.stream.read(&buffer) catch |err| {
            std.debug.print("[Kernel] Read error: {}\n", .{err});
            continue;
        };

        if (bytes_read == 0) continue;

        const message = buffer[0..bytes_read];
        std.debug.print("[Kernel] Received: {s}\n", .{message});

        // 解析并处理信号
        processSignal(allocator, &registry, message, conn.stream) catch |err| {
            std.debug.print("[Kernel] Process error: {}\n", .{err});
        };

        // 检查心跳超时
        registry.checkTimeouts();
    }
}

fn processSignal(allocator: std.mem.Allocator, registry: *OrganRegistry, message: []const u8, stream: net.Stream) !void {
    // 解析 JSON
    const parsed = try json.parseFromSlice(json.Value, allocator, message, .{});
    defer parsed.deinit();

    const root = parsed.value;

    // 确保根节点是 JSON 对象
    if (root != .object) {
        try sendError(stream, "Expected JSON object");
        return;
    }

    // 获取信号类型
    const type_val = root.object.get("type") orelse {
        try sendError(stream, "Missing required field: type");
        return;
    };
    const type_str = switch (type_val) {
        .string => |s| s,
        else => {
            try sendError(stream, "Invalid signal type");
            return;
        },
    };

    // 处理不同类型的信号
    if (std.mem.eql(u8, type_str, "REGISTER")) {
        try handleRegister(allocator, registry, root, stream);
    } else if (std.mem.eql(u8, type_str, "INTENT")) {
        try handleIntent(allocator, registry, root, stream);
    } else if (std.mem.eql(u8, type_str, "FEELING")) {
        try handleFeeling(allocator, registry, root, stream);
    } else if (std.mem.eql(u8, type_str, "BEAT")) {
        try handleBeat(allocator, registry, root, stream);
    } else {
        try sendError(stream, "Unknown signal type");
    }
}

fn handleRegister(allocator: std.mem.Allocator, registry: *OrganRegistry, root: json.Value, stream: net.Stream) !void {
    const organ_id_val = root.object.get("organ_id") orelse {
        try sendError(stream, "Missing required field: organ_id");
        return;
    };
    const organ_id = switch (organ_id_val) {
        .string => |s| s,
        else => {
            try sendError(stream, "Invalid organ_id");
            return;
        },
    };

    const capability_val = root.object.get("capability") orelse {
        try sendError(stream, "Missing required field: capability");
        return;
    };
    const capability = switch (capability_val) {
        .string => |s| s,
        else => {
            try sendError(stream, "Invalid capability");
            return;
        },
    };

    // 复制字符串到堆上
    const id_copy = try allocator.dupe(u8, organ_id);
    const cap_copy = try allocator.dupe(u8, capability);

    if (registry.register(id_copy, cap_copy, stream)) {
        std.debug.print("[Kernel] Organ registered: {s} ({s})\n", .{ id_copy, cap_copy });
        try sendAck(stream, "REGISTERED", id_copy);
    } else {
        try sendError(stream, "Registry full");
    }
}

fn handleIntent(allocator: std.mem.Allocator, registry: *OrganRegistry, root: json.Value, stream: net.Stream) !void {
    const target_val = root.object.get("target") orelse {
        try sendError(stream, "Missing required field: target");
        return;
    };
    const target = switch (target_val) {
        .string => |s| s,
        else => {
            try sendError(stream, "Invalid target");
            return;
        },
    };

    // 查找目标器官
    if (registry.find(target)) |organ| {
        if (!organ.is_active) {
            try sendError(stream, "Target organ inactive");
            return;
        }

        // 转发意图到目标器官
        const intent_json = try json.stringifyAlloc(allocator, root, .{});
        defer allocator.free(intent_json);

        _ = try organ.stream.write(intent_json);
        std.debug.print("[Kernel] Intent forwarded to: {s}\n", .{target});

        try sendAck(stream, "FORWARDED", target);
    } else {
        try sendError(stream, "Target organ not found");
    }
}

fn handleFeeling(allocator: std.mem.Allocator, registry: *OrganRegistry, root: json.Value, stream: net.Stream) !void {
    _ = registry;

    std.debug.print("[Kernel] Feeling received from organ\n", .{});

    // 这里应该转发给大脑 (Core)
    const feeling_json = try json.stringifyAlloc(allocator, root, .{});
    defer allocator.free(feeling_json);

    std.debug.print("[Kernel] Feeling: {s}\n", .{feeling_json});

    // 回复确认，避免连接挂起
    try sendAck(stream, "FEELING_RECEIVED", "kernel");
}

fn handleBeat(allocator: std.mem.Allocator, registry: *OrganRegistry, root: json.Value, stream: net.Stream) !void {
    _ = allocator;

    const organ_id_val = root.object.get("organ_id") orelse {
        try sendError(stream, "Missing required field: organ_id");
        return;
    };
    const organ_id = switch (organ_id_val) {
        .string => |s| s,
        else => {
            try sendError(stream, "Invalid organ_id");
            return;
        },
    };

    registry.updateHeartbeat(organ_id);
    std.debug.print("[Kernel] Heartbeat from: {s}\n", .{organ_id});

    // 发送心跳响应
    try sendAck(stream, "BEAT_OK", organ_id);
}

fn sendAck(stream: net.Stream, status: []const u8, organ_id: []const u8) !void {
    var buffer: [256]u8 = undefined;
    const msg = try std.fmt.bufPrint(&buffer, "{{\"type\":\"ACK\",\"status\":\"{s}\",\"organ_id\":\"{s}\"}}\n", .{ status, organ_id });
    _ = try stream.write(msg);
}

fn sendError(stream: net.Stream, message: []const u8) !void {
    var buffer: [256]u8 = undefined;
    const msg = try std.fmt.bufPrint(&buffer, "{{\"type\":\"ERROR\",\"message\":\"{s}\"}}\n", .{message});
    _ = try stream.write(msg);
}
