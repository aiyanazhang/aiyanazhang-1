#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础演示模块单元测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from demos.basic_demos import BasicTupleDemo


class TestBasicTupleDemo(unittest.TestCase):
    """基础元组演示测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.demo = BasicTupleDemo()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.demo.demo_data)
        self.assertIn('numbers', self.demo.demo_data)
        self.assertIn('mixed', self.demo.demo_data)
        self.assertIn('fruits', self.demo.demo_data)
    
    def test_demo_data_types(self):
        """测试演示数据类型"""
        # 检查所有演示数据都是元组
        for key, value in self.demo.demo_data.items():
            self.assertIsInstance(value, tuple, f"{key} should be a tuple")
    
    def test_demo_data_content(self):
        """测试演示数据内容"""
        # 测试数字元组
        self.assertEqual(self.demo.demo_data['numbers'], (1, 2, 3, 4, 5))
        
        # 测试混合类型元组
        mixed = self.demo.demo_data['mixed']
        self.assertEqual(len(mixed), 5)
        self.assertIsInstance(mixed[0], int)
        self.assertIsInstance(mixed[1], str)
        self.assertIsInstance(mixed[2], float)
        self.assertIsInstance(mixed[3], bool)
        self.assertIsNone(mixed[4])
        
        # 测试空元组
        self.assertEqual(self.demo.demo_data['empty'], ())
        
        # 测试单元素元组
        self.assertEqual(len(self.demo.demo_data['single']), 1)
    
    def test_methods_exist(self):
        """测试方法是否存在"""
        methods = [
            'demonstrate_tuple_creation',
            'demonstrate_tuple_access',
            'demonstrate_tuple_iteration',
            'demonstrate_tuple_properties',
            'demonstrate_tuple_methods'
        ]
        
        for method_name in methods:
            self.assertTrue(hasattr(self.demo, method_name))
            self.assertTrue(callable(getattr(self.demo, method_name)))


if __name__ == '__main__':
    unittest.main()