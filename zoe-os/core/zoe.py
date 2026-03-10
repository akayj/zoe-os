#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///
import json, os, sys, subprocess
from pathlib import Path
import requests

def read_file(path: str) -> str:
    try: return Path(path).read_text(encoding="utf-8")
    except Exception as e: return f"Error: {e}"

def write_file(path: str, content: str) -> str:
    try:
        p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return "Success"
    except Exception as e: return f"Error: {e}"

def list_dir(path: str = ".") -> str:
    try: return "\n".join(os.listdir(path)) or "(empty)"
    except Exception as e: return f"Error: {e}"

def bash(command: str) -> str:
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    except Exception as e: return f"Error: {e}"

class Zoe:
    def __init__(self, name="zoe", instruction="Direct assistant."):
        self.name = name; self.instruction = instruction
        self.api_key = os.environ.get("ZOE_API_KEY", "")
        self.base_url = (os.environ.get("ZOE_BASE_URL", "https://api.moonshot.cn/v1")).rstrip("/")
        self.model = os.environ.get("ZOE_MODEL", "kimi-k2.5")
        self.tools = {
            "read_file": {"fn": read_file, "desc": "Read file"},
            "write_file": {"fn": write_file, "desc": "Write file"},
            "list_dir": {"fn": list_dir, "desc": "List files"},
            "bash": {"fn": bash, "desc": "Run command"}
        }

    def run(self, task: str):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = [{"role": "system", "content": self.instruction}, {"role": "user", "content": task}]
        tools_spec = [{"type": "function", "function": {"name": k, "description": v["desc"], "parameters": {"type": "object", "properties": {}}}} for k, v in self.tools.items()]
        
        try:
            r = requests.post(f"{self.base_url}/chat/completions", headers=headers, 
                             json={"model": self.model, "messages": messages, "tools": tools_spec}, timeout=60)
            data = r.json()
            if "choices" not in data: return f"LLM Error: {data.get('error', 'Unknown')}"
            
            msg = data["choices"][0]["message"]
            if not msg.get("tool_calls"): return msg.get("content", "")
            # Simplified for speed in zoe-ls usecase
            return f"Tools needed: {msg['tool_calls'][0]['function']['name']}"
        except Exception as e:
            return f"Runtime Error: {e}"

def main():
    """CLI entry point for zoe command."""
    if len(sys.argv) > 2 and sys.argv[1] == "run":
        print(Zoe().run(sys.argv[2]))
    elif len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        print("Usage: zoe run <task>")
        print("")
        print("A minimalist AI Agent. One file, no framework.")
        print("")
        print("Commands:")
        print("  run <task>    Execute a task")
        print("")
        print("Environment variables:")
        print("  ZOE_API_KEY       API key for LLM (required)")
        print("  ZOE_BASE_URL      Base URL for API (default: https://api.moonshot.cn/v1)")
        print("  ZOE_MODEL         Model name (default: kimi-k2.5)")
    else:
        print("Usage: zoe run <task>")
        print("Run 'zoe --help' for more information.")

if __name__ == "__main__":
    main()
