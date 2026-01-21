"""
基础使用示例
演示如何使用 Endfield-AI 的基本功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_controller import GameController
from src.actions.click_action import ClickAction
from src.actions.key_action import KeyAction
from src.utils.config_manager import ConfigManager
from src.utils.logger import Logger
from src.utils.timer import Timer


def example_basic_usage():
    """基础使用示例"""
    logger = Logger("Example")
    
    # 1. 加载配置
    logger.info("加载配置...")
    config = ConfigManager()
    window_title = config.get("game.window_title")
    logger.info(f"游戏窗口标题: {window_title}")
    
    # 2. 创建游戏控制器
    logger.info("创建游戏控制器...")
    controller = GameController()
    
    # 3. 创建动作实例
    click_action = ClickAction()
    key_action = KeyAction()
    
    # 4. 启动控制器
    controller.start()
    
    try:
        # 5. 执行一些示例动作
        logger.info("执行示例动作...")
        
        # 示例：点击操作
        # click_action.execute(x=100, y=200, button="left")
        
        # 示例：按键操作
        # key_action.execute(key="space", action="press_release")
        
        # 示例：延迟
        Timer.sleep(1.0)
        
        logger.info("示例执行完成")
        
    except Exception as e:
        logger.error(f"执行出错: {e}")
    finally:
        # 6. 停止控制器
        controller.stop()
        logger.info("程序结束")


if __name__ == "__main__":
    example_basic_usage()

