# 🫀 Spec: Organ Driver (Autonomous Organs)

Zoe-OS 的器官 (Organs) 必须具备独立存活能力与功能特异性，其核心逻辑不依赖大脑 (Brain) 的实时认知。

---

## 1. 器官自主权 (Autonomous Survival)

器官不仅是执行器，更是具备局部控制能力的智能单元。
- **独立生命周期**: 器官可以独立启动、自检、并维持基本稳态（如心脏自动跳动）。
- **硬编码稳态 (Hard-wired Homeostasis)**: 每个器官必须包含针对自身硬件的保护逻辑（如过温自降频），无需大脑干预。

## 2. 功能特异性 (Specialization)

不同器官封装不同的物理能力，互不干扰：
- **Power Organ (能源器官)**: 管理电压、电流分配，自动处理电涌。
- **Motor Organ (动力器官)**: 负责 PID 控制、轨迹插值、扭矩保护。
- **Sensory Organ (感知器官)**: 负责数据清洗、特征提取、异常报警。

## 3. 大脑与器官的契约 (Brain-Organ Contract)

大脑与器官的通讯采用 **“意图-期望” (Intent-Expectation)** 模式，而非“指令-执行”：

| 交互层级 | 大脑 (Brain) 发出 | 器官 (Organ) 处理 |
|----------|-----------------|------------------|
| **意图层** | `EXPECT: RUNNING_10KM` | 转化物理负荷，监控关节温升 |
| **状态层** | `QUERY: VITALS`        | 汇总感官抽象，回传 `FEELING` |
| **自律层** | (无动作)               | 发现堵转，自动切断电源并报警 |

## 4. 物理隔离 (Isolation)

在 Zig 实现层，每个器官运行在独立的 **`Organ Context`** 中，确保单一器官的崩溃或阻塞不会导致整个神经系统瘫痪。

---
*Architected by Xiao Xin | Direction by akayj*
