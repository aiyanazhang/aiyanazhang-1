#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用演示模块单元测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from demos.application_demos import ApplicationDemo


class TestApplicationDemo(unittest.TestCase):
    """应用演示测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.demo = ApplicationDemo()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.demo.db_records)
        self.assertIsInstance(self.demo.db_records, tuple)
    
    def test_db_records_structure(self):
        """测试数据库记录结构"""
        for record in self.demo.db_records:
            self.assertIsInstance(record, tuple)
            self.assertEqual(len(record), 5)  # id, name, email, major, grade
            
            # 检查字段类型
            self.assertIsInstance(record[0], int)    # id
            self.assertIsInstance(record[1], str)    # name
            self.assertIsInstance(record[2], str)    # email
            self.assertIsInstance(record[3], str)    # major
            self.assertIsInstance(record[4], float)  # grade
    
    def test_methods_exist(self):
        """测试方法是否存在"""
        methods = [
            'demonstrate_database_records',
            'demonstrate_coordinate_system',
            'demonstrate_configuration_management',
            'demonstrate_multiple_return_values',
            'demonstrate_data_structures'
        ]
        
        for method_name in methods:
            self.assertTrue(hasattr(self.demo, method_name))
            self.assertTrue(callable(getattr(self.demo, method_name)))


if __name__ == '__main__':
    unittest.main()