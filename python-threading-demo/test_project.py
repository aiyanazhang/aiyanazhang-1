#!/usr/bin/env python3
"""
项目测试脚本
"""

import sys
import os

# 添加src到Python路径
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_imports():
    """测试所有模块导入"""
    print("🧪 开始测试项目模块导入...")
    
    try:
        # 测试核心模块
        print("  📦 测试核心创建模块...")
        from core.creation.basic_thread import BasicThreadDemo
        from core.creation.thread_inheritance import ThreadInheritanceDemo
        from core.creation.thread_pool import ThreadPoolDemo
        print("  ✅ 创建模块导入成功")
        
        print("  📦 测试核心管理模块...")
        from core.management.thread_monitor import ThreadStateDemo
        from core.management.lifecycle_manager import LifecycleDemo
        from core.management.exception_handler import ExceptionHandlingDemo
        print("  ✅ 管理模块导入成功")
        
        print("  📦 测试同步模块...")
        from core.synchronization.locks_demo import LocksDemo
        from core.synchronization.condition_demo import ConditionDemo
        from core.synchronization.semaphore_demo import SemaphoreDemo
        print("  ✅ 同步模块导入成功")
        
        print("  📦 测试通信模块...")
        from core.communication.communication_demo import CommunicationDemo
        print("  ✅ 通信模块导入成功")
        
        print("  📦 测试演示场景...")
        from demos.scenarios.comprehensive_demo import ComprehensiveDemo
        print("  ✅ 演示场景导入成功")
        
        print("  📦 测试控制器...")
        from demos.controller.demo_controller import DemoController
        print("  ✅ 控制器导入成功")
        
        print("🎉 所有模块导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_basic_functionality():
    """测试基础功能"""
    print("\n🔧 开始测试基础功能...")
    
    try:
        from demos.controller.demo_controller import DemoController
        
        # 创建控制器实例
        controller = DemoController()
        print("  ✅ 控制器实例创建成功")
        
        # 检查演示项目
        demos = controller.demos
        print(f"  ✅ 发现 {len(demos)} 个演示项目")
        
        for key, demo in demos.items():
            print(f"    [{key}] {demo['name']}")
            
        print("🎉 基础功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e}")
        return False

def test_simple_demo():
    """测试简单演示"""
    print("\n⚡ 运行简单演示测试...")
    
    try:
        from core.creation.basic_thread import BasicThreadDemo
        import threading
        import time
        
        def quick_test():
            """快速测试函数"""
            print(f"    线程 {threading.current_thread().name} 正在运行")
            time.sleep(0.5)
            print(f"    线程 {threading.current_thread().name} 完成")
        
        # 创建简单线程测试
        thread1 = threading.Thread(target=quick_test, name="TestThread1")
        thread2 = threading.Thread(target=quick_test, name="TestThread2")
        
        print("  🚀 启动测试线程...")
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        print("  ✅ 简单演示测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 简单演示测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎭 Python多线程演示项目 - 测试脚本")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("模块导入测试", test_imports),
        ("基础功能测试", test_basic_functionality),
        ("简单演示测试", test_simple_demo)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"💥 {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目准备就绪。")
        print("\n🚀 现在可以运行 'python3 main.py' 开始演示")
    else:
        print("⚠️  部分测试失败，请检查项目配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)