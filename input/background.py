from __future__ import annotations

from core.logging import get_logger
from input.base import InputController

logger = get_logger(__name__)


class BackgroundInput(InputController):
    """后台输入实现的占位类。
    
    后台模式意味着可以在游戏窗口没有焦点的情况下进行操作，
    通常通过 Windows 消息注入或驱动级操作实现。
    
    当前状态：
    - 所有方法都会抛出 NotImplementedError
    - 这是一个占位实现，等待后续接入大漠插件或其他后台输入方案
    
    未来实现方向：
    - 使用大漠插件（DM.dll）进行后台操作
    - 使用 Windows 消息注入（PostMessage/SendMessage）
    - 使用驱动级输入（需要管理员权限）
    """

    def _not_implemented(self) -> None:
        """抛出未实现异常。"""
        raise NotImplementedError(
            "BackgroundInput 尚未实现。"
            "请使用 ForegroundInput，或在此处实现后台输入功能。"
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

