"""Windows 截图实现模块。

基于 Windows API 实现窗口截图功能，支持截图缓存以提高性能。
"""

import ctypes
import threading
import time
from ctypes import wintypes
from typing import Optional

import numpy as np
import win32print

from core.logging import get_logger
from core.types import Rect
from interaction.window_manager import get_window_handle, refresh_window_handle

logger = get_logger(__name__)


class CaptureError(RuntimeError):
    """截图操作失败时抛出的异常。"""
    pass


class WindowsCapture:
    """Windows 窗口截图工具。
    
    使用 Windows API 进行窗口客户区截图，支持截图缓存以提高性能。
    默认支持 1920x1080 分辨率。
    """

    # Windows API 函数
    GetDC = ctypes.windll.user32.GetDC
    CreateCompatibleDC = ctypes.windll.gdi32.CreateCompatibleDC
    GetClientRect = ctypes.windll.user32.GetClientRect
    CreateCompatibleBitmap = ctypes.windll.gdi32.CreateCompatibleBitmap
    SelectObject = ctypes.windll.gdi32.SelectObject
    BitBlt = ctypes.windll.gdi32.BitBlt
    SRCCOPY = 0x00CC0020
    GetBitmapBits = ctypes.windll.gdi32.GetBitmapBits
    DeleteObject = ctypes.windll.gdi32.DeleteObject
    ReleaseDC = ctypes.windll.user32.ReleaseDC
    GetDeviceCaps = win32print.GetDeviceCaps

    def __init__(self, max_fps: int = 30, force_1920x1080: bool = True):
        """初始化 Windows 截图工具。
        
        Args:
            max_fps: 最大截图帧率，默认 30 FPS
            force_1920x1080: 是否强制限制截图为 1920x1080 分辨率，默认 True
        """
        self.max_fps = max_fps
        self.force_1920x1080 = force_1920x1080
        self._capture_cache: np.ndarray = np.zeros((1080, 1920, 4), dtype=np.uint8)
        self._capture_cache_lock = threading.Lock()
        self._last_capture_time = 0.0
        self._fps_timer = 0.0

    def _check_shape(self, img: np.ndarray) -> bool:
        """检查截图尺寸是否正确。
        
        Args:
            img: 截图图像数组
            
        Returns:
            如果尺寸正确返回 True，否则返回 False
        """
        if img is None:
            return False
        # 如果启用了分辨率限制，检查是否为 1920x1080（4通道BGRA）
        if self.force_1920x1080:
            if img.shape == (1080, 1920, 4):
                return True
            return False
        else:
            # 未启用限制时，只要形状有效（3维，最后一维为4）即可
            if len(img.shape) == 3 and img.shape[2] == 4:
                return True
            return False

    def _get_capture(self) -> np.ndarray:
        """执行实际的截图操作。
        
        Returns:
            截图图像数组（BGRA格式）
            如果 force_1920x1080 为 True，形状为 (1080, 1920, 4)
            否则使用实际窗口尺寸
            
        Raises:
            CaptureError: 如果截图失败
        """
        try:
            handle = get_window_handle()
        except Exception as e:
            logger.warning(f"获取窗口句柄失败: {e}")
            refresh_window_handle()
            handle = get_window_handle()

        # 获取窗口客户区尺寸
        rect = wintypes.RECT()
        self.GetClientRect(handle, ctypes.byref(rect))
        width, height = rect.right, rect.bottom

        # 如果启用了分辨率限制，强制使用 1920x1080
        if self.force_1920x1080:
            # 处理缩放情况（如果检测到缩放，强制使用 1920x1080）
            if height in [int(1080 / scale) for scale in [0.75, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]]:
                logger.debug(f"检测到窗口缩放，使用标准分辨率 1920x1080")
                width = 1920
                height = 1080
            else:
                # 直接强制使用 1920x1080
                width = 1920
                height = 1080

        # 开始截图
        dc = self.GetDC(handle)
        if dc == 0:
            raise CaptureError("无法获取设备上下文")
        
        try:
            cdc = self.CreateCompatibleDC(dc)
            bitmap = self.CreateCompatibleBitmap(dc, width, height)
            self.SelectObject(cdc, bitmap)
            self.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, self.SRCCOPY)

            # 读取位图数据
            total_bytes = width * height * 4
            buffer = bytearray(total_bytes)
            byte_array = ctypes.c_ubyte * total_bytes
            self.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

            # 清理资源
            self.DeleteObject(bitmap)
            self.DeleteObject(cdc)
        finally:
            self.ReleaseDC(handle, dc)

        # 转换为 numpy 数组（BGRA格式）
        img = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
        return img

    def capture(self, recapture_limit: float = 0.0) -> np.ndarray:
        """截取窗口图像。
        
        如果距离上次截图时间小于 recapture_limit 秒，则返回缓存的截图。
        否则执行新的截图操作。
        
        Args:
            recapture_limit: 截图缓存时间限制（秒），默认 0.0（不使用缓存）
            
        Returns:
            截图图像数组（BGRA格式）
            如果 force_1920x1080 为 True，形状为 (1080, 1920, 4)
            否则使用实际窗口尺寸
            
        Raises:
            CaptureError: 如果截图失败
        """
        current_time = time.time()
        
        # 检查是否需要重新截图
        if recapture_limit > 0.0 and (current_time - self._last_capture_time) < recapture_limit:
            # 使用缓存
            self._capture_cache_lock.acquire()
            try:
                return self._capture_cache.copy()
            finally:
                self._capture_cache_lock.release()
        
        # 检查帧率限制
        time_since_last = current_time - self._fps_timer
        min_interval = 1.0 / self.max_fps
        
        if time_since_last < min_interval:
            # 帧率限制，返回缓存
            self._capture_cache_lock.acquire()
            try:
                return self._capture_cache.copy()
            finally:
                self._capture_cache_lock.release()

        # 执行截图
        self._fps_timer = current_time
        
        # 重试机制：如果截图失败，尝试刷新句柄后重试
        max_retries = 3
        for attempt in range(max_retries):
            try:
                img = self._get_capture()
                
                # 检查截图尺寸
                if not self._check_shape(img):
                    if attempt < max_retries - 1:
                        logger.warning(f"截图尺寸不正确: {img.shape}，尝试刷新窗口句柄...")
                        refresh_window_handle()
                        time.sleep(0.1)
                        continue
                    else:
                        raise CaptureError(f"截图尺寸不正确: {img.shape}")
                
                # 更新缓存
                self._capture_cache_lock.acquire()
                try:
                    self._capture_cache = img.copy()
                    self._last_capture_time = current_time
                finally:
                    self._capture_cache_lock.release()
                
                return img
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"截图失败（尝试 {attempt + 1}/{max_retries}）: {e}")
                    refresh_window_handle()
                    time.sleep(0.5)
                else:
                    raise CaptureError(f"截图失败: {e}") from e
        
        # 理论上不会到达这里
        raise CaptureError("截图失败：未知错误")
