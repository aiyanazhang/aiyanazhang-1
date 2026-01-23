#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World Python脚本系统主程序
负责程序入口点和整体流程控制
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.args_parser import ArgumentParser
from src.greeting import GreetingGenerator
from src.output import OutputManager
from src.config import ConfigManager


class HelloWorldApp:
    """Hello World应用程序主类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.config_manager = ConfigManager()
        self.arg_parser = ArgumentParser()
        self.greeting_generator = GreetingGenerator()
        self.output_manager = OutputManager()
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志记录"""
        log_level = self.config_manager.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self, args=None):
        """运行应用程序主逻辑"""
        try:
            # 解析命令行参数
            if args is None:
                args = sys.argv[1:]
            
            parsed_args = self.arg_parser.parse(args)
            self.logger.debug(f"解析参数: {parsed_args}")
            
            # 应用配置文件设置
            merged_config = self._merge_config_with_args(parsed_args)
            self.logger.debug(f"合并配置: {merged_config}")
            
            # 生成问候消息
            greeting_message = self.greeting_generator.generate(
                name=merged_config.get('name', 'World'),
                language=merged_config.get('language', 'en'),
                verbose=merged_config.get('verbose', False)
            )
            
            # 格式化并输出结果
            formatted_output = self.output_manager.format_output(
                message=greeting_message,
                format_type=merged_config.get('format', 'text'),
                enable_colors=merged_config.get('enable_colors', True)
            )
            
            self.output_manager.display(formatted_output)
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("程序被用户中断")
            return 1
            
        except Exception as e:
            self.logger.error(f"程序执行出现错误: {e}")
            if parsed_args and parsed_args.get('verbose'):
                import traceback
                traceback.print_exc()
            return 1
    
    def _merge_config_with_args(self, args):
        """合并配置文件和命令行参数"""
        # 从配置文件加载默认设置
        config = self.config_manager.load_config()
        
        # 命令行参数覆盖配置文件设置
        for key, value in args.items():
            if value is not None:
                config[key] = value
        
        return config


def main():
    """程序入口点"""
    app = HelloWorldApp()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()