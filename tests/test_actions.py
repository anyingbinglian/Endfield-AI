"""
动作模块测试
"""
import unittest
from src.actions.click_action import ClickAction
from src.actions.key_action import KeyAction


class TestActions(unittest.TestCase):
    """动作测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.click_action = ClickAction()
        self.key_action = KeyAction()
        
    def test_click_action_validate(self):
        """测试点击动作参数验证"""
        self.assertTrue(self.click_action.validate(x=100, y=200, button="left"))
        self.assertFalse(self.click_action.validate(x="100", y=200))
        self.assertFalse(self.click_action.validate(x=100, y=200, button="invalid"))
        
    def test_key_action_validate(self):
        """测试键盘动作参数验证"""
        self.assertTrue(self.key_action.validate(key="a", action="press"))
        self.assertFalse(self.key_action.validate(key="", action="press"))
        self.assertFalse(self.key_action.validate(key="a", action="invalid"))


if __name__ == "__main__":
    unittest.main()

