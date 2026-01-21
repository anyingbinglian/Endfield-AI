"""
配置管理测试
"""
import unittest
from src.utils.config_manager import ConfigManager
import os
import tempfile


class TestConfigManager(unittest.TestCase):
    """配置管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.config = ConfigManager(self.config_file)
        
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
        
    def test_get_default_config(self):
        """测试获取默认配置"""
        self.assertIsNotNone(self.config.get("game"))
        self.assertEqual(self.config.get("game.window_title"), "明日方舟：终末地")
        
    def test_set_and_get(self):
        """测试设置和获取配置"""
        self.config.set("test.key", "value")
        self.assertEqual(self.config.get("test.key"), "value")
        
    def test_save_and_load(self):
        """测试保存和加载配置"""
        self.config.set("test.key", "value")
        self.config.save_config()
        
        new_config = ConfigManager(self.config_file)
        self.assertEqual(new_config.get("test.key"), "value")


if __name__ == "__main__":
    unittest.main()

