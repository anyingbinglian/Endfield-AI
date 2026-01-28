from __future__ import annotations

from core.logging import get_logger
from input.base import InputController

logger = get_logger(__name__)


class BackgroundInput(InputController):
    """Placeholder background implementation.

    Currently forwards to foreground-like behavior via NotImplementedError.
    You can later plug in DM or message-based input here.
    """

    def _not_implemented(self) -> None:
        raise NotImplementedError(
            "BackgroundInput is not implemented yet. "
            "Use ForegroundInput or implement a backend here."
        )

    def move_to(self, x: int, y: int, *, relative: bool = False) -> None:
        self._not_implemented()

    def click(self, button: str = "left") -> None:
        self._not_implemented()

    def double_click(self, button: str = "left") -> None:
        self._not_implemented()

    def mouse_down(self, button: str = "left") -> None:
        self._not_implemented()

    def mouse_up(self, button: str = "left") -> None:
        self._not_implemented()

    def drag_to(self, x: int, y: int, button: str = "left") -> None:
        self._not_implemented()

    def key_down(self, key: str) -> None:
        self._not_implemented()

    def key_up(self, key: str) -> None:
        self._not_implemented()

    def key_press(self, key: str, duration: float | None = None) -> None:
        self._not_implemented()

    def sleep(self, seconds: float) -> None:
        self._not_implemented()

