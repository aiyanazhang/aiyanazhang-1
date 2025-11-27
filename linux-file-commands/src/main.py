#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux文件操作命令查询工具主程序

本模块是Linux文件操作命令查询工具的主入口程序，负责整合所有功能模块，
提供命令行和交互式两种使用界面。支持命令查询、分类浏览、详细信息显示等功能。

主要功能：
- 命令行模式：支持直接通过参数执行查询操作
- 交互式模式：提供友好的交互界面，支持连续操作
- 多种输出格式：表格、列表、JSON等多种显示方式
- 高级搜索：支持关键词搜索和过滤功能
- 命令详情：提供详细的命令说明、参数、示例等信息

作者: AI Assistant
版本: 1.0.0
创建时间: 2024
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from parser import CommandParser, InteractiveParser
from category import CategoryManager, CategoryDisplayer
from search import AdvancedSearchEngine
from detail import CommandDetailManager, CommandDetailFormatter, CommandComparison
from formatter import OutputFormatter, OutputFormat, ColorTheme

class LinuxFileCommandsTool:
    """
    Linux文件操作命令工具主类
    
    这是整个工具的核心控制类，负责协调各个功能模块的工作，
    管理用户交互，处理命令行参数，并提供统一的输出格式。
    
    属性:
        data_dir (Path): 数据文件目录路径
        commands_file (Path): 命令数据文件路径
        categories_file (Path): 分类数据文件路径
        
    主要组件:
        - category_manager: 分类管理器
        - search_engine: 搜索引擎
        - detail_manager: 详情管理器
        - formatter: 输出格式化器
        - cmd_parser: 命令行解析器
        - interactive_parser: 交互式解析器
    
    作者: AI Assistant
    """
    
    def __init__(self, data_dir: str, enable_color: bool = True):
        """
        初始化Linux文件命令工具
        
        Args:
            data_dir (str): 数据文件目录路径
            enable_color (bool): 是否启用彩色输出，默认为True
            
        Raises:
            FileNotFoundError: 当数据文件不存在时抛出
            RuntimeError: 当组件初始化失败时抛出
        """
        self.data_dir = Path(data_dir)
        self.commands_file = self.data_dir / 'commands.json'
        self.categories_file = self.data_dir / 'categories.json'
        
        # 初始化组件
        self._initialize_components(enable_color)
    
    def _initialize_components(self, enable_color: bool) -> None:
        """
        初始化各个功能组件
        
        按照依赖关系初始化所有必要的组件，包括数据管理器、
        搜索引擎、格式化器等。确保组件间的正确协作。
        
        Args:
            enable_color (bool): 是否启用彩色输出
            
        Raises:
            FileNotFoundError: 当必要的数据文件不存在时
            RuntimeError: 当任何组件初始化失败时
        """
        # 检查数据文件
        if not self.commands_file.exists():
            raise FileNotFoundError(f"命令数据文件不存在: {self.commands_file}")
        
        try:
            # 核心组件
            self.category_manager = CategoryManager(
                str(self.commands_file), 
                str(self.categories_file)
            )
            self.category_displayer = CategoryDisplayer(self.category_manager)
            
            self.search_engine = AdvancedSearchEngine(
                str(self.commands_file),
                str(self.categories_file)
            )
            
            self.detail_manager = CommandDetailManager(str(self.commands_file))
            self.detail_formatter = CommandDetailFormatter(self.detail_manager)
            self.command_comparison = CommandComparison(self.detail_manager)
            
            # 格式化和解析组件
            self.theme = ColorTheme(enabled=enable_color)
            self.formatter = OutputFormatter(self.theme)
            self.cmd_parser = CommandParser()
            self.interactive_parser = InteractiveParser()
            
        except Exception as e:
            raise RuntimeError(f"初始化组件失败: {e}")
    
    def run_command_line(self, args: Optional[List[str]] = None) -> int:
        """
        运行命令行模式
        
        解析命令行参数并执行相应的操作。支持各种查询、搜索、
        列表显示等功能。
        
        Args:
            args (Optional[List[str]]): 命令行参数列表，如果为None则使用sys.argv
            
        Returns:
            int: 退出码，0表示成功，非0表示失败
            
        Examples:
            >>> tool = LinuxFileCommandsTool('/path/to/data')
            >>> exit_code = tool.run_command_line(['--search', 'find'])
        """
        try:
            # 解析参数
            parsed_args = self.cmd_parser.parse_args(args)
            config = self.cmd_parser.validate_args(parsed_args)
            
            # 执行操作
            result = self._execute_operation(config)
            
            if result:
                return 0
            else:
                return 1
                
        except SystemExit as e:
            # argparse 的 exit
            return e.code if e.code is not None else 0
        except Exception as e:
            error_msg = self.formatter.create_status_message(f"错误: {e}", 'error')
            print(error_msg, file=sys.stderr)
            return 1
    
    def run_interactive(self) -> int:
        """
        运行交互式模式
        
        提供一个友好的交互式界面，用户可以连续执行多个操作，
        包括搜索命令、查看详情、浏览分类等。支持命令补全和帮助。
        
        Returns:
            int: 退出码，0表示正常退出，非0表示异常退出
            
        Features:
            - 实时命令解析
            - 错误处理和提示
            - 优雅的中断处理
            - 彩色输出和格式化
        """
        try:
            self._print_welcome()
            
            while True:
                try:
                    # 获取用户输入
                    user_input = input(f"{self.theme.info}linux-cmd> {self.theme.reset}").strip()
                    
                    if not user_input:
                        continue
                    
                    # 解析交互命令
                    command_config = self.interactive_parser.parse_interactive_command(user_input)
                    
                    # 处理特殊命令
                    if command_config['type'] == 'quit':
                        break
                    elif command_config['type'] == 'help':
                        print(self.interactive_parser.get_help_text())
                        continue
                    elif command_config['type'] == 'invalid':
                        print(self.formatter.create_status_message(
                            command_config['message'], 'warning'
                        ))
                        continue
                    
                    # 执行操作
                    config = {
                        'operation': command_config,
                        'display': {'format': 'table', 'sort': 'name', 'no_color': False, 'page_size': 20},
                        'filters': {},
                        'config_file': None
                    }
                    
                    self._execute_operation(config)
                    print()  # 添加空行分隔
                    
                except KeyboardInterrupt:
                    print(f"\n{self.formatter.create_status_message('使用 quit 或 q 退出', 'info')}")
                except EOFError:
                    break
                except Exception as e:
                    error_msg = self.formatter.create_status_message(f"执行错误: {e}", 'error')
                    print(error_msg)
            
            print(f"{self.formatter.create_status_message('再见！', 'success')}")
            return 0
            
        except Exception as e:
            error_msg = self.formatter.create_status_message(f"交互模式错误: {e}", 'error')
            print(error_msg, file=sys.stderr)
            return 1
    
    def _print_welcome(self) -> None:
        """
        打印交互模式的欢迎信息
        
        显示工具的标题、版本信息和基本使用提示，
        为用户提供友好的开始体验。
        """
        welcome_text = f"""
{self.theme.header}╔═══════════════════════════════════════════════════════════════╗
║                 Linux 文件操作命令查询工具                    ║
║                    版本 1.0.0                                ║
╚═══════════════════════════════════════════════════════════════╝{self.theme.reset}

{self.theme.info}欢迎使用！输入 'help' 查看可用命令，输入 'quit' 退出。{self.theme.reset}
        """
        print(welcome_text)
    
    def _execute_operation(self, config: Dict[str, Any]) -> bool:
        """
        执行具体的操作
        
        根据配置信息调用相应的处理函数，执行用户请求的操作。
        这是所有操作的统一入口点。
        
        Args:
            config (Dict[str, Any]): 操作配置，包含操作类型、显示配置、过滤条件等
            
        Returns:
            bool: 操作是否成功执行
            
        Supported Operations:
            - list_all: 列出所有命令
            - list_by_category: 按分类列出命令
            - list_categories: 列出所有分类
            - search: 搜索命令
            - show_detail: 显示命令详情
            - interactive: 进入交互模式
        """
        operation = config['operation']
        display_config = config['display']
        filters = config['filters']
        
        op_type = operation['type']
        
        try:
            if op_type == 'list_all':
                return self._handle_list_all(display_config, filters)
            
            elif op_type == 'list_by_category':
                return self._handle_list_by_category(
                    operation['category'], display_config
                )
            
            elif op_type == 'list_categories':
                return self._handle_list_categories(display_config)
            
            elif op_type == 'search':
                return self._handle_search(
                    operation['keyword'], display_config, filters
                )
            
            elif op_type == 'show_detail':
                return self._handle_show_detail(
                    operation['command'], display_config
                )
            
            elif op_type == 'interactive':
                return self.run_interactive() == 0
            
            else:
                print(self.formatter.create_status_message(
                    f"未知操作类型: {op_type}", 'error'
                ))
                return False
                
        except Exception as e:
            print(self.formatter.create_status_message(
                f"执行操作失败: {e}", 'error'
            ))
            return False
    
    def _handle_list_all(self, display_config: Dict[str, Any], 
                        filters: Dict[str, str]) -> bool:
        """处理列出所有命令"""
        commands = self.category_manager.list_all_commands(
            filters=filters,
            sort_by=display_config.get('sort', 'name')
        )
        
        if not commands:
            print(self.formatter.create_status_message("没有找到匹配的命令", 'info'))
            return True
        
        # 准备显示数据
        display_data = []
        for cmd in commands:
            display_data.append({
                '命令': f"{self.theme.command}{cmd['name']}{self.theme.reset}",
                '描述': cmd.get('description', ''),
                '分类': ', '.join(cmd.get('categories', [])[:2])  # 只显示前两个分类
            })
        
        # 格式化输出
        format_type = self._get_output_format(display_config.get('format', 'table'))
        
        if display_config.get('page_size', 20) and len(display_data) > display_config['page_size']:
            # 分页显示
            paginated = self.formatter.format_with_pagination(
                display_data, format_type,
                page_size=display_config['page_size'],
                page_num=1
            )
            self.formatter.print_output(paginated['lines'])
            print(f"\n{self.theme.dim}{paginated['page_info']}{self.theme.reset}")
        else:
            # 直接显示
            lines = self.formatter.format_output(display_data, format_type)
            self.formatter.print_output(lines)
        
        return True
    
    def _handle_list_by_category(self, category: str, 
                                display_config: Dict[str, Any]) -> bool:
        """处理按分类列出命令"""
        category_info = self.category_displayer.display_category_commands(
            category, include_details=False
        )
        
        if category_info['count'] == 0:
            # 显示可用分类
            print(self.formatter.create_status_message(
                f"分类 '{category}' 不存在或没有命令", 'warning'
            ))
            
            print(f"\n{self.theme.info}可用分类:{self.theme.reset}")
            categories = self.category_displayer.display_all_categories()
            for cat in categories:
                print(f"  • {cat['name']}: {cat['description']}")
            
            return False
        
        # 显示分类信息
        print(f"{self.theme.header}=== {category} ({category_info['count']}个命令) ==={self.theme.reset}\n")
        
        # 准备显示数据
        display_data = []
        for cmd in category_info['commands']:
            display_data.append({
                '命令': f"{self.theme.command}{cmd['name']}{self.theme.reset}",
                '描述': cmd['description']
            })
        
        # 格式化输出
        format_type = self._get_output_format(display_config.get('format', 'list'))
        lines = self.formatter.format_output(display_data, format_type)
        self.formatter.print_output(lines)
        
        return True
    
    def _handle_list_categories(self, display_config: Dict[str, Any]) -> bool:
        """处理列出所有分类"""
        categories = self.category_displayer.display_all_categories()
        
        print(f"{self.theme.header}=== 命令分类 ==={self.theme.reset}\n")
        
        # 准备显示数据
        display_data = []
        for cat in categories:
            display_data.append({
                '分类': f"{self.theme.category}{cat['name']}{self.theme.reset}",
                '描述': cat['description'],
                '命令数': str(cat['command_count'])
            })
        
        # 格式化输出
        format_type = self._get_output_format(display_config.get('format', 'table'))
        lines = self.formatter.format_output(display_data, format_type)
        self.formatter.print_output(lines)
        
        return True
    
    def _handle_search(self, keyword: str, display_config: Dict[str, Any],
                      filters: Dict[str, str]) -> bool:
        """处理搜索命令"""
        results = self.search_engine.advanced_search(
            keyword, filters=filters, sort_by='relevance'
        )
        
        if not results:
            print(self.formatter.create_status_message(
                f"没有找到匹配 '{keyword}' 的命令", 'info'
            ))
            
            # 提供建议
            suggestions = self.search_engine.suggest_commands(keyword)
            if suggestions:
                print(f"\n{self.theme.info}您是否要查找:{self.theme.reset}")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            
            return False
        
        print(f"{self.theme.header}=== 搜索结果: '{keyword}' ({len(results)}个匹配) ==={self.theme.reset}\n")
        
        # 准备显示数据
        display_data = []
        for result in results:
            cmd = result['command']
            display_data.append({
                '命令': f"{self.theme.command}{cmd['name']}{self.theme.reset}",
                '描述': cmd.get('description', ''),
                '相关度': f"{result['relevance_score']}%",
                '匹配类型': result['match_type']
            })
        
        # 格式化输出
        format_type = self._get_output_format(display_config.get('format', 'table'))
        lines = self.formatter.format_output(display_data, format_type)
        self.formatter.print_output(lines)
        
        return True
    
    def _handle_show_detail(self, command: str, 
                           display_config: Dict[str, Any]) -> bool:
        """处理显示命令详情"""
        detail = self.detail_formatter.format_command_detail(command, style='full')
        
        if 'error' in detail:
            print(self.formatter.create_status_message(detail['error'], 'error'))
            
            if 'suggestions' in detail and detail['suggestions']:
                print(f"\n{self.theme.info}相似命令建议:{self.theme.reset}")
                for suggestion in detail['suggestions']:
                    print(f"  • {suggestion}")
            
            return False
        
        # 显示详细信息
        self._display_command_detail(detail)
        return True
    
    def _display_command_detail(self, detail: Dict[str, Any]) -> None:
        """显示命令详细信息"""
        name = detail['name']
        
        # 标题
        print(f"{self.theme.header}╔═══ {name} ═══╗{self.theme.reset}")
        print(f"{self.theme.description}{detail['description']}{self.theme.reset}")
        
        # 分类
        if detail['categories']:
            categories_str = ', '.join(detail['categories'])
            print(f"{self.theme.dim}分类: {categories_str}{self.theme.reset}")
        
        # 语法
        print(f"\n{self.theme.info}【语法】{self.theme.reset}")
        syntax = detail['syntax']
        print(f"  {self.theme.command}{syntax['basic']}{self.theme.reset}")
        
        if syntax.get('explanation'):
            print(f"  {self.theme.dim}{syntax['explanation']}{self.theme.reset}")
        
        # 常用选项
        if detail['options']:
            print(f"\n{self.theme.info}【常用选项】{self.theme.reset}")
            for opt in detail['options']:
                print(f"  {self.theme.option}{opt['option']:<8}{self.theme.reset} {opt['description']}")
        
        # 使用示例
        if detail['examples']:
            print(f"\n{self.theme.info}【使用示例】{self.theme.reset}")
            for example in detail['examples']:
                print(f"  {example['number']}. {self.theme.example}{example['command']}{self.theme.reset}")
                print(f"     {self.theme.dim}{example['explanation']}{self.theme.reset}")
        
        # 相关命令
        if detail['related_commands']:
            related_str = ', '.join(detail['related_commands'])
            print(f"\n{self.theme.info}【相关命令】{self.theme.reset}")
            print(f"  {related_str}")
        
        # 安全提示
        if detail['safety_tips']:
            print(f"\n{self.theme.warning}【安全提示】{self.theme.reset}")
            print(f"  {detail['safety_tips']}")
        
        # 附加信息
        additional_info = detail.get('additional_info', {})
        if additional_info:
            print(f"\n{self.theme.info}【附加信息】{self.theme.reset}")
            for key, value in additional_info.items():
                if key == 'type':
                    print(f"  命令类型: {value}")
                elif key == 'warning':
                    print(f"  {self.theme.warning}⚠ {value}{self.theme.reset}")
                elif key == 'learning_tip':
                    print(f"  💡 {value}")
                else:
                    print(f"  {key}: {value}")
    
    def _get_output_format(self, format_str: str) -> OutputFormat:
        """获取输出格式"""
        format_map = {
            'table': OutputFormat.TABLE,
            'list': OutputFormat.LIST,
            'json': OutputFormat.JSON,
            'tree': OutputFormat.TREE,
            'compact': OutputFormat.COMPACT
        }
        return format_map.get(format_str, OutputFormat.TABLE)

def main():
    """
    程序主入口函数
    
    负责程序的启动逻辑，包括参数检查、工具实例化、
    模式选择等。根据命令行参数决定启动命令行模式还是交互模式。
    
    逻辑流程:
    1. 确定数据目录位置
    2. 创建工具实例
    3. 根据参数选择运行模式
    4. 处理异常和退出码
    
    异常处理:
    - KeyboardInterrupt: 用户中断
    - 其他异常: 程序错误
    """
    # 获取数据目录
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    try:
        # 创建工具实例
        tool = LinuxFileCommandsTool(str(data_dir))
        
        # 检查命令行参数
        if len(sys.argv) == 1:
            # 没有参数，启动交互模式
            sys.exit(tool.run_interactive())
        else:
            # 有参数，运行命令行模式
            sys.exit(tool.run_command_line())
            
    except KeyboardInterrupt:
        print("\n程序被中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序错误: {e}", file=sys.stderr)
        sys.exit(1)

# 程序入口点
# 当脚本被直接执行时启动主函数
if __name__ == '__main__':
    main()