from pydantic import BaseModel
from typing import Set

class Config(BaseModel):
    disabled_groups: Set[int] = set()  # 默认禁用的群聊列表
    enabled_ban_groups: Set[int] = set()  # 默认允许禁言的群聊列表
    ban_duration: int = 600  # 默认禁言时间（秒）