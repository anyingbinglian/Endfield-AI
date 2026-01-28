"""交互模块常量定义。

定义截图通道模式、匹配返回模式等常量。
"""

# 截图通道模式
NORMAL_CHANNELS = 0  # 3通道BGR（标准RGB图像）
BACKGROUND_CHANNELS = 1  # 背景通道（处理透明通道，提取背景）
UI_CHANNELS = 2  # UI通道（处理透明通道，提取UI元素）
FOUR_CHANNELS = 3  # 4通道BGRA（包含透明通道）

# 匹配返回模式
IMG_RATE = 0  # 返回相似度分数（float）
IMG_POSI = 1  # 返回相似度分数和位置坐标（tuple: (float, tuple[int, int])）
IMG_POINT = 2  # 返回位置点（tuple[int, int]）
IMG_RECT = 3  # 返回边界框（Rect对象）
IMG_BOOL = 4  # 返回布尔值（bool）
IMG_BOOLRATE = 5  # 如果匹配成功返回分数，否则返回False（Union[float, bool]）
