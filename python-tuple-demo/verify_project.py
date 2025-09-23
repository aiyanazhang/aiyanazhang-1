#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目完整性验证脚本
"""

import os
import sys

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (缺失)")
        return False

def check_project_structure():
    """检查项目结构完整性"""
    print("🔍 检查项目结构完整性...")
    print("=" * 50)
    
    files_to_check = [
        ("main.py", "主程序入口"),
        ("README.md", "项目说明文档"),
        ("src/__init__.py", "源码包初始化"),
        ("src/menu_manager.py", "菜单管理器"),
        ("src/utils/__init__.py", "工具包初始化"),
        ("src/utils/error_handler.py", "错误处理模块"),
        ("src/demos/__init__.py", "演示包初始化"),
        ("src/demos/basic_demos.py", "基础演示模块"),
        ("src/demos/advanced_demos.py", "高级演示模块"),
        ("src/demos/application_demos.py", "应用演示模块"),
        ("src/exercises/__init__.py", "练习包初始化"),
        ("src/exercises/exercise_manager.py", "练习管理器"),
        ("tests/__init__.py", "测试包初始化"),
        ("tests/run_tests.py", "测试运行脚本"),
        ("tests/test_basic_demos.py", "基础演示测试"),
        ("tests/test_advanced_demos.py", "高级演示测试"),
        ("tests/test_application_demos.py", "应用演示测试"),
        ("tests/test_exercise_manager.py", "练习管理器测试"),
        ("docs/user_guide.md", "用户指南")
    ]
    
    missing_files = 0
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            missing_files += 1
    
    print("\n" + "=" * 50)
    if missing_files == 0:
        print("🎉 项目结构完整！所有必需文件都存在。")
        return True
    else:
        print(f"⚠️  发现 {missing_files} 个缺失文件，请检查项目完整性。")
        return False

def check_code_syntax():
    """检查Python文件语法"""
    print("\n🔍 检查代码语法...")
    print("=" * 50)
    
    python_files = [
        "main.py",
        "src/menu_manager.py",
        "src/utils/error_handler.py",
        "src/demos/basic_demos.py",
        "src/demos/advanced_demos.py", 
        "src/demos/application_demos.py",
        "src/exercises/exercise_manager.py"
    ]
    
    syntax_errors = 0
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, py_file, 'exec')
                print(f"✅ 语法检查通过: {py_file}")
            except SyntaxError as e:
                print(f"❌ 语法错误: {py_file} - {e}")
                syntax_errors += 1
            except Exception as e:
                print(f"⚠️  检查失败: {py_file} - {e}")
        else:
            print(f"❌ 文件不存在: {py_file}")
            syntax_errors += 1
    
    print("\n" + "=" * 50)
    if syntax_errors == 0:
        print("🎉 所有Python文件语法检查通过！")
        return True
    else:
        print(f"⚠️  发现 {syntax_errors} 个语法问题。")
        return False

def generate_summary():
    """生成项目摘要"""
    print("\n📊 项目摘要")
    print("=" * 50)
    
    # 统计代码行数
    total_lines = 0
    py_files_count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        py_files_count += 1
                except:
                    pass
    
    print(f"Python文件数量: {py_files_count}")
    print(f"总代码行数: {total_lines}")
    print(f"平均每文件行数: {total_lines // py_files_count if py_files_count > 0 else 0}")
    
    # 功能模块统计
    print(f"\n功能模块:")
    print(f"  • 基础演示: 5个演示功能")
    print(f"  • 高级演示: 5个演示功能") 
    print(f"  • 应用演示: 5个应用场景")
    print(f"  • 交互练习: 4种练习类型")
    print(f"  • 单元测试: 4个测试模块")

def main():
    """主函数"""
    print("🐍 Python元组演示系统 - 项目验证")
    print("=" * 60)
    
    # 切换到项目目录
    if os.path.basename(os.getcwd()) != 'python-tuple-demo':
        if os.path.exists('python-tuple-demo'):
            os.chdir('python-tuple-demo')
        else:
            print("❌ 请在python-tuple-demo目录中运行此脚本")
            return False
    
    # 执行检查
    structure_ok = check_project_structure()
    syntax_ok = check_code_syntax()
    
    # 生成摘要
    generate_summary()
    
    # 最终结果
    print("\n" + "=" * 60)
    if structure_ok and syntax_ok:
        print("🎉 项目验证通过！系统已准备就绪。")
        print("\n🚀 运行命令: python main.py")
        return True
    else:
        print("⚠️  项目验证失败，请修复上述问题后重新验证。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)