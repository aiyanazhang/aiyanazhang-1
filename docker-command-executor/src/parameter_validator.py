"""
参数验证器模块
验证命令和参数的安全性和有效性
"""

import re
import os
import logging
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from .command_parser import ParsedCommand
from .config_manager import SecurityConfig


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class SecurityValidator:
    """安全验证器"""
    
    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        self.logger = logging.getLogger(__name__)
        
        # 危险路径模式
        self.dangerous_paths = {
            '/etc/passwd', '/etc/shadow', '/etc/sudoers',
            '/proc', '/sys', '/dev', '/boot',
            '/.ssh', '/root', '/var/log/auth.log'
        }
        
        # 危险参数模式
        self.dangerous_patterns = [
            r'.*\$\(.*\).*',      # 命令替换
            r'.*`.*`.*',          # 反引号命令替换  
            r'.*\${.*}.*',        # 变量替换
            r'.*\|\s*\w+.*',      # 管道操作
            r'.*[;&|].*',         # 命令连接符
            r'.*>\s*\w+.*',       # 重定向
            r'.*<\s*\w+.*',       # 输入重定向
        ]
        
        # 文件扩展名白名单
        self.safe_extensions = {
            '.txt', '.log', '.conf', '.cfg', '.ini', '.yml', '.yaml',
            '.json', '.xml', '.csv', '.md', '.rst', '.py', '.sh',
            '.js', '.html', '.css', '.sql'
        }
    
    def validate_command(self, parsed_command: ParsedCommand) -> ValidationResult:
        """验证完整命令"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        # 验证命令本身
        cmd_result = self._validate_command_name(parsed_command.command)
        errors.extend(cmd_result.errors)
        warnings.extend(cmd_result.warnings)
        if cmd_result.risk_level == 'high':
            risk_level = 'high'
        elif cmd_result.risk_level == 'medium' and risk_level != 'high':
            risk_level = 'medium'
        
        # 验证参数
        args_result = self._validate_arguments(parsed_command.args)
        errors.extend(args_result.errors)
        warnings.extend(args_result.warnings)
        if args_result.risk_level == 'high':
            risk_level = 'high'
        elif args_result.risk_level == 'medium' and risk_level != 'high':
            risk_level = 'medium'
        
        # 验证路径
        paths_result = self._validate_paths(parsed_command.args)
        errors.extend(paths_result.errors)
        warnings.extend(paths_result.warnings)
        if paths_result.risk_level == 'high':
            risk_level = 'high'
        elif paths_result.risk_level == 'medium' and risk_level != 'high':
            risk_level = 'medium'
        
        # 验证环境变量
        if parsed_command.environment:
            env_result = self._validate_environment(parsed_command.environment)
            errors.extend(env_result.errors)
            warnings.extend(env_result.warnings)
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.warning(f"命令验证失败: {parsed_command.command}, 错误: {errors}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )
    
    def _validate_command_name(self, command: str) -> ValidationResult:
        """验证命令名称"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        # 检查是否在被禁止的命令列表中
        if command in self.config.blocked_commands:
            errors.append(f"命令 '{command}' 被明确禁止")
            risk_level = 'high'
            return ValidationResult(False, errors, warnings, risk_level)
        
        # 检查是否在允许的命令列表中
        if command not in self.config.allowed_commands:
            errors.append(f"命令 '{command}' 不在允许列表中")
            risk_level = 'high'
            return ValidationResult(False, errors, warnings, risk_level)
        
        # 检查命令格式
        if not re.match(r'^[a-zA-Z0-9_-]+$', command):
            errors.append("命令名包含非法字符")
            risk_level = 'high'
        
        # 检查命令长度
        if len(command) > 50:
            errors.append("命令名过长")
            risk_level = 'medium'
        
        # 特殊命令风险评估
        high_risk_commands = ['find', 'grep', 'awk', 'sed']
        medium_risk_commands = ['cat', 'head', 'tail']
        
        if command in high_risk_commands:
            risk_level = 'medium'
            warnings.append(f"命令 '{command}' 需要谨慎使用")
        elif command in medium_risk_commands:
            if risk_level == 'low':
                risk_level = 'low'
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )
    
    def _validate_arguments(self, args: List[str]) -> ValidationResult:
        """验证命令参数"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        for i, arg in enumerate(args):
            # 检查参数长度
            if len(arg) > 1000:
                errors.append(f"参数 {i+1} 过长 (>{1000} 字符)")
                risk_level = 'high'
                continue
            
            # 检查危险模式
            for pattern in self.dangerous_patterns:
                if re.match(pattern, arg):
                    errors.append(f"参数 {i+1} 包含危险模式: {arg}")
                    risk_level = 'high'
                    break
            
            # 检查特殊字符
            dangerous_chars = ['`', '$', '(', ')', '{', '}', ';', '&', '|']
            found_chars = [char for char in dangerous_chars if char in arg]
            if found_chars:
                errors.append(f"参数 {i+1} 包含危险字符: {found_chars}")
                risk_level = 'high'
            
            # 检查null字节
            if '\x00' in arg:
                errors.append(f"参数 {i+1} 包含null字节")
                risk_level = 'high'
            
            # 检查unicode控制字符
            if any(ord(c) < 32 for c in arg if c not in ['\t', '\n', '\r']):
                warnings.append(f"参数 {i+1} 包含控制字符")
                if risk_level == 'low':
                    risk_level = 'medium'
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )
    
    def _validate_paths(self, args: List[str]) -> ValidationResult:
        """验证路径参数"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        for i, arg in enumerate(args):
            # 跳过非路径参数（选项等）
            if arg.startswith('-'):
                continue
            
            # 检查是否看起来像路径
            if '/' in arg or arg.startswith('.') or arg.startswith('~'):
                path_result = self._validate_single_path(arg)
                if not path_result.is_valid:
                    errors.extend([f"参数 {i+1} 路径错误: {err}" for err in path_result.errors])
                    risk_level = 'high'
                
                if path_result.warnings:
                    warnings.extend([f"参数 {i+1} 路径警告: {warn}" for warn in path_result.warnings])
                    if risk_level == 'low':
                        risk_level = 'medium'
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )
    
    def _validate_single_path(self, path: str) -> ValidationResult:
        """验证单个路径"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        # 标准化路径
        try:
            normalized_path = os.path.normpath(path)
        except Exception:
            errors.append("路径格式无效")
            return ValidationResult(False, errors, warnings, 'high')
        
        # 检查路径遍历
        if '..' in normalized_path:
            errors.append("路径包含父目录引用 (..)")
            risk_level = 'high'
        
        # 检查绝对路径中的危险目录
        if os.path.isabs(normalized_path):
            for dangerous_path in self.dangerous_paths:
                if normalized_path.startswith(dangerous_path):
                    errors.append(f"访问危险路径: {dangerous_path}")
                    risk_level = 'high'
                    break
        
        # 检查隐藏文件/目录
        if '/.ssh' in normalized_path or path.startswith('.'):
            warnings.append("访问隐藏文件或目录")
            if risk_level == 'low':
                risk_level = 'medium'
        
        # 检查文件扩展名
        _, ext = os.path.splitext(normalized_path)
        if ext and ext.lower() not in self.safe_extensions:
            warnings.append(f"文件扩展名可能不安全: {ext}")
            if risk_level == 'low':
                risk_level = 'medium'
        
        # 检查路径长度
        if len(normalized_path) > 255:
            errors.append("路径过长")
            risk_level = 'medium'
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )
    
    def _validate_environment(self, env_vars: Dict[str, str]) -> ValidationResult:
        """验证环境变量"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        # 危险的环境变量名
        dangerous_env_vars = {
            'LD_PRELOAD', 'LD_LIBRARY_PATH', 'PATH', 'SHELL',
            'IFS', 'PS1', 'PS2', 'PROMPT_COMMAND'
        }
        
        for key, value in env_vars.items():
            # 检查变量名
            if not re.match(r'^[A-Z_][A-Z0-9_]*$', key):
                errors.append(f"环境变量名格式无效: {key}")
                risk_level = 'high'
            
            if key in dangerous_env_vars:
                errors.append(f"危险的环境变量: {key}")
                risk_level = 'high'
            
            # 检查变量值
            if len(value) > 1000:
                errors.append(f"环境变量值过长: {key}")
                risk_level = 'medium'
            
            # 检查危险字符
            if any(char in value for char in ['`', '$', ';', '&', '|']):
                errors.append(f"环境变量值包含危险字符: {key}")
                risk_level = 'high'
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )


