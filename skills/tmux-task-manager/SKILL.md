---
name: tmux-task-manager
description: 当需要运行耗时任务（>5 分钟）、后台进程、或需要实时监控进度时触发。适用于长脚本执行、API rate limit 延迟重试、跨会话任务、需要终端交互的场景。不要总结流程！
---

# Tmux Task Manager - 长任务管理 Skill

基于 tmux session/window/pane + Python 后台线程心跳的任务管理系统。

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                   OpenClaw + tmux                        │
├─────────────────────────────────────────────────────────┤
│  自然语言指令 → tmux_manager.py → tmux session          │
│                      ↓                                   │
│          Python 后台线程心跳（每 N 秒）                   │
│                      ↓                                   │
│          capture-pane → 终端输出（可选推送）             │
└─────────────────────────────────────────────────────────┘
```

## 使用场景

### 1. 运行长任务（后台模式）
```bash
tmux-task run "study" "python3 scrape_github.py"
```

### 2. 运行并立即 attach 进去看输出
```bash
tmux-task run "study" "python3 scrape_github.py" --attach
```

### 3. 延迟重试（rate limit 场景）
```bash
tmux-task run "retry-github" "sleep 300 && openclaw cron run <job_id>"
```

### 4. 查看进度（从日志文件读取）
```bash
tmux-task peek "study"           # 最后 10 行
tmux-task peek "study" --lines 50
tmux-task peek "study" --follow  # 持续跟踪（tail -f）
```

### 5. Attach 到运行中的会话
```bash
tmux-task attach "study"
# 或直接用 tmux
tmux attach -t study
```

### 6. 管理会话
```bash
tmux-task list          # 查看所有运行中的任务
tmux-task stop "study"  # 停止任务
```

## 核心功能

### Session 管理
- 自动创建隔离的 tmux session
- 支持命名规范：`{project}-{timestamp}`
- 日志持久化到 `~/.tmux-logs/`

### 实时输出（tee 双写）
```bash
# 命令输出同时显示在 pane 和写入日志
command 2>&1 | tee -a ~/.tmux-logs/{session}.log
```
- **tmux attach 进去直接看到完整实时输出**
- **日志文件完整记录所有输出**
- **peek 命令从日志读取，更快更稳定**

### 心跳监控
- Python 后台线程实现（避免 cron 环境变量问题）
- 心跳间隔可配置（默认 60 秒）
- 监控日志文件变化，显示新增内容

### 延迟执行
- 支持 `sleep N && command` 模式
- 适用于 API rate limit 重试场景

## tmux 高级特性（2026-03-09 学习）

### Hooks（钩子）
```bash
# 任务完成后触发
tmux set-hook -g after-new-window "display-message '任务完成'"

# 客户端连接时触发
tmux set-hook -g client-attached "display-message '欢迎回来'"
```

### Control Mode
```bash
# 程序化控制 tmux
tmux -CC new-session -d -s mytask "<命令>"
```

### 窗口分割
```bash
# 垂直分割
tmux split-window -v -t <会话名> "<命令>"

# 水平分割
tmux split-window -h -t <会话名> "<命令>"
```

## 最佳实践

1. **所有超过 5 分钟的任务必须用 tmux-task 运行**
2. **心跳间隔默认 60 秒，可根据任务调整**
3. **API rate limit 场景用延迟重试：`sleep 300 && command`**
4. **敏感任务启用日志加密**

## 与 cron 的对比

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 定时重复执行 | openclaw cron | 内置调度，支持 announce 推送 |
| 一次性长任务 | tmux-task | 环境变量完整，支持实时监控 |
| API rate limit 重试 | tmux-task | 可用 sleep 延迟，不占用 cron 配额 |
| 需要终端交互 | tmux-task | 完整的 pseudo-terminal |

---
*Powered by tmux + Python threading + tee*
*最后更新：2026-03-09 21:00*
