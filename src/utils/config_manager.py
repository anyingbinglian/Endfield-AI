"""
配置管理工具：管理项目配置
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import Logger


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_file: str = "config/config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.logger = Logger("ConfigManager")
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config: Dict[str, Any] = {}
        self.load_config()
        
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 是否成功加载
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"加载配置文件: {self.config_file}")
            else:
                self.config = self._get_default_config()
                self.save_config()
                self.logger.info(f"创建默认配置文件: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.config = self._get_default_config()
            return False
            
    def save_config(self) -> bool:
        """
        保存配置文件
        
        Returns:
            bool: 是否成功保存
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"保存配置文件: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键 (如 "game.window_title")
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
            
        Returns:
            bool: 是否成功设置
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        return True
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "game": {
                "window_title": "明日方舟：终末地",
                "window_class": "",
                "auto_focus": True
            },
            "detection": {
                "match_threshold": 0.8,
                "screenshot_interval": 0.5
            },
            "action": {
                "click_delay": 0.1,
                "key_delay": 0.05
            },
            "log": {
                "level": "INFO",
                "save_to_file": True
            }
        }

