from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from core.logging import get_logger
from core.types import Point, Rect
from vision.templates import Template, TemplateStore

logger = get_logger(__name__)


@dataclass
class MatchResult:
    """模板匹配结果。
    
    Attributes:
        score: 匹配相似度分数（0.0-1.0），越接近 1.0 越相似
        rect: 匹配到的区域矩形（窗口内坐标）
        center: 匹配区域的中心点坐标（窗口内坐标），通常用于点击操作
    """
    score: float
    rect: Rect
    center: Point


class TemplateMatcher:
    """模板匹配器，基于 OpenCV 的模板匹配算法。
    
    使用归一化相关系数匹配（TM_CCOEFF_NORMED），
    这种方法对光照变化有一定的鲁棒性。
    
    匹配过程：
    1. 如果模板定义了 ROI，先裁剪屏幕到该区域
    2. 在屏幕图像中搜索模板图片
    3. 找到相似度最高的位置
    4. 如果相似度 >= threshold，返回匹配结果
    """

    def __init__(self, store: TemplateStore) -> None:
        """初始化模板匹配器。
        
        Args:
            store: 模板管理器，用于加载模板图片
        """
        self.store = store

    def match(
        self,
        screen: np.ndarray,
        template: Template,
    ) -> Optional[MatchResult]:
        """在屏幕图像中匹配模板，返回最佳匹配结果。
        
        Args:
            screen: 屏幕截图（BGR 格式的 numpy 数组）
            template: 要匹配的模板对象
        
        Returns:
            如果找到匹配（相似度 >= threshold），返回 MatchResult；
            否则返回 None
        
        Note:
            - 如果屏幕图像小于模板图像，直接返回 None
            - 匹配结果中的坐标是窗口内坐标（如果定义了 ROI，会加上 ROI 的偏移）
        """
        screen_img = screen.copy()

        # 如果模板定义了 ROI（感兴趣区域），先裁剪屏幕图像
        if template.roi is not None:
            x, y, r, b = template.roi.to_tuple()
            screen_img = screen_img[y:b, x:r]

        # 加载模板图片
        tmpl_img = self.store.load_image(template.path)

        # 检查屏幕是否足够大
        if screen_img.shape[0] < tmpl_img.shape[0] or screen_img.shape[1] < tmpl_img.shape[1]:
            logger.debug("屏幕图像小于模板 %s，跳过匹配", template.name)
            return None

        # 执行模板匹配（使用归一化相关系数）
        res = cv2.matchTemplate(screen_img, tmpl_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        logger.debug("模板 '%s' 匹配分数=%.4f", template.name, max_val)

        # 检查是否达到阈值
        if max_val < template.threshold:
            return None

        # 计算匹配区域的矩形和中心点
        top_left = max_loc  # 在裁剪后的图像中的位置
        h, w = tmpl_img.shape[:2]
        
        # 如果定义了 ROI，需要加上 ROI 的偏移量，转换为窗口内坐标
        offset_x = template.roi.x if template.roi is not None else 0
        offset_y = template.roi.y if template.roi is not None else 0

        left = top_left[0] + offset_x
        top = top_left[1] + offset_y
        rect = Rect(x=left, y=top, width=w, height=h)
        center: Point = (left + w // 2, top + h // 2)

        return MatchResult(score=max_val, rect=rect, center=center)

    def exists(self, screen: np.ndarray, template: Template) -> bool:
        """检查模板是否存在于屏幕图像中。
        
        Args:
            screen: 屏幕截图
            template: 要检查的模板
        
        Returns:
            如果找到匹配返回 True，否则返回 False
        """
        return self.match(screen, template) is not None

