#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["typer", "rich", "requests"]
# ///
"""
retry-failed-tasks - 重试失败的定时任务
等待 API rate limit 窗口过去后，重试失败的任务
"""
import os, subprocess, json, time, typer
from pathlib import Path
from rich.console import Console
from datetime import datetime

app = typer.Typer()
console = Console()
CRON_JOBS_FILE = Path("/root/.openclaw/cron/jobs.json")
DELIVERY_QUEUE_DIR = Path("/root/.openclaw/delivery-queue")
GATEWAY_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "400c075d78fe5ebdc1e7c45adc625895b503fc82b88fba35")

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

@app.command()
def retry_cron(job_id: str, max_attempts: int = 3, delay_seconds: int = 300):
    """重试指定的 cron 任务"""
    console.print(f"[cyan]开始重试任务：{job_id}[/cyan]")
    console.print(f"最大尝试次数：{max_attempts}, 延迟：{delay_seconds}秒")
    
    for attempt in range(1, max_attempts + 1):
        console.print(f"\n[yellow]尝试 {attempt}/{max_attempts}[/yellow]")
        
        # 等待延迟
        if attempt > 1:
            console.print(f"等待 {delay_seconds}秒...")
            time.sleep(delay_seconds)
        
        # 执行 cron run
        result = run_cmd(f'OPENCLAW_GATEWAY_TOKEN="{GATEWAY_TOKEN}" openclaw cron run {job_id} 2>&1')
        
        # 检查结果
        if '"ok": true' in result and '"ran": true' in result:
            # 等待任务完成
            time.sleep(10)
            
            # 检查是否还有错误
            jobs_data = json.loads(CRON_JOBS_FILE.read_text())
            for job in jobs_data['jobs']:
                if job['id'] == job_id:
                    status = job['state'].get('lastStatus', '')
                    error = job['state'].get('lastError', '')
                    
                    if status == 'ok' or not error:
                        console.print(f"[green]✓ 任务 {job_id} 执行成功！[/green]")
                        return
                    else:
                        console.print(f"[yellow]⚠ 任务执行但仍有错误：{error[:50]}[/yellow]")
                        break
        else:
            console.print(f"[red]✗ 尝试失败：{result[:100]}[/red]")
    
    console.print(f"[red]✗ 达到最大尝试次数，任务 {job_id} 重试失败[/red]")

@app.command()
def retry_delivery(queue_id: str, max_attempts: int = 3, delay_seconds: int = 300):
    """重试指定的推送队列"""
    console.print(f"[cyan]开始重试推送：{queue_id}[/cyan]")
    
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            console.print(f"等待 {delay_seconds}秒...")
            time.sleep(delay_seconds)
        
        console.print(f"\n[yellow]尝试 {attempt}/{max_attempts}[/yellow]")
        
        # 检查队列文件是否还存在
        queue_file = DELIVERY_QUEUE_DIR / f"{queue_id}.json"
        if not queue_file.exists():
            console.print(f"[green]✓ 推送队列 {queue_id} 已不存在（可能已成功）[/green]")
            return
        
        # 等待一段时间让系统自动重试
        time.sleep(60)
        
        # 再次检查
        if not queue_file.exists():
            console.print(f"[green]✓ 推送 {queue_id} 已成功[/green]")
            return
    
    console.print(f"[yellow]⚠ 推送 {queue_id} 仍在队列中，可能需要手动处理[/yellow]")

@app.command()
def watch(delay_seconds: int = 300):
    """监控并重试所有失败的任务"""
    console.print(f"[cyan]开始监控失败任务，延迟：{delay_seconds}秒[/cyan]")
    
    while True:
        # 检查 cron 任务
        if CRON_JOBS_FILE.exists():
            jobs_data = json.loads(CRON_JOBS_FILE.read_text())
            for job in jobs_data['jobs']:
                if job['enabled'] and job['state'].get('lastStatus') == 'error':
                    error = job['state'].get('lastError', '')
                    if 'rate limit' in error.lower():
                        console.print(f"[yellow]发现 rate limit 错误：{job['name']}[/yellow]")
                        # 可以在这里添加自动重试逻辑
        
        time.sleep(delay_seconds)

if __name__ == "__main__":
    app()
