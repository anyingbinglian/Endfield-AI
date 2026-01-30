"""Windows 输入控制模块。

基于 Windows 消息（PostMessage）实现鼠标和键盘输入控制。
"""

import ctypes
import time

import win32api
import win32con
import win32gui

from core.logging import get_logger
from interaction.window_manager import get_window_handle
from common import vkcode

logger = get_logger(__name__)


class InteractionNormal:
    """Windows 前台输入控制器。
    
    使用 Windows 消息（PostMessage）实现鼠标和键盘输入。
    所有操作都是针对游戏窗口的。
    """

    # Windows 消息常量
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_MOUSEWHEEL = 0x020A
    WM_RBUTTONDOWN = 0x0204
    WM_RBUTTONDBLCLK = 0x0206
    WM_RBUTTONUP = 0x0205
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101

    # Windows API 函数
    PostMessageW = ctypes.windll.user32.PostMessageW
    MapVirtualKeyW = ctypes.windll.user32.MapVirtualKeyW

    def __init__(self):
        """初始化输入控制器。"""
        self.VK_CODE = vkcode.VK_CODE
        self.WHEEL_DELTA = 120
        self.DEFAULT_DELAY_TIME = 0.05
        self.DEBUG_MODE = False
        self.CONSOLE_ONLY = False

    def _get_virtual_keycode(self, key: str) -> int:
        """获取虚拟键码。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
            
        Returns:
            虚拟键码
            
        Raises:
            ValueError: 如果按键名称不支持
        """
        key_lower = key.lower()
        if key_lower in self.VK_CODE:
            return self.VK_CODE[key_lower]
        
        # 尝试直接转换单个字符
        if len(key) == 1:
            vk_code = ctypes.windll.user32.VkKeyScanA(ord(key.lower()))
            if vk_code != -1:
                return vk_code & 0xFF
        
        raise ValueError(f"不支持的按键: {key}")

    # ========== 鼠标操作 ==========

    def left_click(self) -> None:
        """左键单击。"""
        if self.CONSOLE_ONLY:
            return
        
        handle = get_window_handle()
        wparam = 0
        lparam = 0 << 16 | 0
        
        self.PostMessageW(handle, self.WM_LBUTTONDOWN, wparam, lparam)
        time.sleep(0.06)
        self.PostMessageW(handle, self.WM_LBUTTONUP, wparam, lparam)

    def left_down(self) -> None:
        """按下左键（保持按下状态）。"""
        if self.CONSOLE_ONLY:
            return
        
        handle = get_window_handle()
        wparam = 0
        lparam = 0 << 16 | 0
        
        # 发送多次按下消息以确保稳定
        for _ in range(3):
            self.PostMessageW(handle, self.WM_LBUTTONDOWN, wparam, lparam)
            time.sleep(0.01)

    def left_up(self) -> None:
        """释放左键。"""
        if self.CONSOLE_ONLY:
            return
        
        handle = get_window_handle()
        wparam = 0
        lparam = 0 << 16 | 0
        
        # 发送多次释放消息以确保稳定
        for _ in range(3):
            self.PostMessageW(handle, self.WM_LBUTTONUP, wparam, lparam)
            time.sleep(0.01)

    def left_double_click(self, dt: float = 0.05) -> None:
        """左键双击。
        
        Args:
            dt: 两次点击之间的间隔时间（秒），默认 0.05
        """
        self.left_click()
        time.sleep(dt)
        self.left_click()

    def right_click(self) -> None:
        """右键单击。"""
        if self.CONSOLE_ONLY:
            return
        
        handle = get_window_handle()
        wparam = 0
        lparam = 0 << 16 | 0
        
        self.PostMessageW(handle, self.WM_RBUTTONDOWN, wparam, lparam)
        time.sleep(0.06)
        self.PostMessageW(handle, self.WM_RBUTTONUP, wparam, lparam)

    def middle_click(self) -> None:
        """中键单击。
        
        注意：中键使用 pyautogui 实现，因为 Windows 消息对中键支持有限。
        """
        import pyautogui
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
            handle = get_window_handle()
            wx, wy, _, _ = win32gui.GetWindowRect(handle)
            screen_x = x + wx
            
            if is_borderless_window:
                screen_y = y + wy
            else:
                # 有边框窗口需要考虑标题栏高度（约26像素）
                screen_y = y + wy + 26
            
            win32api.SetCursorPos((screen_x, screen_y))

    # ========== 键盘操作 ==========

    def key_down(self, key: str) -> None:
        """按下键盘按键（保持按下状态）。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        if self.CONSOLE_ONLY:
            return
        
        try:
            vk_code = self._get_virtual_keycode(key)
            scan_code = self.MapVirtualKeyW(vk_code, 0)
            wparam = vk_code
            lparam = (scan_code << 16) | 1
            
            handle = get_window_handle()
            self.PostMessageW(handle, self.WM_KEYDOWN, wparam, lparam)
        except ValueError as e:
            logger.error(f"按键按下失败: {e}")

    def key_up(self, key: str) -> None:
        """释放键盘按键。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        if self.CONSOLE_ONLY:
            return
        
        try:
            vk_code = self._get_virtual_keycode(key)
            scan_code = self.MapVirtualKeyW(vk_code, 0)
            wparam = vk_code
            # WM_KEYUP 的 lparam 格式：scan_code << 16 | 0xC0000001
            lparam = (scan_code << 16) | 0xC0000001
            
            handle = get_window_handle()
            self.PostMessageW(handle, self.WM_KEYUP, wparam, lparam)
        except ValueError as e:
            logger.error(f"按键释放失败: {e}")

    def key_press(self, key: str) -> None:
        """按下并释放键盘按键（完整的按键操作）。
        
        Args:
            key: 按键名称（如 'w', 'space', 'esc'）
        """
        if self.CONSOLE_ONLY:
            return
        
        try:
            vk_code = self._get_virtual_keycode(key)
            scan_code = self.MapVirtualKeyW(vk_code, 0)
            wparam = vk_code
            
            # 按下
            lparam_down = (scan_code << 16) | 1
            # 释放
            lparam_up = (scan_code << 16) | 0xC0000001
            
            handle = get_window_handle()
            self.PostMessageW(handle, self.WM_KEYDOWN, wparam, lparam_down)
            time.sleep(0.05)
            self.PostMessageW(handle, self.WM_KEYUP, wparam, lparam_up)
        except ValueError as e:
            logger.error(f"按键操作失败: {e}")

