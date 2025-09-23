#!/usr/bin/env python3
"""
Python多线程基础演示项目主程序入口
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from demos.controller.demo_controller import DemoController
from utils.logging.logger import setup_logger

def main():
    """主程序入口函数"""
    # 设置日志
    setup_logger()
    
    # 创建并启动演示控制器
    controller = DemoController()
    controller.run()

if __name__ == "__main__":
    main()