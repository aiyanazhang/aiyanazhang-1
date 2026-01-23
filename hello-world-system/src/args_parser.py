# -*- coding: utf-8 -*-
"""
参数处理模块
负责解析和验证命令行参数
"""

import argparse
import sys
from typing import Dict, List, Optional


class ArgumentParser:
    """命令行参数解析器"""
    
    def __init__(self):
        """初始化参数解析器"""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            prog='hello-world',
            description='一个可扩展的Hello World Python脚本系统',
            epilog='示例: python main.py --name "张三" --language zh --format json',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 基础参数
        parser.add_argument(
            '--name', '-n',
            type=str,
            help='问候对象的名称 (默认: World)'
        )
        
        parser.add_argument(
            '--language', '-l',
            choices=['en', 'zh'],
            help='输出语言 (en: 英文, zh: 中文, 默认: en)'
        )
        
        parser.add_argument(
            '--format', '-f',
            choices=['text', 'json', 'xml'],
            help='输出格式 (默认: text)'
        )
        
        # 可选参数
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='显示详细信息'
        )
        
        parser.add_argument(
            '--config', '-c',
            type=str,
            help='指定配置文件路径'
        )
        
        parser.add_argument(
            '--no-colors',
            action='store_true',
            help='禁用彩色输出'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='Hello World System 1.0.0'
        )
        
        return parser
    
    def parse(self, args: Optional[List[str]] = None) -> Dict:
        """
        解析命令行参数
        
        Args:
            args: 命令行参数列表，如果为None则使用sys.argv
            
        Returns:
            解析后的参数字典
            
        Raises:
            SystemExit: 当参数解析失败时
        """
        try:
            parsed_args = self.parser.parse_args(args)
            
            # 转换为字典并进行后处理
            args_dict = vars(parsed_args)
            
            # 处理特殊参数
            if args_dict.get('no_colors'):
                args_dict['enable_colors'] = False
                del args_dict['no_colors']
            else:
                args_dict['enable_colors'] = True
            
            # 验证参数
            self._validate_args(args_dict)
            
            return args_dict
            
        except argparse.ArgumentTypeError as e:
            self._handle_argument_error(f"参数类型错误: {e}")
        except ValueError as e:
            self._handle_argument_error(f"参数值错误: {e}")
        except Exception as e:
            self._handle_argument_error(f"参数解析失败: {e}")
    
    def _validate_args(self, args_dict: Dict) -> None:
        """
        验证参数的合法性
        
        Args:
            args_dict: 参数字典
            
        Raises:
            ValueError: 当参数不合法时
        """
        # 验证用户名长度
        name = args_dict.get('name')
        if name and len(name) > 100:
            raise ValueError("用户名长度不能超过100个字符")
        
        # 验证配置文件路径
        config_path = args_dict.get('config')
        if config_path:
            import os
            if not os.path.exists(config_path):
                raise ValueError(f"配置文件不存在: {config_path}")
            if not os.path.isfile(config_path):
                raise ValueError(f"配置路径不是有效文件: {config_path}")
    
    def _handle_argument_error(self, error_message: str) -> None:
        """
        处理参数错误
        
        Args:
            error_message: 错误信息
        """
        print(f"错误: {error_message}", file=sys.stderr)
        print("\n使用 --help 查看详细使用说明", file=sys.stderr)
        sys.exit(2)
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return self.parser.format_help()
    
    def get_usage(self) -> str:
        """获取使用说明"""
        return self.parser.format_usage()


class ArgumentValidator:
    """参数验证器"""
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        验证用户名
        
        Args:
            name: 用户名
            
        Returns:
            是否有效
        """
        if not name:
            return False
        if len(name) > 100:
            return False
        # 检查是否包含不安全字符
        unsafe_chars = ['<', '>', '&', '"', "'", '\\', '/', '|']
        return not any(char in name for char in unsafe_chars)
    
    @staticmethod
    def validate_language(language: str) -> bool:
        """
        验证语言代码
        
        Args:
            language: 语言代码
            
        Returns:
            是否有效
        """
        return language in ['en', 'zh']
    
    @staticmethod
    def validate_format(format_type: str) -> bool:
        """
        验证输出格式
        
        Args:
            format_type: 输出格式
            
        Returns:
            是否有效
        """
        return format_type in ['text', 'json', 'xml']