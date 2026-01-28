from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class WindowConfig:
    """Configuration related to the game window."""
    # TODO: Update with actual Endfield window titles when available
    window_titles: List[str] = (
        "Arknights: Endfield",
        "明日方舟：终末地",
    )


WINDOW_CONFIG = WindowConfig()

