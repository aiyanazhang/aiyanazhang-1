#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级演示模块单元测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from demos.advanced_demos import AdvancedTupleDemo


class TestAdvancedTupleDemo(unittest.TestCase):
    """高级元组演示测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.demo = AdvancedTupleDemo()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.demo.demo_data)
        self.assertIn('coordinates', self.demo.demo_data)
        self.assertIn('student_records', self.demo.demo_data)
    
    def test_coordinate_data(self):
        """测试坐标数据"""
        coords = self.demo.demo_data['coordinates']
        self.assertIsInstance(coords, tuple)
        
        # 检查每个坐标点都是二元元组
        for point in coords:
            self.assertIsInstance(point, tuple)
            self.assertEqual(len(point), 2)
            self.assertIsInstance(point[0], int)
            self.assertIsInstance(point[1], int)
    
    def test_student_records_data(self):
        """测试学生记录数据"""
        records = self.demo.demo_data['student_records']
        self.assertIsInstance(records, tuple)
        
        # 检查每个学生记录格式
        for record in records:
            self.assertIsInstance(record, tuple)
            self.assertEqual(len(record), 3)  # name, age, grade
            self.assertIsInstance(record[0], str)    # name
            self.assertIsInstance(record[1], int)    # age
            self.assertIsInstance(record[2], float)  # grade
    
    def test_methods_exist(self):
        """测试方法是否存在"""
        methods = [
            'demonstrate_tuple_unpacking',
            'demonstrate_nested_tuples', 
            'demonstrate_named_tuples',
            'demonstrate_tuple_comprehension',
            'demonstrate_tuple_sorting'
        ]
        
        for method_name in methods:
            self.assertTrue(hasattr(self.demo, method_name))
            self.assertTrue(callable(getattr(self.demo, method_name)))


if __name__ == '__main__':
    unittest.main()