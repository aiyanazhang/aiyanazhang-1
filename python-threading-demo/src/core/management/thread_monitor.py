"""
线程状态监控模块

演示如何监控线程的运行状态和性能指标
"""

import threading
import time
import psutil
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ThreadInfo:
    """线程信息数据类"""
    thread_id: int
    thread_name: str
    is_alive: bool
    is_daemon: bool
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    state: str = "UNKNOWN"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    exception: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'thread_id': self.thread_id,
            'thread_name': self.thread_name,
            'is_alive': self.is_alive,
            'is_daemon': self.is_daemon,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'state': self.state,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'exception': str(self.exception) if self.exception else None
        }


class ThreadMonitor:
    """线程监控器"""
    
    def __init__(self):
        self.monitored_threads: Dict[int, ThreadInfo] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.process = psutil.Process(os.getpid())
        
    def register_thread(self, thread: threading.Thread) -> None:
        """注册线程以进行监控"""
        with self.lock:
            thread_info = ThreadInfo(
                thread_id=thread.ident if thread.ident else 0,
                thread_name=thread.name,
                is_alive=thread.is_alive(),
                is_daemon=thread.daemon,
                start_time=datetime.now() if thread.is_alive() else None,
                state="CREATED"
            )
            self.monitored_threads[thread.ident if thread.ident else 0] = thread_info
            
    def update_thread_status(self, thread: threading.Thread) -> None:
        """更新线程状态"""
        thread_id = thread.ident if thread.ident else 0
        
        with self.lock:
            if thread_id in self.monitored_threads:
                info = self.monitored_threads[thread_id]
                info.is_alive = thread.is_alive()
                
                if not info.start_time and thread.is_alive():
                    info.start_time = datetime.now()
                    info.state = "RUNNING"
                elif info.is_alive:
                    info.state = "RUNNING"
                elif not info.is_alive and info.state != "TERMINATED":
                    info.state = "TERMINATED"
                    info.end_time = datetime.now()
                    
    def get_thread_stats(self) -> Dict[str, Any]:
        """获取线程统计信息"""
        with self.lock:
            total_threads = len(self.monitored_threads)
            alive_threads = sum(1 for info in self.monitored_threads.values() if info.is_alive)
            daemon_threads = sum(1 for info in self.monitored_threads.values() if info.is_daemon)
            
            # 获取系统资源使用情况
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_threads': total_threads,
                'alive_threads': alive_threads,
                'daemon_threads': daemon_threads,
                'terminated_threads': total_threads - alive_threads,
                'system_memory_mb': memory_info.rss / 1024 / 1024,
                'system_cpu_percent': cpu_percent,
                'thread_details': [info.to_dict() for info in self.monitored_threads.values()]
            }
            
    def start_monitoring(self, interval: float = 1.0) -> None:
        """开始监控线程"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            name="ThreadMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> None:
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            
    def _monitor_loop(self, interval: float) -> None:
        """监控循环"""
        while self.monitoring_active:
            try:
                # 更新所有已注册线程的状态
                current_threads = {t.ident: t for t in threading.enumerate() if t.ident}
                
                with self.lock:
                    for thread_id, info in self.monitored_threads.items():
                        if thread_id in current_threads:
                            thread = current_threads[thread_id]
                            info.is_alive = thread.is_alive()
                            if not info.is_alive and info.state == "RUNNING":
                                info.state = "TERMINATED"
                                info.end_time = datetime.now()
                                
                time.sleep(interval)
            except Exception as e:
                print(f"监控循环出错: {e}")
                
    def print_status_report(self) -> None:
        """打印状态报告"""
        stats = self.get_thread_stats()
        
        print(f"\n=== 线程监控报告 ({stats['timestamp']}) ===")
        print(f"总线程数: {stats['total_threads']}")
        print(f"活跃线程: {stats['alive_threads']}")
        print(f"守护线程: {stats['daemon_threads']}")
        print(f"已终止线程: {stats['terminated_threads']}")
        print(f"内存使用: {stats['system_memory_mb']:.2f} MB")
        print(f"CPU使用率: {stats['system_cpu_percent']:.1f}%")
        
        print("\n线程详情:")
        for detail in stats['thread_details']:
            status_icon = "🟢" if detail['is_alive'] else "🔴"
            daemon_icon = "👻" if detail['is_daemon'] else "👤"
            print(f"  {status_icon} {daemon_icon} {detail['thread_name']} "
                  f"({detail['state']}) - ID: {detail['thread_id']}")


class ThreadStateDemo:
    """线程状态监控演示"""
    
    def __init__(self):
        self.monitor = ThreadMonitor()
        self.demo_threads: List[threading.Thread] = []
        
    def sample_worker(self, name: str, duration: int, should_fail: bool = False) -> None:
        """示例工作函数"""
        print(f"[{name}] 开始工作，预计 {duration} 秒")
        
        try:
            for i in range(duration):
                if should_fail and i == duration // 2:
                    raise ValueError(f"线程 {name} 模拟异常")
                    
                print(f"[{name}] 工作进度: {i+1}/{duration}")
                time.sleep(1)
                
            print(f"[{name}] 工作完成")
            
        except Exception as e:
            print(f"[{name}] 发生异常: {e}")
            raise
            
    def demo_basic_monitoring(self) -> None:
        """演示基础线程监控"""
        print("\n=== 基础线程监控演示 ===")
        print("演示如何监控线程的基本状态")
        
        # 启动监控
        print("启动线程监控器...")
        self.monitor.start_monitoring(interval=0.5)
        
        # 创建一些示例线程
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=self.sample_worker,
                args=(f"Worker-{i+1}", 3 + i),
                name=f"DemoWorker{i+1}"
            )
            threads.append(thread)
            
        # 注册线程到监控器
        for thread in threads:
            self.monitor.register_thread(thread)
            
        print(f"创建了 {len(threads)} 个演示线程")
        
        # 显示初始状态
        self.monitor.print_status_report()
        
        # 启动线程
        print("\n启动所有线程...")
        for thread in threads:
            thread.start()
            self.monitor.update_thread_status(thread)
            
        # 定期显示状态
        for i in range(8):  # 监控8秒
            time.sleep(1)
            print(f"\n--- 监控中 ({i+1}/8) ---")
            self.monitor.print_status_report()
            
        # 等待线程完成
        print("\n等待线程完成...")
        for thread in threads:
            thread.join()
            self.monitor.update_thread_status(thread)
            
        # 显示最终状态
        print("\n=== 最终状态 ===")
        self.monitor.print_status_report()
        
        # 停止监控
        self.monitor.stop_monitoring()
        
    def demo_exception_monitoring(self) -> None:
        """演示异常线程监控"""
        print("\n=== 异常线程监控演示 ===")
        print("演示如何监控可能出现异常的线程")
        
        # 重启监控
        self.monitor = ThreadMonitor()
        self.monitor.start_monitoring(interval=0.3)
        
        # 创建一些可能出错的线程
        thread_configs = [
            ("NormalWorker", 2, False),
            ("FailingWorker", 3, True),
            ("AnotherNormal", 1, False)
        ]
        
        threads = []
        for name, duration, should_fail in thread_configs:
            thread = threading.Thread(
                target=self.sample_worker,
                args=(name, duration, should_fail),
                name=name
            )
            threads.append(thread)
            self.monitor.register_thread(thread)
            
        print(f"创建了 {len(threads)} 个线程（包含会失败的线程）")
        
        # 启动线程并监控
        for thread in threads:
            thread.start()
            
        # 监控线程状态
        monitoring_time = 5
        for i in range(monitoring_time):
            time.sleep(1)
            print(f"\n--- 异常监控中 ({i+1}/{monitoring_time}) ---")
            self.monitor.print_status_report()
            
        # 等待线程完成（包括异常线程）
        for thread in threads:
            try:
                thread.join(timeout=1)
            except Exception as e:
                print(f"等待线程 {thread.name} 时出现异常: {e}")
                
        print("\n=== 异常监控最终状态 ===")
        self.monitor.print_status_report()
        
        # 清理
        self.monitor.stop_monitoring()
        
    def demo_real_time_monitoring(self) -> None:
        """演示实时监控"""
        print("\n=== 实时监控演示 ===")
        print("演示线程状态的实时变化")
        
        # 创建新的监控器
        self.monitor = ThreadMonitor()
        self.monitor.start_monitoring(interval=0.2)
        
        def dynamic_worker(name: str):
            """动态工作负载线程"""
            phases = ["初始化", "处理数据", "计算结果", "清理资源"]
            
            for phase in phases:
                print(f"[{name}] {phase}...")
                time.sleep(random.uniform(0.5, 1.5))
                
        # 交错启动线程
        threads = []
        for i in range(4):
            thread = threading.Thread(
                target=dynamic_worker,
                args=(f"DynamicWorker-{i+1}",),
                name=f"DynamicWorker{i+1}"
            )
            threads.append(thread)
            self.monitor.register_thread(thread)
            
        print("交错启动线程，观察实时状态变化...")
        
        # 交错启动
        for i, thread in enumerate(threads):
            thread.start()
            print(f"\n启动线程 {thread.name}")
            self.monitor.print_status_report()
            time.sleep(0.8)  # 错开启动时间
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        print("\n=== 实时监控完成 ===")
        self.monitor.print_status_report()
        
        # 清理
        self.monitor.stop_monitoring()
        
    def run_all_demos(self) -> None:
        """运行所有监控演示"""
        print("开始线程状态监控演示...")
        
        try:
            self.demo_basic_monitoring()
            time.sleep(1)
            
            self.demo_exception_monitoring()
            time.sleep(1)
            
            self.demo_real_time_monitoring()
            
        except KeyboardInterrupt:
            print("\n监控演示被用户中断")
        except Exception as e:
            print(f"\n监控演示过程中发生错误: {e}")
        finally:
            # 确保清理监控器
            if hasattr(self, 'monitor'):
                self.monitor.stop_monitoring()
            print("\n线程状态监控演示结束")


def main():
    """主函数，用于测试"""
    import random
    demo = ThreadStateDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()