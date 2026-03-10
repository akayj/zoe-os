#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""
Zoe-Agent: Minimalist AI Agent Framework for OpenClaw Skills

Inspired by:
  - SimpleCLI (one file, no framework, streams as it arrives)
  - Pi-Agent (sense → think → act → verify self-healing loop)

Design principles:
  1. ONE FILE — entire agent lives in a single Python script
  2. NO FRAMEWORK — no langchain, no crewai, just requests + stdlib
  3. SELF-HEALING — built-in retry with exponential backoff
  4. CHECKPOINT — state survives crashes, resume from where you left off
  5. OFFLINE-BRAIN — works without OpenClaw Gateway when needed

Usage as library:
    from zoe import Zoe, Tool
    
    def check_weather(city: str) -> str:
        return requests.get(f"https://wttr.in/{city}?format=3").text
    
    agent = Zoe(
        name="weather-bot",
        instruction="You check weather for cities.",
        tools=[Tool("check_weather", "Get weather for a city", check_weather)],
    )
    result = agent.run("What's the weather in Shanghai?")

Usage as CLI:
    ./zoe.py run "Check if openclaw has a new release"
    ./zoe.py status
    ./zoe.py resume
"""

import json, os, sys, time, hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Optional

import requests

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────

DEFAULT_MODEL = os.environ.get("ZOE_MODEL", "kimi-k2.5")
DEFAULT_BASE_URL = os.environ.get("ZOE_BASE_URL", "https://api.moonshot.cn/v1")
DEFAULT_API_KEY = os.environ.get("ZOE_API_KEY", "")

MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds


# ─── 2. TOOL DEFINITION ──────────────────────────────────────────────────────

@dataclass
class Tool:
    """A single tool the agent can call. Just a name, description, and function."""
    name: str
    description: str
    fn: Callable
    parameters: dict = field(default_factory=lambda: {"type": "object", "properties": {}})

    def to_openai_spec(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# ─── 3. CHECKPOINT STATE ─────────────────────────────────────────────────────

@dataclass
class ZoeState:
    """Crash-safe state. Survives process restarts."""
    phase: str = "idle"          # idle → sensing → thinking → acting → verifying → done
    task: str = ""
    history: list = field(default_factory=list)
    retries: int = 0
    last_error: str = ""
    result: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0

    def save(self, path: Path):
        self.updated_at = time.time()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: Path) -> "ZoeState":
        if path.exists():
            data = json.loads(path.read_text())
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls(created_at=time.time())


# ─── 4. ZOE CORE ─────────────────────────────────────────────────────────────

class Zoe:
    """
    The entire agent in one class.
    
    Sense  → gather context (read files, check APIs)
    Think  → ask LLM what to do next
    Act    → execute the chosen tool
    Verify → confirm the action succeeded, retry if not
    """

    def __init__(
        self,
        name: str = "zoe",
        instruction: str = "You are a helpful assistant.",
        tools: list[Tool] | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = DEFAULT_API_KEY,
        state_dir: str | None = None,
    ):
        self.name = name
        self.instruction = instruction
        self.tools = {t.name: t for t in (tools or [])}
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.state_path = Path(state_dir or f"/tmp/zoe-{name}") / "state.json"
        self.state = ZoeState.load(self.state_path)

    # ── LLM call (raw requests, no SDK) ──

    def _chat(self, messages: list, use_tools: bool = True) -> dict:
        """Single LLM API call with retry + backoff. No SDK dependency."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if use_tools and self.tools:
            payload["tools"] = [t.to_openai_spec() for t in self.tools.values()]

        for attempt in range(MAX_RETRIES):
            try:
                r = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                if r.status_code == 429:
                    wait = BACKOFF_BASE ** (attempt + 1)
                    print(f"⏳ Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE ** (attempt + 1)
                    print(f"⚠️ Error: {e}, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        return {}

    # ── Sense-Think-Act-Verify loop ──

    def run(self, task: str, max_turns: int = 10) -> str:
        """
        Main agent loop. Runs until the task is complete or max_turns reached.
        
        The loop:
          1. SENSE  — build context (system prompt + history + task)
          2. THINK  — ask LLM for next action
          3. ACT    — if LLM chose a tool, execute it
          4. VERIFY — check result, decide if done or retry
        """
        self.state.task = task
        self.state.phase = "sensing"
        self.state.history = []
        self.state.retries = 0
        self.state.save(self.state_path)

        # Build initial messages
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": task},
        ]

        for turn in range(max_turns):
            # ── SENSE ──
            self.state.phase = "sensing"
            self.state.save(self.state_path)
            print(f"🔍 [{turn+1}/{max_turns}] Sensing...")

            # ── THINK ──
            self.state.phase = "thinking"
            self.state.save(self.state_path)
            print(f"🧠 [{turn+1}/{max_turns}] Thinking...")

            try:
                response = self._chat(messages)
            except Exception as e:
                self.state.last_error = str(e)
                self.state.phase = "error"
                self.state.save(self.state_path)
                print(f"❌ LLM call failed: {e}")
                return f"Error: {e}"

            choice = response.get("choices", [{}])[0]
            msg = choice.get("message", {})
            finish_reason = choice.get("finish_reason", "")

            # Save assistant message to history
            messages.append(msg)

            # ── If no tool call, we're done ──
            if finish_reason != "tool_calls" or not msg.get("tool_calls"):
                self.state.phase = "done"
                self.state.result = msg.get("content", "")
                self.state.save(self.state_path)
                print(f"✅ Done.")
                return self.state.result

            # ── ACT ──
            self.state.phase = "acting"
            self.state.save(self.state_path)

            for tool_call in msg["tool_calls"]:
                fn_name = tool_call["function"]["name"]
                fn_args_raw = tool_call["function"].get("arguments", "{}")

                print(f"⚡ [{turn+1}/{max_turns}] Acting: {fn_name}({fn_args_raw})")

                # Execute tool
                tool = self.tools.get(fn_name)
                if not tool:
                    result = f"Error: unknown tool '{fn_name}'"
                else:
                    try:
                        args = json.loads(fn_args_raw) if fn_args_raw else {}
                        result = str(tool.fn(**args))
                    except Exception as e:
                        result = f"Error: {e}"
                        self.state.retries += 1
                        print(f"🔧 Tool error, will retry ({self.state.retries}/{MAX_RETRIES})")

                # ── VERIFY ──
                self.state.phase = "verifying"
                self.state.save(self.state_path)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result,
                })

            # Check if we should give up
            if self.state.retries >= MAX_RETRIES:
                self.state.phase = "failed"
                self.state.save(self.state_path)
                print(f"💀 Max retries reached.")
                return f"Failed after {MAX_RETRIES} retries. Last error: {self.state.last_error}"

        self.state.phase = "timeout"
        self.state.save(self.state_path)
        return "Reached max turns without completion."

    def _build_system_prompt(self) -> str:
        tools_desc = ""
        if self.tools:
            tool_lines = [f"  - {t.name}: {t.description}" for t in self.tools.values()]
            tools_desc = "\n\nAvailable tools:\n" + "\n".join(tool_lines)

        return f"""{self.instruction}

You are a Zoe-Agent — a minimalist, self-healing AI agent.
Your approach: Sense → Think → Act → Verify.
- Be direct. No fluff.
- If a tool fails, analyze the error and try a different approach.
- If you have enough information to answer, respond directly without using tools.{tools_desc}"""

    def status(self) -> dict:
        return asdict(self.state)


