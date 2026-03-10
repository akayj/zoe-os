---
name: zoe-agent
description: Zoe-Agent — Minimalist AI Agent framework. Single-file, no framework, self-healing loop. Use as library to build Pi-style agents, or as CLI for one-shot tasks.
metadata: {"openclaw":{"requires":{"bins":["uv"]},"emoji":"🤖"}}
---

# Zoe-Agent: Minimalist AI Agent Framework

> One file. No framework. Self-healing.

Zoe is a **single-file AI agent framework** inspired by [SimpleCLI](https://github.com/Zen-Open-Source/SimpleCLI)'s radical minimalism and the Pi-Agent sense-think-act-verify loop.

## Design Principles

| Principle | SimpleCLI DNA | Pi-Agent DNA |
|-----------|---------------|--------------|
| **One File** | ✅ Entire app = `index.js` | ✅ Entire agent = `zoe.py` |
| **No Framework** | ✅ Just `@anthropic-ai/sdk` | ✅ Just `requests` |
| **Stateful Memory** | ✅ History array | ✅ Checkpoint JSON |
| **Streaming** | ✅ Token-by-token | 🔄 Future: SSE support |
| **Self-Healing** | ❌ N/A | ✅ Retry + backoff + resume |
| **Offline Brain** | ❌ N/A | ✅ Works without Gateway |

## Architecture

```
        ┌──────────┐
        │  SENSE   │ ← Gather context, read state
        └────┬─────┘
             ↓
        ┌──────────┐
        │  THINK   │ ← LLM decides next action
        └────┬─────┘
             ↓
        ┌──────────┐
        │   ACT    │ ← Execute tool / command
        └────┬─────┘
             ↓
        ┌──────────┐
   ┌──→ │ VERIFY   │ ← Check result, retry if failed
   │    └────┬─────┘
   │         ↓
   │    Success? ──→ Done ✅
   │         │
   └── No ───┘ (retry with backoff)
```

## Usage as Library (Recommended)

Build your own Pi-style agent in 10 lines:

```python
from zoe import Zoe, Tool

def check_version() -> str:
    import subprocess
    return subprocess.run(["openclaw", "--version"], capture_output=True, text=True).stdout

agent = Zoe(
    name="upgrader",
    instruction="You check OpenClaw versions and recommend upgrades.",
    tools=[Tool("check_version", "Get current OpenClaw version", check_version)],
    api_key="your-key",
)

result = agent.run("Is my OpenClaw up to date?")
print(result)
```

## Usage as CLI

```bash
# Run a one-shot task
ZOE_API_KEY=sk-xxx ./src/zoe.py run "What is 2+2?"

# Check agent state
./src/zoe.py status

# Resume from crash
./src/zoe.py resume
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ZOE_API_KEY` | (required) | LLM API key |
| `ZOE_BASE_URL` | `https://api.moonshot.cn/v1` | API endpoint |
| `ZOE_MODEL` | `kimi-k2.5` | Model to use |

## File Structure

```
skills/zoe-agent/
├── SKILL.md          ← You are here
├── manifest.json     ← AgentSkills spec metadata
└── src/
    └── zoe.py        ← THE ENTIRE FRAMEWORK (one file)
```

## Why Zoe?

- **Not another framework** — no abstractions to learn, no magic, no DSL
- **Read it in 5 minutes** — ~200 lines of actual logic
- **Crash-safe** — checkpoint state auto-saves, resume anytime
- **LLM-agnostic** — any OpenAI-compatible API (Kimi, OpenAI, Claude via proxy)
- **Pi-native** — born for OpenClaw's Pi-Agent pattern

## Rebuilding Skills with Zoe

To convert any existing skill to Zoe-Agent pattern:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///
import sys; sys.path.insert(0, "/root/.openclaw/workspace/skills/zoe-agent/src")
from zoe import Zoe, Tool

# Define your tools
def my_custom_tool(param: str) -> str:
    # your logic here
    return "result"

agent = Zoe(
    name="my-skill",
    instruction="Your skill-specific instructions here.",
    tools=[Tool("my_tool", "Description", my_custom_tool)],
)

if __name__ == "__main__":
    agent.run(sys.argv[1] if len(sys.argv) > 1 else "default task")
```

*Built with ❤️ by 小新 & 余剑剑 — Powered by the Pi-Agent philosophy*
