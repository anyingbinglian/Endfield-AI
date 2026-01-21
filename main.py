"""
Endfield-AI 主入口文件
"""
from src.core.game_controller import GameController
from src.utils.logger import Logger
from src.utils.config_manager import ConfigManager


def main():
    """主函数"""
    logger = Logger("Main")
    config = ConfigManager()
    
    logger.info("=" * 50)
    logger.info("Endfield-AI 游戏自动化助手启动")
    logger.info("=" * 50)
    
    # 创建游戏控制器
    controller = GameController()
    
    # 启动自动化
    controller.start()
    
    try:
        # TODO: 实现主循环逻辑
        logger.info("主循环运行中...")
        # 示例：保持运行
        import time
        while controller.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("接收到中断信号")
    finally:
        controller.stop()
        logger.info("程序退出")


if __name__ == "__main__":
    main()

