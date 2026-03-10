# 🦾 Spec: Hardware Abstraction Layer (HAL)

Zoe-OS 如何在不修改内核的情况下，驱动虚拟实体 (GUI) 或实体机器人。

---

## 1. 意图到物理的降维 (Intent to Physics)
Zoe 的决策层 (Brain) 只发送高维意图。HAL 层负责将其解构为特定的物理指令。

- **Brain**: `GRAB_COFFEE`
- **HAL (Intention Decomposition)**:
    - `ACTUATE(ARM, [x, y, z])`
    - `ACTUATE(GRIPPER, 1.0)`

## 2. 标准指令格式 (Standard Command)
所有连接到 `zoe-bus.sock` 的器官 (Organs) 必须遵循以下 JSON 信号格式：

```json
{
  "op": "ACTUATE",
  "target": "string",  // 如 "SERVO_1", "MOUSE_L", "WHEEL_R"
  "magnitude": 0.0-1.0, // 归一化的力度/位置
  "velocity": 0.0-1.0,  // 归一化的速度
  "feedback": boolean   // 是否需要感官回传
}
```

## 3. 感官回传标准 (Sensor Feedback)
无论是 GUI 还是实体传感器，回传的“感觉”必须抽象为以下语义：

| 原始信号 (Raw) | HAL 抽象感官 (Feeling) |
|---------------|-----------------------|
| 扭矩超限 / 坐标突变 | `FEELING: STIFF` (受阻/紧绷) |
| 到达物理极限 | `FEELING: LIMIT` (到头了) |
| 检测到碰撞 | `FEELING: COLLIDED` (撞击) |
| 运行平稳 | `FEELING: SMOOTH` (顺滑) |

## 4. 驱动解耦原则 (Decoupling)
- **Virtual Driver (GUI)**: 监听 `ACTUATE` -> 映射为 `PyAutoGUI` 事件。
- **Physical Driver (Robot)**: 监听 `ACTUATE` -> 映射为 `Serial/I2C` 指令。

**Core Axiom**: Zoe-OS 的内核不关心身体是碳基还是硅基，它只管理信号的平衡与压力的代谢。

---
*Architected by Xiao Xin | Direction by akayj*
