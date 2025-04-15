import random
from nonebot.plugin import PluginMetadata
from nonebot import on_command, logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

from .config import Config

# 实例化 Config
config = Config()

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-revolver",
    description="简易左轮禁言小游戏插件",
    usage="简易左轮禁言小游戏插件",
    homepage="",
    type="application",
    supported_adapters={"~onebot.v11"},  # 支持onebot v11适配器
)

__plugin_usage__ = """俄罗斯轮盘帮助：
    开启游戏：轮盘（当群内有一名玩家使用该指令时，游戏开始）
    开始对决：开枪（任意一个人使用该指令，处理开枪逻辑）
    【注：同一时间群内只能有一场对决】
"""

# 初始化游戏命令
revolver_start = on_command("轮盘", aliases={"左轮", "转盘", "装弹"}, priority=5, block=True)
revolver_shoot = on_command("开枪", priority=5, block=True)

# 全局变量存储子弹位置和当前开枪位置
bullet_position = None
chamber_position = 6  # 开枪位置初始为6

# 不可以使用此插件的群聊列表
DISABLED_GROUPS = config.DISABLED_GROUPS  # 替换为实际的群号

# 可以禁言的群聊列表
ENABLED_BAN_GROUPS = config.ENABLED_BAN_GROUPS  # 替换为实际的群号

# 禁言时间（秒）
BAN_DURATION = config.BAN_DURATION  # 10分钟

# 全局变量存储进行中的对局状态
ongoing_games = set()  # 存储正在进行对局的群聊 ID

# 开始游戏
@revolver_start.handle()
async def start_game(event: MessageEvent):
    global bullet_position, chamber_position, ongoing_games

    # 检查群聊是否被禁用
    if event.group_id in DISABLED_GROUPS:
        return await revolver_start.finish("当前群聊已禁用此插件，无法使用“轮盘”功能。")

    # 检查是否已有进行中的对局
    if event.group_id in ongoing_games:
        return await revolver_start.finish("当前群聊已有进行中的对局，请等待对局结束后再开始新游戏！")

    # 初始化游戏状态
    bullet_position = random.randint(1, 6)  # 随机生成子弹位置
    chamber_position = 6  # 初始化开枪位置为6
    ongoing_games.add(event.group_id)  # 标记该群聊有进行中的对局
    logger.info(f"游戏开始，子弹位置为：{bullet_position}")
    await revolver_start.finish("游戏开始！左轮手枪已装填子弹，轮到你开枪了！")

# 处理开枪命令
@revolver_shoot.handle()
async def shoot(bot: Bot, event: MessageEvent):
    global bullet_position, chamber_position, ongoing_games

    # 检查群聊是否被禁用
    if event.group_id in DISABLED_GROUPS:
        return await revolver_shoot.finish("当前群聊已禁用此插件，无法使用“开枪”功能。")

    # 检查子弹位置是否为空
    if bullet_position is None:
        return await revolver_shoot.finish("当前没有装弹，请先使用“轮盘”指令装弹后再开枪！")

    logger.info(f"当前开枪位置：{chamber_position}，子弹位置：{bullet_position}")
    if chamber_position == bullet_position:
        # 检查是否是超级用户
        superusers = bot.config.superusers
        if str(event.user_id) in superusers:
            bullet_position = None  # 重置子弹位置，结束游戏
            chamber_position = 6  # 重置开枪位置
            ongoing_games.discard(event.group_id)  # 移除进行中的对局标记
            return await revolver_shoot.finish("砰！你中弹了！但你是超级用户，不会被禁言。游戏结束！")
        # 中弹，检查是否允许禁言
        if event.group_id in ENABLED_BAN_GROUPS:
            try:
                await bot.set_group_ban(
                    group_id=event.group_id,
                    user_id=event.user_id,
                    duration=BAN_DURATION
                )
                bullet_position = None  # 重置子弹位置，结束游戏
                chamber_position = 6  # 重置开枪位置
                ongoing_games.discard(event.group_id)  # 移除进行中的对局标记
                logger.info("禁言成功，游戏结束！")
                await revolver_shoot.send(f"砰！恭喜你获得【急性铜中毒】！ 你已被禁言{BAN_DURATION // 60}分钟。游戏结束！")
            except FinishedException:
                raise  # 继续抛出 FinishedException，不进行处理
            except Exception as e:
                logger.error(f"禁言失败：{e}")
                bullet_position = None  # 重置子弹位置，结束游戏
                chamber_position = 6  # 重置开枪位置
                ongoing_games.discard(event.group_id)  # 移除进行中的对局标记
                await revolver_shoot.finish("砰！恭喜你获得【急性铜中毒】！但无法禁言，请检查权限。游戏结束！")
                return await revolver_shoot.finish("砰！恭喜你获得【急性铜中毒】！但无法禁言，请检查权限。游戏结束！")
        else:
            bullet_position = None  # 重置子弹位置，结束游戏
            chamber_position = 6  # 重置开枪位置
            ongoing_games.discard(event.group_id)  # 移除进行中的对局标记
            return await revolver_shoot.finish("砰！恭喜你获得【急性铜中毒】！但当前群聊不支持禁言功能。游戏结束！")
    else:
        chamber_position -= 1  # 每次开枪后减1
        if chamber_position < 1:  # 如果位置小于1，循环回到6
            chamber_position = 6
        return await revolver_shoot.finish("咔！幸运地没有中弹，下一位继续！")
