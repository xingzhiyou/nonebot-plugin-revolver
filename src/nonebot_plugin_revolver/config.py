# config.py
from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    disabled_groups: List[int] = []  # 禁用的群聊
    enabled_ban_groups: List[int] = []  # 可以禁言的群聊
    rolling_ban: bool = False  # 是否随机禁言时间
    ban_duration: int = 600  # 默认禁言时间（秒）
    
    # 新增主题配置
    theme: str = "lottery"  
    # 默认主题，可选：lottery, food, magic, programming, divination, investment, adventure, social, sports
    # 如果不配置theme，会自动随机选择一个主题
    # 在.env配置文件中
    # REVOLVER_THEME="lottery"  # 使用抽奖主题

    allow_theme_switch: bool = True  # 是否允许通过命令切换主题
    
    class Config:
        extra = "ignore"