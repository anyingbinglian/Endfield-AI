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
    use_window_rect: bool = True  # True: capture only game window, False: full screen


class ScreenshotError(RuntimeError):
    pass


class ScreenCapture:
    """Screen capture utility based on mss.

    By default captures the game window only (client area).
    """

    def __init__(
        self,
        window: Optional[WindowInfo] = None,
        config: Optional[ScreenCaptureConfig] = None,
    ) -> None:
        self.window = window or find_game_window()
        self.config = config or ScreenCaptureConfig()
        self._sct = mss.mss()

    def _get_capture_region(self, rect: Optional[Rect]) -> dict:
        if rect is not None:
            left = rect.x
            top = rect.y
            width = rect.width
            height = rect.height
        elif self.config.use_window_rect:
            # Window rectangle in screen coordinates
            left = self.window.left
            top = self.window.top
            width = self.window.width
            height = self.window.height
        else:
            # Full primary screen
            mon = self._sct.monitors[1]
            left = mon["left"]
            top = mon["top"]
            width = mon["width"]
            height = mon["height"]

        return {"left": left, "top": top, "width": width, "height": height}

    def grab(self, region: Optional[Rect] = None) -> np.ndarray:
        """Capture screen or window region as an RGB image (numpy array)."""
        bbox = self._get_capture_region(region)
        logger.debug("ScreenCapture.grab: %s", bbox)

        try:
            shot = self._sct.grab(bbox)
        except Exception as exc:  # noqa: BLE001
            raise ScreenshotError(f"Failed to capture screen: {exc}") from exc

        img = np.array(shot)  # BGRA
        # Convert BGRA -> BGR
        img = img[:, :, :3]
        return img

