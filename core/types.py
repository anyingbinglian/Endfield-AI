from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

# 坐标点类型：表示窗口内的一个像素点坐标 (x, y)
Point = Tuple[int, int]


@dataclass(frozen=True)
class Rect:
    """窗口内坐标系的矩形区域（轴对齐矩形）。
    
    用于表示截图区域、模板匹配区域等。
    坐标系统：左上角为原点(0,0)，x向右递增，y向下递增。
    
    Attributes:
        x: 矩形左上角的 x 坐标
        y: 矩形左上角的 y 坐标
        width: 矩形的宽度（像素）
        height: 矩形的高度（像素）
    """
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """返回矩形右边界 x 坐标（不包含，即 x + width）。"""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """返回矩形下边界 y 坐标（不包含，即 y + height）。"""
        return self.y + self.height

    def to_tuple(self) -> tuple[int, int, int, int]:
        """转换为元组格式 (left, top, right, bottom)。
        
        返回:
            包含四个整数的元组，表示矩形的边界坐标
        """
        return self.x, self.y, self.right, self.bottom
