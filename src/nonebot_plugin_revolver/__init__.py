import random
from nonebot.plugin import PluginMetadata, get_plugin_config
from nonebot import on_command, logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from asyncio import Lock

# 导入消息管理器
from .message_manager import msg_manager
from .config import Config

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="简易左轮禁言",
    description="简易左轮禁言小游戏插件，支持多种主题",
    usage="轮盘/抽奖/试毒/施法等、开枪/开奖/品尝/释放等",
    homepage="https://github.com/xingzhiyou/nonebot-plugin-revolver",
    type="application",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 使用 get_plugin_config 获取插件配置
conf = get_plugin_config(Config)

# 设置主题
if hasattr(conf, 'theme') and conf.theme:
    msg_manager.set_theme(conf.theme)
else:
    # 默认使用随机主题
    msg_manager.set_theme(msg_manager.get_random_theme())

# 获取当前主题的命令配置
current_theme = msg_manager.get_current_theme()

# 初始化游戏命令（使用当前主题的配置）
revolver_start = on_command(
    current_theme["start_cmd"],
    aliases=set(current_theme["start_aliases"]),
    priority=5,
    block=True
)
revolver_shoot = on_command(
    current_theme["shoot_cmd"],
    priority=5,
    block=True
)

# 全局变量存储子弹位置和当前开枪位置
bullet_position = None
chamber_position = 6  # 开枪位置初始为6

# 不可以使用此插件的群聊列表
DISABLED_GROUPS = conf.disabled_groups if hasattr(conf, 'disabled_groups') else []

# 可以禁言的群聊列表
ENABLED_BAN_GROUPS = conf.enabled_ban_groups if hasattr(conf, 'enabled_ban_groups') else []

# 是否禁言随机时间
ROLLING_BAN = conf.rolling_ban if hasattr(conf, 'rolling_ban') else False

# 禁言时间（秒）
BAN_DURATION = conf.ban_duration if hasattr(conf, 'ban_duration') else 600

# 全局变量存储进行中的对局状态
ongoing_games = set()  # 存储正在进行对局的群聊 ID

game_lock = Lock()

# 开始游戏
@revolver_start.handle()
async def start_game(event: MessageEvent):
    global bullet_position, chamber_position, ongoing_games

    logger.info(f"接收到{current_theme['start_cmd']}指令，群聊ID：{event.group_id}，用户ID：{event.user_id}")
    logger.info(f"可以禁言的群聊列表：{ENABLED_BAN_GROUPS}")
    logger.info(f"当前有对战的群聊列表：{ongoing_games}")
    logger.debug(f"{current_theme['bullet_name']}位置：{bullet_position}，开枪位置：{chamber_position}")

    async with game_lock:
        # 检查群聊是否被禁用
        if event.group_id in DISABLED_GROUPS:
            return await revolver_start.finish(
                msg_manager.get_message("disabled_group", current_theme["start_cmd"])
            )

        # 检查是否已有进行中的对局
        if event.group_id in ongoing_games:
            return await revolver_start.finish(
                msg_manager.get_message("game_in_progress")
            )

        # 初始化游戏状态
        ongoing_games.add(event.group_id)  # 标记该群聊有进行中的对局
        return await revolver_start.finish(
            msg_manager.get_message("game_start")
        )

# 处理开枪命令
@revolver_shoot.handle()
async def shoot(bot: Bot, event: MessageEvent):
    global bullet_position, chamber_position, ongoing_games

    async with game_lock:
        # 检查群聊是否被禁用
        if event.group_id in DISABLED_GROUPS:
            return await revolver_shoot.finish(
                msg_manager.get_message("disabled_group", current_theme["shoot_cmd"])
            )

        # 检查子弹位置是否为空
        if bullet_position is None:
            if event.group_id in ongoing_games:
                # 装弹
                bullet_position = random.randint(1, 6)
                chamber_position = 6
                logger.info(f"{current_theme['bullet_name']}成功，游戏开始！")
            else:
                return await revolver_shoot.finish(
                    msg_manager.get_message("no_bullet", current_theme["start_cmd"])
                )

        logger.info(f"当前群聊：{event.group_id}，当前开枪位置：{chamber_position}，{current_theme['bullet_name']}位置：{bullet_position}")
        
        if chamber_position == bullet_position:
            # 中弹，检查是否允许禁言
            if event.group_id in ENABLED_BAN_GROUPS:
                # 检查是否是超级用户
                superusers = bot.config.superusers
                if str(event.user_id) in superusers:
                    bullet_position = None  # 重置子弹位置，结束游戏
                    chamber_position = 6  # 重置开枪位置
                    ongoing_games.discard(event.group_id)  # 移除进行中的对局标记
                    return await revolver_shoot.finish(
                        msg_manager.get_message("superuser_hit", current_theme["hit_name"])
                    )
                
                try:
                    if ROLLING_BAN:
                        ban_duration = random.randint(1, BAN_DURATION)
                    else:
                        ban_duration = BAN_DURATION

                    await bot.set_group_ban(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        duration=ban_duration
                    )
                    bullet_position = None
                    chamber_position = 6
                    ongoing_games.discard(event.group_id)
                    logger.info("禁言成功，游戏结束！")
                    
                    # 发送禁言成功消息
                    await revolver_shoot.send(
                        msg_manager.get_message("hit_with_ban", ban_duration // 60)
                    )
                    
                except FinishedException:
                    raise
                except Exception as e:
                    logger.error(f"禁言失败：{e}")
                    bullet_position = None
                    chamber_position = 6
                    ongoing_games.discard(event.group_id)
                    return await revolver_shoot.finish(
                        msg_manager.get_message("ban_failed", current_theme["hit_name"])
                    )
            else:
                bullet_position = None
                chamber_position = 6
                ongoing_games.discard(event.group_id)
                return await revolver_shoot.finish(
                    msg_manager.get_message("hit_no_ban", current_theme["hit_name"])
                )
        else:
            chamber_position -= 1
            if chamber_position < 1:
                chamber_position = 6
            return await revolver_shoot.finish(
                msg_manager.get_message("miss", current_theme["hit_name"])
            )


# 可选：添加切换主题的命令
if hasattr(conf, 'allow_theme_switch') and conf.allow_theme_switch:
    from nonebot.params import CommandArg
    from nonebot.adapters.onebot.v11 import Message
    
    theme_cmd = on_command("切换主题", priority=5, block=True)
    
    @theme_cmd.handle()
    async def switch_theme(event: MessageEvent, bot: Bot, args: Message = CommandArg()):
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            # 显示所有可用主题
            themes = msg_manager.get_all_themes()
            current = msg_manager.current_theme
            themes_str = "\n".join([
                f"{'→' if t == current else '  '} {t}" for t in themes
            ])
            await theme_cmd.finish(f"📚 当前主题：{current}\n🌈 可用主题：\n{themes_str}\n\n使用：/切换主题 主题名")
        else:
            theme_name = arg_text
            if msg_manager.set_theme(theme_name):
                global current_theme
                current_theme = msg_manager.get_current_theme()
                await theme_cmd.finish(f"✅ 已切换到主题：{theme_name}")
            else:
                await theme_cmd.finish(f"❌ 主题 '{theme_name}' 不存在")