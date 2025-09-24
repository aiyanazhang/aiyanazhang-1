#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责配置文件的解析、管理和验证
"""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 自定义配置文件路径
        """
        self.config = configparser.ConfigParser()
        self.config_path = config_path or self._get_default_config_path()
        self.protected_rules = {}
        
        # 加载配置
        self._load_default_config()
        self._load_user_config()
        self._load_protected_rules()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return os.path.expanduser("~/.clean-script.conf")
    
    def _get_protected_rules_path(self) -> str:
        """获取保护规则文件路径"""
        return os.path.expanduser("~/.clean-script-protected.json")
    
    def _load_default_config(self):
        """加载默认配置"""
        # 默认配置值
        defaults = {
            'DEFAULT_BACKUP_DIR': os.path.expanduser("~/.clean-script-backups"),
            'MAX_BACKUP_AGE_DAYS': '30',
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': os.path.expanduser("~/.clean-script.log"),
            'ENABLE_BACKUP': 'true',
            'REQUIRE_CONFIRMATION': 'true',
            'PROTECTED_DIRS': '/bin:/usr:/etc:/home',
            'DANGEROUS_PATTERNS': '*:/*:.*',
            'USE_COLORS': 'true',
            'SHOW_PROGRESS': 'true',
            'PAGE_SIZE': '20',
            'LARGE_FILE_THRESHOLD': '100',
            'RECENT_MODIFIED_THRESHOLD': '24'
        }
        
        # 设置默认值
        for key, value in defaults.items():
            self.config.set('DEFAULT', key, value)
    
    def _load_user_config(self):
        """加载用户配置文件"""
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.config_path}: {e}")
    
    def _load_protected_rules(self):
        """加载保护规则文件"""
        protected_path = self._get_protected_rules_path()
        
        # 默认保护规则
        default_rules = {
            "system_dirs": ["/bin", "/usr", "/etc", "/var"],
            "config_files": [".bashrc", ".profile", ".gitconfig"],
            "important_extensions": [".sql", ".json", ".yaml", ".md"],
            "project_files": ["package.json", "Makefile", "requirements.txt"],
            "user_rules": []
        }
        
        if os.path.exists(protected_path):
            try:
                with open(protected_path, 'r', encoding='utf-8') as f:
                    self.protected_rules = json.load(f)
            except Exception as e:
                print(f"警告: 无法加载保护规则文件 {protected_path}: {e}")
                self.protected_rules = default_rules
        else:
            self.protected_rules = default_rules
    
    def get(self, key: str, fallback: Any = None) -> str:
        """
        获取配置值
        
        Args:
            key: 配置键
            fallback: 默认值
            
        Returns:
            配置值
        """
        return self.config.get('DEFAULT', key, fallback=fallback)
    
    def get_bool(self, key: str, fallback: bool = False) -> bool:
        """
        获取布尔类型配置值
        
        Args:
            key: 配置键
            fallback: 默认值
            
        Returns:
            布尔值
        """
        try:
            return self.config.getboolean('DEFAULT', key)
        except:
            return fallback
    
    def get_int(self, key: str, fallback: int = 0) -> int:
        """
        获取整数类型配置值
        
        Args:
            key: 配置键
            fallback: 默认值
            
        Returns:
            整数值
        """
        try:
            return self.config.getint('DEFAULT', key)
        except:
            return fallback
    
    def get_list(self, key: str, separator: str = ':') -> List[str]:
        """
        获取列表类型配置值
        
        Args:
            key: 配置键
            separator: 分隔符
            
        Returns:
            列表值
        """
        value = self.get(key, '')
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def get_protected_dirs(self) -> List[str]:
        """获取受保护的目录列表"""
        return self.protected_rules.get('system_dirs', [])
    
    def get_config_files(self) -> List[str]:
        """获取配置文件列表"""
        return self.protected_rules.get('config_files', [])
    
    def get_important_extensions(self) -> List[str]:
        """获取重要文件扩展名列表"""
        return self.protected_rules.get('important_extensions', [])
    
    def get_project_files(self) -> List[str]:
        """获取项目文件列表"""
        return self.protected_rules.get('project_files', [])
    
    def get_user_rules(self) -> List[Dict[str, str]]:
        """获取用户自定义规则"""
        return self.protected_rules.get('user_rules', [])
    
    def is_protected_dir(self, path: str) -> bool:
        """
        检查路径是否为受保护目录
        
        Args:
            path: 文件路径
            
        Returns:
            是否受保护
        """
        abs_path = os.path.abspath(path)
        for protected_dir in self.get_protected_dirs():
            if abs_path.startswith(protected_dir):
                return True
        return False
    
    def create_default_config(self):
        """创建默认配置文件"""
        if not os.path.exists(self.config_path):
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            print(f"已创建默认配置文件: {self.config_path}")
    
    def create_default_protected_rules(self):
        """创建默认保护规则文件"""
        protected_path = self._get_protected_rules_path()
        if not os.path.exists(protected_path):
            with open(protected_path, 'w', encoding='utf-8') as f:
                json.dump(self.protected_rules, f, ensure_ascii=False, indent=2)
            
            print(f"已创建默认保护规则文件: {protected_path}")
    
    def validate_config(self) -> List[str]:
        """
        验证配置的有效性
        
        Returns:
            错误信息列表
        """
        errors = []
        
        # 检查备份目录
        backup_dir = self.get('DEFAULT_BACKUP_DIR')
        if backup_dir and not os.path.exists(os.path.dirname(backup_dir)):
            errors.append(f"备份目录的父目录不存在: {backup_dir}")
        
        # 检查日志文件
        log_file = self.get('LOG_FILE')
        if log_file and not os.path.exists(os.path.dirname(log_file)):
            errors.append(f"日志文件的父目录不存在: {log_file}")
        
        # 检查数值配置
        try:
            age_days = self.get_int('MAX_BACKUP_AGE_DAYS')
            if age_days < 0:
                errors.append("MAX_BACKUP_AGE_DAYS 必须为非负整数")
        except:
            errors.append("MAX_BACKUP_AGE_DAYS 配置格式错误")
        
        return errors


# 全局配置实例
config_manager = None


def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager


def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    初始化配置管理器
    
    Args:
        config_path: 自定义配置文件路径
        
    Returns:
        配置管理器实例
    """
    global config_manager
    config_manager = ConfigManager(config_path)
    return config_manager


if __name__ == '__main__':
    # 测试配置管理器
    config = ConfigManager()
    
    print("=== 配置测试 ===")
    print(f"备份目录: {config.get('DEFAULT_BACKUP_DIR')}")
    print(f"启用备份: {config.get_bool('ENABLE_BACKUP')}")
    print(f"页面大小: {config.get_int('PAGE_SIZE')}")
    print(f"受保护目录: {config.get_protected_dirs()}")
    
    # 验证配置
    errors = config.validate_config()
    if errors:
        print("配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置验证通过")