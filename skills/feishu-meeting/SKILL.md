---
name: feishu-meeting
description: Feishu/Lark calendar meeting management — create, cancel, update, and list meetings with attendees. Activate when user mentions scheduling meetings, booking rooms, inviting people to events, canceling meetings, or any calendar-related operations on Feishu/Lark.
---

# Feishu Meeting

基于 Python + DuckDB 的飞书会议管理工具。

## 核心特性

- ✅ **DuckDB 通讯录缓存** — 本地查询，避免重复 API 调用
- ✅ **Typer CLI** — 现代化命令行界面
- ✅ **自动通知** — 创建/取消会议时自动发送通知
- ✅ **参会人可见** — 默认 `attendee_ability: can_see_others`

## 安装

已全局安装，可直接使用：
```bash
feishu-meeting --help
```

## 快速开始

### 1. 查看本地通讯录
```bash
feishu-meeting list-contacts
```

### 2. 添加联系人（手动）
```bash
feishu-meeting add-contact "email@example.com" --alias "张三" --name "张三"
```

### 3. 创建会议
```bash
feishu-meeting create "项目评审会" "2026-03-09 14:00" 60 "ou_xxx,ou_yyy"
```
参数：
- 标题
- 开始时间（YYYY-MM-DD HH:MM）
- 时长（分钟）
- 参会人（逗号分隔，支持 name/email/alias/open_id）

### 4. 取消会议
```bash
feishu-meeting cancel <event_id>
```

## 配置

配置文件：`references/config.json`

```json
{
  "app_id": "cli_xxx",
  "app_secret": "xxx",
  "calendar_id": "feishu.cn_xxx@group.calendar.feishu.cn",
  "timezone": "Asia/Shanghai",
  "default_duration_min": 30,
  "default_attendee_ability": "can_see_others"
}
```

也可通过环境变量覆盖：
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_CALENDAR_ID`

## 数据文件

- `data/contacts.duckdb` — 本地通讯录缓存（DuckDB 格式）
- `references/config.json` — 飞书应用配置
- `references/api-notes.md` — API 注意事项

## 技术细节

- **传输方式**: stdio（本地执行）
- **依赖管理**: uv + PEP 723（自包裹脚本）
- **数据库**: DuckDB（轻量级，无需服务器）
- **API 版本**: Feishu Open API v4

## 依赖权限

| 权限 | 用途 | 状态 |
|------|------|------|
| `calendar:calendar:read` | 读取日历 | ✅ 已有 |
| `calendar:calendar.event:create` | 创建事件 | ✅ 已有 |
| `contact:user.id:readonly` | 查询用户 ID | ✅ 已有 |
| `search:user` | 姓名搜索 | ❌ 需 user_access_token |
| `vc:room:readonly` | 会议室查询 | ❌ 待开通 |

---
*最后更新：2026-03-08*
