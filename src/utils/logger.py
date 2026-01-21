"""
日志工具：统一的日志管理
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """日志工具类"""
    
    _log_dir = Path("logs")
    _log_dir.mkdir(exist_ok=True)
    
    def __init__(self, name: str, level: int = logging.INFO):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
            
            # 文件处理器
            log_file = self._log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message)

