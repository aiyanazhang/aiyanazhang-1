#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令解析器模块

本模块负责解析用户输入的命令行参数和交互式命令，提供两种不同的解析器：
1. CommandParser: 处理命令行参数解析，支持各种选项和过滤条件
2. InteractiveParser: 处理交互模式下的用户输入，支持简化的命令语法

主要功能:
- 命令行参数解析和验证
- 交互式命令识别和路由
- 参数有效性检查
- 帮助信息生成
- 错误处理和用户提示

支持的操作类型:
- list_all: 列出所有命令
- list_by_category: 按分类列出命令
- search: 搜索命令
- show_detail: 显示命令详情
- interactive: 进入交互模式

作者: AI Assistant
版本: 1.0.0
创建时间: 2024
"""

import argparse
import sys
from typing import Dict, List, Optional, Any

class CommandParser:
    """
    命令行参数解析器
    
    负责解析和验证从命令行传入的参数，将用户输入转换为程序可以理解的配置。
    支持多种操作模式和丰富的显示选项，提供灵活的过滤和排序功能。
    
    主要职责:
    - 定义和管理命令行参数结构
    - 解析用户输入的参数
    - 验证参数的有效性和完整性
    - 生成标准化的操作配置
    - 提供帮助和使用说明
    
    属性:
        parser (argparse.ArgumentParser): argparse解析器实例
    
    使用示例:
        >>> parser = CommandParser()
        >>> args = parser.parse_args(['--search', 'find'])
        >>> config = parser.validate_args(args)
    
    作者: AI Assistant
    """
    
    def __init__(self):
        """
        初始化命令行参数解析器
        
        创建argparse解析器实例并配置所有支持的命令行选项。
        设置互斥组、参数组和默认值等。
        """
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        创建并配置argparse参数解析器
        
        定义所有支持的命令行选项，包括主要操作选项、显示选项、
        过滤选项等。设置参数的类型、默认值、帮助信息等。
        
        Returns:
            argparse.ArgumentParser: 配置完成的参数解析器
            
        Features:
            - 互斥的主要操作选项
            - 分组的显示和过滤选项
            - 详细的帮助信息和使用示例
            - 自定义的格式化器
        """
        parser = argparse.ArgumentParser(
            prog='linux-file-commands',
            description='Linux文件操作命令查询工具',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  %(prog)s --list                    # 显示所有命令
  %(prog)s --category 基础文件操作    # 显示指定分类的命令
  %(prog)s --search grep            # 搜索包含关键词的命令
  %(prog)s --detail ls              # 显示指定命令的详细信息
  %(prog)s --interactive            # 启动交互模式
            """
        )
        
        # 主要操作选项（互斥）
        main_group = parser.add_mutually_exclusive_group()
        main_group.add_argument(
            '--list', '-l',
            action='store_true',
            help='显示所有可用命令'
        )
        main_group.add_argument(
            '--category', '-c',
            type=str,
            metavar='CATEGORY',
            help='按分类显示命令'
        )
        main_group.add_argument(
            '--search', '-s',
            type=str,
            metavar='KEYWORD',
            help='搜索命令（支持命令名和描述）'
        )
        main_group.add_argument(
            '--detail', '-d',
            type=str,
            metavar='COMMAND',
            help='显示指定命令的详细信息'
        )
        main_group.add_argument(
            '--interactive', '-i',
            action='store_true',
            help='启动交互模式'
        )
        
        # 显示选项
        display_group = parser.add_argument_group('显示选项')
        display_group.add_argument(
            '--format', '-f',
            choices=['table', 'list', 'json'],
            default='table',
            help='输出格式 (默认: table)'
        )
        display_group.add_argument(
            '--sort',
            choices=['name', 'category', 'usage'],
            default='name',
            help='排序方式 (默认: name)'
        )
        display_group.add_argument(
            '--no-color',
            action='store_true',
            help='禁用颜色输出'
        )
        display_group.add_argument(
            '--page-size',
            type=int,
            default=20,
            metavar='N',
            help='分页大小 (默认: 20)'
        )
        
        # 过滤选项
        filter_group = parser.add_argument_group('过滤选项')
        filter_group.add_argument(
            '--difficulty',
            choices=['初级', '中级', '高级'],
            help='按难度级别过滤'
        )
        filter_group.add_argument(
            '--frequency',
            choices=['高频', '中频', '低频'],
            help='按使用频率过滤'
        )
        
        # 其他选项
        parser.add_argument(
            '--config',
            type=str,
            metavar='FILE',
            help='指定配置文件路径'
        )
        parser.add_argument(
            '--version', '-v',
            action='version',
            version='%(prog)s 1.0.0'
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        解析命令行参数
        
        使用argparse解析器处理命令行参数，如果解析失败会自动显示
        错误信息和帮助。
        
        Args:
            args (Optional[List[str]]): 要解析的参数列表，如果为None则使用sys.argv
            
        Returns:
            argparse.Namespace: 解析后的参数对象
            
        Raises:
            SystemExit: 当参数解析失败或用户请求帮助时
        """
        return self.parser.parse_args(args)
    
    def validate_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        验证参数并生成操作配置
        
        对解析后的参数进行验证，并转换为程序内部使用的标准化配置格式。
        检查参数的有效性和一致性。
        
        Args:
            args (argparse.Namespace): argparse解析后的参数对象
            
        Returns:
            Dict[str, Any]: 标准化的配置字典，包含以下键：
                - operation: 操作类型和参数
                - display: 显示选项配置
                - filters: 过滤条件配置
                - config_file: 配置文件路径
                
        Raises:
            ValueError: 当参数验证失败时
            
        Example:
            配置结构:
            {
                'operation': {'type': 'search', 'keyword': 'find'},
                'display': {'format': 'table', 'sort': 'name'},
                'filters': {'difficulty': '中级'},
                'config_file': None
            }
        """
        config = {
            'operation': self._determine_operation(args),
            'display': self._extract_display_options(args),
            'filters': self._extract_filter_options(args),
            'config_file': args.config
        }
        
        # 验证操作参数
        self._validate_operation_params(config['operation'])
        
        return config
    
    def _determine_operation(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        根据参数确定要执行的操作类型
        
        分析解析后的参数，确定用户想要执行的具体操作。
        处理互斥选项的优先级和默认行为。
        
        Args:
            args (argparse.Namespace): 解析后的参数对象
            
        Returns:
            Dict[str, Any]: 操作配置字典，包含操作类型和相关参数
            
        Operation Types:
            - list_all: 列出所有命令
            - list_by_category: 按分类列出命令
            - search: 搜索命令
            - show_detail: 显示命令详情
            - interactive: 交互模式（默认）
        """
        if args.list:
            return {'type': 'list_all'}
        elif args.category:
            return {'type': 'list_by_category', 'category': args.category}
        elif args.search:
            return {'type': 'search', 'keyword': args.search}
        elif args.detail:
            return {'type': 'show_detail', 'command': args.detail}
        elif args.interactive:
            return {'type': 'interactive'}
        else:
            # 默认操作
            return {'type': 'interactive'}
    
    def _extract_display_options(self, args: argparse.Namespace) -> Dict[str, Any]:
        """提取显示选项"""
        return {
            'format': args.format,
            'sort': args.sort,
            'no_color': args.no_color,
            'page_size': args.page_size
        }
    
    def _extract_filter_options(self, args: argparse.Namespace) -> Dict[str, Any]:
        """提取过滤选项"""
        filters = {}
        if args.difficulty:
            filters['difficulty'] = args.difficulty
        if args.frequency:
            filters['frequency'] = args.frequency
        return filters
    
    def _validate_operation_params(self, operation: Dict[str, Any]) -> None:
        """验证操作参数"""
        op_type = operation['type']
        
        if op_type == 'list_by_category':
            category = operation.get('category')
            if not category:
                raise ValueError("分类参数不能为空")
        
        elif op_type == 'search':
            keyword = operation.get('keyword')
            if not keyword or len(keyword.strip()) < 2:
                raise ValueError("搜索关键词至少需要2个字符")
        
        elif op_type == 'show_detail':
            command = operation.get('command')
            if not command:
                raise ValueError("命令名称不能为空")
    
    def print_help(self) -> None:
        """打印帮助信息"""
        self.parser.print_help()
    
    def print_usage(self) -> None:
        """打印使用方法"""
        self.parser.print_usage()

class InteractiveParser:
    """
    交互模式命令解析器
    
    专门处理交互模式下用户输入的命令，提供更加友好和简化的命令语法。
    支持命令补全、别名、简写等交互式特性。
    
    主要功能:
    - 解析交互式命令输入
    - 提供命令别名和简写支持
    - 生成帮助和提示信息
    - 处理特殊命令（如quit、help等）
    - 错误恢复和用户引导
    
    支持的交互命令:
    - help, h, ?: 显示帮助
    - quit, q, exit: 退出程序
    - list, l: 列出所有命令
    - search <keyword>, s <keyword>: 搜索命令
    - detail <command>, d <command>: 显示详情
    - category <name>, c <name>: 按分类列出
    
    作者: AI Assistant
    """
    
    def __init__(self):
        self.commands = {
            'help': self._help_command,
            'h': self._help_command,
            'list': self._list_command,
            'l': self._list_command,
            'category': self._category_command,
            'cat': self._category_command,
            'c': self._category_command,
            'search': self._search_command,
            's': self._search_command,
            'detail': self._detail_command,
            'd': self._detail_command,
            'quit': self._quit_command,
            'q': self._quit_command,
            'exit': self._quit_command
        }
    
    def parse_interactive_command(self, user_input: str) -> Dict[str, Any]:
        """解析交互模式下的用户输入"""
        if not user_input.strip():
            return {'type': 'invalid', 'message': '请输入命令'}
        
        parts = user_input.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            return self.commands[command](args)
        else:
            return {
                'type': 'invalid',
                'message': f'未知命令: {command}，输入 help 查看可用命令'
            }
    
    def _help_command(self, args: List[str]) -> Dict[str, Any]:
        """帮助命令"""
        return {'type': 'help'}
    
    def _list_command(self, args: List[str]) -> Dict[str, Any]:
        """列表命令"""
        return {'type': 'list_all'}
    
    def _category_command(self, args: List[str]) -> Dict[str, Any]:
        """分类命令"""
        if not args:
            return {'type': 'list_categories'}
        return {'type': 'list_by_category', 'category': ' '.join(args)}
    
    def _search_command(self, args: List[str]) -> Dict[str, Any]:
        """搜索命令"""
        if not args:
            return {'type': 'invalid', 'message': '请提供搜索关键词'}
        return {'type': 'search', 'keyword': ' '.join(args)}
    
    def _detail_command(self, args: List[str]) -> Dict[str, Any]:
        """详情命令"""
        if not args:
            return {'type': 'invalid', 'message': '请提供命令名称'}
        return {'type': 'show_detail', 'command': args[0]}
    
    def _quit_command(self, args: List[str]) -> Dict[str, Any]:
        """退出命令"""
        return {'type': 'quit'}
    
    def get_help_text(self) -> str:
        """获取交互模式帮助文本"""
        return """
可用命令:
  help, h                    - 显示此帮助信息
  list, l                    - 显示所有命令
  category [分类名], cat, c   - 显示分类或指定分类的命令
  search <关键词>, s         - 搜索命令
  detail <命令名>, d         - 显示命令详情
  quit, q, exit             - 退出程序

示例:
  > list                    # 显示所有命令
  > category 基础文件操作    # 显示基础文件操作分类的命令
  > search file            # 搜索包含"file"的命令
  > detail ls              # 显示ls命令的详细信息
        """

def main():
    """测试函数"""
    parser = CommandParser()
    
    # 测试命令行解析
    test_args = [
        ['--list'],
        ['--category', '基础文件操作'],
        ['--search', 'file'],
        ['--detail', 'ls'],
        ['--interactive']
    ]
    
    for args in test_args:
        try:
            parsed = parser.parse_args(args)
            config = parser.validate_args(parsed)
            print(f"参数: {args}")
            print(f"配置: {config}")
            print("-" * 50)
        except Exception as e:
            print(f"解析失败: {args}, 错误: {e}")
    
    # 测试交互解析
    interactive = InteractiveParser()
    test_inputs = [
        'help',
        'list',
        'category 基础文件操作',
        'search file',
        'detail ls',
        'invalid_command'
    ]
    
    print("\n交互模式测试:")
    for inp in test_inputs:
        result = interactive.parse_interactive_command(inp)
        print(f"输入: '{inp}' -> {result}")

if __name__ == '__main__':
    main()