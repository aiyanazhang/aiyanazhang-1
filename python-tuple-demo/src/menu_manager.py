#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜单管理器

提供交互式菜单系统，管理各个演示模块的调用
"""

import os
import sys
from typing import Dict, Callable

from utils.error_handler import ErrorHandler, InputValidator
from demos.basic_demos import BasicTupleDemo
from demos.advanced_demos import AdvancedTupleDemo
from demos.application_demos import ApplicationDemo
from exercises.exercise_manager import ExerciseManager


class MenuManager:
    """主菜单管理器"""
    
    def __init__(self):
        """初始化菜单管理器"""
        self.running = True
        self.basic_demo = BasicTupleDemo()
        self.advanced_demo = AdvancedTupleDemo()
        self.app_demo = ApplicationDemo()
        self.exercise_manager = ExerciseManager()
        self.menu_items = {
            '1': ('基础操作演示', self._show_basic_demos),
            '2': ('高级操作演示', self._show_advanced_demos),
            '3': ('实际应用场景', self._show_application_demos),
            '4': ('交互式练习', self._show_interactive_exercises),
            '5': ('帮助文档', self._show_help),
            '6': ('系统设置', self._show_settings),
            '0': ('退出系统', self._exit_system)
        }
    
    def run(self) -> None:
        """启动菜单循环"""
        while self.running:
            try:
                self._display_main_menu()
                choice = self._get_user_choice()
                self._execute_choice(choice)
            except KeyboardInterrupt:
                print("\n\n检测到中断信号，正在退出...")
                self.running = False
            except Exception as e:
                ErrorHandler.handle_error(e, "菜单系统运行")
    
    def _display_main_menu(self) -> None:
        """显示主菜单"""
        self._clear_screen()
        print("🐍 Python 元组使用演示系统")
        print("=" * 50)
        print()
        
        for key, (description, _) in self.menu_items.items():
            if key == '0':
                print()
            print(f"  [{key}] {description}")
        
        print()
        print("-" * 50)
    
    def _get_user_choice(self) -> str:
        """获取用户选择"""
        valid_choices = list(self.menu_items.keys())
        return InputValidator.get_valid_choice(
            "请选择操作 >>> ",
            valid_choices,
            "无效选择"
        )
    
    def _execute_choice(self, choice: str) -> None:
        """执行用户选择的操作"""
        if choice in self.menu_items:
            _, action = self.menu_items[choice]
            ErrorHandler.safe_execute(action, error_context=f"执行菜单项 {choice}")
        else:
            print("❌ 无效的选择")
    
    def _show_basic_demos(self) -> None:
        """显示基础操作演示菜单"""
        self._clear_screen()
        print("📚 基础操作演示")
        print("=" * 30)
        print()
        
        basic_menu = {
            '1': '元组创建演示',
            '2': '元组访问演示', 
            '3': '元组遍历演示',
            '4': '元组特性演示',
            '5': '元组方法演示',
            '0': '返回主菜单'
        }
        
        while True:
            for key, description in basic_menu.items():
                if key == '0':
                    print()
                print(f"  [{key}] {description}")
            
            print()
            choice = InputValidator.get_valid_choice(
                "请选择演示内容 >>> ",
                list(basic_menu.keys()),
                "无效选择"
            )
            
            if choice == '0':
                break
            elif choice == '1':
                self._demo_tuple_creation()
            elif choice == '2':
                self._demo_tuple_access()
            elif choice == '3':
                self._demo_tuple_iteration()
            elif choice == '4':
                self._demo_tuple_properties()
            elif choice == '5':
                self._demo_tuple_methods()
            
            InputValidator.pause_for_user()
    
    def _show_advanced_demos(self) -> None:
        """显示高级操作演示菜单"""
        self._clear_screen()
        print("🚀 高级操作演示")
        print("=" * 30)
        print()
        
        advanced_menu = {
            '1': '元组解包演示',
            '2': '嵌套元组演示',
            '3': '命名元组演示',
            '4': '元组推导演示',
            '5': '元组排序演示',
            '0': '返回主菜单'
        }
        
        while True:
            for key, description in advanced_menu.items():
                if key == '0':
                    print()
                print(f"  [{key}] {description}")
            
            print()
            choice = InputValidator.get_valid_choice(
                "请选择演示内容 >>> ",
                list(advanced_menu.keys()),
                "无效选择"
            )
            
            if choice == '0':
                break
            elif choice == '1':
                self._demo_tuple_unpacking()
            elif choice == '2':
                self._demo_nested_tuples()
            elif choice == '3':
                self._demo_named_tuples()
            elif choice == '4':
                self._demo_tuple_comprehension()
            elif choice == '5':
                self._demo_tuple_sorting()
            
            InputValidator.pause_for_user()
    
    def _show_application_demos(self) -> None:
        """显示实际应用场景演示菜单"""
        self._clear_screen()
        print("💼 实际应用场景演示")
        print("=" * 40)
        print()
        
        app_menu = {
            '1': '数据库记录模拟',
            '2': '坐标系统应用',
            '3': '配置参数管理',
            '4': '函数多值返回',
            '5': '数据结构设计',
            '0': '返回主菜单'
        }
        
        while True:
            for key, description in app_menu.items():
                if key == '0':
                    print()
                print(f"  [{key}] {description}")
            
            print()
            choice = InputValidator.get_valid_choice(
                "请选择应用场景 >>> ",
                list(app_menu.keys()),
                "无效选择"
            )
            
            if choice == '0':
                break
            elif choice == '1':
                self._demo_database_records()
            elif choice == '2':
                self._demo_coordinate_system()
            elif choice == '3':
                self._demo_configuration_management()
            elif choice == '4':
                self._demo_multiple_return_values()
            elif choice == '5':
                self._demo_data_structures()
            
            InputValidator.pause_for_user()
    
    def _show_interactive_exercises(self) -> None:
        """显示交互式练习菜单"""
        self._clear_screen()
        print("✏️  交互式练习")
        print("=" * 30)
        print()
        
        exercise_menu = {
            '1': '基础语法练习',
            '2': '数据操作练习',
            '3': '应用场景练习',
            '4': '综合挑战题',
            '5': '查看练习统计',
            '0': '返回主菜单'
        }
        
        while True:
            for key, description in exercise_menu.items():
                if key == '0':
                    print()
                print(f"  [{key}] {description}")
            
            print()
            choice = InputValidator.get_valid_choice(
                "请选择练习类型 >>> ",
                list(exercise_menu.keys()),
                "无效选择"
            )
            
            if choice == '0':
                break
            elif choice == '1':
                self._exercise_basic_syntax()
            elif choice == '2':
                self._exercise_data_operations()
            elif choice == '3':
                self._exercise_applications()
            elif choice == '4':
                self._exercise_comprehensive()
            elif choice == '5':
                self._show_exercise_stats()
            
            InputValidator.pause_for_user()
    
    def _show_help(self) -> None:
        """显示帮助文档"""
        self._clear_screen()
        print("📖 帮助文档")
        print("=" * 30)
        print()
        print("🔹 本系统提供全面的Python元组学习和演示功能")
        print("🔹 包含从基础到高级的各种元组操作示例")
        print("🔹 提供实际应用场景的演示和练习")
        print("🔹 支持交互式学习和自我检测")
        print()
        print("📋 使用说明：")
        print("  • 在菜单中输入对应数字进行选择")
        print("  • 按Ctrl+C可以随时退出")
        print("  • 遇到问题请查看错误提示信息")
        print()
        print("🎯 学习建议：")
        print("  • 先从基础操作开始学习")
        print("  • 理解概念后尝试高级操作")
        print("  • 通过应用场景加深理解")
        print("  • 完成练习验证掌握程度")
        
        InputValidator.pause_for_user()
    
    def _show_settings(self) -> None:
        """显示系统设置"""
        self._clear_screen()
        print("⚙️  系统设置")
        print("=" * 30)
        print()
        print("🔹 当前设置：")
        print("  • 演示速度：正常")
        print("  • 详细程度：中等")
        print("  • 交互模式：启用")
        print("  • 输出格式：控制台")
        print()
        print("⚠️  设置功能将在后续版本中提供")
        
        InputValidator.pause_for_user()
    
    def _exit_system(self) -> None:
        """退出系统"""
        print("\n👋 感谢使用Python元组演示系统！")
        print("希望本系统对您的学习有所帮助！")
        self.running = False
    
    def _clear_screen(self) -> None:
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    # 基础演示方法
    def _demo_tuple_creation(self):
        """元组创建演示"""
        self._clear_screen()
        self.basic_demo.demonstrate_tuple_creation()
    
    def _demo_tuple_access(self):
        """元组访问演示"""
        self._clear_screen()
        self.basic_demo.demonstrate_tuple_access()
    
    def _demo_tuple_iteration(self):
        """元组遍历演示"""
        self._clear_screen()
        self.basic_demo.demonstrate_tuple_iteration()
    
    def _demo_tuple_properties(self):
        """元组特性演示"""
        self._clear_screen()
        self.basic_demo.demonstrate_tuple_properties()
    
    def _demo_tuple_methods(self):
        """元组方法演示"""
        self._clear_screen()
        self.basic_demo.demonstrate_tuple_methods()
    
    # 高级演示方法
    def _demo_tuple_unpacking(self):
        """元组解包演示"""
        self._clear_screen()
        self.advanced_demo.demonstrate_tuple_unpacking()
    
    def _demo_nested_tuples(self):
        """嵌套元组演示"""
        self._clear_screen()
        self.advanced_demo.demonstrate_nested_tuples()
    
    def _demo_named_tuples(self):
        """命名元组演示"""
        self._clear_screen()
        self.advanced_demo.demonstrate_named_tuples()
    
    def _demo_tuple_comprehension(self):
        """元组推导演示"""
        self._clear_screen()
        self.advanced_demo.demonstrate_tuple_comprehension()
    
    def _demo_tuple_sorting(self):
        """元组排序演示"""
        self._clear_screen()
        self.advanced_demo.demonstrate_tuple_sorting()
    
    # 应用演示方法
    def _demo_database_records(self):
        """数据库记录演示"""
        self._clear_screen()
        self.app_demo.demonstrate_database_records()
    
    def _demo_coordinate_system(self):
        """坐标系统演示"""
        self._clear_screen()
        self.app_demo.demonstrate_coordinate_system()
    
    def _demo_configuration_management(self):
        """配置管理演示"""
        self._clear_screen()
        self.app_demo.demonstrate_configuration_management()
    
    def _demo_multiple_return_values(self):
        """多值返回演示"""
        self._clear_screen()
        self.app_demo.demonstrate_multiple_return_values()
    
    def _demo_data_structures(self):
        """数据结构演示"""
        self._clear_screen()
        self.app_demo.demonstrate_data_structures()
    
    # 练习方法
    def _exercise_basic_syntax(self):
        """基础语法练习"""
        self._clear_screen()
        self.exercise_manager.basic_syntax_exercises()
    
    def _exercise_data_operations(self):
        """数据操作练习"""
        self._clear_screen()
        self.exercise_manager.data_operations_exercises()
    
    def _exercise_applications(self):
        """应用场景练习"""
        self._clear_screen()
        self.exercise_manager.application_exercises()
    
    def _exercise_comprehensive(self):
        """综合挑战练习"""
        self._clear_screen()
        self.exercise_manager.comprehensive_challenge()
    
    def _show_exercise_stats(self):
        """显示练习统计"""
        self._clear_screen()
        self.exercise_manager.show_exercise_stats()