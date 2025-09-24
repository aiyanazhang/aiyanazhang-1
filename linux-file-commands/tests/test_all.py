#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux文件命令查询工具测试脚本
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import patch, StringIO

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser import CommandParser, InteractiveParser
from category import CategoryManager, CategoryDisplayer
from search import AdvancedSearchEngine
from detail import CommandDetailManager, CommandDetailFormatter
from formatter import OutputFormatter, OutputFormat, ColorTheme
from main import LinuxFileCommandsTool

class TestCommandParser(unittest.TestCase):
    """命令解析器测试"""
    
    def setUp(self):
        self.parser = CommandParser()
        self.interactive_parser = InteractiveParser()
    
    def test_list_command(self):
        """测试列表命令解析"""
        args = self.parser.parse_args(['--list'])
        config = self.parser.validate_args(args)
        self.assertEqual(config['operation']['type'], 'list_all')
    
    def test_search_command(self):
        """测试搜索命令解析"""
        args = self.parser.parse_args(['--search', 'file'])
        config = self.parser.validate_args(args)
        self.assertEqual(config['operation']['type'], 'search')
        self.assertEqual(config['operation']['keyword'], 'file')
    
    def test_interactive_parsing(self):
        """测试交互模式解析"""
        result = self.interactive_parser.parse_interactive_command('list')
        self.assertEqual(result['type'], 'list_all')
        
        result = self.interactive_parser.parse_interactive_command('search grep')
        self.assertEqual(result['type'], 'search')
        self.assertEqual(result['keyword'], 'grep')

class TestCategoryManager(unittest.TestCase):
    """分类管理器测试"""
    
    def setUp(self):
        data_dir = Path(__file__).parent.parent / 'data'
        self.manager = CategoryManager(
            str(data_dir / 'commands.json'),
            str(data_dir / 'categories.json')
        )
        self.displayer = CategoryDisplayer(self.manager)
    
    def test_get_all_categories(self):
        """测试获取所有分类"""
        categories = self.manager.get_all_categories()
        self.assertIsInstance(categories, dict)
        self.assertGreater(len(categories), 0)
    
    def test_get_category_commands(self):
        """测试获取分类命令"""
        commands = self.manager.get_category_commands('基础文件操作')
        self.assertIsInstance(commands, list)
    
    def test_list_all_commands(self):
        """测试列出所有命令"""
        commands = self.manager.list_all_commands()
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)

class TestSearchEngine(unittest.TestCase):
    """搜索引擎测试"""
    
    def setUp(self):
        data_dir = Path(__file__).parent.parent / 'data'
        self.engine = AdvancedSearchEngine(
            str(data_dir / 'commands.json'),
            str(data_dir / 'categories.json')
        )
    
    def test_exact_search(self):
        """测试精确搜索"""
        results = self.engine.search('ls')
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['command']['name'], 'ls')
    
    def test_keyword_search(self):
        """测试关键词搜索"""
        results = self.engine.search('文件')
        self.assertIsInstance(results, list)
    
    def test_suggestions(self):
        """测试命令建议"""
        suggestions = self.engine.suggest_commands('l')
        self.assertIsInstance(suggestions, list)

class TestDetailManager(unittest.TestCase):
    """详情管理器测试"""
    
    def setUp(self):
        data_dir = Path(__file__).parent.parent / 'data'
        self.manager = CommandDetailManager(str(data_dir / 'commands.json'))
        self.formatter = CommandDetailFormatter(self.manager)
    
    def test_get_command_detail(self):
        """测试获取命令详情"""
        detail = self.manager.get_command_detail('ls')
        self.assertIsNotNone(detail)
        self.assertEqual(detail['name'], 'ls')
    
    def test_command_exists(self):
        """测试命令存在检查"""
        self.assertTrue(self.manager.command_exists('ls'))
        self.assertFalse(self.manager.command_exists('nonexistent'))
    
    def test_format_command_detail(self):
        """测试命令详情格式化"""
        detail = self.formatter.format_command_detail('ls')
        self.assertIn('name', detail)
        self.assertIn('description', detail)
        self.assertEqual(detail['name'], 'ls')

