#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理和用户输入验证系统

提供统一的错误处理机制和用户输入验证功能
"""

import traceback
from typing import Any, Callable, Optional


class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "未知错误") -> None:
        """
        处理异常并显示友好的错误信息
        
        Args:
            error: 异常对象
            context: 错误发生的上下文
        """
        print(f"\n❌ 错误：{context}")
        
        if isinstance(error, IndexError):
            print("📍 索引超出范围，请检查索引值是否正确")
        elif isinstance(error, TypeError):
            print("📍 类型错误，请检查数据类型是否正确")
        elif isinstance(error, ValueError):
            print("📍 值错误，请检查输入的值是否有效")
        elif isinstance(error, AttributeError):
            print("📍 属性错误，请检查对象是否具有该属性或方法")
        elif isinstance(error, KeyboardInterrupt):
            print("📍 用户中断操作")
        else:
            print(f"📍 系统错误：{str(error)}")
        
        # 在调试模式下显示详细错误信息
        if hasattr(ErrorHandler, 'debug_mode') and ErrorHandler.debug_mode:
            print(f"\n调试信息：\n{traceback.format_exc()}")
    
    @staticmethod
    def safe_execute(func: Callable, *args, error_context: str = "执行操作", **kwargs) -> Any:
        """
        安全执行函数，自动处理异常
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            error_context: 错误上下文描述
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果或None（如果出错）
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, error_context)
            return None


class InputValidator:
    """用户输入验证器"""
    
    @staticmethod
    def get_valid_choice(prompt: str, valid_choices: list, error_msg: str = "无效选择") -> str:
        """
        获取有效的用户选择
        
        Args:
            prompt: 提示信息
            valid_choices: 有效选择列表
            error_msg: 错误提示信息
            
        Returns:
            用户的有效选择
        """
        while True:
            try:
                choice = input(prompt).strip()
                if choice in valid_choices:
                    return choice
                else:
                    print(f"❌ {error_msg}，请从以下选项中选择：{', '.join(valid_choices)}")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                ErrorHandler.handle_error(e, "输入验证")
    
    @staticmethod
    def get_valid_integer(prompt: str, min_val: Optional[int] = None, 
                         max_val: Optional[int] = None) -> int:
        """
        获取有效的整数输入
        
        Args:
            prompt: 提示信息
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            有效的整数
        """
        while True:
            try:
                value = int(input(prompt).strip())
                
                if min_val is not None and value < min_val:
                    print(f"❌ 输入值不能小于 {min_val}")
                    continue
                    
                if max_val is not None and value > max_val:
                    print(f"❌ 输入值不能大于 {max_val}")
                    continue
                    
                return value
                
            except ValueError:
                print("❌ 请输入有效的整数")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                ErrorHandler.handle_error(e, "整数输入验证")
    
    @staticmethod
    def get_yes_no_choice(prompt: str, default: str = "y") -> bool:
        """
        获取是/否选择
        
        Args:
            prompt: 提示信息
            default: 默认选择（'y' 或 'n'）
            
        Returns:
            True表示是，False表示否
        """
        full_prompt = f"{prompt} [{'Y/n' if default.lower() == 'y' else 'y/N'}]: "
        
        while True:
            try:
                choice = input(full_prompt).strip().lower()
                
                if not choice:  # 空输入使用默认值
                    choice = default.lower()
                
                if choice in ['y', 'yes', '是', '1']:
                    return True
                elif choice in ['n', 'no', '否', '0']:
                    return False
                else:
                    print("❌ 请输入 y/yes/是 或 n/no/否")
                    
            except KeyboardInterrupt:
                raise
            except Exception as e:
                ErrorHandler.handle_error(e, "是否选择验证")
    
    @staticmethod
    def pause_for_user(message: str = "按回车键继续...") -> None:
        """
        暂停等待用户输入
        
        Args:
            message: 提示信息
        """
        try:
            input(f"\n{message}")
        except KeyboardInterrupt:
            raise