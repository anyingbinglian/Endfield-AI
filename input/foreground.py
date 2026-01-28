from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import pyautogui
import win32gui  # type: ignore

from core.config import WINDOW_CONFIG
from core.logging import get_logger
from core.types import Point
from input.base import InputController, WindowNotFoundError

logger = get_logger(__name__)


@dataclass
class WindowInfo:
    """游戏窗口信息，包含窗口句柄和位置信息。
    
    Attributes:
        handle: Windows 窗口句柄（HWND）
        left: 窗口左边界在屏幕上的 x 坐标
        top: 窗口上边界在屏幕上的 y 坐标
        right: 窗口右边界在屏幕上的 x 坐标
        bottom: 窗口下边界在屏幕上的 y 坐标
    """
    handle: int
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        """窗口宽度（像素）。"""
        return self.right - self.left

    @property
    def height(self) -> int:
        """窗口高度（像素）。"""
        return self.bottom - self.top

    def client_to_screen(self, x: int, y: int) -> Point:
        """将窗口内坐标转换为屏幕坐标。
        
        注意：这是一个简化实现，假设窗口无边框或边框可忽略。
        如果需要更精确的转换，可以使用 GetClientRect + ClientToScreen API。
        
        Args:
            x: 窗口内的 x 坐标
            y: 窗口内的 y 坐标
        
        Returns:
            屏幕坐标 (screen_x, screen_y)
        """
        return self.left + x, self.top + y


def _enum_windows() -> list[WindowInfo]:
    """枚举所有可见的窗口，返回窗口信息列表。
    
    使用 Windows API 遍历所有窗口，只返回可见的、有标题的窗口。
    
    Returns:
        所有可见窗口的信息列表
    """
    windows: list[WindowInfo] = []

    def callback(hwnd, _):
        # 跳过不可见的窗口
        if not win32gui.IsWindowVisible(hwnd):
            return True
        # 跳过无标题的窗口
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
        # 获取窗口矩形区域（屏幕坐标）
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        windows.append(WindowInfo(hwnd, left, top, right, bottom))
        return True

    win32gui.EnumWindows(callback, None)
    return windows


def find_game_window() -> WindowInfo:
    """根据配置的窗口标题查找游戏窗口。
    
    遍历所有可见窗口，匹配标题中包含配置字符串的窗口。
    匹配时不区分大小写。
    
    Returns:
        找到的游戏窗口信息
    
    Raises:
        WindowNotFoundError: 如果找不到匹配的窗口
    """
    candidates = _enum_windows()
    target_titles = set(t.lower() for t in WINDOW_CONFIG.window_titles)

    for win in candidates:
        title = win32gui.GetWindowText(win.handle).lower()
        # 检查窗口标题是否包含任何一个目标标题
        if any(tt in title for tt in target_titles):
            logger.info("找到游戏窗口: %s", win32gui.GetWindowText(win.handle))
            return win

    raise WindowNotFoundError(
        f"无法找到游戏窗口。尝试的标题: {WINDOW_CONFIG.window_titles}"
    )


