#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World系统单元测试套件
测试所有模块的功能
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from args_parser import ArgumentParser, ArgumentValidator
from greeting import GreetingGenerator, GreetingFormatter
from output import OutputManager, OutputValidator
from config import ConfigManager, ConfigValidator
from i18n import LanguageManager, get_text, set_language


class TestArgumentParser(unittest.TestCase):
    """测试参数解析器"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = ArgumentParser()
    
    def test_parse_no_args(self):
        """测试无参数解析"""
        result = self.parser.parse([])
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('enable_colors'))
    
    def test_parse_name_arg(self):
        """测试名称参数"""
        result = self.parser.parse(['--name', 'TestUser'])
        self.assertEqual(result['name'], 'TestUser')
    
    def test_parse_language_arg(self):
        """测试语言参数"""
        result = self.parser.parse(['--language', 'zh'])
        self.assertEqual(result['language'], 'zh')
    
    def test_parse_format_arg(self):
        """测试格式参数"""
        result = self.parser.parse(['--format', 'json'])
        self.assertEqual(result['format'], 'json')
    
    def test_parse_verbose_flag(self):
        """测试详细模式标志"""
        result = self.parser.parse(['--verbose'])
        self.assertTrue(result['verbose'])
    
    def test_parse_no_colors_flag(self):
        """测试禁用颜色标志"""
        result = self.parser.parse(['--no-colors'])
        self.assertFalse(result['enable_colors'])
    
    def test_parse_invalid_language(self):
        """测试无效语言参数"""
        with self.assertRaises(SystemExit):
            self.parser.parse(['--language', 'invalid'])
    
    def test_parse_invalid_format(self):
        """测试无效格式参数"""
        with self.assertRaises(SystemExit):
            self.parser.parse(['--format', 'invalid'])
    
    def test_argument_validator_valid_name(self):
        """测试有效名称验证"""
        self.assertTrue(ArgumentValidator.validate_name('TestUser'))
        self.assertTrue(ArgumentValidator.validate_name('张三'))
    
    def test_argument_validator_invalid_name(self):
        """测试无效名称验证"""
        self.assertFalse(ArgumentValidator.validate_name(''))
        self.assertFalse(ArgumentValidator.validate_name('<script>'))
        self.assertFalse(ArgumentValidator.validate_name('a' * 101))
    
    def test_argument_validator_language(self):
        """测试语言验证"""
        self.assertTrue(ArgumentValidator.validate_language('en'))
        self.assertTrue(ArgumentValidator.validate_language('zh'))
        self.assertFalse(ArgumentValidator.validate_language('fr'))
    
    def test_argument_validator_format(self):
        """测试格式验证"""
        self.assertTrue(ArgumentValidator.validate_format('text'))
        self.assertTrue(ArgumentValidator.validate_format('json'))
        self.assertTrue(ArgumentValidator.validate_format('xml'))
        self.assertFalse(ArgumentValidator.validate_format('yaml'))


class TestGreetingGenerator(unittest.TestCase):
    """测试问候生成器"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = GreetingGenerator()
    
    def test_generate_default(self):
        """测试默认问候生成"""
        result = self.generator.generate()
        self.assertIn('message', result)
        self.assertIn('World', result['message'])
        self.assertEqual(result['language'], 'en')
    
    def test_generate_with_name(self):
        """测试带名称的问候生成"""
        result = self.generator.generate(name='TestUser')
        self.assertIn('TestUser', result['message'])
        self.assertEqual(result['name'], 'TestUser')
    
    def test_generate_chinese(self):
        """测试中文问候生成"""
        result = self.generator.generate(name='张三', language='zh')
        self.assertIn('你好', result['message'])
        self.assertIn('张三', result['message'])
        self.assertEqual(result['language'], 'zh')
    
    def test_generate_verbose(self):
        """测试详细模式问候生成"""
        result = self.generator.generate(verbose=True)
        self.assertTrue(result['verbose'])
        self.assertIn('timestamp', result)
        self.assertEqual(result['template_used'], 'verbose')
    
    def test_generate_invalid_language(self):
        """测试无效语言回退"""
        result = self.generator.generate(language='invalid')
        self.assertEqual(result['language'], 'en')
    
    def test_sanitize_name(self):
        """测试名称清理"""
        result = self.generator.generate(name='<script>alert("test")</script>')
        self.assertNotIn('<script>', result['name'])
        self.assertIn('&lt;', result['name'])
    
    def test_long_name_truncation(self):
        """测试长名称截断"""
        long_name = 'a' * 100
        result = self.generator.generate(name=long_name)
        self.assertTrue(len(result['name']) <= 53)  # 50 + "..."
    
    def test_get_supported_languages(self):
        """测试获取支持的语言"""
        languages = self.generator.get_supported_languages()
        self.assertIn('en', languages)
        self.assertIn('zh', languages)
    
    def test_add_language_template(self):
        """测试添加语言模板"""
        new_template = {
            'basic': 'Bonjour, {name}!',
            'verbose': 'Bonjour, {name}! Bienvenue.\nHeure: {timestamp}',
            'default_name': 'Monde'
        }
        self.generator.add_language_template('fr', new_template)
        self.assertIn('fr', self.generator.get_supported_languages())
    
    def test_greeting_formatter_box_style(self):
        """测试盒子风格格式化"""
        formatted = GreetingFormatter.add_decorations('Hello, World!', 'box')
        self.assertIn('+', formatted)
        self.assertIn('|', formatted)
    
    def test_greeting_formatter_stars_style(self):
        """测试星号风格格式化"""
        formatted = GreetingFormatter.add_decorations('Hello, World!', 'stars')
        self.assertIn('***', formatted)
    
    def test_greeting_formatter_add_emoji(self):
        """测试添加表情符号"""
        formatted = GreetingFormatter.add_emoji('Hello, World!', 'en')
        self.assertIn('👋', formatted)


