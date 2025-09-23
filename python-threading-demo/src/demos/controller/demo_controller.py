"""
演示控制器 - 主要的用户界面和演示管理
"""

import sys
import time
from typing import Dict, List, Callable, Any

# 导入各个演示模块
try:
    from ..core.creation.basic_thread import BasicThreadDemo
    from ..core.creation.thread_inheritance import ThreadInheritanceDemo
    from ..core.creation.thread_pool import ThreadPoolDemo
    from ..core.management.thread_monitor import ThreadStateDemo
    from ..core.management.lifecycle_manager import LifecycleDemo
    from ..core.management.exception_handler import ExceptionHandlingDemo
    from ..core.synchronization.locks_demo import LocksDemo
    from ..core.synchronization.condition_demo import ConditionDemo
    from ..core.synchronization.semaphore_demo import SemaphoreDemo
    from ..core.communication.communication_demo import CommunicationDemo
    from ..scenarios.comprehensive_demo import ComprehensiveDemo
    from ..utils.monitoring.performance_monitor import MonitoringDemo
    from ..utils.logging.advanced_logger import LoggingDemo
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from core.creation.basic_thread import BasicThreadDemo
    from core.creation.thread_inheritance import ThreadInheritanceDemo
    from core.creation.thread_pool import ThreadPoolDemo
    from core.management.thread_monitor import ThreadStateDemo
    from core.management.lifecycle_manager import LifecycleDemo
    from core.management.exception_handler import ExceptionHandlingDemo
    from core.synchronization.locks_demo import LocksDemo
    from core.synchronization.condition_demo import ConditionDemo
    from core.synchronization.semaphore_demo import SemaphoreDemo
    from core.communication.communication_demo import CommunicationDemo
    from demos.scenarios.comprehensive_demo import ComprehensiveDemo
    from utils.monitoring.performance_monitor import MonitoringDemo
    from utils.logging.advanced_logger import LoggingDemo


class DemoController:
    """演示控制器"""
    
    def __init__(self):
        self.demos = self._initialize_demos()
        
    def _initialize_demos(self) -> Dict[str, Dict[str, Any]]:
        """初始化演示项目"""
        return {
            "1": {
                "name": "基础线程创建演示",
                "description": "演示threading.Thread的基本用法",
                "demo_class": BasicThreadDemo,
                "method": "run_all_demos"
            },
            "2": {
                "name": "线程类继承演示", 
                "description": "演示通过继承Thread类创建自定义线程",
                "demo_class": ThreadInheritanceDemo,
                "method": "run_all_demos"
            },
            "3": {
                "name": "线程池演示",
                "description": "演示ThreadPoolExecutor的使用",
                "demo_class": ThreadPoolDemo,
                "method": "run_all_demos"
            },
            "4": {
                "name": "线程状态监控演示",
                "description": "演示线程状态监控和性能指标",
                "demo_class": ThreadStateDemo,
                "method": "run_all_demos"
            },
            "5": {
                "name": "线程生命周期管理演示",
                "description": "演示线程从创建到销毁的完整生命周期",
                "demo_class": LifecycleDemo,
                "method": "run_all_demos"
            },
            "6": {
                "name": "线程异常处理演示",
                "description": "演示多线程环境下的异常处理策略",
                "demo_class": ExceptionHandlingDemo,
                "method": "run_all_demos"
            },
            "7": {
                "name": "互斥锁演示",
                "description": "演示Lock和RLock的使用",
                "demo_class": LocksDemo,
                "method": "run_all_demos"
            },
            "8": {
                "name": "条件变量演示",
                "description": "演示Condition的使用场景",
                "demo_class": ConditionDemo,
                "method": "run_all_demos"
            },
            "9": {
                "name": "信号量演示",
                "description": "演示Semaphore控制资源访问",
                "demo_class": SemaphoreDemo,
                "method": "run_all_demos"
            },
            "10": {
                "name": "线程通信演示",
                "description": "演示Queue、Event等线程间通信",
                "demo_class": CommunicationDemo,
                "method": "run_all_demos"
            },
            "11": {
                "name": "综合场景演示",
                "description": "综合应用场景（并发计算、爬虫模拟等）",
                "demo_class": ComprehensiveDemo,
                "method": "run_all_demos"
            },
            "12": {
                "name": "性能监控演示",
                "description": "线程性能监控和系统资源分析",
                "demo_class": MonitoringDemo,
                "method": "run_all_demos"
            },
            "13": {
                "name": "高级日志演示",
                "description": "结构化日志记录和分析系统",
                "demo_class": LoggingDemo,
                "method": "run_all_demos"
            }
        }
        
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🧵 Python多线程基础演示系统")
        print("="*60)
        print("\n请选择要演示的内容:")
        
        for key, demo in self.demos.items():
            print(f"  [{key}] {demo['name']}")
            print(f"      {demo['description']}")
            
        print(f"\n  [0] 退出程序")
        print(f"  [a] 运行所有演示")
        print("-" * 60)
        
    def run_demo(self, demo_key: str):
        """运行指定的演示"""
        if demo_key not in self.demos:
            print("❌ 无效的选择")
            return
            
        demo_info = self.demos[demo_key]
        print(f"\n🚀 开始运行: {demo_info['name']}")
        print(f"📝 描述: {demo_info['description']}")
        print("-" * 60)
        
        try:
            # 创建演示实例并运行
            demo_instance = demo_info['demo_class']()
            method = getattr(demo_instance, demo_info['method'])
            
            start_time = time.time()
            method()
            end_time = time.time()
            
            print("-" * 60)
            print(f"✅ 演示完成，耗时: {end_time - start_time:.2f} 秒")
            
        except KeyboardInterrupt:
            print("\n⚠️  演示被用户中断")
        except Exception as e:
            print(f"\n❌ 演示运行错误: {e}")
            import traceback
            traceback.print_exc()
            
    def run_all_demos(self):
        """运行所有演示"""
        print("\n🎯 开始运行所有演示...")
        total_start_time = time.time()
        
        for key in sorted(self.demos.keys()):
            print(f"\n{'='*20} 演示 {key} {'='*20}")
            self.run_demo(key)
            
            # 演示间暂停
            print("\n按回车键继续下一个演示...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n演示被中断")
                break
                
        total_end_time = time.time()
        print(f"\n🎉 所有演示完成，总耗时: {total_end_time - total_start_time:.2f} 秒")
        
    def run(self):
        """运行演示控制器"""
        print("🎭 欢迎使用 Python多线程基础演示系统!")
        print("📚 本系统将帮助您学习Python多线程编程的核心概念")
        
        while True:
            try:
                self.show_menu()
                choice = input("\n👉 请输入选择: ").strip().lower()
                
                if choice == '0' or choice == 'q' or choice == 'quit':
                    print("\n👋 谢谢使用，再见!")
                    break
                elif choice == 'a' or choice == 'all':
                    self.run_all_demos()
                elif choice in self.demos:
                    self.run_demo(choice)
                else:
                    print("❌ 无效的选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见!")
                break
            except Exception as e:
                print(f"\n❌ 程序运行错误: {e}")
                print("请重新选择")


def main():
    """主函数"""
    controller = DemoController()
    controller.run()


if __name__ == "__main__":
    main()