class TestFormatter(unittest.TestCase):
    """格式化器测试"""
    
    def setUp(self):
        self.theme = ColorTheme(enabled=False)  # 禁用颜色以便测试
        self.formatter = OutputFormatter(self.theme)
    
    def test_table_format(self):
        """测试表格格式"""
        data = [{'name': 'ls', 'description': '列出目录内容'}]
        lines = self.formatter.format_output(data, OutputFormat.TABLE)
        self.assertIsInstance(lines, list)
        self.assertGreater(len(lines), 0)
    
    def test_list_format(self):
        """测试列表格式"""
        data = [{'name': 'ls', 'description': '列出目录内容'}]
        lines = self.formatter.format_output(data, OutputFormat.LIST)
        self.assertIsInstance(lines, list)
        self.assertGreater(len(lines), 0)
    
    def test_pagination(self):
        """测试分页"""
        data = [{'name': f'cmd{i}', 'description': f'描述{i}'} for i in range(25)]
        result = self.formatter.format_with_pagination(
            data, OutputFormat.LIST, page_size=10, page_num=1
        )
        self.assertEqual(result['total_pages'], 3)
        self.assertEqual(result['current_page'], 1)

class TestMainTool(unittest.TestCase):
    """主工具测试"""
    
    def setUp(self):
        data_dir = Path(__file__).parent.parent / 'data'
        self.tool = LinuxFileCommandsTool(str(data_dir), enable_color=False)
    
    def test_tool_initialization(self):
        """测试工具初始化"""
        self.assertIsNotNone(self.tool.category_manager)
        self.assertIsNotNone(self.tool.search_engine)
        self.assertIsNotNone(self.tool.detail_manager)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_list_all_operation(self, mock_stdout):
        """测试列出所有命令操作"""
        config = {
            'operation': {'type': 'list_all'},
            'display': {'format': 'list', 'sort': 'name', 'no_color': False, 'page_size': 5},
            'filters': {},
            'config_file': None
        }
        result = self.tool._execute_operation(config)
        self.assertTrue(result)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_search_operation(self, mock_stdout):
        """测试搜索操作"""
        config = {
            'operation': {'type': 'search', 'keyword': 'ls'},
            'display': {'format': 'table', 'sort': 'name', 'no_color': False, 'page_size': 20},
            'filters': {},
            'config_file': None
        }
        result = self.tool._execute_operation(config)
        self.assertTrue(result)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_detail_operation(self, mock_stdout):
        """测试详情显示操作"""
        config = {
            'operation': {'type': 'show_detail', 'command': 'ls'},
            'display': {'format': 'table', 'sort': 'name', 'no_color': False, 'page_size': 20},
            'filters': {},
            'config_file': None
        }
        result = self.tool._execute_operation(config)
        self.assertTrue(result)

def run_integration_tests():
    """运行集成测试"""
    print("=== 运行集成测试 ===")
    
    data_dir = Path(__file__).parent.parent / 'data'
    
    try:
        # 测试工具创建
        print("1. 测试工具初始化...")
        tool = LinuxFileCommandsTool(str(data_dir), enable_color=False)
        print("   ✓ 工具初始化成功")
        
        # 测试命令行参数
        print("2. 测试命令行参数解析...")
        result = tool.run_command_line(['--list'])
        print(f"   ✓ 列表命令执行: {'成功' if result == 0 else '失败'}")
        
        result = tool.run_command_line(['--search', 'file'])
        print(f"   ✓ 搜索命令执行: {'成功' if result == 0 else '失败'}")
        
        result = tool.run_command_line(['--detail', 'ls'])
        print(f"   ✓ 详情命令执行: {'成功' if result == 0 else '失败'}")
        
        result = tool.run_command_line(['--category', '基础文件操作'])
        print(f"   ✓ 分类命令执行: {'成功' if result == 0 else '失败'}")
        
        print("\n所有集成测试通过！")
        return True
        
    except Exception as e:
        print(f"集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Linux文件命令查询工具 - 测试套件")
    print("=" * 50)
    
    # 运行单元测试
    print("\n=== 运行单元测试 ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行集成测试
    print("\n" + "=" * 50)
    success = run_integration_tests()
    
    if success:
        print(f"\n✓ 所有测试通过！工具可以正常使用。")
        return 0
    else:
        print(f"\n✗ 测试失败！请检查错误信息。")
        return 1

if __name__ == '__main__':
    sys.exit(main())