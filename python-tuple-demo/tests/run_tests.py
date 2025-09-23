#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有单元测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_tests():
    """运行所有单元测试"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 Python元组演示系统 - 单元测试")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        exit_code = 0
    else:
        print("❌ 部分测试失败！")
        exit_code = 1
    print("=" * 60)
    
    sys.exit(exit_code)