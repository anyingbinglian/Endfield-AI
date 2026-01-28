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
    handle: int
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def client_to_screen(self, x: int, y: int) -> Point:
        """Convert window-client coordinates to screen coordinates."""
        # Simple assumption: no border or border can be ignored
        # For more precision, use GetClientRect + ClientToScreen
        return self.left + x, self.top + y


def _enum_windows() -> list[WindowInfo]:
    windows: list[WindowInfo] = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        windows.append(WindowInfo(hwnd, left, top, right, bottom))
        return True

    win32gui.EnumWindows(callback, None)
    return windows


def find_game_window() -> WindowInfo:
    """Find the game window by known titles."""
    candidates = _enum_windows()
    target_titles = set(t.lower() for t in WINDOW_CONFIG.window_titles)

    for win in candidates:
        title = win32gui.GetWindowText(win.handle).lower()
        if any(tt in title for tt in target_titles):
            logger.info("Found game window: %s", win32gui.GetWindowText(win.handle))
            return win

    raise WindowNotFoundError(
        f"Could not find game window. Tried titles: {WINDOW_CONFIG.window_titles}"
    )


class ForegroundInput(InputController):
    """Foreground implementation using pyautogui and window coordinates."""

    def __init__(self, window: Optional[WindowInfo] = None) -> None:
        self.window = window or find_game_window()
        # Disable pyautogui safety delays
        pyautogui.PAUSE = 0.0
        pyautogui.FAILSAFE = True

    # --- internal helpers ---

    def _screen_pos(self, x: int, y: int, *, relative: bool) -> Point:
        if relative:
            # Relative move is in screen coordinates for pyautogui
            return x, y
        sx, sy = self.window.client_to_screen(x, y)
        return sx, sy

    def _normalize_button(self, button: str) -> str:
        btn = button.lower()
        if btn not in {"left", "right", "middle"}:
            raise ValueError(f"Unsupported mouse button: {button}")
        return btn

    # --- InputController implementation ---

    def move_to(self, x: int, y: int, *, relative: bool = False) -> None:
        sx, sy = self._screen_pos(x, y, relative=relative)
        logger.debug("move_to: (%s, %s), relative=%s", x, y, relative)
        if relative:
            pyautogui.moveRel(sx, sy, duration=0)
        else:
            pyautogui.moveTo(sx, sy, duration=0)

    def click(self, button: str = "left") -> None:
        btn = self._normalize_button(button)
        logger.debug("click: button=%s", btn)
        pyautogui.click(button=btn)

    def double_click(self, button: str = "left") -> None:
        btn = self._normalize_button(button)
        logger.debug("double_click: button=%s", btn)
        pyautogui.doubleClick(button=btn)

    def mouse_down(self, button: str = "left") -> None:
        btn = self._normalize_button(button)
        logger.debug("mouse_down: button=%s", btn)
        pyautogui.mouseDown(button=btn)

    def mouse_up(self, button: str = "left") -> None:
        btn = self._normalize_button(button)
        logger.debug("mouse_up: button=%s", btn)
        pyautogui.mouseUp(button=btn)

    def drag_to(self, x: int, y: int, button: str = "left") -> None:
        btn = self._normalize_button(button)
        sx, sy = self._screen_pos(x, y, relative=False)
        logger.debug("drag_to: (%s, %s), button=%s", x, y, btn)
        pyautogui.dragTo(sx, sy, button=btn, duration=0)

    # Keyboard

    def key_down(self, key: str) -> None:
        logger.debug("key_down: %s", key)
        pyautogui.keyDown(key)

    def key_up(self, key: str) -> None:
        logger.debug("key_up: %s", key)
        pyautogui.keyUp(key)

    def key_press(self, key: str, duration: float | None = None) -> None:
        logger.debug("key_press: %s, duration=%s", key, duration)
        if duration is None or duration <= 0:
            pyautogui.press(key)
        else:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)

    def sleep(self, seconds: float) -> None:
        logger.debug("sleep: %.3fs", seconds)
        time.sleep(seconds)