class ForegroundInput(InputController):
    """前台输入实现，使用 pyautogui 和窗口坐标系统。
    
    前台模式意味着游戏窗口需要有焦点，鼠标和键盘操作会实际移动鼠标和按下按键。
    所有坐标都使用窗口内坐标（0,0 为窗口客户区左上角），底层会自动转换为屏幕坐标。
    
    特点：
    - 实现简单，兼容性好
    - 需要游戏窗口有焦点
    - 会实际移动鼠标，可能影响用户操作
    """

    def __init__(self, window: Optional[WindowInfo] = None) -> None:
        """初始化前台输入控制器。
        
        Args:
            window: 可选的窗口信息。如果不提供，会自动查找游戏窗口
        """
        self.window = window or find_game_window()
        # 禁用 pyautogui 的安全延迟，提高操作速度
        pyautogui.PAUSE = 0.0
        # 启用故障保护（鼠标移到屏幕左上角会触发异常，防止失控）
        pyautogui.FAILSAFE = True

    # ========== 内部辅助方法 ==========

    def _screen_pos(self, x: int, y: int, *, relative: bool) -> Point:
        """将窗口坐标转换为屏幕坐标。
        
        Args:
            x: x 坐标
            y: y 坐标
            relative: 是否为相对移动
        
        Returns:
            屏幕坐标 (screen_x, screen_y)
        """
        if relative:
            # 相对移动时，坐标已经是屏幕坐标系的偏移量
            return x, y
        # 绝对移动时，需要转换为屏幕坐标
        sx, sy = self.window.client_to_screen(x, y)
        return sx, sy

    def _normalize_button(self, button: str) -> str:
        """规范化鼠标按键名称。
        
        Args:
            button: 按键名称（不区分大小写）
        
        Returns:
            规范化后的按键名称（小写）
        
        Raises:
            ValueError: 如果按键名称不支持
        """
        btn = button.lower()
        if btn not in {"left", "right", "middle"}:
            raise ValueError(f"不支持的鼠标按键: {button}")
        return btn

    # ========== InputController 接口实现 ==========

    def move_to(self, x: int, y: int, *, relative: bool = False) -> None:
        """移动鼠标到指定坐标。"""
        sx, sy = self._screen_pos(x, y, relative=relative)
        logger.debug("移动鼠标到: (%s, %s), 相对移动=%s", x, y, relative)
        if relative:
            pyautogui.moveRel(sx, sy, duration=0)
        else:
            pyautogui.moveTo(sx, sy, duration=0)

    def click(self, button: str = "left") -> None:
        """单击鼠标按键。"""
        btn = self._normalize_button(button)
        logger.debug("点击鼠标: 按键=%s", btn)
        pyautogui.click(button=btn)

    def double_click(self, button: str = "left") -> None:
        """双击鼠标按键。"""
        btn = self._normalize_button(button)
        logger.debug("双击鼠标: 按键=%s", btn)
        pyautogui.doubleClick(button=btn)

    def mouse_down(self, button: str = "left") -> None:
        """按下鼠标按键（保持按下状态）。"""
        btn = self._normalize_button(button)
        logger.debug("按下鼠标: 按键=%s", btn)
        pyautogui.mouseDown(button=btn)

    def mouse_up(self, button: str = "left") -> None:
        """释放鼠标按键。"""
        btn = self._normalize_button(button)
        logger.debug("释放鼠标: 按键=%s", btn)
        pyautogui.mouseUp(button=btn)

    def drag_to(self, x: int, y: int, button: str = "left") -> None:
        """拖拽鼠标到目标位置。"""
        btn = self._normalize_button(button)
        sx, sy = self._screen_pos(x, y, relative=False)
        logger.debug("拖拽到: (%s, %s), 按键=%s", x, y, btn)
        pyautogui.dragTo(sx, sy, button=btn, duration=0)

    # ========== 键盘操作 ==========

    def key_down(self, key: str) -> None:
        """按下键盘按键（保持按下状态）。"""
        logger.debug("按下键盘: %s", key)
        pyautogui.keyDown(key)

    def key_up(self, key: str) -> None:
        """释放键盘按键。"""
        logger.debug("释放键盘: %s", key)
        pyautogui.keyUp(key)

    def key_press(self, key: str, duration: float | None = None) -> None:
        """按下并释放键盘按键。
        
        如果指定了 duration，则按下后保持指定时间再释放。
        """
        logger.debug("按下键盘按键: %s, 持续时间=%s", key, duration)
        if duration is None or duration <= 0:
            pyautogui.press(key)
        else:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)

    def sleep(self, seconds: float) -> None:
        """延时等待。"""
        logger.debug("延时等待: %.3f 秒", seconds)
        time.sleep(seconds)

