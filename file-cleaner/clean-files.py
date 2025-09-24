#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件清理工具启动脚本
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
script_dir = Path(__file__).parent
src_dir = script_dir / 'src'
sys.path.insert(0, str(src_dir))

# 导入主程序
from main import main

if __name__ == '__main__':
    main()