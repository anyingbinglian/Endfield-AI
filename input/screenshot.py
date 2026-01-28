from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import mss
import numpy as np

import win32gui  # type: ignore

from core.logging import get_logger
from core.types import Rect
from input.foreground import WindowInfo, find_game_window

logger = get_logger(__name__)


@dataclass
class ScreenCaptureConfig:
    """截图配置选项。
    
    Attributes:
        use_window_rect: 如果为 True，只截取游戏窗口区域；
                         如果为 False，截取整个主屏幕
    """
    use_window_rect: bool = True


class ScreenshotError(RuntimeError):
    """截图操作失败时抛出的异常。
    
    可能的原因：
    - 窗口已关闭
    - 区域坐标无效
    - 系统权限不足
    """
    pass


class ScreenCapture:
    """屏幕截图工具，基于 mss 库实现。
    
    默认情况下只截取游戏窗口区域（客户区），这样可以：
    - 提高截图速度
    - 减少不必要的数据
    - 简化后续的图像处理
    
    截图返回的是 BGR 格式的 numpy 数组（OpenCV 标准格式），
    可以直接用于 OpenCV 的图像处理操作。
    """

    def __init__(
        self,
        window: Optional[WindowInfo] = None,
        config: Optional[ScreenCaptureConfig] = None,
    ) -> None:
        """初始化截图工具。
        
        Args:
            window: 可选的窗口信息。如果不提供，会自动查找游戏窗口
            config: 可选的截图配置。如果不提供，使用默认配置（只截窗口）
        """
        self.window = window or find_game_window()
        self.config = config or ScreenCaptureConfig()
        self._sct = mss.mss()  # mss 截图库实例

    def _get_capture_region(self, rect: Optional[Rect]) -> dict:
        """计算要截图的区域（屏幕坐标）。
        
        Args:
            rect: 可选的窗口内矩形区域。如果提供，则截取该区域；
                  如果为 None，则根据配置决定截取窗口或全屏
        
        Returns:
            包含 left, top, width, height 的字典，用于 mss.grab()
        """
        if rect is not None:
            # 指定了具体区域，截取该区域
            # 注意：rect 是窗口内坐标，需要转换为屏幕坐标
            left = self.window.left + rect.x
            top = self.window.top + rect.y
            width = rect.width
            height = rect.height
        elif self.config.use_window_rect:
            # 截取整个游戏窗口（屏幕坐标）
            left = self.window.left
            top = self.window.top
            width = self.window.width
            height = self.window.height
        else:
            # 截取整个主屏幕
            mon = self._sct.monitors[1]  # monitors[0] 是所有显示器的合并区域
            left = mon["left"]
            top = mon["top"]
            width = mon["width"]
            height = mon["height"]

        return {"left": left, "top": top, "width": width, "height": height}

    def grab(self, region: Optional[Rect] = None) -> np.ndarray:
        """截取屏幕或窗口区域，返回 BGR 格式的图像数组。
        
        Args:
            region: 可选的窗口内矩形区域。如果为 None，则根据配置截取窗口或全屏
        
        Returns:
            BGR 格式的 numpy 数组，形状为 (height, width, 3)
            可以直接用于 OpenCV 的图像处理操作
        
        Raises:
            ScreenshotError: 如果截图失败
        """
        bbox = self._get_capture_region(region)
        logger.debug("截图区域: %s", bbox)

        try:
            shot = self._sct.grab(bbox)
        except Exception as exc:  # noqa: BLE001
            raise ScreenshotError(f"截图失败: {exc}") from exc

        # mss 返回的是 BGRA 格式（带透明通道）
        img = np.array(shot)
        # 去掉 alpha 通道，转换为 BGR 格式（OpenCV 标准）
        img = img[:, :, :3]
        return img

