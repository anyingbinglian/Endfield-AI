from __future__ import annotations

import time
from typing import Optional

import numpy as np

from core.logging import get_logger
from core.types import Rect
from input.base import InputController
from input.screenshot import ScreenCapture
from vision.matching import TemplateMatcher, MatchResult
from vision.templates import TemplateStore

logger = get_logger(__name__)


class MatchTimeoutError(RuntimeError):
    pass


class UiDetectors:
    """High-level UI detection helpers based on screenshot + template matching."""

    def __init__(
        self,
        screen_capture: ScreenCapture,
        matcher: TemplateMatcher,
        store: TemplateStore,
        input_ctrl: InputController,
    ) -> None:
        self.screen_capture = screen_capture
        self.matcher = matcher
        self.store = store
        self.input_ctrl = input_ctrl

    def _current_screen(self, region: Optional[Rect] = None) -> np.ndarray:
        return self.screen_capture.grab(region)

    def wait_for(
        self,
        template_name: str,
        timeout: float = 10.0,
        interval: float = 0.3,
    ) -> MatchResult:
        """Wait until a template appears or timeout.

        Raises MatchTimeoutError if not found.
        """
        template = self.store.get(template_name)
        end_time = time.time() + timeout

        while True:
            screen = self._current_screen()
            result = self.matcher.match(screen, template)
            if result is not None:
                logger.info("Template '%s' appeared with score=%.3f", template_name, result.score)
                return result

            if time.time() > end_time:
                raise MatchTimeoutError(f"Timeout waiting for template '{template_name}'")

            self.input_ctrl.sleep(interval)

    def click_if_exists(
        self,
        template_name: str,
        *,
        button: str = "left",
        threshold_override: Optional[float] = None,
    ) -> bool:
        """If template exists on current screen, click its center and return True."""
        template = self.store.get(template_name)
        screen = self._current_screen()
        result = self.matcher.match(screen, template)
        if result is None:
            return False

        if threshold_override is not None and result.score < threshold_override:
            return False

        x, y = result.center
        logger.info("click_if_exists: %s at (%s,%s), score=%.3f", template_name, x, y, result.score)
        self.input_ctrl.move_to(x, y)
        self.input_ctrl.click(button=button)
        return True

