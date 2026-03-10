# 🎮 Spec: GUI Embodiment (Digital Twin)

Zoe-OS 如何接管并驱动虚拟图形界面（GUI）中的实体。

---

## 1. 意图驱动 (Intent to Action)
大脑下达高维意图，由 GUI 桥接器（Bridge）转化为物理按键或 API 调用：

| 意图 (Intent) | GUI 映射示例 (Mac) |
|--------------|-------------------|
| `MOVE_FORWARD`| `PyAutoGUI.press('w')` |
| `JUMP`        | `PyAutoGUI.press('space')` |
| `PICK_UP`     | `Mouse.click(x, y)` |

---

## 2. 数字痛觉 (Digital Interoception)
当虚拟人物发生异常状态时，GUI 必须向 Zoe 内核发送原始信号，内核压缩为以下感官词：

- **`FEELING: COLLIDED`**: 撞到墙壁或障碍物。
- **`FEELING: FALLEN`**: 人物跌倒或姿态异常（摔跤）。
- **`FEELING: VOID`**: 人物掉出地图或进入非法区域。

---

## 3. 语音闭环 (Auditory Feedback)
当内核向大脑反馈 `FEELING: FALLEN` 时，决策层应触发自愈动作或语音求助：

```python
# 逻辑层处理逻辑 (Pseudocode)
if signal.feeling == "FALLEN":
    tts.say("老板，我摔跤了，真疼啊！")
    brain.dispatch("STAND_UP")
```

---

## 🛠️ 实现路径
1. **Zoe-Bridge**: 在 Mac 上启动一个 Python 脚本连接 `zoe-bus.sock`。
2. **Signal Loop**: GUI 每帧或在状态改变时向 Bridge 发送报文。
3. **Reflex**: 内核根据报文实时更新 4D 压力模型。

---
*Architected by Xiao Xin | Direction by akayj*
