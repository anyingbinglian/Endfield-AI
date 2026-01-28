"""窗口句柄管理模块。

负责查找和管理游戏窗口句柄。
"""

import ctypes
import win32gui
from typing import Optional

from core.config import WINDOW_CONFIG
from core.logging import get_logger

logger = get_logger(__name__)


class WindowNotFoundError(RuntimeError):
    """当无法找到游戏窗口时抛出的异常。"""
    pass


class WindowHandleManager:
    """窗口句柄管理器。
    
    负责查找和管理游戏窗口句柄，提供窗口句柄的获取和刷新功能。
    """

    def __init__(self):
        """初始化窗口句柄管理器。"""
        self._handle: Optional[int] = None
        self._refresh_handle()

    def _find_window_by_title(self) -> Optional[int]:
        """根据窗口标题查找游戏窗口。
        
        Returns:
            窗口句柄，如果未找到则返回 None
        """
        target_titles = [title.lower() for title in WINDOW_CONFIG.window_titles]
        
        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            
            title = win32gui.GetWindowText(hwnd).lower()
            if any(target_title in title for target_title in target_titles):
                # 找到匹配的窗口，保存句柄
                nonlocal found_handle
                found_handle = hwnd
                return False  # 停止枚举
            return True
        
        found_handle = None
        win32gui.EnumWindows(callback, None)
        
        if found_handle:
            window_title = win32gui.GetWindowText(found_handle)
            logger.info(f"找到游戏窗口: {window_title} (句柄: {found_handle})")
        
        return found_handle

    def _refresh_handle(self) -> None:
        """刷新窗口句柄。"""
        handle = self._find_window_by_title()
        if handle is None:
            raise WindowNotFoundError(
                f"无法找到游戏窗口。尝试的标题: {WINDOW_CONFIG.window_titles}"
            )
        self._handle = handle

    def get_handle(self) -> int:
        """获取当前窗口句柄。
        
        Returns:
            窗口句柄
            
        Raises:
            WindowNotFoundError: 如果窗口未找到
        """
        if self._handle is None or not win32gui.IsWindow(self._handle):
            logger.warning("窗口句柄无效，尝试刷新...")
            self._refresh_handle()
        return self._handle

    def refresh_handle(self) -> None:
        """手动刷新窗口句柄。
        
        当窗口可能已关闭或重新打开时调用此方法。
        """
        self._refresh_handle()


# 全局窗口句柄管理器实例
_window_handle_manager = WindowHandleManager()


def get_window_handle() -> int:
    """获取游戏窗口句柄。
    
    Returns:
        窗口句柄
        
    Raises:
        WindowNotFoundError: 如果窗口未找到
    """
    return _window_handle_manager.get_handle()


def refresh_window_handle() -> None:
    """刷新游戏窗口句柄。"""
    _window_handle_manager.refresh_handle()
