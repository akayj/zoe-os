# 🧠 Zoe-OS PBM Layers

Zoe-OS 采用四层标准化架构，支持快速二次开发。

## 1. 物理层 (Physical Layer)
- **器官 (Organs)**: 具体的硬件或系统驱动（如 `organs/fs.zig`, `organs/servo.zig`）。
- **职责**: 处理底层细节，将物理状态压缩为“感官抽象” (Feelings)。

## 2. 传输层 (Transmission Layer)
- **通道 (Pulse)**: 基于 `zoe-socket` 的 Signal 总线。
- **职责**: 以脉冲形式传递意图与感官，严禁细节外溢。

## 3. 记忆层 (Memory Layer)
- **切片 (.seed)**: 结构化经验 DAG。
- **职责**: 提供自传体背景，让决策具备连续性。

## 4. 决策层 (Decision Layer)
- **大脑 (Core)**: Python 逻辑与 LLM。
- **职责**: 接收感官，评估压力，下达高维意图。
