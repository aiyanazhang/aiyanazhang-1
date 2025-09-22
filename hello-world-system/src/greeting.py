# -*- coding: utf-8 -*-
"""
问候逻辑模块
负责生成个性化问候消息
"""

import datetime
from typing import Dict, Optional


class GreetingGenerator:
    """问候消息生成器"""
    
    def __init__(self):
        """初始化问候生成器"""
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """加载问候消息模板"""
        return {
            'en': {
                'basic': "Hello, {name}!",
                'verbose': "Hello, {name}! Welcome to the Hello World System.\nCurrent time: {timestamp}",
                'default_name': "World"
            },
            'zh': {
                'basic': "你好，{name}！",
                'verbose': "你好，{name}！欢迎使用Hello World系统。\n当前时间：{timestamp}",
                'default_name': "世界"
            }
        }
    
    def generate(self, name: Optional[str] = None, language: str = 'en', 
                 verbose: bool = False) -> Dict:
        """
        生成问候消息
        
        Args:
            name: 问候对象的名称
            language: 语言代码 ('en' 或 'zh')
            verbose: 是否生成详细信息
            
        Returns:
            包含问候信息的字典
        """
        # 参数验证和默认值处理
        language = self._validate_language(language)
        name = self._process_name(name, language)
        
        # 生成时间戳
        timestamp = self._generate_timestamp(language)
        
        # 选择模板
        template_key = 'verbose' if verbose else 'basic'
        template = self.templates[language][template_key]
        
        # 生成消息
        message = template.format(name=name, timestamp=timestamp)
        
        # 返回结构化数据
        return {
            'message': message,
            'name': name,
            'language': language,
            'timestamp': timestamp,
            'verbose': verbose,
            'template_used': template_key
        }
    
    def _validate_language(self, language: str) -> str:
        """
        验证并规范化语言代码
        
        Args:
            language: 输入的语言代码
            
        Returns:
            有效的语言代码
        """
        if language not in self.templates:
            return 'en'  # 默认回退到英文
        return language
    
    def _process_name(self, name: Optional[str], language: str) -> str:
        """
        处理用户名称
        
        Args:
            name: 输入的名称
            language: 语言代码
            
        Returns:
            处理后的名称
        """
        if not name or not name.strip():
            return self.templates[language]['default_name']
        
        # 清理和验证名称
        name = name.strip()
        
        # 限制长度
        if len(name) > 50:
            name = name[:50] + "..."
        
        # 处理特殊字符
        name = self._sanitize_name(name)
        
        return name
    
    def _sanitize_name(self, name: str) -> str:
        """
        清理名称中的特殊字符
        
        Args:
            name: 原始名称
            
        Returns:
            清理后的名称
        """
        # 先处理&符号，避免后续重复编码
        name = name.replace('&', '&amp;')
        
        # 然后处理其他特殊字符
        unsafe_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        }
        
        for char, replacement in unsafe_chars.items():
            name = name.replace(char, replacement)
        
        return name
    
    def _generate_timestamp(self, language: str) -> str:
        """
        生成时间戳
        
        Args:
            language: 语言代码
            
        Returns:
            格式化的时间戳字符串
        """
        now = datetime.datetime.now()
        
        if language == 'zh':
            return now.strftime("%Y年%m月%d日 %H:%M:%S")
        else:
            return now.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return list(self.templates.keys())
    
    def add_language_template(self, language: str, templates: Dict) -> None:
        """
        添加新的语言模板
        
        Args:
            language: 语言代码
            templates: 模板字典
        """
        required_keys = ['basic', 'verbose', 'default_name']
        if all(key in templates for key in required_keys):
            self.templates[language] = templates
        else:
            raise ValueError(f"模板必须包含这些键: {required_keys}")


class GreetingFormatter:
    """问候消息格式化器"""
    
    @staticmethod
    def add_decorations(message: str, style: str = 'simple') -> str:
        """
        为消息添加装饰
        
        Args:
            message: 原始消息
            style: 装饰风格
            
        Returns:
            装饰后的消息
        """
        if style == 'box':
            lines = message.split('\n')
            max_length = max(len(line) for line in lines)
            border = '+' + '-' * (max_length + 2) + '+'
            
            result = [border]
            for line in lines:
                result.append(f"| {line.ljust(max_length)} |")
            result.append(border)
            
            return '\n'.join(result)
        
        elif style == 'stars':
            return f"*** {message} ***"
        
        else:  # simple
            return message
    
    @staticmethod
    def add_emoji(message: str, language: str) -> str:
        """
        为消息添加表情符号
        
        Args:
            message: 原始消息
            language: 语言代码
            
        Returns:
            带表情符号的消息
        """
        emoji_map = {
            'en': '👋 ',
            'zh': '👋 '
        }
        
        emoji = emoji_map.get(language, '👋 ')
        return emoji + message