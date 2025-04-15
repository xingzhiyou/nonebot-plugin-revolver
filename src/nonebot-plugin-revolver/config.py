from pydantic import BaseModel
from typing import Set

class Config(BaseModel):
    DISABLED_GROUPS: Set[int] = set()  # 默认禁用的群聊列表
    ENABLED_BAN_GROUPS: Set[int] = set()  # 默认允许禁言的群聊列表
    BAN_DURATION: int = 600  # 默认禁言时间（秒）