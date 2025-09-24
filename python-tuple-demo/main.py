#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python元组使用演示系统 - 主程序入口

本程序提供全面的Python元组操作演示，包括：
- 基础操作演示
- 高级操作演示  
- 实际应用场景
- 交互式练习

作者：AI助手
版本：1.0.0
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.menu_manager import MenuManager
from src.utils.error_handler import ErrorHandler


def main():
    """主程序入口"""
    try:
        print("=" * 60)
        print("🐍 欢迎使用 Python 元组使用演示系统 🐍")
        print("=" * 60)
        print()
        
        # 初始化菜单管理器
        menu_manager = MenuManager()
        
        # 启动主菜单循环
        menu_manager.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用Python元组演示系统！再见！")
    except Exception as e:
        ErrorHandler.handle_error(e, "系统启动失败")
    finally:
        print("\n程序已退出")


if __name__ == "__main__":
    main()