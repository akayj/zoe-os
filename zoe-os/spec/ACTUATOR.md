# 🦾 Actuator Standard: Physical Execution Protocol

Zoe-OS 如何驱动物理实体的舵机与电机。

## 1. 关节控制 (Joint Control)
- **ID**: 每个关节的唯一标识 (0-255)。
- **Angle**: 旋转角度 (弧度或角度)。
- **Torque**: 扭矩限制 (0.0 - 1.0)。

## 2. 物理反射 (Reflexive Actions)
为了保护硬件，有些动作必须在 Zig 内核中硬编码：
- **Collision Halt**: 传感器发现阻力超过阈值，立即停止。
- **Temperature Throttling**: 电机过热自动断电。

## 3. 指令集 (Payload Sample)
```json
{
  "type": "ACTUATOR",
  "content": {
    "action": "MOVE",
    "joint_id": 1,
    "target_angle": 90.0
  }
}
```
