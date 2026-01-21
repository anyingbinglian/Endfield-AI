"""
点击动作：执行鼠标点击操作
"""
from src.actions.base_action import BaseAction
from src.utils.input_controller import InputController


class ClickAction(BaseAction):
    """点击动作类"""
    
    def __init__(self):
        super().__init__("Click")
        self.input_controller = InputController()
        
    def execute(self, x: int, y: int, button: str = "left", **kwargs) -> bool:
        """
        执行点击动作
        
        Args:
            x: 点击X坐标
            y: 点击Y坐标
            button: 鼠标按钮 ("left", "right", "middle")
            **kwargs: 其他参数
            
        Returns:
            bool: 执行是否成功
        """
        if not self.validate(x=x, y=y, button=button):
            return False
            
        try:
            self.input_controller.click(x, y, button)
            self.logger.info(f"点击坐标 ({x}, {y}), 按钮: {button}")
            return True
        except Exception as e:
            self.logger.error(f"点击失败: {e}")
            return False
            
    def validate(self, x: int, y: int, button: str = "left", **kwargs) -> bool:
        """验证点击参数"""
        if not isinstance(x, int) or not isinstance(y, int):
            self.logger.error("坐标必须是整数")
            return False
        if button not in ["left", "right", "middle"]:
            self.logger.error(f"无效的鼠标按钮: {button}")
            return False
        return True

