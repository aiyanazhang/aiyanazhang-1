"""
命令解析器模块
解析用户输入的命令和参数，进行格式化和预处理
"""

import re
import shlex
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """解析后的命令对象"""
    command: str          # 主命令
    args: List[str]       # 命令参数
    raw_input: str        # 原始输入
    working_dir: Optional[str] = None  # 工作目录
    environment: Dict[str, str] = None  # 环境变量
    timeout: Optional[int] = None       # 超时时间


class CommandParser:
    """命令解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 支持的重定向操作符
        self.redirect_operators = ['>', '>>', '<', '|', '2>', '2>>', '&>', '&>>']
        
        # 支持的组合操作符
        self.combine_operators = ['&&', '||', ';', '&']
    
    def parse(self, user_input: str) -> ParsedCommand:
        """
        解析用户输入的命令
        
        Args:
            user_input: 用户输入的原始命令字符串
            
        Returns:
            ParsedCommand: 解析后的命令对象
            
        Raises:
            ValueError: 命令格式不正确时抛出
        """
        if not user_input or not user_input.strip():
            raise ValueError("命令不能为空")
        
        # 清理输入
        cleaned_input = self._clean_input(user_input)
        
        # 检查是否包含不支持的操作符
        self._check_unsupported_operators(cleaned_input)
        
        # 解析命令和参数
        command, args = self._parse_command_and_args(cleaned_input)
        
        # 处理特殊参数
        processed_args, working_dir, environment, timeout = self._process_special_args(args)
        
        return ParsedCommand(
            command=command,
            args=processed_args,
            raw_input=user_input.strip(),
            working_dir=working_dir,
            environment=environment,
            timeout=timeout
        )
    
    def _clean_input(self, user_input: str) -> str:
        """清理用户输入"""
        # 移除首尾空白
        cleaned = user_input.strip()
        
        # 移除多余的空格
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 处理引号
        cleaned = self._normalize_quotes(cleaned)
        
        self.logger.debug(f"清理输入: '{user_input}' -> '{cleaned}'")
        return cleaned
    
    def _normalize_quotes(self, input_str: str) -> str:
        """标准化引号"""
        # 将中文引号转换为英文引号
        input_str = input_str.replace('"', '"').replace('"', '"')
        input_str = input_str.replace(''', "'").replace(''', "'")
        return input_str
    
    def _check_unsupported_operators(self, input_str: str):
        """检查不支持的操作符"""
        # 检查重定向操作符
        for op in self.redirect_operators:
            if op in input_str:
                raise ValueError(f"不支持重定向操作符: {op}")
        
        # 检查组合操作符
        for op in self.combine_operators:
            if op in input_str:
                raise ValueError(f"不支持命令组合操作符: {op}")
        
        # 检查管道操作
        if '|' in input_str:
            raise ValueError("不支持管道操作")
    
    def _parse_command_and_args(self, input_str: str) -> Tuple[str, List[str]]:
        """解析命令和参数"""
        try:
            # 使用shlex进行安全的shell风格解析
            tokens = shlex.split(input_str)
            
            if not tokens:
                raise ValueError("无法解析命令")
            
            command = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            
            self.logger.debug(f"解析命令: 命令='{command}', 参数={args}")
            return command, args
            
        except ValueError as e:
            if "No closing quotation" in str(e):
                raise ValueError("引号不匹配")
            raise ValueError(f"命令解析失败: {e}")
    
    def _process_special_args(self, args: List[str]) -> Tuple[List[str], Optional[str], Dict[str, str], Optional[int]]:
        """处理特殊参数"""
        processed_args = []
        working_dir = None
        environment = {}
        timeout = None
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # 处理工作目录参数
            if arg == '--workdir' and i + 1 < len(args):
                working_dir = args[i + 1]
                i += 2
                continue
            
            # 处理环境变量参数
            if arg == '--env' and i + 1 < len(args):
                env_pair = args[i + 1]
                if '=' in env_pair:
                    key, value = env_pair.split('=', 1)
                    environment[key] = value
                i += 2
                continue
            
            # 处理超时参数
            if arg == '--timeout' and i + 1 < len(args):
                try:
                    timeout = int(args[i + 1])
                except ValueError:
                    raise ValueError("超时时间必须是整数")
                i += 2
                continue
            
            # 普通参数
            processed_args.append(arg)
            i += 1
        
        return processed_args, working_dir, environment, timeout
    
    def validate_command_format(self, command: str) -> bool:
        """验证命令格式"""
        # 检查命令名是否合法
        if not re.match(r'^[a-zA-Z0-9_-]+$', command):
            return False
        
        # 检查命令长度
        if len(command) > 50:
            return False
        
        return True
    
    def validate_arguments(self, args: List[str]) -> bool:
        """验证参数格式"""
        for arg in args:
            # 检查参数长度
            if len(arg) > 500:
                return False
            
            # 检查危险字符
            dangerous_chars = ['`', '$', '(', ')', '{', '}', '[', ']']
            if any(char in arg for char in dangerous_chars):
                return False
        
        return True
    
    def expand_path(self, path: str) -> str:
        """扩展路径"""
        import os
        
        # 处理~符号
        if path.startswith('~'):
            path = os.path.expanduser(path)
        
        # 处理相对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        return path
    
    def format_for_container(self, parsed_command: ParsedCommand) -> List[str]:
        """格式化命令以在容器中执行"""
        command_list = [parsed_command.command]
        command_list.extend(parsed_command.args)
        
        # 转义特殊字符
        escaped_list = []
        for item in command_list:
            # 对包含空格或特殊字符的参数加引号
            if ' ' in item or any(char in item for char in ['"', "'", '\\', '*', '?']):
                escaped_list.append(f'"{item}"')
            else:
                escaped_list.append(item)
        
        return escaped_list
    
    def get_command_summary(self, parsed_command: ParsedCommand) -> str:
        """获取命令摘要用于日志"""
        summary = f"命令: {parsed_command.command}"
        
        if parsed_command.args:
            # 只显示前3个参数，避免日志过长
            displayed_args = parsed_command.args[:3]
            if len(parsed_command.args) > 3:
                displayed_args.append(f"... (+{len(parsed_command.args) - 3}个)")
            summary += f", 参数: {displayed_args}"
        
        if parsed_command.working_dir:
            summary += f", 工作目录: {parsed_command.working_dir}"
        
        if parsed_command.timeout:
            summary += f", 超时: {parsed_command.timeout}s"
        
        return summary


class CommandHistory:
    """命令历史记录"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.history: List[ParsedCommand] = []
    
    def add(self, command: ParsedCommand):
        """添加命令到历史记录"""
        self.history.append(command)
        
        # 保持历史记录大小
        if len(self.history) > self.max_size:
            self.history.pop(0)
    
    def get_recent(self, count: int = 10) -> List[ParsedCommand]:
        """获取最近的命令"""
        return self.history[-count:]
    
    def search(self, pattern: str) -> List[ParsedCommand]:
        """搜索命令历史"""
        results = []
        for cmd in self.history:
            if pattern in cmd.raw_input or pattern in cmd.command:
                results.append(cmd)
        return results
    
    def clear(self):
        """清空历史记录"""
        self.history.clear()