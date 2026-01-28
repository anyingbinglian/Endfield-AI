"""交互模块。

提供统一的交互接口，包括截图、图像识别、鼠标键盘操作等功能。
"""

from interaction.core import InteractionCore
from interaction.constants import (
    BACKGROUND_CHANNELS,
    FOUR_CHANNELS,
    IMG_BOOL,
    IMG_BOOLRATE,
    IMG_POSI,
    IMG_RATE,
    NORMAL_CHANNELS,
    UI_CHANNELS,
)

# 创建全局交互实例
interaction = InteractionCore()

__all__ = [
    'InteractionCore',
    'interaction',
    # 常量
    'NORMAL_CHANNELS',
    'BACKGROUND_CHANNELS',
    'UI_CHANNELS',
    'FOUR_CHANNELS',
    'IMG_RATE',
    'IMG_POSI',
    'IMG_BOOL',
    'IMG_BOOLRATE',
]
