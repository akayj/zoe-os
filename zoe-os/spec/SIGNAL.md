# 🔌 Signal Specification: Sensory Reporting

Zoe-OS 的信号传输准则：**严禁传输物理细节，只准传输感官抽象。**

## 1. 禁令 (The Redlines)
- ❌ 严禁传输具体的 GPIO 引脚号。
- ❌ 严禁传输电压、电流、原始角度数值。
- ❌ 严禁传输超过 3 层的嵌套 JSON。

## 2. 准许 (The Standard Sensations)
底层内核必须将复杂的物理状态压缩为以下标准“感觉”上报大脑：

| 感觉 (Sensation) | 物理对应 | 大脑响应建议 |
|-----------------|---------|--------------|
| `SMOOTH`        | 正常运行 | 维持当前策略 |
| `STIFF`         | 遇到物理阻力 | 尝试变换角度或加大力度 |
| `COLLIDED`      | 发生碰撞 | 立即停止并重寻路 |
| `OVERHEATED`    | 硬件过载 | 强制休息 (Pause) |

## 3. 意图下达 (Intent Injection)
大脑下达的是意图 (Intent)，而非指令 (Instruction)：
- ✅ `"intent": "GRAB_CUP"`
- ❌ `"cmd": "servo_set_angle(4, 90)"`
