#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
练习管理器单元测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exercises.exercise_manager import ExerciseManager


class TestExerciseManager(unittest.TestCase):
    """练习管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = ExerciseManager()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.manager.stats)
        self.assertEqual(self.manager.stats['total_exercises'], 0)
        self.assertEqual(self.manager.stats['correct_answers'], 0)
        self.assertEqual(self.manager.stats['wrong_answers'], 0)
    
    def test_stats_structure(self):
        """测试统计数据结构"""
        required_keys = {'total_exercises', 'correct_answers', 'wrong_answers', 'start_time'}
        self.assertTrue(required_keys.issubset(set(self.manager.stats.keys())))
    
    def test_methods_exist(self):
        """测试方法是否存在"""
        methods = [
            'basic_syntax_exercises',
            'data_operations_exercises',
            'application_exercises', 
            'comprehensive_challenge',
            'show_exercise_stats'
        ]
        
        for method_name in methods:
            self.assertTrue(hasattr(self.manager, method_name))
            self.assertTrue(callable(getattr(self.manager, method_name)))


if __name__ == '__main__':
    unittest.main()