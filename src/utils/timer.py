"""
定时器工具：延迟和定时功能
"""
import time
from typing import Callable, Optional
from src.utils.logger import Logger


class Timer:
    """定时器工具类"""
    
    def __init__(self):
        self.logger = Logger("Timer")
        
    @staticmethod
    def sleep(seconds: float):
        """
        延迟指定时间
        
        Args:
            seconds: 延迟秒数
        """
        time.sleep(seconds)
        
    @staticmethod
    def sleep_random(min_seconds: float, max_seconds: float):
        """
        随机延迟
        
        Args:
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数
        """
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def wait_until(self, condition: Callable[[], bool], 
                   timeout: float = 10.0, interval: float = 0.1) -> bool:
        """
        等待直到条件满足
        
        Args:
            condition: 条件函数，返回True表示条件满足
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            
        Returns:
            bool: 条件是否在超时前满足
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False

