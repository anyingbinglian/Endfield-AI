"""
基础动作类：所有游戏动作的基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.utils.logger import Logger


class BaseAction(ABC):
    """动作基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = Logger(f"Action.{name}")
        
    @abstractmethod
    def execute(self, **kwargs) -> bool:
        """
        执行动作
        
        Args:
            **kwargs: 动作参数
            
        Returns:
            bool: 执行是否成功
        """
        pass
        
    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """
        验证动作参数
        
        Args:
            **kwargs: 动作参数
            
        Returns:
            bool: 参数是否有效
        """
        pass