# ─── 5. CLI ENTRYPOINT ───────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("""
🤖 Zoe-Agent — Minimalist AI Agent Framework

Usage:
  zoe run   "your task here"     Run a task
  zoe status                     Show current state
  zoe resume                     Resume from last checkpoint

Environment:
  ZOE_API_KEY      API key (required)
  ZOE_BASE_URL     API base URL (default: moonshot)
  ZOE_MODEL        Model name (default: kimi-k2.5)

Examples:
  ZOE_API_KEY=sk-xxx ./zoe.py run "Check latest OpenClaw version"
  ./zoe.py status
""")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        state = ZoeState.load(Path("/tmp/zoe-default/state.json"))
        print(json.dumps(asdict(state), indent=2, ensure_ascii=False))

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: zoe run 'your task'")
            sys.exit(1)
        task = " ".join(sys.argv[2:])

        # Demo: create a basic agent with no custom tools
        agent = Zoe(name="default", instruction="You are a helpful CLI assistant.")
        result = agent.run(task)
        print(f"\n📋 Result:\n{result}")

    elif cmd == "resume":
        state = ZoeState.load(Path("/tmp/zoe-default/state.json"))
        if state.phase in ("idle", "done"):
            print("Nothing to resume.")
        else:
            agent = Zoe(name="default", instruction="You are a helpful CLI assistant.")
            agent.state = state
            result = agent.run(state.task)
            print(f"\n📋 Result:\n{result}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
