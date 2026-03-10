# 🔌 Design: Zoe-Socket Protocol

> **"Universal connectivity for the Agentic Era."**

`zoe-socket` 是 Zoe-OS 内部及外部节点联通的核心插口标准。它的设计目标是：**人类可读、机器可解析、跨系统普适**。

---

## 1. 协议报文 (The Human-Readable Packet)

我们不使用二进制，而是使用结构化的 JSON/YAML 报文，确保即使在网络嗅探器里，人也能一眼看出 Agent 在干什么。

```json
{
  "zoe_version": "0.1.3",
  "id": "msg_8892af",
  "type": "INTENT", 
  "sender": "zoe-native-server",
  "target": "zoe-swarm-broadcast",
  "content": {
    "intent": "FILE_READ",
    "params": { "path": "/etc/hosts" },
    "context": "Need network info for diagnostics"
  },
  "signature": "..."
}
```

---

## 2. 接入模式 (Connectivity Modes)

### 🔵 Zoe-Native (原生支持)
- **定义**：直接集成 Zoe 内核的轻量级程序。
- **特点**：零转换，性能最高，原生支持 Sense-Think-Act-Verify 循环。
- **示例**：跑在树莓派上的 `zoe-sensor-node`。

### 🟡 Zoe-Bridge (桥接模式)
- **定义**：一个协议翻译层，将“非 Zoe”系统接入 Swarm。
- **桥接 OpenClaw**：包装 OpenClaw 的 `message/nodes` 接口，让 OpenClaw 表现得像一个 Zoe 节点。
- **桥接外部世界**：将 REST API、Webhook 或 MQTT 转换为 `zoe-socket` 报文。

---

## 3. 语义总线 (The Semantic Bus)

不同于传统的 IP 路由，`zoe-socket` 运行在语义总线上：
1. **Discovery**：新节点插入总线时，广播自己的 **Capability Descriptor** (我能做什么)。
2. **Matching**：总线根据任务的 Intent 自动匹配最合适的 Socket 节点。
3. **Piping**：支持流式传输，一个 Zoe 节点的输出可以直接 Pipe 到另一个节点的输入。

---

## 🗺️ 实现蓝图 (Prototype)

- [ ] **`zoe-link-lib`**: 最小协议封装库。
- [ ] **`oc-bridge`**: 让 OpenClaw 接入 Zoe-Swarm 的第一个官方桥接器。
- [ ] **`web-socket-gateway`**: 允许浏览器或第三方 App 通过简单 Socket 连接 Zoe-OS。

---

*Drafted by Xiao Xin | Protocol Architecture by akayj*