class TestOutputManager(unittest.TestCase):
    """测试输出管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = OutputManager()
        self.sample_message = {
            'message': 'Hello, TestUser!',
            'name': 'TestUser',
            'language': 'en',
            'timestamp': '2024-01-01 12:00:00',
            'verbose': False,
            'template_used': 'basic'
        }
    
    def test_format_text_output(self):
        """测试文本格式输出"""
        result = self.manager.format_output(self.sample_message, 'text')
        self.assertIn('Hello, TestUser!', result)
    
    def test_format_json_output(self):
        """测试JSON格式输出"""
        result = self.manager.format_output(self.sample_message, 'json')
        self.assertTrue(OutputValidator.validate_json(result))
        data = json.loads(result)
        self.assertIn('greeting', data)
    
    def test_format_xml_output(self):
        """测试XML格式输出"""
        result = self.manager.format_output(self.sample_message, 'xml')
        self.assertTrue(OutputValidator.validate_xml(result))
        self.assertIn('<greeting', result)
    
    def test_format_verbose_text(self):
        """测试详细文本格式"""
        verbose_message = self.sample_message.copy()
        verbose_message['verbose'] = True
        result = self.manager.format_output(verbose_message, 'text')
        self.assertIn('详细信息', result)
    
    def test_invalid_format_type(self):
        """测试无效格式类型"""
        with self.assertRaises(ValueError):
            self.manager.format_output(self.sample_message, 'invalid')
    
    @patch('sys.stdout.isatty', return_value=True)
    @patch('os.environ.get', return_value='xterm')
    def test_color_support_detection(self, mock_env, mock_isatty):
        """测试颜色支持检测"""
        self.assertTrue(self.manager._supports_color())
    
    def test_add_colors(self):
        """测试添加颜色"""
        content = "Hello, TestUser!\n=== 详细信息 ===\n用户名: TestUser"
        colored = self.manager._add_colors(content, self.sample_message)
        # 检查是否包含ANSI颜色代码
        self.assertIn('\033[', colored)
    
    def test_display_with_mock_stdout(self):
        """测试显示输出"""
        mock_stdout = MagicMock()
        self.manager.display('Test output', mock_stdout)
        mock_stdout.write.assert_called()
    
    def test_save_to_file(self):
        """测试保存到文件"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success = self.manager.save_to_file('Test content', tmp_path)
            self.assertTrue(success)
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, 'Test content')
        finally:
            os.unlink(tmp_path)


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = ConfigManager()
    
    def test_default_config(self):
        """测试默认配置"""
        config = self.manager.load_config()
        self.assertIn('default_language', config)
        self.assertIn('default_format', config)
        self.assertEqual(config['default_language'], 'en')
    
    def test_get_config_value(self):
        """测试获取配置值"""
        self.manager.current_config = {'test_key': 'test_value'}
        value = self.manager.get('test_key')
        self.assertEqual(value, 'test_value')
    
    def test_get_nested_config_value(self):
        """测试获取嵌套配置值"""
        self.manager.current_config = {
            'output': {
                'show_timestamp': True
            }
        }
        value = self.manager.get('output.show_timestamp')
        self.assertTrue(value)
    
    def test_get_config_value_with_default(self):
        """测试获取配置值带默认值"""
        value = self.manager.get('nonexistent_key', 'default_value')
        self.assertEqual(value, 'default_value')
    
    def test_set_config_value(self):
        """测试设置配置值"""
        self.manager.set('test_key', 'test_value')
        self.assertEqual(self.manager.current_config['test_key'], 'test_value')
    
    def test_set_nested_config_value(self):
        """测试设置嵌套配置值"""
        self.manager.set('output.show_timestamp', False)
        self.assertFalse(self.manager.current_config['output']['show_timestamp'])
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            test_config = {'test_key': 'test_value'}
            success = self.manager.save_config(test_config, tmp_path)
            self.assertTrue(success)
            
            # 创建新的管理器实例来测试加载
            new_manager = ConfigManager(tmp_path)
            loaded_config = new_manager.load_config()
            self.assertEqual(loaded_config['test_key'], 'test_value')
        finally:
            os.unlink(tmp_path)
    
    def test_invalid_config_file(self):
        """测试无效配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write('invalid json content')
            tmp_path = tmp.name
        
        try:
            manager = ConfigManager(tmp_path)
            config = manager.load_config()
            # 应该回退到默认配置
            self.assertEqual(config['default_language'], 'en')
        finally:
            os.unlink(tmp_path)
    
    def test_reset_to_default(self):
        """测试重置为默认配置"""
        self.manager.set('test_key', 'test_value')
        self.manager.reset_to_default()
        self.assertNotIn('test_key', self.manager.current_config)
    
    def test_config_validator(self):
        """测试配置验证器"""
        valid, error = ConfigValidator.validate_json_file('nonexistent.json')
        self.assertFalse(valid)
        self.assertIsNotNone(error)
    
    def test_get_config_schema(self):
        """测试获取配置模式"""
        schema = ConfigValidator.get_config_schema()
        self.assertIn('properties', schema)
        self.assertIn('default_language', schema['properties'])


class TestLanguageManager(unittest.TestCase):
    """测试语言管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = LanguageManager()
    
    def test_default_language(self):
        """测试默认语言"""
        self.assertEqual(self.manager.current_language, 'en')
    
    def test_set_language(self):
        """测试设置语言"""
        success = self.manager.set_language('zh')
        self.assertTrue(success)
        self.assertEqual(self.manager.current_language, 'zh')
    
    def test_set_invalid_language(self):
        """测试设置无效语言"""
        success = self.manager.set_language('invalid')
        self.assertFalse(success)
        self.assertEqual(self.manager.current_language, 'en')
    
    def test_get_text_english(self):
        """测试获取英文文本"""
        self.manager.set_language('en')
        text = self.manager.get_text('hello_world')
        self.assertEqual(text, 'Hello, World!')
    
    def test_get_text_chinese(self):
        """测试获取中文文本"""
        self.manager.set_language('zh')
        text = self.manager.get_text('hello_world')
        self.assertEqual(text, '你好，世界！')
    
    def test_get_text_with_formatting(self):
        """测试获取带格式化的文本"""
        self.manager.set_language('en')
        text = self.manager.get_text('hello_name', name='TestUser')
        self.assertEqual(text, 'Hello, TestUser!')
    
    def test_get_text_nonexistent_key(self):
        """测试获取不存在的键"""
        text = self.manager.get_text('nonexistent_key')
        self.assertEqual(text, 'nonexistent_key')
    
    def test_get_supported_languages(self):
        """测试获取支持的语言"""
        languages = self.manager.get_supported_languages()
        self.assertIn('en', languages)
        self.assertIn('zh', languages)
    
    def test_add_translation(self):
        """测试添加翻译"""
        self.manager.add_translation('fr', {'hello_world': 'Bonjour, Monde!'})
        self.manager.set_language('fr')
        text = self.manager.get_text('hello_world')
        self.assertEqual(text, 'Bonjour, Monde!')
    
    def test_global_functions(self):
        """测试全局函数"""
        # 测试get_text函数
        text = get_text('hello_world', language='zh')
        self.assertEqual(text, '你好，世界！')
        
        # 测试set_language函数
        success = set_language('zh')
        self.assertTrue(success)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_classes = [
        TestArgumentParser,
        TestGreetingGenerator,
        TestOutputManager,
        TestConfigManager,
        TestLanguageManager
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)