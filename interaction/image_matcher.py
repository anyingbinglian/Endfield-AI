"""图像匹配工具模块。

基于 OpenCV 的模板匹配实现图像识别功能。
"""

from typing import Optional, Tuple, Union

import cv2
import numpy as np

from core.logging import get_logger
from core.types import Rect
from interaction.constants import IMG_BOOL, IMG_BOOLRATE, IMG_POSI, IMG_RATE

logger = get_logger(__name__)


class ImageMatchError(RuntimeError):
    """图像匹配操作失败时抛出的异常。"""
    pass


def match_image(
    image: np.ndarray,
    template: np.ndarray,
    is_gray: bool = False,
    return_mode: int = IMG_RATE,
) -> Union[float, Tuple[float, Tuple[int, int]]]:
    """在图像中匹配模板。
    
    使用 OpenCV 的 matchTemplate 进行模板匹配，使用归一化相关系数（TM_CCORR_NORMED）。
    匹配结果范围为 [0, 1]，越接近 1 越相似。
    
    Args:
        image: 源图像（numpy 数组，BGRA 或 BGR 格式）
        template: 模板图像（numpy 数组，BGRA 或 BGR 格式）
        is_gray: 是否使用灰度匹配，默认 False
        return_mode: 返回模式
            - IMG_RATE: 返回相似度分数（float）
            - IMG_POSI: 返回相似度分数和位置坐标（tuple: (float, tuple[int, int])）
            
    Returns:
        根据 return_mode 返回不同的结果：
        - IMG_RATE: 相似度分数（float，范围 0.0-1.0）
        - IMG_POSI: (相似度分数, 位置坐标) 的元组
        
    Raises:
        ImageMatchError: 如果匹配失败
    """
    try:
        # 转换为灰度图（如果需要）
        if is_gray:
            if len(image.shape) == 3:
                if image.shape[2] == 4:
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
                else:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            if len(template.shape) == 3:
                if template.shape[2] == 4:
                    template = cv2.cvtColor(template, cv2.COLOR_BGRA2GRAY)
                else:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # 检查图像尺寸
        if image.shape[0] < template.shape[0] or image.shape[1] < template.shape[1]:
            logger.warning(
                f"源图像尺寸 ({image.shape}) 小于模板尺寸 ({template.shape})，无法匹配"
            )
            if return_mode == IMG_RATE:
                return 0.0
            else:
                return 0.0, (0, 0)
        
        # 执行模板匹配
        # 使用归一化相关系数匹配（TM_CCORR_NORMED）
        # 结果范围为 [0, 1]，越接近 1 越相似
        result = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED)
        
        # 获取最大值和最小值及其位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        matching_rate = max_val
        
        # 根据返回模式返回结果
        if return_mode == IMG_RATE:
            return matching_rate
        elif return_mode == IMG_POSI:
            return matching_rate, max_loc
        else:
            raise ImageMatchError(f"不支持的返回模式: {return_mode}")
            
    except Exception as e:
        raise ImageMatchError(f"图像匹配失败: {e}") from e


def crop_image(image: np.ndarray, region: Rect) -> np.ndarray:
    """裁剪图像区域。
    
    Args:
        image: 源图像
        region: 要裁剪的区域（窗口内坐标）
        
    Returns:
        裁剪后的图像
    """
    x, y = region.x, region.y
    right, bottom = region.right, region.bottom
    return image[y:bottom, x:right]
