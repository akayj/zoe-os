#!/usr/bin/env -S uv run --script
"""
Zoe-Agent Core — the entire framework in one file.

Inspired by:
  - SimpleCLI (one file, no framework)
  - Pi-Agent (sense → think → act → verify)
"""

import json, os, sys, time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Optional

import requests

# ─── CONFIG ───────────────────────────────────────────────────────────────────

MAX_RETRIES = 3
BACKOFF_BASE = 2


# ─── TOOL ─────────────────────────────────────────────────────────────────────

@dataclass
class Tool:
    """A tool the agent can call. Name, description, function."""
    name: str
    description: str
    fn: Callable
    parameters: dict = field(default_factory=lambda: {
        "type": "object", "properties": {}, "required": []
    })

    def to_spec(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# ─── STATE ────────────────────────────────────────────────────────────────────

@dataclass
class ZoeState:
    """Crash-safe checkpoint. Survives restarts."""
    phase: str = "idle"
    task: str = ""
    retries: int = 0
    last_error: str = ""
    result: str = ""
    created_at: float = field(default_factory=time.time)
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
        return cls()


# ─── ZOE ──────────────────────────────────────────────────────────────────────

class Zoe:
    """
    The entire agent.

    Sense  → gather context
    Think  → ask LLM what to do
    Act    → execute tool
    Verify → check result, retry if failed
    """

    def __init__(
        self,
        name: str = "zoe",
        instruction: str = "You are a helpful assistant.",
        tools: list[Tool] | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        state_dir: str | None = None,
        max_retries: int = MAX_RETRIES,
        max_turns: int = 10,
        verbose: bool = False,
    ):
        self.name = name
        self.instruction = instruction
        self.tools = {t.name: t for t in (tools or [])}
        self.model = model or os.environ.get("ZOE_MODEL", "kimi-k2.5")
        self.base_url = (base_url or os.environ.get("ZOE_BASE_URL", "https://api.moonshot.cn/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("ZOE_API_KEY", "")
        self.max_retries = max_retries
        self.max_turns = max_turns
        self.verbose = verbose

        state_root = state_dir or os.environ.get("ZOE_STATE_DIR", f"/tmp/zoe-{name}")
        self.state_path = Path(state_root) / "state.json"
        self.state = ZoeState.load(self.state_path)

    def _log(self, msg: str):
        if self.verbose:
            print(msg, file=sys.stderr)

    # ── LLM ──

    def _chat(self, messages: list) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if self.tools:
            payload["tools"] = [t.to_spec() for t in self.tools.values()]

        for attempt in range(self.max_retries):
            try:
                r = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers, json=payload, timeout=60,
                )
                if r.status_code == 429:
                    wait = BACKOFF_BASE ** (attempt + 1)
                    self._log(f"⏳ Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait = BACKOFF_BASE ** (attempt + 1)
                    self._log(f"⚠️ {e}, retry in {wait}s")
                    time.sleep(wait)
                else:
                    raise
        return {}

    # ── CORE LOOP ──

    def run(self, task: str) -> str:
        """Sense → Think → Act → Verify loop."""
        self.state = ZoeState(task=task, phase="sensing")
        self.state.save(self.state_path)

        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": task},
        ]

        for turn in range(self.max_turns):
            self._log(f"🔄 [{turn+1}/{self.max_turns}]")

            self.state.phase = "thinking"
            self.state.save(self.state_path)

            try:
                response = self._chat(messages)
            except Exception as e:
                self.state.last_error = str(e)
                self.state.phase = "error"
                self.state.save(self.state_path)
                return f"Error: {e}"

            choice = response.get("choices", [{}])[0]
            msg = choice.get("message", {})
            finish = choice.get("finish_reason", "")

            messages.append(msg)

            # No tool call → done
            if finish != "tool_calls" or not msg.get("tool_calls"):
                self.state.phase = "done"
                self.state.result = msg.get("content", "")
                self.state.save(self.state_path)
                return self.state.result

            # Execute tools
            self.state.phase = "acting"
            self.state.save(self.state_path)

            for tc in msg["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = tc["function"].get("arguments", "{}")
                self._log(f"⚡ {fn_name}({fn_args})")

                tool = self.tools.get(fn_name)
                if not tool:
                    result = f"Unknown tool: {fn_name}"
                else:
                    try:
                        args = json.loads(fn_args) if fn_args else {}
                        result = str(tool.fn(**args))
                    except Exception as e:
                        result = f"Error: {e}"
                        self.state.retries += 1

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

            if self.state.retries >= self.max_retries:
                self.state.phase = "failed"
                self.state.save(self.state_path)
                return f"Failed after {self.max_retries} retries"

        self.state.phase = "timeout"
        self.state.save(self.state_path)
        return "Max turns reached"

    def _system_prompt(self) -> str:
        parts = [self.instruction, "", "You are a Zoe-Agent. Be direct. No fluff."]
        if self.tools:
            parts.append("")
            parts.append("Available tools:")
            for t in self.tools.values():
                parts.append(f"  - {t.name}: {t.description}")
        return "\n".join(parts)

    def status(self) -> dict:
        return asdict(self.state)
