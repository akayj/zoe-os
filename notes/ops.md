# 运维经验

## 热更新铁律

OpenClaw Gateway 一旦重启，所有正在进行的会话都会中断。对用户来说就是"小新断线了"。

**规则**：修改 Skill、Config、Cron 任务，绝不重启 Gateway。只在核心版本升级时才动它。

**怎么做**：
- Skill 修改后，OpenClaw 的 watcher 会自动热加载
- Config 修改后，下一个 session 自动生效
- Cron 任务通过 CLI 增删，不需要重启

## 推送三重降级

当你的 AI 助理需要主动推送消息时，链路可能会断。

```
优先级 1：OpenClaw message 工具（最简单）
    ↓ 失败
优先级 2：feishu-pusher（独立脚本，绕过 Gateway）
    ↓ 失败
优先级 3：直接调用飞书 API（最原始但最可靠）
```

## 错峰调度

飞书 API 有频率限制。如果 5 个定时任务都在 09:30 触发，必然有几个会被限流。

**解法**：
```
07:30 早间简报
08:00 壁纸推荐
09:30 GitHub 热榜
10:00 版本检查（仅周二/五）
03:30 DeepSeek 监控（凌晨低峰）
```

任务之间至少间隔 30 分钟。

## Checkpoint 设计

任何可能失败的长任务，都应该在每个关键步骤后保存状态：

```python
state.phase = "backup_done"
state.save()
# ... 执行升级 ...
state.phase = "upgrade_done"
state.save()
```

这样即使进程被杀，下次启动时可以从断点继续，而不是从头来。
