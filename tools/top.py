#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["psutil", "rich"]
# ///
"""
Zoe-Top - 系统监控工具

实时显示:
- 内核状态
- 器官状态
- 资源使用
- 消息统计
"""

import os
import sys
import json
import time
import socket
from pathlib import Path
from datetime import datetime

try:
    import psutil
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.layout import Layout
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ============ 常量定义 ============

SOCKET_PATH = "/tmp/zoe.sock"
STATUS_FILE = "/tmp/zoe-status.json"
MESSAGES_LOG = "/tmp/zoe-messages.log"

# ============ 核心类 ============

class ZoeTop:
    """Zoe-OS 系统监控"""
    
    def __init__(self):
        self.console = Console() if HAS_RICH else None
        self.start_time = time.time()
    
    def check_kernel(self) -> dict:
        """检查内核状态"""
        status = {
            "running": False,
            "socket": SOCKET_PATH,
            "uptime": 0
        }
        
        # 检查 Socket 文件是否存在
        if Path(SOCKET_PATH).exists():
            try:
                # 尝试连接
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect(SOCKET_PATH)
                sock.close()
                status["running"] = True
            except:
                pass
        
        return status
    
    def check_organs(self) -> list:
        """检查器官状态"""
        organs = []
        
        # 从状态文件读取
        if Path(STATUS_FILE).exists():
            try:
                with open(STATUS_FILE) as f:
                    data = json.load(f)
                    for organ_id, info in data.get("organs", {}).items():
                        organs.append({
                            "id": organ_id,
                            "status": info.get("status", "unknown"),
                            "task": info.get("current_task", "")
                        })
            except:
                pass
        
        return organs
    
    def get_system_stats(self) -> dict:
        """获取系统资源统计"""
        stats = {
            "cpu": 0,
            "memory": 0,
            "disk": 0,
            "processes": 0
        }
        
        if psutil:
            stats["cpu"] = psutil.cpu_percent(interval=0.1)
            stats["memory"] = psutil.virtual_memory().percent
            stats["disk"] = psutil.disk_usage("/").percent
            stats["processes"] = len(psutil.pids())
        
        return stats
    
    def get_message_stats(self) -> dict:
        """获取消息统计"""
        stats = {
            "total": 0,
            "last_minute": 0,
            "types": {}
        }
        
        if Path(MESSAGES_LOG).exists():
            try:
                with open(MESSAGES_LOG) as f:
                    lines = f.readlines()[-100:]  # 最近 100 条
                    stats["total"] = len(lines)
                    
                    # 统计最近一分钟的消息
                    now = time.time()
                    for line in lines:
                        try:
                            msg = json.loads(line)
                            msg_time = datetime.fromisoformat(msg.get("timestamp", "")).timestamp()
                            if now - msg_time < 60:
                                stats["last_minute"] += 1
                            
                            msg_type = msg.get("type", "unknown")
                            stats["types"][msg_type] = stats["types"].get(msg_type, 0) + 1
                        except:
                            pass
            except:
                pass
        
        return stats
    
    def render_rich(self):
        """使用 Rich 渲染界面"""
        layout = Layout()
        
        # 内核状态
        kernel = self.check_kernel()
        kernel_table = Table(title="Kernel Status")
        kernel_table.add_column("Property")
        kernel_table.add_column("Value")
        kernel_table.add_row("Status", "🟢 Running" if kernel["running"] else "🔴 Stopped")
        kernel_table.add_row("Socket", kernel["socket"])
        kernel_table.add_row("Uptime", f"{time.time() - self.start_time:.1f}s")
        
        # 器官状态
        organs = self.check_organs()
        organ_table = Table(title="Organs")
        organ_table.add_column("ID")
        organ_table.add_column("Status")
        organ_table.add_column("Task")
        
        if organs:
            for organ in organs:
                status_icon = "🟢" if organ["status"] == "working" else "🟡" if organ["status"] == "idle" else "🔴"
                organ_table.add_row(organ["id"], f"{status_icon} {organ['status']}", organ["task"][:30])
        else:
            organ_table.add_row("-", "No organs registered", "-")
        
        # 系统资源
        stats = self.get_system_stats()
        stats_table = Table(title="System Resources")
        stats_table.add_column("Resource")
        stats_table.add_column("Usage")
        stats_table.add_row("CPU", f"{stats['cpu']:.1f}%")
        stats_table.add_row("Memory", f"{stats['memory']:.1f}%")
        stats_table.add_row("Disk", f"{stats['disk']:.1f}%")
        stats_table.add_row("Processes", str(stats["processes"]))
        
        # 消息统计
        msg_stats = self.get_message_stats()
        msg_table = Table(title="Messages")
        msg_table.add_column("Metric")
        msg_table.add_column("Count")
        msg_table.add_row("Total", str(msg_stats["total"]))
        msg_table.add_row("Last Minute", str(msg_stats["last_minute"]))
        
        # 组合布局
        layout.split_column(
            Layout(Panel(kernel_table, title="🐝 Zoe-OS Monitor")),
            Layout(organ_table),
            Layout(stats_table),
            Layout(msg_table)
        )
        
        return layout
    
    def render_simple(self):
        """简单文本渲染"""
        os.system("clear" if os.name == "posix" else "cls")
        
        print("\n" + "="*60)
        print("🐝 Zoe-OS Monitor")
        print("="*60 + "\n")
        
        # 内核状态
        kernel = self.check_kernel()
        print("[Kernel]")
        print(f"  Status: {'Running' if kernel['running'] else 'Stopped'}")
        print(f"  Socket: {kernel['socket']}")
        print()
        
        # 器官状态
        organs = self.check_organs()
        print("[Organs]")
        if organs:
            for organ in organs:
                print(f"  {organ['id']}: {organ['status']}")
        else:
            print("  No organs registered")
        print()
        
        # 系统资源
        stats = self.get_system_stats()
        print("[System]")
        print(f"  CPU: {stats['cpu']:.1f}%")
        print(f"  Memory: {stats['memory']:.1f}%")
        print(f"  Disk: {stats['disk']:.1f}%")
        print()
        
        # 消息统计
        msg_stats = self.get_message_stats()
        print("[Messages]")
        print(f"  Total: {msg_stats['total']}")
        print(f"  Last Minute: {msg_stats['last_minute']}")
        print()
        
        print("Press Ctrl+C to exit")
    
    def run(self, interval: float = 1.0):
        """运行监控"""
        try:
            if HAS_RICH and self.console:
                with Live(self.render_rich(), console=self.console, refresh_per_second=1/interval) as live:
                    while True:
                        time.sleep(interval)
                        live.update(self.render_rich())
            else:
                while True:
                    self.render_simple()
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")

# ============ CLI 入口 ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Zoe-OS System Monitor")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="刷新间隔 (秒)")
    parser.add_argument("-n", "--once", action="store_true", help="只显示一次")
    args = parser.parse_args()
    
    monitor = ZoeTop()
    
    if args.once:
        if HAS_RICH:
            monitor.console.print(monitor.render_rich())
        else:
            monitor.render_simple()
    else:
        monitor.run(args.interval)

if __name__ == "__main__":
    main()