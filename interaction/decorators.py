"""操作前检查装饰器模块。

提供操作前检查功能，确保在正确的游戏窗口上执行操作。
"""

import inspect
import time
from functools import wraps
from typing import Callable, TypeVar, cast

import win32gui

from core.config import WINDOW_CONFIG
from core.logging import get_logger

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable)


def before_operation(print_log: bool = True):
    """操作前检查装饰器。
    
    在执行操作前：
    1. 检查当前活动窗口是否为游戏窗口（前台模式）
    2. 如果不是，等待直到游戏窗口获得焦点
    3. 记录操作日志（可选）
    
    Args:
        print_log: 是否打印操作日志，默认 True
        
    Example:
        @before_operation(print_log=True)
        def left_click(self):
            # 执行点击操作
            pass
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 获取调用者信息
            if print_log:
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    func_name = inspect.getframeinfo(frame.f_back)[2]
                    logger.debug(
                        f"操作: {func.__name__} | 参数: {args[1:]} | {kwargs} | 调用函数: {func_name}"
                    )
            
            # 检查窗口焦点（前台模式）
            # 注意：这里简化实现，实际使用时可能需要根据配置决定是否检查
            try:
                active_window = win32gui.GetForegroundWindow()
                active_title = win32gui.GetWindowText(active_window).lower()
                
                # 检查活动窗口是否包含游戏窗口标题
                target_titles = [title.lower() for title in WINDOW_CONFIG.window_titles]
                is_game_window = any(target_title in active_title for target_title in target_titles)
                
                if not is_game_window:
                    logger.info(f"当前窗口焦点为 {active_title}，不是游戏窗口，等待恢复...")
                    # 等待游戏窗口获得焦点
                    while True:
                        time.sleep(0.1)
                        active_window = win32gui.GetForegroundWindow()
                        active_title = win32gui.GetWindowText(active_window).lower()
                        is_game_window = any(target_title in active_title for target_title in target_titles)
                        
                        if is_game_window:
                            logger.info("恢复操作")
                            break
                        
                        # 每5秒打印一次提示
                        if int(time.time()) % 5 == 0:
                            logger.info(
                                f"当前窗口焦点为 {active_title}，不是游戏窗口 {target_titles}，"
                                f"操作暂停中..."
                            )
            except Exception as e:
                logger.warning(f"检查窗口焦点时出错: {e}，继续执行操作")
            
            # 执行原函数
            return func(self, *args, **kwargs)
        
        return cast(F, wrapper)
    return decorator
