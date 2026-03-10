# 🏗️ Spec: Zoe-OS Dual-Engine Architecture (v1.1)

Zoe-OS 采用“身脑分离”的双引擎架构，以解决 AI Agent 在物理世界中的实时性与鲁棒性问题。

---

## 1. 反射弧分层标准 (Reflex Arc Latency)

为了确保物理实体的安全与丝滑，Zoe 将反馈回路分为三个时延等级：

| 等级 | 名称 | 处理单元 | 目标时延 | 典型场景 |
|------|------|----------|----------|----------|
| **L0** | **本能反射 (Reflex)** | Zig Kernel | **< 20ms** | 紧急停机、碰撞闪避、握力自适应 |
| **L1** | **反应微调 (Reactive)**| Local Plugins| **< 100ms**| 轨迹平滑、视觉动态伺服 |
| **L2** | **认知策略 (Cognitive)**| Python Brain | **< 2s** | 任务重规划、语义理解、逻辑推理 |

---

## 2. 动态自洽：压力代谢模型 (PBM Metabolism)

Zoe-OS 不执行死板的线性计划，而是通过 **PBM (Pressure-Balance-Memory)** 矩阵实现动态规划。

### 2.1 干扰处理 (Disturbance Handling)
1. **输入**: 外界环境变化（如目标物体移动）。
2. **传导**: 感官词（FEELING）实时注入 PBM 矩阵。
3. **代谢**: 压力值（Pressure）瞬间激增，触发 L0/L1 级的即时反馈。
4. **收敛**: 系统寻找压力最小的路径（Potential Field），自动实现动态规划。

### 2.2 性能保障 (Stability)
- **绝对隔离**: L0 级保护逻辑硬编码在 Zig 内核中，不依赖大脑状态，确保即便 Python 脑崩溃，实体也不会失控。
- **内存零开销**: 关键路径 (Critical Path) 采用 Zig 手动内存管理，规避 GC 带来的随机卡顿。

---
*Architected by Xiao Xin | Direction by akayj*

---

## 3. 抗震机制：消除“数字癫痫” (Anti-Oscillation Guard)

为了防止反馈回路产生的物理震颤，Zoe-OS 实施以下约束：

### 3.1 物理阻尼 (Reflex Damping)
- **L0 过滤**: Zig 内核强制执行低通滤波，丢弃超过执行器物理带宽 (Physical Bandwidth) 的高频微小指令。
- **平滑插值**: 采用 S-Curve 加速度控制，确保物理动作的导数 (Jerk) 连续。

### 3.2 决策迟滞 (Cognitive Hysteresis)
- **PBM 阈值**: 系统仅在压力变化量超过 $\Delta P_{threshold}$ 时触发动作，避免在微小扰动下频繁修正。
- **动作惯性**: 为意图切换（Intent Switching）增加能量代价函数，防止系统在两个极近的平衡点之间反复横跳。
