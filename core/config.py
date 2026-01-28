from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class WindowConfig:
    """游戏窗口相关配置。
    
    用于查找和识别游戏窗口。系统会遍历所有可见窗口，
    匹配窗口标题中包含这些字符串的窗口。
    
    Attributes:
        window_titles: 游戏窗口可能的标题列表。
                       匹配时会进行不区分大小写的子串匹配。
                       例如：如果窗口标题是 "明日方舟：终末地 - 游戏窗口"，
                       只要包含 "明日方舟：终末地" 就能匹配成功。
    
    Note:
        当终末地正式发布后，请根据实际窗口标题更新此配置。
    """
    window_titles: List[str] = (
        "Arknights: Endfield",
        "明日方舟：终末地",
    )


# 全局窗口配置实例，供其他模块使用
WINDOW_CONFIG = WindowConfig()

