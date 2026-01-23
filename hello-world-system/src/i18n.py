# -*- coding: utf-8 -*-
"""
多语言支持模块
提供国际化和本地化支持
"""

from typing import Dict, Any


class LanguageManager:
    """语言管理器"""
    
    def __init__(self):
        """初始化语言管理器"""
        self.translations = self._load_translations()
        self.current_language = 'en'
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        加载翻译字典
        
        Returns:
            翻译字典
        """
        return {
            'en': {
                # 基础消息
                'hello_world': 'Hello, World!',
                'hello_name': 'Hello, {name}!',
                'welcome_message': 'Welcome to the Hello World System.',
                'current_time': 'Current time: {timestamp}',
                
                # 详细信息标签
                'details_header': '=== Details ===',
                'user_name': 'User name: {name}',
                'language': 'Language: {language}',
                'timestamp': 'Timestamp: {timestamp}',
                'template': 'Template: {template}',
                
                # 错误消息
                'error_invalid_name': 'Invalid name provided',
                'error_config_load': 'Failed to load configuration',
                'error_output_format': 'Unsupported output format: {format}',
                'error_file_not_found': 'File not found: {file}',
                
                # 帮助信息
                'help_name': 'Name of the person to greet',
                'help_language': 'Output language (en/zh)',
                'help_format': 'Output format (text/json/xml)',
                'help_verbose': 'Show detailed information',
                'help_config': 'Path to configuration file',
                'help_no_colors': 'Disable colored output',
                
                # 状态消息
                'status_success': 'Operation completed successfully',
                'status_warning': 'Warning: {message}',
                'status_error': 'Error: {message}',
                'status_info': 'Info: {message}',
                
                # 文件操作
                'file_saved': 'File saved: {filename}',
                'file_loaded': 'File loaded: {filename}',
                'config_created': 'Configuration file created: {path}',
                'config_not_found': 'Configuration file not found, using defaults',
                
                # 验证消息
                'validation_name_too_long': 'Name is too long (max {max_length} characters)',
                'validation_invalid_language': 'Invalid language code: {language}',
                'validation_invalid_format': 'Invalid format: {format}',
                
                # 时间格式
                'time_format': '%Y-%m-%d %H:%M:%S',
                
                # 元数据
                'metadata_version': 'Version',
                'metadata_format': 'Format',
                'metadata_generated_at': 'Generated at'
            },
            
            'zh': {
                # 基础消息
                'hello_world': '你好，世界！',
                'hello_name': '你好，{name}！',
                'welcome_message': '欢迎使用Hello World系统。',
                'current_time': '当前时间：{timestamp}',
                
                # 详细信息标签
                'details_header': '=== 详细信息 ===',
                'user_name': '用户名：{name}',
                'language': '语言：{language}',
                'timestamp': '时间戳：{timestamp}',
                'template': '模板：{template}',
                
                # 错误消息
                'error_invalid_name': '提供的名称无效',
                'error_config_load': '加载配置失败',
                'error_output_format': '不支持的输出格式：{format}',
                'error_file_not_found': '文件未找到：{file}',
                
                # 帮助信息
                'help_name': '要问候的人员姓名',
                'help_language': '输出语言（en/zh）',
                'help_format': '输出格式（text/json/xml）',
                'help_verbose': '显示详细信息',
                'help_config': '配置文件路径',
                'help_no_colors': '禁用彩色输出',
                
                # 状态消息
                'status_success': '操作成功完成',
                'status_warning': '警告：{message}',
                'status_error': '错误：{message}',
                'status_info': '信息：{message}',
                
                # 文件操作
                'file_saved': '文件已保存：{filename}',
                'file_loaded': '文件已加载：{filename}',
                'config_created': '配置文件已创建：{path}',
                'config_not_found': '未找到配置文件，使用默认设置',
                
                # 验证消息
                'validation_name_too_long': '名称过长（最多{max_length}个字符）',
                'validation_invalid_language': '无效的语言代码：{language}',
                'validation_invalid_format': '无效的格式：{format}',
                
                # 时间格式
                'time_format': '%Y年%m月%d日 %H:%M:%S',
                
                # 元数据
                'metadata_version': '版本',
                'metadata_format': '格式',
                'metadata_generated_at': '生成时间'
            }
        }
    
    def set_language(self, language: str) -> bool:
        """
        设置当前语言
        
        Args:
            language: 语言代码
            
        Returns:
            是否设置成功
        """
        if language in self.translations:
            self.current_language = language
            return True
        return False
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        text = self.translations.get(self.current_language, {}).get(key, key)
        
        try:
            return text.format(**kwargs)
        except KeyError:
            # 如果格式化失败，返回原始文本
            return text
    
    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return list(self.translations.keys())
    
    def add_translation(self, language: str, translations: Dict[str, str]) -> None:
        """
        添加新的翻译
        
        Args:
            language: 语言代码
            translations: 翻译字典
        """
        if language not in self.translations:
            self.translations[language] = {}
        
        self.translations[language].update(translations)


# 全局语言管理器实例
language_manager = LanguageManager()


def get_text(key: str, language: str = None, **kwargs) -> str:
    """
    获取翻译文本的便捷函数
    
    Args:
        key: 翻译键
        language: 语言代码，如果为None则使用当前语言
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    if language:
        original_language = language_manager.current_language
        language_manager.set_language(language)
        text = language_manager.get_text(key, **kwargs)
        language_manager.set_language(original_language)
        return text
    else:
        return language_manager.get_text(key, **kwargs)


def set_language(language: str) -> bool:
    """
    设置全局语言的便捷函数
    
    Args:
        language: 语言代码
        
    Returns:
        是否设置成功
    """
    return language_manager.set_language(language)