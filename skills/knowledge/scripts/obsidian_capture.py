#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["rich", "typer"]
# ///

"""
obsidian-capture.py - 快速捕获想法到 Obsidian Inbox

替代原来的 obsidian-capture.sh
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

# 配置
VAULT_DIR = Path.home() / "ObsidianVault"
INBOX_DIR = VAULT_DIR / "00-Inbox"

def sanitize_filename(text: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[^\w\s-]', '', text).strip()[:50]

def get_inbox_file() -> Path:
    """获取今天的 Inbox 文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    return INBOX_DIR / f"{today}.md"

def ensure_inbox():
    """确保 Inbox 目录存在"""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

def format_capture(content: str, tags: Optional[list] = None) -> str:
    """格式化捕获内容"""
    timestamp = datetime.now().strftime("%H:%M")
    tag_str = " " + " ".join([f"#{t}" for t in tags]) if tags else ""
    
    return f"""
## {timestamp}{tag_str}
{content}

"""

@app.command()
def capture(
    content: str = typer.Argument(..., help="要捕获的内容"),
    tags: Optional[str] = typer.Option(None, "-t", "--tags", help="标签，逗号分隔"),
):
    """快速捕获想法到 Obsidian Inbox"""
    ensure_inbox()
    
    inbox_file = get_inbox_file()
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    
    # 格式化内容
    capture_content = format_capture(content, tag_list)
    
    # 写入文件
    if inbox_file.exists():
        # 追加到现有文件
        with open(inbox_file, "a", encoding="utf-8") as f:
            f.write(capture_content)
    else:
        # 创建新文件
        header = f"# {datetime.now().strftime('%Y-%m-%d')} Inbox\n\n"
        with open(inbox_file, "w", encoding="utf-8") as f:
            f.write(header + capture_content)
    
    console.print(f"[green]✓[/green] 已捕获到 {inbox_file}")

@app.command()
def quick(content: str = typer.Argument(..., help="快速捕获（不显示输出）")):
    """静默捕获（用于脚本调用）"""
    ensure_inbox()
    inbox_file = get_inbox_file()
    capture_content = format_capture(content)
    
    if inbox_file.exists():
        with open(inbox_file, "a", encoding="utf-8") as f:
            f.write(capture_content)
    else:
        header = f"# {datetime.now().strftime('%Y-%m-%d')} Inbox\n\n"
        with open(inbox_file, "w", encoding="utf-8") as f:
            f.write(header + capture_content)

if __name__ == "__main__":
    app()
