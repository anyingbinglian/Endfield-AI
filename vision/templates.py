from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional

import cv2
import numpy as np

from core.logging import get_logger
from core.types import Rect

logger = get_logger(__name__)


@dataclass(frozen=True)
class Template:
    name: str
    path: str
    threshold: float = 0.8
    roi: Optional[Rect] = None  # Region of interest in window coords


class TemplateStore:
    """Manage template definitions and load images on demand."""

    def __init__(self, root_dir: str) -> None:
        self.root_dir = root_dir
        self._templates: Dict[str, Template] = {}

    def register(
        self,
        name: str,
        relative_path: str,
        *,
        threshold: float = 0.8,
        roi: Optional[Rect] = None,
    ) -> None:
        full_path = os.path.join(self.root_dir, relative_path)
        tmpl = Template(name=name, path=full_path, threshold=threshold, roi=roi)
        logger.info("Register template: %s -> %s", name, full_path)
        self._templates[name] = tmpl

    def get(self, name: str) -> Template:
        if name not in self._templates:
            raise KeyError(f"Template not registered: {name}")
        return self._templates[name]

    @staticmethod
    @lru_cache(maxsize=128)
    def load_image(path: str) -> np.ndarray:
        logger.debug("Loading template image: %s", path)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Failed to load template image: {path}")
        return img

