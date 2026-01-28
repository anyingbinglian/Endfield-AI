import logging
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    """配置全局日志系统，使用简洁易读的格式。
    
    此函数只会初始化一次，重复调用不会重复添加处理器。
    日志格式：时间 [级别] 模块名 - 消息内容
    
    Args:
        level: 日志级别，默认为 INFO。可选值：
            - logging.DEBUG: 调试信息
            - logging.INFO: 一般信息
            - logging.WARNING: 警告信息
            - logging.ERROR: 错误信息
            - logging.CRITICAL: 严重错误
    """
    root = logging.getLogger()
    if root.handlers:
        # 已经配置过了，避免重复添加处理器
        return

    # 设置日志格式：时间 [级别] 模块名 - 消息
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",  # 只显示时分秒
    )

    # 使用控制台输出
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取一个配置好的日志记录器。
    
    如果全局日志系统还未初始化，会自动调用 setup_logging() 进行初始化。
    
    Args:
        name: 日志记录器的名称，通常传入 __name__。
              如果为 None，则返回根日志记录器。
    
    Returns:
        配置好的日志记录器实例
    """
    setup_logging()
    return logging.getLogger(name)

