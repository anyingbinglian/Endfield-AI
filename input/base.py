from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class InputController(Protocol):
    """Abstract input interface for mouse & keyboard operations."""

    # Mouse operations

    def move_to(self, x: int, y: int, *, relative: bool = False) -> None:
        """Move mouse to (x, y) in window coordinates, or relative if specified."""
        ...

    def click(self, button: str = "left") -> None:
        """Click mouse button once."""
        ...

    def double_click(self, button: str = "left") -> None:
        """Double click mouse button."""
        ...

    def mouse_down(self, button: str = "left") -> None:
        """Press and hold mouse button."""
        ...

    def mouse_up(self, button: str = "left") -> None:
        """Release mouse button."""
        ...

    def drag_to(self, x: int, y: int, button: str = "left") -> None:
        """Drag from current position to (x, y)."""
        ...

    # Keyboard operations

    def key_down(self, key: str) -> None:
        """Press and hold a key. Example: 'w', 'space', 'esc'."""
        ...

    def key_up(self, key: str) -> None:
        """Release a key."""
        ...

    def key_press(self, key: str, duration: float | None = None) -> None:
        """Press a key with optional duration (hold then release)."""
        ...

    # Misc

    def sleep(self, seconds: float) -> None:
        """Sleep helper to centralize timing and logging if needed."""
        ...


class WindowNotFoundError(RuntimeError):
    """Raised when the game window cannot be located."""
    pass

