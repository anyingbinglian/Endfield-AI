"""Windows 前台输入控制模块。

基于 pyautogui 和 pydirectinput 实现鼠标和键盘输入控制。
适用于前台操作，直接控制物理鼠标和键盘。
"""

import time

import pyautogui
import pydirectinput
import win32api
import win32con
import win32gui

from core.logging import get_logger
from interaction.window_manager import get_window_handle

logger = get_logger(__name__)


class InteractionFront:
    """Windows 前台输入控制器。
    
    使用 pyautogui 和 pydirectinput 实现鼠标和键盘输入。
    所有操作都是针对前台窗口的，直接控制物理鼠标和键盘。
    """

    def __init__(self, is_borderless_window: bool = False):
        """初始化输入控制器。
        
        Args:
            is_borderless_window: 如果为 True，表示窗口是无边框窗口
        """
        self.is_borderless_window = is_borderless_window
        self.DEBUG_MODE = False
        self.CONSOLE_ONLY = False

    def _fix_xy(self, x: int, y: int, is_borderless_window: bool = None) -> tuple[int, int]:
        """将窗口内坐标转换为屏幕坐标。
        
        Args:
            x: 窗口内 x 坐标
            y: 窗口内 y 坐标
            is_borderless_window: 是否无边框窗口，如果为 None 则使用实例属性
            
        Returns:
            (screen_x, screen_y) 屏幕坐标
        """
        handle = get_window_handle()
        wx, wy, w, h = win32gui.GetWindowRect(handle)
        screen_x = x + wx
        
        # 使用传入参数或实例属性
        borderless = is_borderless_window if is_borderless_window is not None else self.is_borderless_window
        
        if borderless:
            screen_y = y + wy
        else:
            # 有边框窗口需要考虑标题栏高度（约26-31像素）
            screen_y = y + wy + 26
        
        return screen_x, screen_y

    # ========== 鼠标操作 ==========

    def left_click(self) -> None:
        """左键单击。"""
        if not self.CONSOLE_ONLY:
            pyautogui.leftClick()

    def left_down(self) -> None:
        """按下左键（保持按下状态）。"""
        if not self.CONSOLE_ONLY:
            pyautogui.mouseDown(button='left')

    def left_up(self) -> None:
        """释放左键。"""
        if not self.CONSOLE_ONLY:
            pyautogui.mouseUp(button='left')

    def left_double_click(self, dt: float = 0.05) -> None:
        """左键双击。
        
        Args:
            dt: 两次点击之间的间隔时间（秒），默认 0.05（此参数在此实现中不使用）
        """
        if not self.CONSOLE_ONLY:
            pyautogui.doubleClick()

    def right_click(self) -> None:
        """右键单击。"""
        if not self.CONSOLE_ONLY:
            pyautogui.rightClick()

    def middle_click(self) -> None:
        """中键单击。"""
        if not self.CONSOLE_ONLY:
            pyautogui.click(button='middle')

    def move_to(self, x: int, y: int, relative: bool = False, is_borderless_window: bool = False) -> None:
        """移动鼠标到指定坐标。
        
        Args:
            x: 目标 x 坐标（窗口内坐标）
            y: 目标 y 坐标（窗口内坐标）
            relative: 如果为 True，则相对于当前位置移动
            is_borderless_window: 如果为 True，表示窗口是无边框窗口
        """
        x = int(x)
        y = int(y)

        if relative:
            # 相对移动
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y)
        else:
            # 绝对移动：需要转换为屏幕坐标
            # 使用传入的参数（如果提供）或实例属性
            borderless = is_borderless_window if is_borderless_window else self.is_borderless_window
            screen_x, screen_y = self._fix_xy(x, y, is_borderless_window=borderless)
            
            # 使用 pydirectinput 移动鼠标（更可靠）
            pydirectinput.moveTo(screen_x, screen_y)
            # 也可以使用 win32api.SetCursorPos((screen_x, screen_y))

    # ========== 键盘操作 ==========

    def key_down(self, key: str) -> None:
        """按下键盘按键（保持按下状态）。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        if not self.CONSOLE_ONLY:
            pyautogui.keyDown(key)

    def key_up(self, key: str) -> None:
        """释放键盘按键。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        if not self.CONSOLE_ONLY:
            pyautogui.keyUp(key)

    def key_press(self, key: str) -> None:
        """按下并释放键盘按键（完整的按键操作）。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        if not self.CONSOLE_ONLY:
            pyautogui.press(key)

