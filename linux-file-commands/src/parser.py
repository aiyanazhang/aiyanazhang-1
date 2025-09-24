#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令解析器模块
负责解析用户输入的命令行参数，并路由到相应的操作
"""

import argparse
import sys
from typing import Dict, List, Optional, Any

class CommandParser:
    """命令行参数解析器"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
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
        """解析命令行参数"""
        return self.parser.parse_args(args)
    
    def validate_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """验证参数并返回操作配置"""
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
        """确定要执行的操作"""
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
    """交互模式命令解析器"""
    
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