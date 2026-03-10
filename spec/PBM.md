# 🧠 Zoe-OS PBM Layers

Zoe-OS 采用四层标准化架构，支持快速二次开发。

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    决策层 (Decision)                         │
│                    Python + LLM                             │
│              接收感官 → 评估压力 → 下达意图                    │
├─────────────────────────────────────────────────────────────┤
│                    记忆层 (Memory)                           │
                    │    .seed 文件 / 经验 DAG                 │
│              提供自传体背景，决策具备连续性                      │
├─────────────────────────────────────────────────────────────┤
│                    传输层 (Transmission)                     │
│                    Unix Socket / Pulse                      │
│              以脉冲形式传递意图与感官，严禁细节外溢              │
├─────────────────────────────────────────────────────────────┤
│                    物理层 (Physical)                         │
│                    Zig 驱动 / Organs                         │
│              处理底层细节，将物理状态压缩为感官                 │
└─────────────────────────────────────────────────────────────┘
```

## 1. 物理层 (Physical Layer)

### 器官 (Organs)

具体的硬件或系统驱动，如：

- `organs/fs.zig` - 文件系统器官
- `organs/servo.zig` - 舵机控制器官
- `organs/display.zig` - 显示器官
- `organs/network.zig` - 网络器官

### 职责

- 处理底层硬件/系统细节
- 将物理状态压缩为"感官抽象" (Feelings)
- 执行来自上层的意图 (Intent)

### 感官抽象示例

```json
{
  "type": "FEELING",
  "source": "fs",
  "content": {
    "pressure": 0.7,
    "summary": "磁盘空间紧张",
    "details": { "used": "85%", "free": "15GB" }
  }
}
```

## 2. 传输层 (Transmission Layer)

### 通道 (Pulse)

基于 `zoe.sock` 的 Signal 总线。

### 职责

- 以脉冲形式传递意图与感官
- 严禁细节外溢（只传语义，不传原始数据）
- 维护器官注册表

### 通信协议

```json
// 器官注册
{"type": "REGISTER", "capability": "FILE_SYSTEM", "organ_id": "fs-01"}

// 意图下发
{"type": "INTENT", "target": "fs-01", "action": "CLEANUP", "params": {}}

// 感官上报
{"type": "FEELING", "source": "fs-01", "content": {...}}
```

## 3. 记忆层 (Memory Layer)

### 切片 (.seed)

结构化经验 DAG，格式：

```
.seed/
├── 2026-03-10.seed    # 今日经验
├── 2026-03-09.seed    # 昨日经验
└── core.seed          # 核心记忆
```

### 职责

- 提供自传体背景
- 让决策具备连续性
- 支持经验回放与学习

### .seed 文件格式

```json
{
  "date": "2026-03-10",
  "episodes": [
    {
      "time": "19:30",
      "intent": "整理桌面",
      "actions": ["扫描文件", "分类", "移动"],
      "outcome": "success",
      "lessons": ["用户偏好按类型分类"]
    }
  ]
}
```

## 4. 决策层 (Decision Layer)

### 大脑 (Core)

Python 逻辑与 LLM，核心是 Sense→Think→Act→Verify 循环。

### 职责

- 接收感官 (Feelings)
- 评估压力 (Pressure)
- 下达高维意图 (Intent)
- 验证结果 (Verify)

### 认知循环

```python
while True:
    feelings = receive_feelings()      # Sense
    pressure = evaluate_pressure(feelings)  # Think
    intent = decide_intent(pressure)   # Think
    result = execute_intent(intent)    # Act
    verify(result)                      # Verify
```

## 层间通信规则

| 源层        | 目标层   | 允许内容 | 禁止内容 |
| ----------- | -------- | -------- | -------- |
| 物理 → 传输 | 感官抽象 | 原始数据 |
| 传输 → 记忆 | 压缩事件 | 完整日志 |
| 记忆 → 决策 | 经验摘要 | 原始记录 |
| 决策 → 传输 | 意图指令 | 实现代码 |

## 故障恢复机制

### 物理层故障

- 器官心跳超时 → 标记离线 → 通知决策层
- 自动重连 → 恢复注册 → 继续服务

### 传输层故障

- Socket 断开 → 重建连接 → 重放未确认消息

### 决策层故障

- LLM 超时 → 降级到规则引擎 → 记录异常
