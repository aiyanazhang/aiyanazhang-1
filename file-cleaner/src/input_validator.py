#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入验证模块
验证用户输入的文件名或模式，确保输入格式正确且安全
"""

import re
import os
from typing import List, Tuple, Dict, Optional
from enum import Enum


class InputType(Enum):
    """输入类型枚举"""
    EXACT_FILE = "exact_file"          # 精确文件名
    WILDCARD = "wildcard"              # 通配符模式
    REGEX = "regex"                    # 正则表达式
    DANGEROUS = "dangerous"            # 危险模式


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "低"                         # 低风险
    MEDIUM = "中"                      # 中风险
    HIGH = "高"                        # 高风险
    EXTREME = "极高"                   # 极高风险


class ValidationResult:
    """验证结果类"""
    
    def __init__(self, is_valid: bool, input_type: InputType, 
                 risk_level: RiskLevel, message: str = ""):
        """
        初始化验证结果
        
        Args:
            is_valid: 是否有效
            input_type: 输入类型
            risk_level: 风险等级
            message: 描述信息
        """
        self.is_valid = is_valid
        self.input_type = input_type
        self.risk_level = risk_level
        self.message = message


class InputValidator:
    """输入验证器"""
    
    def __init__(self):
        """初始化验证器"""
        # 危险模式列表
        self.dangerous_patterns = [
            '*',           # 匹配所有文件
            '/*',          # 根目录下所有文件
            '.',           # 当前目录
            '..',          # 上级目录
            '~/*',         # 用户目录下所有文件
            '/*/',         # 所有目录
            '*..*',        # 可能的路径遍历
        ]
        
        # 系统关键文件模式
        self.system_patterns = [
            '/bin/*',
            '/usr/*', 
            '/etc/*',
            '/var/*',
            '/lib/*',
            '/boot/*',
            '/sys/*',
            '/proc/*',
            '/dev/*'
        ]
        
        # 配置文件模式
        self.config_patterns = [
            '.*rc',        # .bashrc, .vimrc等
            '.*profile',   # .profile等
            '.*config',    # .gitconfig等
            '.ssh/*',      # SSH配置
        ]
        
        # 最大模式长度
        self.max_pattern_length = 200
        
        # 最大正则表达式复杂度
        self.max_regex_complexity = 50
    
    def validate_input(self, user_input: str) -> ValidationResult:
        """
        验证用户输入
        
        Args:
            user_input: 用户输入的模式
            
        Returns:
            验证结果
        """
        if not user_input or not user_input.strip():
            return ValidationResult(
                False, InputType.EXACT_FILE, RiskLevel.LOW,
                "输入不能为空"
            )
        
        user_input = user_input.strip()
        
        # 长度检查
        if len(user_input) > self.max_pattern_length:
            return ValidationResult(
                False, InputType.DANGEROUS, RiskLevel.EXTREME,
                f"输入过长，最大长度为 {self.max_pattern_length} 字符"
            )
        
        # 检查危险模式
        if self._is_dangerous_pattern(user_input):
            return ValidationResult(
                False, InputType.DANGEROUS, RiskLevel.EXTREME,
                "检测到危险模式，此模式可能删除大量重要文件"
            )
        
        # 检查系统文件模式
        if self._is_system_pattern(user_input):
            return ValidationResult(
                False, InputType.DANGEROUS, RiskLevel.EXTREME,
                "不能删除系统目录下的文件"
            )
        
        # 确定输入类型和风险等级
        input_type, risk_level, message = self._analyze_pattern(user_input)
        
        return ValidationResult(True, input_type, risk_level, message)
    
    def _is_dangerous_pattern(self, pattern: str) -> bool:
        """
        检查是否为危险模式
        
        Args:
            pattern: 输入模式
            
        Returns:
            是否危险
        """
        # 直接匹配危险模式
        if pattern in self.dangerous_patterns:
            return True
        
        # 检查是否包含危险字符组合
        dangerous_chars = ['*/', '/*', '**', '...', '~/']
        for danger in dangerous_chars:
            if danger in pattern:
                return True
        
        # 检查路径遍历
        if '..' in pattern or pattern.startswith('/'):
            return True
        
        return False
    
    def _is_system_pattern(self, pattern: str) -> bool:
        """
        检查是否为系统文件模式
        
        Args:
            pattern: 输入模式
            
        Returns:
            是否为系统文件模式
        """
        for sys_pattern in self.system_patterns:
            if pattern.startswith(sys_pattern.replace('*', '')):
                return True
        return False
    
    def _analyze_pattern(self, pattern: str) -> Tuple[InputType, RiskLevel, str]:
        """
        分析模式类型和风险等级
        
        Args:
            pattern: 输入模式
            
        Returns:
            (输入类型, 风险等级, 描述信息)
        """
        # 检查是否为正则表达式模式
        if self._is_regex_pattern(pattern):
            complexity = self._calculate_regex_complexity(pattern)
            if complexity > self.max_regex_complexity:
                return (InputType.DANGEROUS, RiskLevel.EXTREME, 
                       "正则表达式过于复杂")
            return (InputType.REGEX, RiskLevel.HIGH, 
                   f"正则表达式模式，复杂度: {complexity}")
        
        # 检查是否包含通配符
        if '*' in pattern or '?' in pattern or '[' in pattern:
            return self._analyze_wildcard_pattern(pattern)
        
        # 精确文件名
        if self._is_config_file(pattern):
            return (InputType.EXACT_FILE, RiskLevel.MEDIUM, 
                   "配置文件，需要额外确认")
        
        if self._is_hidden_file(pattern):
            return (InputType.EXACT_FILE, RiskLevel.MEDIUM, 
                   "隐藏文件，需要谨慎操作")
        
        return (InputType.EXACT_FILE, RiskLevel.LOW, "精确文件名匹配")
    
    def _is_regex_pattern(self, pattern: str) -> bool:
        """
        判断是否为正则表达式模式
        
        Args:
            pattern: 输入模式
            
        Returns:
            是否为正则表达式
        """
        # 检查正则表达式特殊字符
        regex_chars = ['^', '$', '+', '{', '}', '(', ')', '|', '\\']
        return any(char in pattern for char in regex_chars)
    
    def _calculate_regex_complexity(self, pattern: str) -> int:
        """
        计算正则表达式复杂度
        
        Args:
            pattern: 正则表达式
            
        Returns:
            复杂度分数
        """
        complexity = 0
        
        # 基础长度
        complexity += len(pattern) // 10
        
        # 特殊字符计分
        special_chars = {
            '*': 2, '+': 2, '?': 1, '{': 3, '}': 3,
            '(': 2, ')': 2, '[': 2, ']': 2, '|': 3,
            '^': 1, '$': 1, '\\': 1
        }
        
        for char, score in special_chars.items():
            complexity += pattern.count(char) * score
        
        return complexity
    
    def _analyze_wildcard_pattern(self, pattern: str) -> Tuple[InputType, RiskLevel, str]:
        """
        分析通配符模式
        
        Args:
            pattern: 通配符模式
            
        Returns:
            (输入类型, 风险等级, 描述信息)
        """
        # 计算通配符数量
        wildcard_count = pattern.count('*') + pattern.count('?')
        
        # 检查模式类型
        if pattern.startswith('*.'):
            # 扩展名模式，如 *.tmp
            ext = pattern[2:]
            if self._is_safe_extension(ext):
                return (InputType.WILDCARD, RiskLevel.LOW, 
                       f"安全的扩展名模式: {ext}")
            else:
                return (InputType.WILDCARD, RiskLevel.MEDIUM,
                       f"扩展名模式，需要确认: {ext}")
        
        elif pattern.endswith('*'):
            # 前缀模式，如 temp*
            prefix = pattern[:-1]
            if len(prefix) < 3:
                return (InputType.WILDCARD, RiskLevel.HIGH,
                       "前缀过短，可能匹配过多文件")
            else:
                return (InputType.WILDCARD, RiskLevel.MEDIUM,
                       f"前缀模式: {prefix}")
        
        elif wildcard_count > 3:
            return (InputType.WILDCARD, RiskLevel.HIGH,
                   "通配符过多，可能匹配意外文件")
        
        else:
            return (InputType.WILDCARD, RiskLevel.MEDIUM,
                   "通配符模式，需要确认匹配范围")
    
    def _is_config_file(self, filename: str) -> bool:
        """
        检查是否为配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            是否为配置文件
        """
        config_extensions = ['.conf', '.config', '.cfg', '.ini', '.json', '.yaml', '.yml']
        config_files = ['Makefile', 'dockerfile', 'requirements.txt', 'package.json']
        
        # 检查扩展名
        for ext in config_extensions:
            if filename.lower().endswith(ext):
                return True
        
        # 检查特定文件名
        if filename.lower() in [f.lower() for f in config_files]:
            return True
        
        return False
    
    def _is_hidden_file(self, filename: str) -> bool:
        """
        检查是否为隐藏文件
        
        Args:
            filename: 文件名
            
        Returns:
            是否为隐藏文件
        """
        return filename.startswith('.')
    
    def _is_safe_extension(self, extension: str) -> bool:
        """
        检查是否为安全的文件扩展名
        
        Args:
            extension: 文件扩展名
            
        Returns:
            是否安全
        """
        safe_extensions = [
            'tmp', 'temp', 'log', 'cache', 'bak', 'backup',
            'old', 'orig', 'swp', 'swo', '~'
        ]
        return extension.lower() in safe_extensions
    
    def get_safe_patterns(self) -> List[str]:
        """
        获取安全模式示例
        
        Returns:
            安全模式列表
        """
        return [
            "*.tmp",           # 临时文件
            "*.log",           # 日志文件
            "*.cache",         # 缓存文件
            "*.bak",           # 备份文件
            "temp*",           # 临时文件前缀
            "backup_*",        # 备份文件前缀
            "*.old",           # 旧文件
            "specific_file.txt" # 具体文件名
        ]
    
    def get_risk_description(self, risk_level: RiskLevel) -> str:
        """
        获取风险等级描述
        
        Args:
            risk_level: 风险等级
            
        Returns:
            风险描述
        """
        descriptions = {
            RiskLevel.LOW: "低风险 - 通常可以安全删除",
            RiskLevel.MEDIUM: "中风险 - 需要用户确认",
            RiskLevel.HIGH: "高风险 - 需要额外确认和警告",
            RiskLevel.EXTREME: "极高风险 - 拒绝执行或需要特殊确认"
        }
        return descriptions.get(risk_level, "未知风险等级")


def validate_user_input(user_input: str) -> ValidationResult:
    """
    验证用户输入的便捷函数
    
    Args:
        user_input: 用户输入
        
    Returns:
        验证结果
    """
    validator = InputValidator()
    return validator.validate_input(user_input)


if __name__ == '__main__':
    # 测试用例
    validator = InputValidator()
    
    test_cases = [
        "*.tmp",                    # 安全扩展名
        "temp*",                    # 前缀模式
        "specific_file.txt",        # 精确文件名
        "*",                        # 危险模式
        "/bin/*",                   # 系统目录
        "test.*",                   # 通配符
        "^test.*\\.bak$",          # 正则表达式
        ".bashrc",                  # 配置文件
        "",                         # 空输入
        "a" * 300,                  # 过长输入
    ]
    
    print("=== 输入验证测试 ===")
    for pattern in test_cases:
        result = validator.validate_input(pattern)
        print(f"模式: '{pattern[:30]}{'...' if len(pattern) > 30 else ''}'")
        print(f"  有效: {result.is_valid}")
        print(f"  类型: {result.input_type.value}")
        print(f"  风险: {result.risk_level.value}")
        print(f"  说明: {result.message}")
        print()
    
    print("=== 安全模式示例 ===")
    for pattern in validator.get_safe_patterns():
        print(f"  {pattern}")