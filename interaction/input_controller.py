"""Windows 输入控制模块。

基于 Windows 消息（PostMessage）实现鼠标和键盘输入控制。
"""

import ctypes
import time
from typing import Dict

import win32api
import win32con
import win32gui

from core.logging import get_logger
from interaction.window_manager import get_window_handle

logger = get_logger(__name__)


# Windows 虚拟键码映射
VK_CODE: Dict[str, int] = {
    'backspace': 0x08,
    'tab': 0x09,
    'clear': 0x0C,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'pause': 0x13,
    'caps_lock': 0x14,
    'esc': 0x1B,
    'spacebar': 0x20,
    'space': 0x20,  # spacebar 的别名
    'page_up': 0x21,
    'page_down': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left_arrow': 0x25,
    'up_arrow': 0x26,
    'right_arrow': 0x27,
    'down_arrow': 0x28,
    'select': 0x29,
    'print': 0x2A,
    'execute': 0x2B,
    'print_screen': 0x2C,
    'ins': 0x2D,
    'del': 0x2E,
    'help': 0x2F,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'a': 0x41,
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4A,
    'k': 0x4B,
    'l': 0x4C,
    'm': 0x4D,
    'n': 0x4E,
    'o': 0x4F,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5A,
    'numpad_0': 0x60,
    'numpad_1': 0x61,
    'numpad_2': 0x62,
    'numpad_3': 0x63,
    'numpad_4': 0x64,
    'numpad_5': 0x65,
    'numpad_6': 0x66,
    'numpad_7': 0x67,
    'numpad_8': 0x68,
    'numpad_9': 0x69,
    'multiply_key': 0x6A,
    'add_key': 0x6B,
    'separator_key': 0x6C,
    'subtract_key': 0x6D,
    'decimal_key': 0x6E,
    'divide_key': 0x6F,
    'F1': 0x70,
    'F2': 0x71,
    'F3': 0x72,
    'F4': 0x73,
    'F5': 0x74,
    'F6': 0x75,
    'F7': 0x76,
    'F8': 0x77,
    'F9': 0x78,
    'F10': 0x79,
    'F11': 0x7A,
    'F12': 0x7B,
    'num_lock': 0x90,
    'scroll_lock': 0x91,
    'left_shift': 0xA0,
    'right_shift': 0xA1,
    'left_control': 0xA2,
    'right_control': 0xA3,
    'left_menu': 0xA4,
    'right_menu': 0xA5,
    'left_shift': 0xA0,
    'right_shift': 0xA1,
    'left_control': 0xA2,
    'right_control': 0xA3,
    'left_menu': 0xA4,
    'right_menu': 0xA5,
}


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
        if key_lower in VK_CODE:
            return VK_CODE[key_lower]
        
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
