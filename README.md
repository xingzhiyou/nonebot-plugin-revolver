# nonebot-plugin-revolver

## 简介
`nonebot-plugin-revolver` 是一个简易左轮禁言小游戏插件，适用于 NoneBot 框架。通过该插件，群成员可以体验刺激的“俄罗斯轮盘”游戏。

## 使用方法
### 指令说明
- **开启游戏**：  
  使用指令 `轮盘`，当群内有一名玩家使用该指令时，游戏开始。

- **开始对决**：  
  使用指令 `开枪`，任意一个人使用该指令后，触发开枪逻辑。

> **注意**：同一时间群内只能有一场对决。

### 示例
1. 玩家 A 在群内发送 `轮盘`，游戏开始。
2. 玩家 B 发送 `开枪`，触发开枪逻辑，游戏继续。

## 支持的适配器
- OneBot v11

## 安装
1. 使用 `pip` 安装插件：
   ```bash
   pip install nonebot-plugin-revolver
   ```
2. 在 NoneBot 项目的 `bot.py` 中加载插件：
   ```python
   nonebot.load_plugin("nonebot_plugin_revolver")
   ```
## 配置
在使用插件前，可以通过 `.env` 配置项进行自定义设置：

- `DISABLED_GROUPS`：设置默认禁用插件的群聊 ID 列表。
- `ENABLED_BAN_GROUPS`：设置默认允许禁言功能的群聊 ID 列表。
- `BAN_DURATION`：设置默认禁言时间，单位为秒。

## 贡献
欢迎提交 Issue 和 Pull Request 来改进本插件。

## 许可证
本项目基于 MIT 许可证开源。  