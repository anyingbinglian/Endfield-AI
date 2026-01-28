from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from core.logging import get_logger
from core.types import Point, Rect
from vision.templates import Template, TemplateStore

logger = get_logger(__name__)


@dataclass
class MatchResult:
    score: float
    rect: Rect
    center: Point


class TemplateMatcher:
    """Simple template matching wrapper based on OpenCV."""

    def __init__(self, store: TemplateStore) -> None:
        self.store = store

    def match(
        self,
        screen: np.ndarray,
        template: Template,
    ) -> Optional[MatchResult]:
        """Return best match result if above threshold, else None."""
        screen_img = screen.copy()

        # If ROI is defined, crop screen first
        if template.roi is not None:
            x, y, r, b = template.roi.to_tuple()
            screen_img = screen_img[y:b, x:r]

        tmpl_img = self.store.load_image(template.path)

        if screen_img.shape[0] < tmpl_img.shape[0] or screen_img.shape[1] < tmpl_img.shape[1]:
            logger.debug("Screen smaller than template for %s, skipping", template.name)
            return None

        res = cv2.matchTemplate(screen_img, tmpl_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        logger.debug("Template '%s' matched score=%.4f", template.name, max_val)

        if max_val < template.threshold:
            return None

        top_left = max_loc
        h, w = tmpl_img.shape[:2]
        # In roi case, add offset
        offset_x = template.roi.x if template.roi is not None else 0
        offset_y = template.roi.y if template.roi is not None else 0

        left = top_left[0] + offset_x
        top = top_left[1] + offset_y
        rect = Rect(x=left, y=top, width=w, height=h)
        center: Point = (left + w // 2, top + h // 2)

        return MatchResult(score=max_val, rect=rect, center=center)

    def exists(self, screen: np.ndarray, template: Template) -> bool:
        return self.match(screen, template) is not None

