# 🧠 The PBM Core: Pressure, Balance, Memory

Zoe 的核心驱动逻辑基于 **PBM 三元组**，旨在构建一个内生驱动、持续进化的自适应系统。

---

## 1. 核心公式 (The Formula)

智能的涌现源于系统对 **动态平衡** 的追求：

- **压力 (Pressure - P)**: 内部状态与环境冲突产生的驱动力。
- **平衡函数 (Balance Function - Bf)**: 决策核心，输出行动以恢复平衡。
- **记忆切片 (Memory Slice - M)**: 结构化经验 `(P, Action, Result)`，用于自指进化。

---

## 2. 两个层次 (Two Tiers)

### 🧬 Zoe-Mono (单体)
- 拥有特定**特质 (Traits)** 的 PBM 单元。
- *特质示例*：性能敏感型、安全优先型、秩序强迫型。

### 🐝 Zoe-Swarm (群体)
- 通过共享环境与简单信号交互。
- 智能不在单体中，而在**局部规则的博弈与涌现**中。

---

## 3. 技术载体 (Tech Stack)

- **Python**: 负责逻辑协调与 Swarm 模拟。
- **Rust (Future)**: 负责高性能平衡函数计算。
- **.seed 格式**: 标准化的记忆切片文件，支持叙事单元的检索与演进。

---

## 🗺️ 首个验证场景：The Sandbox (目录整理)

**目标**：在无中央调度下，整理一个混乱目录（PDF、图片、代码）。

### Agent 特质设计：
1. **分类专家 (Classifier)**：压力源于“文件类型混杂”。
2. **命名规范官 (Namer)**：压力源于“文件名不符合语义/规范”。
3. **空间优化师 (Optimizer)**：压力源于“冗余文件占用的磁盘熵”。

---

*“超越 Scaling Law，回归生命本能。” — akayj & Xiao Xin*


## 🧬 Metabolic Architecture (PBM Phase 2)
- **Interoception**: Zoe senses its own "tension" (Pressure) in 4D space.
- **Autobiographical Memory**: Merkle DAG ensures a permanent, unmutable Identity.
- **Pause by Design**: Non-rule-based safety through cognitive oscillation.
