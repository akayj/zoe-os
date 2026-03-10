#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///
"""
Zoe Core - 认知引擎

核心功能:
- Sense: 接收感官输入
- Think: LLM 推理决策
- Act: 执行工具调用
- Verify: 验证执行结果
"""
import json, os, sys, subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import requests

# ============ 工具定义 ============

def read_file(path: str) -> str:
    """读取文件内容"""
    try: 
        return Path(path).read_text(encoding="utf-8")
    except Exception as e: 
        return f"Error: {e}"

def write_file(path: str, content: str) -> str:
    """写入文件内容"""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return "Success"
    except Exception as e: 
        return f"Error: {e}"

def list_dir(path: str = ".") -> str:
    """列出目录内容"""
    try: 
        return "\n".join(os.listdir(path)) or "(empty)"
    except Exception as e: 
        return f"Error: {e}"

def bash(command: str) -> str:
    """执行 Bash 命令"""
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        result = f"STDOUT:\n{r.stdout}"
        if r.stderr:
            result += f"\nSTDERR:\n{r.stderr}"
        return result
    except subprocess.TimeoutExpired:
        return "Error: Command timeout (30s)"
    except Exception as e: 
        return f"Error: {e}"

# 工具规范定义 (OpenAI Function Calling 格式)
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定路径的文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "将内容写入指定路径的文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "列出目录中的文件和子目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径，默认为当前目录"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "执行 Bash 命令",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"}
                },
                "required": ["command"]
            }
        }
    }
]

# 工具函数映射
TOOLS_FN = {
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir,
    "bash": bash
}

# ============ Zoe 核心类 ============

@dataclass
class Zoe:
    """Zoe 认知引擎"""
    name: str = "zoe"
    instruction: str = "Direct assistant."
    
    # LLM 配置
    api_key: str = field(default_factory=lambda: os.environ.get("ZOE_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.environ.get("ZOE_BASE_URL", "https://api.moonshot.cn/v1").rstrip("/"))
    model: str = field(default_factory=lambda: os.environ.get("ZOE_MODEL", "kimi-k2.5"))
    
    # 对话历史
    messages: List[Dict[str, Any]] = field(default_factory=list)
    
    # 配置
    max_iterations: int = 10  # 最大工具调用迭代次数
    max_retries: int = 3      # API 调用重试次数
    
    def __post_init__(self):
        # 初始化系统消息
        if not self.messages:
            self.messages = [{"role": "system", "content": self.instruction}]
    
    def _call_llm(self) -> Optional[Dict[str, Any]]:
        """调用 LLM API，带重试机制"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": self.messages,
                        "tools": TOOLS_SPEC,
                        "tool_choice": "auto"
                    },
                    timeout=60
                )
                data = response.json()
                
                if "error" in data:
                    print(f"[Zoe] LLM Error: {data['error']}", file=sys.stderr)
                    return None
                
                return data
                
            except requests.Timeout:
                print(f"[Zoe] API timeout, retry {attempt + 1}/{self.max_retries}", file=sys.stderr)
            except Exception as e:
                print(f"[Zoe] API error: {e}", file=sys.stderr)
        
        return None
    
    def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """执行工具调用"""
        if name not in TOOLS_FN:
            return f"Error: Unknown tool '{name}'"
        
        try:
            result = TOOLS_FN[name](**arguments)
            return result
        except Exception as e:
            return f"Error: {e}"
    
    def run(self, task: str, verbose: bool = False) -> str:
        """
        执行任务 - 完整的 Sense→Think→Act→Verify 循环
        
        Args:
            task: 用户任务描述
            verbose: 是否输出详细日志
        
        Returns:
            最终响应内容
        """
        # Sense: 接收用户输入
        self.messages.append({"role": "user", "content": task})
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            if verbose:
                print(f"[Zoe] Iteration {iteration}")
            
            # Think: LLM 推理
            data = self._call_llm()
            if not data or "choices" not in data:
                return "Error: LLM call failed"
            
            msg = data["choices"][0]["message"]
            self.messages.append(msg)
            
            # 检查是否需要工具调用
            tool_calls = msg.get("tool_calls")
            if not tool_calls:
                # 无工具调用，返回最终结果
                return msg.get("content", "")
            
            # Act: 执行工具调用
            for tool_call in tool_calls:
                fn_name = tool_call["function"]["name"]
                fn_args = json.loads(tool_call["function"]["arguments"])
                
                if verbose:
                    print(f"[Zoe] Calling {fn_name}({fn_args})")
                
                result = self._execute_tool(fn_name, fn_args)
                
                if verbose:
                    print(f"[Zoe] Result: {result[:100]}..." if len(result) > 100 else f"[Zoe] Result: {result}")
                
                # 添加工具结果到消息历史
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result
                })
        
        # 超过最大迭代次数
        return "Error: Max iterations reached without completion"
    
    def reset(self):
        """重置对话历史"""
        self.messages = [{"role": "system", "content": self.instruction}]
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.messages.copy()

# ============ CLI 入口 ============

def main():
    """CLI 入口点"""
    if len(sys.argv) > 2 and sys.argv[1] == "run":
        task = " ".join(sys.argv[2:])
        zoe = Zoe()
        result = zoe.run(task, verbose=True)
        print(result)
        
    elif len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        print("""Usage: zoe run <task>

A minimalist AI Agent. One file, no framework.

Commands:
  run <task>    Execute a task

Environment variables:
  ZOE_API_KEY       API key for LLM (required)
  ZOE_BASE_URL      Base URL for API (default: https://api.moonshot.cn/v1)
  ZOE_MODEL         Model name (default: kimi-k2.5)

Features:
  - Full tool-calling loop with iterative execution
  - Conversation history management
  - Automatic retry on API failures
  - Maximum iteration limit to prevent infinite loops
""")
    else:
        print("Usage: zoe run <task>")
        print("Run 'zoe --help' for more information.")

if __name__ == "__main__":
    main()

