#!/usr/bin/env python3
"""
测试运行脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tests.test_all import run_tests

if __name__ == '__main__':
    print("开始运行Docker命令执行工具测试套件...")
    print("=" * 60)
    
    success = run_tests()
    
    print("=" * 60)
    if success:
        print("✓ 所有测试通过!")
        sys.exit(0)
    else:
        print("✗ 测试失败!")
        sys.exit(1)