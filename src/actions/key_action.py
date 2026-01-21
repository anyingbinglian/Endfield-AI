"""
键盘动作：执行键盘按键操作
"""
from src.actions.base_action import BaseAction
from src.utils.input_controller import InputController


class KeyAction(BaseAction):
    """键盘动作类"""
    
    def __init__(self):
        super().__init__("Key")
        self.input_controller = InputController()
        
    def execute(self, key: str, action: str = "press", **kwargs) -> bool:
        """
        执行键盘动作
        
        Args:
            key: 按键名称
            action: 动作类型 ("press", "release", "press_release")
            **kwargs: 其他参数
            
        Returns:
            bool: 执行是否成功
        """
        if not self.validate(key=key, action=action):
            return False
            
        try:
            if action == "press":
                self.input_controller.key_press(key)
            elif action == "release":
                self.input_controller.key_release(key)
            else:
                self.input_controller.key_press_release(key)
                
            self.logger.info(f"按键: {key}, 动作: {action}")
            return True
        except Exception as e:
            self.logger.error(f"按键操作失败: {e}")
            return False
            
    def validate(self, key: str, action: str = "press", **kwargs) -> bool:
        """验证键盘参数"""
        if not key:
            self.logger.error("按键名称不能为空")
            return False
        if action not in ["press", "release", "press_release"]:
            self.logger.error(f"无效的动作类型: {action}")
            return False
        return True

