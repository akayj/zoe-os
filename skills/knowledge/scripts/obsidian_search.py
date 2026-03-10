#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["rich", "typer"]
# ///

"""
obsidian-search.py - 搜索 Obsidian 知识库

替代原来的 obsidian-search.sh
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer()
console = Console()

# 配置
VAULT_DIR = Path.home() / "ObsidianVault"

def search_files(query: str, max_results: int = 20) -> List[dict]:
    """搜索文件内容"""
    results = []
    query_lower = query.lower()
    
    # 搜索所有 markdown 文件
    for md_file in VAULT_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            content_lower = content.lower()
            
            if query_lower in content_lower:
                # 找到匹配，提取上下文
                lines = content.split("\n")
                matches = []
                
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # 提取前后 2 行作为上下文
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = "\n".join(lines[start:end])
                        matches.append(context)
                
                if matches:
                    results.append({
                        "file": md_file.relative_to(VAULT_DIR),
                        "matches": matches[:3],  # 最多 3 处匹配
                        "size": len(content)
                    })
                    
                    if len(results) >= max_results:
                        break
                        
        except Exception as e:
            continue
    
    return results

@app.command()
def search(
    query: str = typer.Argument(..., help="搜索关键词"),
    max_results: int = typer.Option(10, "-n", "--max", help="最大结果数"),
    context: bool = typer.Option(True, "--context/--no-context", help="显示上下文"),
):
    """搜索 Obsidian 知识库"""
    
    if not VAULT_DIR.exists():
        console.print(f"[red]✗ 知识库不存在：{VAULT_DIR}[/red]")
        return
    
    console.print(f"[bold]搜索：[/bold]{query}\n")
    
    results = search_files(query, max_results)
    
    if not results:
        console.print("[yellow]未找到匹配结果[/yellow]")
        return
    
    console.print(f"找到 [green]{len(results)}[/green] 个文件\n")
    
    for i, result in enumerate(results, 1):
        console.print(Panel(
            f"[bold cyan]{result['file']}[/bold cyan] ({result['size']} bytes)\n\n" +
            ("\n---\n".join(result['matches']) if context else ""),
            title=f"结果 {i}",
            border_style="blue"
        ))

@app.command()
def recent(
    days: int = typer.Option(7, "-d", "--days", help="最近 N 天"),
):
    """显示最近修改的文件"""
    
    if not VAULT_DIR.exists():
        console.print(f"[red]✗ 知识库不存在：{VAULT_DIR}[/red]")
        return
    
    # 获取所有 markdown 文件并按修改时间排序
    files = []
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for md_file in VAULT_DIR.rglob("*.md"):
        try:
            mtime = md_file.stat().st_mtime
            if mtime > cutoff:
                files.append({
                    "file": md_file.relative_to(VAULT_DIR),
                    "mtime": mtime,
                    "size": md_file.stat().st_size
                })
        except:
            continue
    
    # 按时间排序
    files.sort(key=lambda x: x["mtime"], reverse=True)
    
    table = Table(title=f"📄 最近 {days} 天修改的文件")
    table.add_column("文件", style="cyan")
    table.add_column("修改时间", style="green")
    table.add_column("大小", style="magenta")
    
    for f in files[:20]:  # 最多显示 20 个
        mtime_str = datetime.fromtimestamp(f["mtime"]).strftime("%m-%d %H:%M")
        table.add_row(str(f["file"]), mtime_str, f"{f['size']} bytes")
    
    console.print(table)

@app.command()
def stats():
    """知识库统计"""
    
    if not VAULT_DIR.exists():
        console.print(f"[red]✗ 知识库不存在：{VAULT_DIR}[/red]")
        return
    
    # 统计
    md_files = list(VAULT_DIR.rglob("*.md"))
    total_size = sum(f.stat().st_size for f in md_files)
    
    # 按目录统计
    dir_stats = {}
    for f in md_files:
        dir_name = str(f.parent.relative_to(VAULT_DIR))
        if dir_name not in dir_stats:
            dir_stats[dir_name] = {"count": 0, "size": 0}
        dir_stats[dir_name]["count"] += 1
        dir_stats[dir_name]["size"] += f.stat().st_size
    
    console.print(Panel(
        f"[bold]📊 知识库统计[/bold]\n\n"
        f"总文件数：{len(md_files)}\n"
        f"总大小：{total_size / 1024:.1f} KB\n"
        f"平均大小：{total_size / len(md_files) / 1024:.1f} KB" if md_files else "N/A",
        title="统计"
    ))
    
    # 目录统计
    table = Table(title="按目录统计")
    table.add_column("目录", style="cyan")
    table.add_column("文件数", style="green")
    table.add_column("大小", style="magenta")
    
    for dir_name, stats in sorted(dir_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
        table.add_row(dir_name, str(stats["count"]), f"{stats['size'] / 1024:.1f} KB")
    
    console.print(table)

if __name__ == "__main__":
    app()
