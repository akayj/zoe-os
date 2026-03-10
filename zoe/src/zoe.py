#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""
Zoe-Agent: Minimalist, Self-Healing AI Agent Framework.
One file. No framework. Built-in survival tools (read, write, list, bash).
"""
import json, os, sys, time, subprocess, base64
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Optional
import requests

# ─── 1. SURVIVAL TOOLS (Built-in) ───────────────────────────────────────────

def read_file(path: str) -> str:
    """Read content from a file."""
    try: return Path(path).read_text(encoding="utf-8")
    except Exception as e: return f"Error: {e}"

def write_file(path: str, content: str) -> str:
    """Write content to a file (overwrites)."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e: return f"Error: {e}"

def list_dir(path: str = ".") -> str:
    """List files in a directory."""
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "(empty)"
    except Exception as e: return f"Error: {e}"

def bash(command: str) -> str:
    """Execute a shell command (be careful!)."""
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    except Exception as e: return f"Error: {e}"

# ─── 2. CORE CLASSES ────────────────────────────────────────────────────────

@dataclass
class Tool:
    name: str
    description: str
    fn: Callable
    parameters: dict = field(default_factory=lambda: {"type": "object", "properties": {}})

    def to_spec(self) -> dict:
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": self.parameters}}

@dataclass
class ZoeState:
    phase: str = "idle"; task: str = ""; retries: int = 0; last_error: str = ""; result: str = ""
    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False))
    @classmethod
    def load(cls, path: Path):
        if path.exists(): return cls(**json.load(path.open()))
        return cls()

class Zoe:
    def __init__(self, name="zoe", instruction="Helpful assistant.", tools=None, api_key=None, base_url=None, model=None, verbose=True):
        self.name = name; self.instruction = instruction; self.verbose = verbose
        self.api_key = api_key or os.environ.get("ZOE_API_KEY", "")
        self.base_url = (base_url or os.environ.get("ZOE_BASE_URL", "https://api.moonshot.cn/v1")).rstrip("/")
        self.model = model or os.environ.get("ZOE_MODEL", "kimi-k2.5")
        self.state_path = Path(f"/tmp/zoe-{name}/state.json")
        self.state = ZoeState.load(self.state_path)
        
        # Built-in survival tools
        self.tools = {
            "read_file": Tool("read_file", "Read a file's content", read_file, {"type": "object", "properties": {"path": {"type": "string"}}}),
            "write_file": Tool("write_file", "Write content to a file", write_file, {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}),
            "list_dir": Tool("list_dir", "List files in a directory", list_dir, {"type": "object", "properties": {"path": {"type": "string", "default": "."}}}),
            "bash": Tool("bash", "Execute shell command", bash, {"type": "object", "properties": {"command": {"type": "string"}}})
        }
        if tools: self.tools.update({t.name: t for t in tools})

    def _log(self, m): 
        if self.verbose: print(f"🤖 [Zoe] {m}", file=sys.stderr)

    def _chat(self, messages):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "messages": messages, "tools": [t.to_spec() for t in self.tools.values()]}
        for i in range(3):
            try:
                r = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60)
                r.raise_for_status(); return r.json()
            except Exception as e:
                time.sleep(2**(i+1)); self._log(f"Retry {i+1} due to {e}")
        raise Exception("LLM call failed after retries")

    def run(self, task: str):
        self.state = ZoeState(task=task, phase="running"); self.state.save(self.state_path)
        messages = [{"role": "system", "content": f"{self.instruction}\nBuilt-in tools: read_file, write_file, list_dir, bash. Sense → Think → Act → Verify."}, {"role": "user", "content": task}]
        
        for turn in range(10):
            self._log(f"Turn {turn+1} Thinking..."); res = self._chat(messages)
            msg = res["choices"][0]["message"]; messages.append(msg)
            
            if not msg.get("tool_calls"):
                self.state.result = msg.get("content", ""); self.state.phase = "done"; self.state.save(self.state_path)
                return self.state.result
            
            self.state.phase = "acting"; self.state.save(self.state_path)
            for tc in msg["tool_calls"]:
                fn, args = tc["function"]["name"], json.loads(tc["function"].get("arguments", "{}"))
                self._log(f"Executing {fn}({args})"); out = self.tools[fn].fn(**args)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": out})
        return "Timeout"

# ─── 3. CLI ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2: 
        print("zoe run 'task' | status | version"); return
    cmd = sys.argv[1]
    if cmd == "run": print(Zoe().run(" ".join(sys.argv[2:])))
    elif cmd == "version": print("zoe-agent 0.1.3 (built-in survival tools)")

if __name__ == "__main__": main()
