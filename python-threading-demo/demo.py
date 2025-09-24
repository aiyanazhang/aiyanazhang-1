#!/usr/bin/env python3
"""
Python多线程演示系统 - 快速演示脚本
快速展示系统的主要功能
"""

import sys
import os
import time

# 添加src目录到路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from basic_thread_demo import BasicThreadDemo


def quick_demo():
    """快速演示主要功能"""
    print("🚀 Python多线程演示系统 - 快速演示")
    print("=" * 60)
    
    # 演示1：基础线程
    print("\n1️⃣ 基础线程演示")
    print("-" * 30)
    demo = BasicThreadDemo()
    demo.simple_thread()
    
    print("\n✅ 快速演示完成！")
    print("\n💡 想要体验更多功能？运行以下命令：")
    print("   python main.py           # 交互模式")
    print("   python main.py --help    # 查看帮助")
    print("   python main.py 1 2 3     # 运行指定演示")


if __name__ == "__main__":
    quick_demo()