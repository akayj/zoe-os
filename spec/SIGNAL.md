# 🌐 Zoe-OS Universal Connectivity

Zoe-OS 采用 **"内核恒定，能力插拔"** 的架构。

## 架构概览

```
                    ┌──────────────────┐
                    │   Core (Python)  │
                    │      大脑        │
                    └────────┬─────────┘
                             │ INTENT
                             ▼
                    ┌──────────────────┐
                    │   Kernel (Zig)   │
                    │    语义总线       │
                    └────────┬─────────┘
                             │ zoe.sock
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ Organ: FS    │ │ Organ: Servo │ │ Organ: Net   │
     │   文件系统    │ │    舵机      │ │    网络      │
     └──────────────┘ └──────────────┘ └──────────────┘
```

## 1. 核心 (The Kernel) - Zig

内核是永恒的。它不包含任何场景代码。

### 唯一任务

- 维护 `zoe-bus.sock` 语义总线
- 转发意图到目标器官
- 收集感官上报

### 反射机制

内核内置了对总线健康的监控：

- 器官心跳超时 → 标记离线 → 回收资源
- 异常信号 → 记录日志 → 通知大脑

### 内核代码示例

```zig
// kernel/pulse.zig 核心逻辑
while (true) {
    const signal = try receive_signal();
    switch (signal.type) {
        .REGISTER => try register_organ(signal),
        .INTENT => try forward_intent(signal),
        .FEELING => try forward_to_brain(signal),
        .BEAT => try update_heartbeat(signal),
    }
}
```

## 2. 器官 (The Organs) - Any Language

器官是动态的。你只需要用你擅长的语言写好驱动，并连接总线。

### 注册流程

```json
// 1. 连接 Socket
connect("/tmp/zoe.sock")

// 2. 发送注册信号
{
  "type": "REGISTER",
  "organ_id": "fs-01",
  "capability": "FILE_SYSTEM",
  "version": "0.1.0",
  "actions": ["READ", "WRITE", "LIST", "DELETE"]
}

// 3. 等待确认
{
  "type": "ACK",
  "status": "REGISTERED",
  "organ_id": "fs-01"
}
```

### 执行循环

```python
while True:
    signal = socket.recv()
    if signal["type"] == "INTENT":
        result = execute(signal["action"], signal["params"])
        socket.send({"type": "FEELING", "result": result})
```

## 3. 大脑 (The Core) - Python

大脑是灵魂。它通过总线指挥所有已注册的器官。

### 无需改动

换场景只需增加/更换器官节点，大脑代码保持极简。

### 意图下发

```python
# 大脑决定整理桌面
intent = {
    "type": "INTENT",
    "target": "fs-01",
    "action": "ORGANIZE",
    "params": {"path": "~/Desktop", "strategy": "by_type"}
}
zoe_bus.send(intent)
```

---

## Signal 协议规范

### 消息类型

| 类型     | 方向           | 用途     |
| -------- | -------------- | -------- |
| REGISTER | Organ → Kernel | 器官注册 |
| INTENT   | Core → Organ   | 意图下发 |
| FEELING  | Organ → Core   | 感官上报 |
| BEAT     | Organ → Kernel | 心跳信号 |
| ACK      | Kernel → Organ | 确认响应 |
| ERROR    | Any → Any      | 错误报告 |

### 消息格式

#### REGISTER

```json
{
  "type": "REGISTER",
  "organ_id": "string",
  "capability": "FILE_SYSTEM | SERVO | NETWORK | DISPLAY | CUSTOM",
  "version": "semver",
  "actions": ["string"],
  "metadata": {}
}
```

#### INTENT

```json
{
  "type": "INTENT",
  "id": "uuid",
  "target": "organ_id",
  "action": "string",
  "params": {},
  "priority": "low | normal | high | critical",
  "timeout": 30
}
```

#### FEELING

```json
{
  "type": "FEELING",
  "source": "organ_id",
  "intent_id": "uuid",
  "status": "success | failure | partial",
  "pressure": 0.0-1.0,
  "summary": "string",
  "details": {}
}
```

#### BEAT

```json
{
  "type": "BEAT",
  "organ_id": "string",
  "timestamp": "ISO8601",
  "entropy": 0.0-1.0
}
```

#### ACK

```json
{
  "type": "ACK",
  "status": "ok | error",
  "message_id": "uuid",
  "error": "string?"
}
```

#### ERROR

```json
{
  "type": "ERROR",
  "code": "string",
  "message": "string",
  "source": "organ_id?",
  "recoverable": true | false
}
```

---

### 示例：如何适配新场景

#### 1. 机器人场景

```python
# servo_driver.py
import socket
import json

sock = socket.connect("/tmp/zoe.sock")
sock.send(json.dumps({
    "type": "REGISTER",
    "organ_id": "servo-01",
    "capability": "SERVO",
    "actions": ["MOVE", "STOP", "RESET"]
}))

while True:
    msg = json.loads(sock.recv())
    if msg["type"] == "INTENT":
        # 执行舵机动作
        execute_servo(msg["action"], msg["params"])
```

#### 2. 桌面整理场景

```python
# file_sorter.py
import socket
import json

sock = socket.connect("/tmp/zoe.sock")
sock.send(json.dumps({
    "type": "REGISTER",
    "organ_id": "fs-01",
    "capability": "FILE_SYSTEM",
    "actions": ["ORGANIZE", "CLEANUP", "SCAN"]
}))

while True:
    msg = json.loads(sock.recv())
    if msg["type"] == "INTENT":
        # 执行文件操作
        organize_files(msg["params"])
```

#### 3. Zoe-OS 内核

稳坐中军，一行代码不用改。
