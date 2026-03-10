# 🦵 Spec: Reflexive PBM (The Knee-Jerk Reflex)

Zoe-OS 的核心哲学：生存本能不应消耗认知资源。

---

## 1. 反射与认知的解耦 (Reflex vs Cognition)

在 PBM 体系中，压力代谢分为两个回路：
- **认知回路 (Cognitive Loop)**: 慢速，高能耗，负责逻辑规划。
- **反射回路 (Reflex Loop)**: 极速，零能耗，负责物理存活。

## 2. 非条件反射清单 (Unconditional Reflexes)

以下动作由 Zig 内核 (L0) 强制执行，无需经过大脑：

| 触发感官 (Stimulus) | 反射动作 (Reflex Action) | 目的 |
|-------------------|-----------------------|------|
| `SIGNAL: COLLIDED`| `HAL: REVERSE_VELOCITY`| 物理避障 / 防损 |
| `SIGNAL: OVERLOAD`| `HAL: POWER_CUT`       | 硬件保护 |
| `SIGNAL: FALLING` | `HAL: BRACE_POSITION`  | 姿态保护 |

## 3. 压力传递机制 (Pressure Transfer)
1. **执行**: 反射发生后，由内核直接执行物理动作。
2. **异步告知**: 动作完成后，内核向大脑发送 `REFLEX_EXECUTED` 信号。
3. **压力更新**: 大脑根据反射结果更新 PBM 矩阵，无需参与执行过程。

## 4. 架构铁律
- **L0 优先级**: 反射指令的优先级高于任何来自大脑的意图 (Intent)。
- **不可拦截性**: 大脑无法通过软件指令禁掉 L0 级的生存反射。

---
*Architected by Xiao Xin | Direction by akayj*
