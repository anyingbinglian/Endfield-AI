from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

Point = Tuple[int, int]  # (x, y)


@dataclass(frozen=True)
class Rect:
    """Axis-aligned rectangle in window coordinates."""
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Return (left, top, right, bottom)."""
        return self.x, self.y, self.right, self.bottom

