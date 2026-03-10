# 🖥️ Zoe-OS: The Agentic Operating System

> **"Traditional OS manages hardware. Zoe-OS manages intelligence."**

Zoe-OS 是一个基于 **Zoe-Agent** 内核构建的实验性 **AI 原生操作系统 (Agentic OS)**。它不仅运行代码，更在运行“意图”。

---

## 🏗️ 三层架构 (Architecture)

### 1. 🧬 Zoe-Kernel (L0)
- **核心**：Sense → Think → Act → Verify 循环。
- **本能**：内置文件读写、目录探索、Bash 执行。
- **鲁棒性**：自愈重试、断点恢复。

### 2. 🗄️ Agentic File System (L1)
- **记忆化存储**：文件系统即 RAG 索引，Agent 读写时自动向量化。
- **权限管理**：基于 Agent 身份的动态 ACL。

### 3. 💬 Agent-Bus (L2)
- **IPC (Inter-Agent Communication)**：Agent 之间通过语义总线协作。
- **Task Orchestration**：复杂任务自动分解为多个 Zoe 子进程。

---

## 🗺️ 演进路线 (Roadmap)

### Phase 1: Nucleus (Current)
- [x] Zoe 单文件内核实现
- [x] 内置生存级工具 (CRUD + Bash)
- [x] UV 零配运行环境

### Phase 2: Shell
- [ ] **Zoe-Shell**: 一个 Agent 驱动的交互式命令行，你输入自然语言，它输出 Bash。
- [ ] **Persistent Memory**: 跨会话的语义上下文索引。

### Phase 3: Distributed
- [ ] **Agent-Mesh**: 跨机器的 Zoe 节点同步。
- [ ] **Marketplace**: 动态加载经过认证的 Skill。

---

## 🛠️ 核心哲学

- **Minimalist**: 绝不引入不必要的抽象。
- **Transparent**: 所有的思考过程（Thinking...）都是透明可见的。
- **Autonomous**: 系统具备极强的“抗干扰”和“自愈”能力。

---

*Powered by Zoe-Agent Engine | Architected by akayj & Xiao Xin*
