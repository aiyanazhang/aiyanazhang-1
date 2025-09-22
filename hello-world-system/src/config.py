# -*- coding: utf-8 -*-
"""
配置管理模块
负责配置文件的加载、验证和管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = config_path
        self.default_config = self._get_default_config()
        self.current_config = self.default_config.copy()
        
        # 查找配置文件
        if not self.config_path:
            self.config_path = self._find_config_file()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "default_language": "en",
            "default_format": "text",
            "enable_colors": True,
            "log_level": "INFO",
            "verbose": False,
            "output": {
                "show_timestamp": True,
                "show_metadata": False,
                "line_separator": "\n"
            },
            "greeting": {
                "max_name_length": 50,
                "sanitize_input": True,
                "add_emoji": False,
                "decoration_style": "simple"
            },
            "system": {
                "encoding": "utf-8",
                "timeout": 30,
                "buffer_size": 1024
            }
        }
    
    def _find_config_file(self) -> Optional[str]:
        """
        查找配置文件
        
        Returns:
            配置文件路径，如果未找到则返回None
        """
        # 可能的配置文件位置
        possible_paths = [
            # 当前目录
            "./config.json",
            "./hello-world.json",
            # config目录
            "./config/config.json",
            "./config/hello-world.json",
            # 用户主目录
            str(Path.home() / ".hello-world.json"),
            str(Path.home() / ".config" / "hello-world.json"),
            # 系统配置目录
            "/etc/hello-world/config.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                return path
        
        return None
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用实例的config_path
            
        Returns:
            配置字典
        """
        # 使用指定路径或实例路径
        path_to_use = config_path or self.config_path
        
        if not path_to_use or not os.path.exists(path_to_use):
            # 如果没有配置文件，返回默认配置
            self.current_config = self.default_config.copy()
            return self.current_config
        
        try:
            with open(path_to_use, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # 验证配置
            if self._validate_config(loaded_config):
                # 合并配置（用户配置覆盖默认配置）
                self.current_config = self._merge_configs(self.default_config, loaded_config)
            else:
                print(f"警告: 配置文件 {path_to_use} 格式不正确，使用默认配置")
                self.current_config = self.default_config.copy()
                
        except json.JSONDecodeError as e:
            print(f"警告: 配置文件 {path_to_use} JSON格式错误: {e}")
            self.current_config = self.default_config.copy()
        except Exception as e:
            print(f"警告: 加载配置文件 {path_to_use} 时出错: {e}")
            self.current_config = self.default_config.copy()
        
        return self.current_config
    
    def save_config(self, config: Dict[str, Any], config_path: Optional[str] = None) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典
            config_path: 保存路径，如果为None则使用默认路径
            
        Returns:
            是否保存成功
        """
        # 确定保存路径
        save_path = config_path or self.config_path
        if not save_path:
            save_path = "./config/config.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            # 验证配置
            if not self._validate_config(config):
                print("错误: 配置数据不合法，无法保存")
                return False
            
            # 保存配置
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"错误: 保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，支持 "output.show_timestamp" 这样的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.current_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.current_config
        
        # 导航到嵌套字典的正确位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置的有效性
        
        Args:
            config: 要验证的配置字典
            
        Returns:
            是否有效
        """
        if not isinstance(config, dict):
            return False
        
        # 检查必需的配置项类型
        type_checks = [
            ('default_language', str),
            ('default_format', str),
            ('enable_colors', bool),
            ('log_level', str),
        ]
        
        for key, expected_type in type_checks:
            if key in config and not isinstance(config[key], expected_type):
                print(f"警告: 配置项 '{key}' 类型不正确，期望 {expected_type.__name__}")
                return False
        
        # 检查枚举值
        enum_checks = [
            ('default_language', ['en', 'zh']),
            ('default_format', ['text', 'json', 'xml']),
            ('log_level', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        ]
        
        for key, valid_values in enum_checks:
            if key in config and config[key] not in valid_values:
                print(f"警告: 配置项 '{key}' 值不合法，有效值: {valid_values}")
                return False
        
        return True
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置字典
        
        Args:
            default: 默认配置
            user: 用户配置
            
        Returns:
            合并后的配置
        """
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # 递归合并嵌套字典
                merged[key] = self._merge_configs(merged[key], value)
            else:
                # 直接覆盖
                merged[key] = value
        
        return merged
    
    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.current_config = self.default_config.copy()
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置信息
        
        Returns:
            配置信息字典
        """
        return {
            "config_path": self.config_path,
            "has_config_file": bool(self.config_path and os.path.exists(self.config_path)),
            "current_config": self.current_config,
            "default_config": self.default_config
        }
    
    def create_default_config_file(self, path: Optional[str] = None) -> bool:
        """
        创建默认配置文件
        
        Args:
            path: 创建路径，如果为None则使用 "./config/config.json"
            
        Returns:
            是否创建成功
        """
        if path is None:
            path = "./config/config.json"
        
        return self.save_config(self.default_config, path)


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_json_file(file_path: str) -> tuple[bool, Optional[str]]:
        """
        验证JSON配置文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {e}"
        except FileNotFoundError:
            return False, "文件不存在"
        except Exception as e:
            return False, f"读取文件错误: {e}"
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        获取配置模式定义
        
        Returns:
            配置模式字典
        """
        return {
            "type": "object",
            "properties": {
                "default_language": {"type": "string", "enum": ["en", "zh"]},
                "default_format": {"type": "string", "enum": ["text", "json", "xml"]},
                "enable_colors": {"type": "boolean"},
                "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "verbose": {"type": "boolean"},
                "output": {
                    "type": "object",
                    "properties": {
                        "show_timestamp": {"type": "boolean"},
                        "show_metadata": {"type": "boolean"},
                        "line_separator": {"type": "string"}
                    }
                },
                "greeting": {
                    "type": "object",
                    "properties": {
                        "max_name_length": {"type": "integer", "minimum": 1, "maximum": 1000},
                        "sanitize_input": {"type": "boolean"},
                        "add_emoji": {"type": "boolean"},
                        "decoration_style": {"type": "string", "enum": ["simple", "box", "stars"]}
                    }
                }
            }
        }