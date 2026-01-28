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
    """等待模板出现超时时抛出的异常。
    
    当 wait_for() 方法在指定时间内未找到模板时抛出。
    """
    pass


class UiDetectors:
    """高级 UI 检测工具，结合截图和模板匹配提供便捷的操作接口。
    
    这个类封装了常见的 UI 检测和操作模式，例如：
    - 等待某个 UI 元素出现
    - 检测并点击按钮
    
    使用示例：
        detectors = UiDetectors(screen, matcher, store, input_ctrl)
        detectors.wait_for("loading_screen", timeout=5.0)
        if detectors.click_if_exists("start_button"):
            print("点击了开始按钮")
    """

    def __init__(
        self,
        screen_capture: ScreenCapture,
        matcher: TemplateMatcher,
        store: TemplateStore,
        input_ctrl: InputController,
    ) -> None:
        """初始化 UI 检测器。
        
        Args:
            screen_capture: 截图工具实例
            matcher: 模板匹配器实例
            store: 模板管理器实例
            input_ctrl: 输入控制器实例（用于点击等操作）
        """
        self.screen_capture = screen_capture
        self.matcher = matcher
        self.store = store
        self.input_ctrl = input_ctrl

    def _current_screen(self, region: Optional[Rect] = None) -> np.ndarray:
        """获取当前屏幕截图。
        
        Args:
            region: 可选的截图区域限制
        
        Returns:
            当前屏幕的截图（BGR 格式）
        """
        return self.screen_capture.grab(region)

    def wait_for(
        self,
        template_name: str,
        timeout: float = 10.0,
        interval: float = 0.3,
    ) -> MatchResult:
        """等待指定的模板出现，直到超时。
        
        这个方法会不断截图并尝试匹配模板，直到找到匹配或超时。
        适用于等待加载界面、等待按钮出现等场景。
        
        Args:
            template_name: 要等待的模板名称（必须已注册）
            timeout: 超时时间（秒），默认 10 秒
            interval: 每次检查的间隔时间（秒），默认 0.3 秒
                     间隔太短会增加 CPU 负担，太长会降低响应速度
        
        Returns:
            匹配结果对象，包含匹配位置和相似度
        
        Raises:
            MatchTimeoutError: 如果超时仍未找到模板
            KeyError: 如果模板名称未注册
        
        Example:
            # 等待加载界面消失
            try:
                result = detectors.wait_for("game_ui", timeout=15.0)
                print(f"游戏界面出现，相似度: {result.score}")
            except MatchTimeoutError:
                print("等待超时")
        """
        template = self.store.get(template_name)
        end_time = time.time() + timeout

        while True:
            # 截图并尝试匹配
            screen = self._current_screen()
            result = self.matcher.match(screen, template)
            
            if result is not None:
                logger.info("模板 '%s' 出现，相似度=%.3f", template_name, result.score)
                return result

            # 检查是否超时
            if time.time() > end_time:
                raise MatchTimeoutError(f"等待模板 '{template_name}' 超时")

            # 等待一段时间后再次检查
            self.input_ctrl.sleep(interval)

    def click_if_exists(
        self,
        template_name: str,
        *,
        button: str = "left",
        threshold_override: Optional[float] = None,
    ) -> bool:
        """如果模板存在于当前屏幕，则点击其中心位置。
        
        这是一个常用的操作模式：检测按钮是否存在，存在就点击。
        适用于点击各种 UI 按钮、确认对话框等场景。
        
        Args:
            template_name: 要检测的模板名称（必须已注册）
            button: 要使用的鼠标按键，默认为 'left'（左键）
            threshold_override: 可选的阈值覆盖，如果指定则使用此值而非模板默认阈值
                                用于临时提高或降低匹配要求
        
        Returns:
            如果找到并点击了模板返回 True，否则返回 False
        
        Raises:
            KeyError: 如果模板名称未注册
        
        Example:
            # 点击"确定"按钮（如果存在）
            if detectors.click_if_exists("confirm_button"):
                print("已点击确定按钮")
            else:
                print("未找到确定按钮")
        """
        template = self.store.get(template_name)
        screen = self._current_screen()
        result = self.matcher.match(screen, template)
        
        # 未找到匹配
        if result is None:
            return False

        # 如果指定了阈值覆盖，检查是否满足
        if threshold_override is not None and result.score < threshold_override:
            return False

        # 找到匹配，点击中心位置
        x, y = result.center
        logger.info(
            "检测到模板 '%s' 在 (%s,%s)，相似度=%.3f，执行点击",
            template_name,
            x,
            y,
            result.score,
        )
        self.input_ctrl.move_to(x, y)
        self.input_ctrl.click(button=button)
        return True

