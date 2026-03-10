# Zoe-Agent

> One file. No framework. Self-healing.

极简 AI Agent **内核**。不是操作系统，不是框架，就是 Agent 本身。

## 定位

Zoe 是 Agent 的**最小可行实现**：
- 一个类 `Zoe` = 完整 Agent 引擎
- 一个装饰器 `@tool` = 工具注册
- 一个命令 `zoe run` = CLI 入口

仅此而已。没有调度器、没有插件系统、没有复杂抽象。

## 设计来源

| 灵感 | 取了什么 | 没取什么 |
|------|----------|----------|
| SimpleCLI | 单文件、零框架、5 分钟可读 | Node.js 依赖 |
| Pi-Agent | Sense→Think→Act→Verify | 复杂的状态机 |

## 架构

```
  SENSE   →  读环境、读状态
    ↓
  THINK   →  LLM 决定下一步
    ↓
   ACT    →  执行工具（如果有）
    ↓
  VERIFY  →  检查成功？→ Done
    │
    └── 失败 → 指数退避 → 重试
```

## 安装与运行 (UV 驱动)

Zoe 深度适配 [uv](https://github.com/astral-sh/uv)，支持极速安装与零配置运行。

### 1. 零安装运行 (推荐)
无需预先安装，直接执行：
```bash
uv run zoe run "检查系统状态"
```

### 2. 全局工具安装
如果你想在任何路径直接使用 `zoe` 命令：
```bash
uv tool install .
# 现在可以直接执行:
zoe run "任务"
```

### 3. 开发模式
```bash
uv venv && source .venv/bin/activate
uv pip install -e .
```

## 使用

### CLI

```bash
zoe run "检查系统状态"
zoe status
zoe resume
```

### 库

```python
from zoe_agent import Zoe, Tool

@Tool("ping", "Ping a host")
def ping(host: str) -> str:
    import subprocess
    r = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True)
    return r.stdout

agent = Zoe(name="checker", tools=[ping])
result = agent.run("8.8.8.8 通吗？")
```

## 约束

- 只依赖 `requests`
- 核心代码 < 300 行
- 任何 OpenAI 兼容 API
- 不承诺向后兼容（0.x 阶段）

## 不是这些

- ❌ 不是操作系统（没有进程管理）
- ❌ 不是框架（没有插件、没有钩子）
- ❌ 不是平台（没有服务发现、没有集群）

就是 Agent。用完即走。
