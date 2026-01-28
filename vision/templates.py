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
    """UI 模板定义，用于模板匹配。
    
    模板是一张小的图片，用于在游戏截图中查找匹配的 UI 元素
    （如按钮、图标、文字等）。
    
    Attributes:
        name: 模板的唯一名称，用于标识和查找
        path: 模板图片文件的完整路径
        threshold: 匹配阈值（0.0-1.0），只有相似度 >= threshold 才算匹配成功
                   默认 0.8，表示 80% 相似度
        roi: 可选的感兴趣区域（Region of Interest），限制搜索范围
             如果指定，只在窗口的这个区域内搜索模板
             如果为 None，在整个窗口内搜索
    """
    name: str
    path: str
    threshold: float = 0.8
    roi: Optional[Rect] = None


class TemplateStore:
    """模板管理器，负责注册、存储和加载 UI 模板图片。
    
    模板图片应该放在一个统一的目录下（如 templates/），
    通过 register() 方法注册模板，系统会自动管理模板的加载和缓存。
    
    使用示例：
        store = TemplateStore("templates/")
        store.register("start_button", "ui/start.png", threshold=0.85)
        template = store.get("start_button")
    """

    def __init__(self, root_dir: str) -> None:
        """初始化模板管理器。
        
        Args:
            root_dir: 模板图片的根目录路径（相对或绝对路径）
        """
        self.root_dir = root_dir
        self._templates: Dict[str, Template] = {}  # 模板名称 -> Template 对象

    def register(
        self,
        name: str,
        relative_path: str,
        *,
        threshold: float = 0.8,
        roi: Optional[Rect] = None,
    ) -> None:
        """注册一个模板。
        
        Args:
            name: 模板的唯一名称
            relative_path: 相对于 root_dir 的图片路径，如 "ui/start.png"
            threshold: 匹配阈值（0.0-1.0），默认 0.8
            roi: 可选的搜索区域限制
        
        Example:
            store.register("login_button", "ui/login.png", threshold=0.9)
        """
        full_path = os.path.join(self.root_dir, relative_path)
        tmpl = Template(name=name, path=full_path, threshold=threshold, roi=roi)
        logger.info("注册模板: %s -> %s", name, full_path)
        self._templates[name] = tmpl

    def get(self, name: str) -> Template:
        """根据名称获取模板。
        
        Args:
            name: 模板名称
        
        Returns:
            Template 对象
        
        Raises:
            KeyError: 如果模板未注册
        """
        if name not in self._templates:
            raise KeyError(f"模板未注册: {name}")
        return self._templates[name]

    @staticmethod
    @lru_cache(maxsize=128)
    def load_image(path: str) -> np.ndarray:
        """加载模板图片，使用 LRU 缓存提高性能。
        
        相同的图片路径只会加载一次，后续直接从缓存读取。
        缓存最多保存 128 张图片，超出后自动淘汰最久未使用的。
        
        Args:
            path: 图片文件的完整路径
        
        Returns:
            BGR 格式的 numpy 数组
        
        Raises:
            FileNotFoundError: 如果图片文件不存在或无法读取
        """
        logger.debug("加载模板图片: %s", path)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"无法加载模板图片: {path}")
        return img

