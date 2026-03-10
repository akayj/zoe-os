#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["rich", "requests"]
# ///
"""
zoe-ls: The Semantic List tool for Zoe-OS.
Analyzes directory contents and provides "intelligence-aware" summaries.
"""
import os, sys, json
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def get_file_intelligence(path):
    """
    Simulates calling Zoe Kernel to analyze a file.
    In a real OS, this would query the local .seed database.
    """
    stats = os.stat(path)
    size = f"{stats.st_size / 1024:.1f}KB"
    
    # 语义模拟逻辑
    name = os.path.basename(path)
    if name.endswith(".py"): 
        intel = "[cyan]Active Logic[/cyan]"
        tag = "Core"
    elif name.endswith(".md"): 
        intel = "[green]Knowledge Base[/green]"
        tag = "Memory"
    elif name.endswith(".seed"): 
        intel = "[magenta]Experience Slice[/magenta]"
        tag = "PBM"
    else: 
        intel = "Static Data"
        tag = "Entropy"
        
    return size, intel, tag

def list_semantic_dir(path="."):
    table = Table(title=f"📂 Zoe-OS Semantic FS: {os.path.abspath(path)}", header_style="bold blue")
    table.add_column("Name", style="bold")
    table.add_column("Size", justify="right")
    table.add_column("Nature")
    table.add_column("Tag", style="dim")

    for item in sorted(os.listdir(path)):
        if item.startswith("."): continue
        size, nature, tag = get_file_intelligence(os.path.join(path, item))
        table.add_row(item, size, nature, tag)

    console.print(table)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    list_semantic_dir(target)
