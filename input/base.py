from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class InputController(Protocol):
    """输入控制器的抽象接口，定义鼠标和键盘操作的标准方法。
    
    这是一个协议类（Protocol），任何实现了这些方法的类都可以作为输入控制器使用。
    这样设计的好处是：上层代码只需要依赖这个接口，而不关心具体是前台实现还是后台实现。
    
    支持的鼠标按键：'left'（左键）、'right'（右键）、'middle'（中键）
    支持的键盘按键：'w', 'a', 's', 'd', 'space', 'esc', 'enter' 等标准按键名称
    """

    # ========== 鼠标操作 ==========

    def move_to(self, x: int, y: int, *, relative: bool = False) -> None:
        """移动鼠标到指定坐标。
        
        Args:
            x: 目标 x 坐标（窗口内坐标）
            y: 目标 y 坐标（窗口内坐标）
            relative: 如果为 True，则相对于当前位置移动 (x, y) 像素；
                      如果为 False（默认），则移动到绝对坐标 (x, y)
        """
        ...

    def click(self, button: str = "left") -> None:
        """单击鼠标按键。
        
        Args:
            button: 要点击的鼠标按键，默认为 'left'（左键）
        """
        ...

    def double_click(self, button: str = "left") -> None:
        """双击鼠标按键。
        
        Args:
            button: 要双击的鼠标按键，默认为 'left'（左键）
        """
        ...

    def mouse_down(self, button: str = "left") -> None:
        """按下并保持鼠标按键（不释放）。
        
        通常与 mouse_up() 配合使用，实现拖拽等操作。
        
        Args:
            button: 要按下的鼠标按键，默认为 'left'（左键）
        """
        ...

    def mouse_up(self, button: str = "left") -> None:
        """释放鼠标按键。
        
        通常与 mouse_down() 配合使用，实现拖拽等操作。
        
        Args:
            button: 要释放的鼠标按键，默认为 'left'（左键）
        """
        ...

    def drag_to(self, x: int, y: int, button: str = "left") -> None:
        """从当前位置拖拽到目标坐标。
        
        实现方式：先按下鼠标按键，移动到目标位置，然后释放。
        
        Args:
            x: 目标 x 坐标（窗口内坐标）
            y: 目标 y 坐标（窗口内坐标）
            button: 用于拖拽的鼠标按键，默认为 'left'（左键）
        """
        ...

    # ========== 键盘操作 ==========

    def key_down(self, key: str) -> None:
        """按下并保持键盘按键（不释放）。
        
        通常与 key_up() 配合使用，实现长按等操作。
        
        Args:
            key: 要按下的按键名称，例如：'w', 'space', 'esc', 'enter'
        """
        ...

    def key_up(self, key: str) -> None:
        """释放键盘按键。
        
        通常与 key_down() 配合使用，实现长按等操作。
        
        Args:
            key: 要释放的按键名称，例如：'w', 'space', 'esc', 'enter'
        """
        ...

    def key_press(self, key: str, duration: float | None = None) -> None:
        """按下并释放键盘按键（完整的按键操作）。
        
        Args:
            key: 要按下的按键名称，例如：'w', 'space', 'esc', 'enter'
            duration: 如果指定，则按下后保持 duration 秒再释放；
                      如果为 None 或 <= 0，则立即按下并释放
        """
        ...

    # ========== 辅助方法 ==========

    def sleep(self, seconds: float) -> None:
        """延时等待。
        
        这是一个辅助方法，用于统一管理延时操作，方便后续添加日志等功能。
        
        Args:
            seconds: 要等待的秒数（可以是小数，如 0.5 表示 500 毫秒）
        """
        ...


class WindowNotFoundError(RuntimeError):
    """当无法找到游戏窗口时抛出的异常。
    
    通常发生在：
    1. 游戏未启动
    2. 窗口标题配置不正确
    3. 窗口被最小化或隐藏
    """
    pass

