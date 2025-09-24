"""
Python多线程演示系统主程序
集成所有演示模块，提供统一的演示入口
"""

import sys
import os
import time
from typing import Dict, Any
import threading
from datetime import datetime

# 添加src目录到路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from basic_thread_demo import BasicThreadDemo
from thread_pool_demo import ThreadPoolDemo
from producer_consumer_demo import ProducerConsumerDemo
from thread_sync_demo import ThreadSyncDemo
from file_downloader import demo_file_downloader
from data_processor import demo_sales_data_processing, demo_log_data_processing


class ThreadingDemoSystem:
    """Python多线程演示系统主类"""
    
    def __init__(self):
        self.demos = {
            '1': {
                'name': '基础线程演示',
                'description': '展示Python threading模块的基本使用方法',
                'class': BasicThreadDemo,
                'icon': '🧵'
            },
            '2': {
                'name': '线程池演示',
                'description': '展示concurrent.futures模块的ThreadPoolExecutor使用',
                'class': ThreadPoolDemo,
                'icon': '⚡'
            },
            '3': {
                'name': '生产者消费者演示',
                'description': '实现经典的生产者消费者模式，展示线程间通信',
                'class': ProducerConsumerDemo,
                'icon': '🏭'
            },
            '4': {
                'name': '线程同步演示',
                'description': '展示各种线程同步原语的使用，确保线程安全',
                'class': ThreadSyncDemo,
                'icon': '🔒'
            },
            '5': {
                'name': '文件下载器',
                'description': '并发下载多个文件的实际应用场景',
                'class': None,  # 使用函数
                'function': demo_file_downloader,
                'icon': '📥'
            },
            '6': {
                'name': '数据处理器',
                'description': '大数据集并行处理的实际应用场景',
                'class': None,  # 使用函数
                'function': demo_sales_data_processing,
                'icon': '📊'
            },
            '7': {
                'name': '日志分析器',
                'description': '日志数据并行分析处理',
                'class': None,  # 使用函数
                'function': demo_log_data_processing,
                'icon': '📋'
            }
        }
        
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            import psutil
            memory_total = psutil.virtual_memory().total // (1024**3)  # GB
        except ImportError:
            memory_total = 8  # 默认8GB
        
        return {
            'python_version': sys.version,
            'cpu_count': os.cpu_count(),
            'memory_total': memory_total,
            'platform': sys.platform,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def print_header(self):
        """打印系统头部信息"""
        print("=" * 80)
        print("🐍 Python 多线程演示系统")
        print("=" * 80)
        print(f"🖥️  系统信息:")
        print(f"   Python版本: {self.system_info['python_version'].split()[0]}")
        print(f"   CPU核心数: {self.system_info['cpu_count']}")
        print(f"   系统内存: {self.system_info['memory_total']} GB")
        print(f"   运行平台: {self.system_info['platform']}")
        print(f"   当前时间: {self.system_info['current_time']}")
        print(f"   活跃线程数: {threading.active_count()}")
        print("=" * 80)
    
    def print_menu(self):
        """打印主菜单"""
        print("\n📋 请选择要运行的演示:")
        print("-" * 60)
        
        for key, demo in self.demos.items():
            print(f"  {key}. {demo['icon']} {demo['name']}")
            print(f"     {demo['description']}")
            print()
        
        print("  0. 🚀 运行所有演示")
        print("  q. 🚪 退出系统")
        print("-" * 60)
    
    def run_demo(self, demo_key: str) -> bool:
        """运行指定的演示"""
        if demo_key not in self.demos:
            print(f"❌ 无效的选择: {demo_key}")
            return False
        
        demo = self.demos[demo_key]
        
        print(f"\n{demo['icon']} 启动演示: {demo['name']}")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            if demo['class']:
                # 使用类的方式
                demo_instance = demo['class']()
                demo_instance.run_all_demos()
            elif 'function' in demo:
                # 使用函数的方式
                demo['function']()
            else:
                print(f"❌ 演示配置错误: {demo['name']}")
                return False
            
            end_time = time.time()
            
            print(f"\n✅ 演示完成: {demo['name']}")
            print(f"⏱️  总耗时: {end_time - start_time:.2f}秒")
            print(f"🧵 当前活跃线程数: {threading.active_count()}")
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n⚠️  演示被用户中断: {demo['name']}")
            return False
        except Exception as e:
            print(f"\n❌ 演示执行出错: {demo['name']}")
            print(f"错误详情: {e}")
            return False
    
    def run_all_demos(self):
        """运行所有演示"""
        print(f"\n🚀 开始运行所有演示")
        print("=" * 80)
        
        total_start_time = time.time()
        successful_demos = 0
        failed_demos = 0
        
        for key in sorted(self.demos.keys()):
            demo = self.demos[key]
            
            print(f"\n{'='*20} 演示 {key}/{len(self.demos)}: {demo['name']} {'='*20}")
            
            if self.run_demo(key):
                successful_demos += 1
            else:
                failed_demos += 1
            
            # 演示间暂停
            if key != max(self.demos.keys()):
                print(f"\n⏸️  暂停3秒后继续下一个演示...")
                time.sleep(3)
        
        total_end_time = time.time()
        
        # 总结
        print(f"\n🎯 所有演示执行完成")
        print("=" * 80)
        print(f"📊 执行统计:")
        print(f"   总演示数: {len(self.demos)}")
        print(f"   成功演示: {successful_demos}")
        print(f"   失败演示: {failed_demos}")
        print(f"   成功率: {(successful_demos / len(self.demos)) * 100:.1f}%")
        print(f"   总耗时: {total_end_time - total_start_time:.2f}秒")
        print(f"   最终活跃线程数: {threading.active_count()}")
        print("=" * 80)
    
    def interactive_mode(self):
        """交互模式"""
        self.print_header()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("👉 请输入选择 (0-7, q): ").strip().lower()
                
                if choice == 'q':
                    print(f"\n👋 感谢使用Python多线程演示系统！")
                    break
                elif choice == '0':
                    self.run_all_demos()
                elif choice in self.demos:
                    self.run_demo(choice)
                else:
                    print(f"❌ 无效选择，请输入 0-7 或 q")
                
                # 询问是否继续
                if choice != 'q':
                    print(f"\n" + "-" * 60)
                    continue_choice = input("是否继续？(y/n): ").strip().lower()
                    if continue_choice in ['n', 'no']:
                        print(f"\n👋 感谢使用Python多线程演示系统！")
                        break
                    
            except KeyboardInterrupt:
                print(f"\n\n👋 用户中断，感谢使用Python多线程演示系统！")
                break
            except Exception as e:
                print(f"❌ 输入处理错误: {e}")
                continue
    
    def command_line_mode(self, demo_keys: list):
        """命令行模式"""
        self.print_header()
        
        print(f"🎯 命令行模式 - 运行指定演示: {', '.join(demo_keys)}")
        
        for demo_key in demo_keys:
            if demo_key == 'all':
                self.run_all_demos()
            elif demo_key in self.demos:
                self.run_demo(demo_key)
            else:
                print(f"❌ 无效的演示选择: {demo_key}")


def print_usage():
    """打印使用说明"""
    print("使用方法:")
    print("  python main.py                    # 交互模式")
    print("  python main.py all                # 运行所有演示")
    print("  python main.py 1 2 3             # 运行指定的演示")
    print("  python main.py --help            # 显示帮助")
    print()
    print("演示列表:")
    demos = {
        '1': '基础线程演示',
        '2': '线程池演示', 
        '3': '生产者消费者演示',
        '4': '线程同步演示',
        '5': '文件下载器',
        '6': '数据处理器',
        '7': '日志分析器'
    }
    for key, name in demos.items():
        print(f"  {key}: {name}")


def main():
    """主函数"""
    system = ThreadingDemoSystem()
    
    # 解析命令行参数
    if len(sys.argv) == 1:
        # 无参数，启动交互模式
        system.interactive_mode()
    elif len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']:
        # 显示帮助
        print_usage()
    else:
        # 命令行模式
        demo_keys = sys.argv[1:]
        system.command_line_mode(demo_keys)


if __name__ == "__main__":
    main()