class ResourceValidator:
    """资源验证器"""
    
    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        self.logger = logging.getLogger(__name__)
    
    def validate_resource_limits(self, parsed_command: ParsedCommand) -> ValidationResult:
        """验证资源限制"""
        errors = []
        warnings = []
        risk_level = 'low'
        
        # 检查超时时间
        if parsed_command.timeout:
            if parsed_command.timeout > 300:  # 5分钟
                errors.append("超时时间过长 (>5分钟)")
                risk_level = 'medium'
            elif parsed_command.timeout < 1:
                errors.append("超时时间过短 (<1秒)")
                risk_level = 'medium'
        
        # 检查可能消耗大量资源的命令
        resource_intensive_commands = {
            'find': '可能消耗大量磁盘I/O',
            'grep': '可能消耗大量内存',
            'awk': '可能消耗大量CPU',
            'sed': '可能消耗大量内存'
        }
        
        if parsed_command.command in resource_intensive_commands:
            warnings.append(resource_intensive_commands[parsed_command.command])
            if risk_level == 'low':
                risk_level = 'medium'
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level
        )


class ParameterValidator:
    """参数验证器主类"""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_validator = SecurityValidator(security_config)
        self.resource_validator = ResourceValidator(security_config)
        self.logger = logging.getLogger(__name__)
    
    def validate(self, parsed_command: ParsedCommand) -> ValidationResult:
        """执行完整验证"""
        self.logger.info(f"开始验证命令: {parsed_command.command}")
        
        # 安全验证
        security_result = self.security_validator.validate_command(parsed_command)
        
        # 资源验证  
        resource_result = self.resource_validator.validate_resource_limits(parsed_command)
        
        # 合并结果
        all_errors = security_result.errors + resource_result.errors
        all_warnings = security_result.warnings + resource_result.warnings
        
        # 确定最高风险级别
        risk_levels = ['low', 'medium', 'high']
        max_risk = max(
            risk_levels.index(security_result.risk_level),
            risk_levels.index(resource_result.risk_level)
        )
        final_risk_level = risk_levels[max_risk]
        
        is_valid = len(all_errors) == 0
        
        result = ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            risk_level=final_risk_level
        )
        
        # 记录验证结果
        if is_valid:
            self.logger.info(f"命令验证通过: {parsed_command.command}, 风险级别: {final_risk_level}")
            if all_warnings:
                self.logger.warning(f"验证警告: {all_warnings}")
        else:
            self.logger.error(f"命令验证失败: {parsed_command.command}, 错误: {all_errors}")
        
        return result
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """获取验证结果摘要"""
        if result.is_valid:
            summary = f"✓ 验证通过 (风险级别: {result.risk_level})"
            if result.warnings:
                summary += f"\n警告: {'; '.join(result.warnings)}"
        else:
            summary = f"✗ 验证失败\n错误: {'; '.join(result.errors)}"
            if result.warnings:
                summary += f"\n警告: {'; '.join(result.warnings)}"
        
        return summary