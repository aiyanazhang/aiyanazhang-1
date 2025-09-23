"""
基础线程创建演示模块

演示如何使用threading.Thread创建基本线程
"""

import threading
import time
import random
from typing import Callable, Any, Dict, List


class BasicThreadDemo:
    """基础线程创建演示类"""
    
    def __init__(self):
        self.threads: List[threading.Thread] = []
        self.results: Dict[str, Any] = {}
        
    def simple_worker_function(self, name: str, duration: int) -> None:
        """简单的工作函数，用于演示基础线程创建"""
        print(f"[{name}] 线程开始执行，预计运行 {duration} 秒")
        
        for i in range(duration):
            print(f"[{name}] 正在执行任务... ({i+1}/{duration})")
            time.sleep(1)
            
        result = f"线程 {name} 完成了 {duration} 秒的工作"
        self.results[name] = result
        print(f"[{name}] 线程执行完毕")
        
    def calculation_worker(self, name: str, start: int, end: int) -> None:
        """计算工作函数，演示带参数的线程"""
        print(f"[{name}] 开始计算 {start} 到 {end} 的平方和")
        
        total = 0
        for i in range(start, end + 1):
            total += i * i
            # 模拟计算时间
            time.sleep(0.001)
            
        self.results[name] = total
        print(f"[{name}] 计算完成，结果: {total}")
        
    def demo_basic_thread_creation(self) -> None:
        """演示基础线程创建"""
        print("\n=== 基础线程创建演示 ===")
        print("演示如何创建和启动基本线程")
        
        # 创建简单的工作线程
        thread1 = threading.Thread(
            target=self.simple_worker_function,
            args=("Worker-1", 3),
            name="BasicWorker1"
        )
        
        thread2 = threading.Thread(
            target=self.simple_worker_function,
            args=("Worker-2", 2),
            name="BasicWorker2"
        )
        
        # 存储线程引用
        self.threads.extend([thread1, thread2])
        
        print(f"创建了 {len(self.threads)} 个线程")
        print("线程信息:")
        for thread in self.threads:
            print(f"  - 线程名称: {thread.name}, 是否存活: {thread.is_alive()}")
            
        # 启动线程
        print("\n启动线程...")
        for thread in self.threads:
            thread.start()
            print(f"线程 {thread.name} 已启动")
            
        # 等待线程完成
        print("\n等待线程完成...")
        for thread in self.threads:
            thread.join()
            print(f"线程 {thread.name} 已完成")
            
        print("\n所有线程执行结果:")
        for name, result in self.results.items():
            print(f"  - {result}")
            
    def demo_thread_with_parameters(self) -> None:
        """演示带参数的线程创建"""
        print("\n=== 带参数的线程创建演示 ===")
        print("演示如何向线程传递不同类型的参数")
        
        # 清理之前的线程和结果
        self.threads.clear()
        self.results.clear()
        
        # 创建多个计算线程，传递不同参数
        thread_configs = [
            ("Calculator-1", 1, 100),
            ("Calculator-2", 101, 200),
            ("Calculator-3", 201, 300)
        ]
        
        for name, start, end in thread_configs:
            thread = threading.Thread(
                target=self.calculation_worker,
                args=(name, start, end),
                name=name
            )
            self.threads.append(thread)
            
        print(f"创建了 {len(self.threads)} 个计算线程")
        
        # 启动所有线程
        print("\n启动计算线程...")
        start_time = time.time()
        for thread in self.threads:
            thread.start()
            
        # 等待完成
        for thread in self.threads:
            thread.join()
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n所有计算完成，总耗时: {execution_time:.2f} 秒")
        print("计算结果:")
        for name, result in self.results.items():
            print(f"  - {name}: {result}")
            
    def demo_daemon_threads(self) -> None:
        """演示守护线程"""
        print("\n=== 守护线程演示 ===")
        print("演示守护线程与普通线程的区别")
        
        def daemon_worker(name: str):
            """守护线程工作函数"""
            for i in range(10):
                print(f"[守护线程 {name}] 运行中... {i+1}/10")
                time.sleep(0.5)
            print(f"[守护线程 {name}] 工作完成")
            
        def normal_worker(name: str):
            """普通线程工作函数"""
            for i in range(3):
                print(f"[普通线程 {name}] 运行中... {i+1}/3")
                time.sleep(1)
            print(f"[普通线程 {name}] 工作完成")
            
        # 创建守护线程
        daemon_thread = threading.Thread(
            target=daemon_worker,
            args=("Daemon-1",),
            name="DaemonThread"
        )
        daemon_thread.daemon = True  # 设置为守护线程
        
        # 创建普通线程
        normal_thread = threading.Thread(
            target=normal_worker,
            args=("Normal-1",),
            name="NormalThread"
        )
        
        print("线程类型信息:")
        print(f"  - {daemon_thread.name}: 守护线程={daemon_thread.daemon}")
        print(f"  - {normal_thread.name}: 守护线程={normal_thread.daemon}")
        
        # 启动线程
        print("\n启动线程...")
        daemon_thread.start()
        normal_thread.start()
        
        # 只等待普通线程完成
        normal_thread.join()
        
        print("普通线程完成，程序即将退出")
        print("守护线程会随着主程序退出而终止")
        
    def run_all_demos(self) -> None:
        """运行所有基础线程创建演示"""
        print("开始基础线程创建演示...")
        
        try:
            self.demo_basic_thread_creation()
            time.sleep(1)
            
            self.demo_thread_with_parameters()
            time.sleep(1)
            
            self.demo_daemon_threads()
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")
        finally:
            print("\n基础线程创建演示结束")


def main():
    """主函数，用于测试"""
    demo = BasicThreadDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()