"""
性能监控模块

监控线程执行性能和系统资源使用情况
"""

import threading
import time
import psutil
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import queue


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime
    thread_count: int
    active_threads: int
    daemon_threads: int
    cpu_usage: float
    memory_usage: float
    memory_rss: int
    memory_vms: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'thread_count': self.thread_count,
            'active_threads': self.active_threads,
            'daemon_threads': self.daemon_threads,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'memory_rss': self.memory_rss,
            'memory_vms': self.memory_vms
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.monitor_thread: Optional[threading.Thread] = None
        self.process = psutil.Process(os.getpid())
        self.lock = threading.Lock()
        self.callbacks: List[callable] = []
        
    def add_callback(self, callback: callable):
        """添加性能指标回调函数"""
        self.callbacks.append(callback)
        
    def start_monitoring(self):
        """开始性能监控"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="PerformanceMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        print(f"[性能监控] 开始监控，间隔: {self.interval}秒")
        
    def stop_monitoring(self):
        """停止性能监控"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("[性能监控] 监控已停止")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                
                with self.lock:
                    self.metrics_history.append(metrics)
                    # 保持历史记录不超过1000条
                    if len(self.metrics_history) > 1000:
                        self.metrics_history.pop(0)
                        
                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        print(f"[性能监控] 回调函数执行失败: {e}")
                        
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"[性能监控] 监控循环出错: {e}")
                time.sleep(self.interval)
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        # 线程信息
        all_threads = threading.enumerate()
        active_threads = [t for t in all_threads if t.is_alive()]
        daemon_threads = [t for t in all_threads if t.daemon]
        
        # 系统资源信息
        try:
            cpu_usage = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            cpu_usage = 0.0
            memory_info = psutil._common.pmem(rss=0, vms=0)
            memory_percent = 0.0
            
        return PerformanceMetrics(
            timestamp=datetime.now(),
            thread_count=len(all_threads),
            active_threads=len(active_threads),
            daemon_threads=len(daemon_threads),
            cpu_usage=cpu_usage,
            memory_usage=memory_percent,
            memory_rss=memory_info.rss,
            memory_vms=memory_info.vms
        )
        
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        return self._collect_metrics()
        
    def get_metrics_history(self) -> List[PerformanceMetrics]:
        """获取历史性能指标"""
        with self.lock:
            return self.metrics_history.copy()
            
    def get_statistics(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        with self.lock:
            if not self.metrics_history:
                return {"error": "没有性能数据"}
                
            cpu_values = [m.cpu_usage for m in self.metrics_history]
            memory_values = [m.memory_usage for m in self.metrics_history]
            thread_counts = [m.thread_count for m in self.metrics_history]
            
            return {
                'data_points': len(self.metrics_history),
                'time_range': {
                    'start': self.metrics_history[0].timestamp.isoformat(),
                    'end': self.metrics_history[-1].timestamp.isoformat()
                },
                'cpu_usage': {
                    'min': min(cpu_values),
                    'max': max(cpu_values),
                    'avg': sum(cpu_values) / len(cpu_values)
                },
                'memory_usage': {
                    'min': min(memory_values),
                    'max': max(memory_values),
                    'avg': sum(memory_values) / len(memory_values)
                },
                'thread_count': {
                    'min': min(thread_counts),
                    'max': max(thread_counts),
                    'avg': sum(thread_counts) / len(thread_counts)
                }
            }
            
    def save_metrics(self, filename: str):
        """保存性能指标到文件"""
        with self.lock:
            data = {
                'collection_info': {
                    'interval': self.interval,
                    'total_points': len(self.metrics_history)
                },
                'metrics': [m.to_dict() for m in self.metrics_history],
                'statistics': self.get_statistics()
            }
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[性能监控] 指标已保存到: {filename}")
        except Exception as e:
            print(f"[性能监控] 保存指标失败: {e}")
            
    def print_current_status(self):
        """打印当前状态"""
        metrics = self.get_current_metrics()
        if metrics:
            print(f"\n=== 当前性能状态 ===")
            print(f"时间: {metrics.timestamp.strftime('%H:%M:%S')}")
            print(f"线程总数: {metrics.thread_count}")
            print(f"活跃线程: {metrics.active_threads}")
            print(f"守护线程: {metrics.daemon_threads}")
            print(f"CPU使用率: {metrics.cpu_usage:.1f}%")
            print(f"内存使用率: {metrics.memory_usage:.1f}%")
            print(f"内存占用: {metrics.memory_rss / 1024 / 1024:.1f} MB")
            
    def create_report(self) -> str:
        """创建性能报告"""
        stats = self.get_statistics()
        if 'error' in stats:
            return stats['error']
            
        report = []
        report.append("=== 性能监控报告 ===")
        report.append(f"数据点数: {stats['data_points']}")
        report.append(f"监控时间: {stats['time_range']['start']} 到 {stats['time_range']['end']}")
        report.append("")
        
        report.append("CPU使用率:")
        report.append(f"  最小值: {stats['cpu_usage']['min']:.1f}%")
        report.append(f"  最大值: {stats['cpu_usage']['max']:.1f}%")
        report.append(f"  平均值: {stats['cpu_usage']['avg']:.1f}%")
        report.append("")
        
        report.append("内存使用率:")
        report.append(f"  最小值: {stats['memory_usage']['min']:.1f}%")
        report.append(f"  最大值: {stats['memory_usage']['max']:.1f}%")
        report.append(f"  平均值: {stats['memory_usage']['avg']:.1f}%")
        report.append("")
        
        report.append("线程数量:")
        report.append(f"  最小值: {stats['thread_count']['min']}")
        report.append(f"  最大值: {stats['thread_count']['max']}")
        report.append(f"  平均值: {stats['thread_count']['avg']:.1f}")
        
        return "\n".join(report)


class MonitoringDemo:
    """监控演示"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor(interval=0.5)
        self.setup_callbacks()
        
    def setup_callbacks(self):
        """设置监控回调"""
        def high_cpu_alert(metrics: PerformanceMetrics):
            """高CPU使用率告警"""
            if metrics.cpu_usage > 80:
                print(f"⚠️  [告警] CPU使用率过高: {metrics.cpu_usage:.1f}%")
                
        def thread_count_monitor(metrics: PerformanceMetrics):
            """线程数量监控"""
            if metrics.thread_count > 20:
                print(f"📊 [监控] 线程数量较多: {metrics.thread_count}")
                
        self.monitor.add_callback(high_cpu_alert)
        self.monitor.add_callback(thread_count_monitor)
        
    def demo_basic_monitoring(self):
        """基础监控演示"""
        print("\n=== 基础性能监控演示 ===")
        
        # 启动监控
        self.monitor.start_monitoring()
        
        def cpu_intensive_task(task_id: int):
            """CPU密集型任务"""
            print(f"[Task{task_id}] 开始CPU密集型计算")
            start = time.time()
            # 计算斐波那契数列
            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            
            result = fibonacci(35)  # 这会消耗一些CPU
            end = time.time()
            print(f"[Task{task_id}] 计算完成，结果: {result}，耗时: {end-start:.2f}秒")
            
        # 创建CPU密集型任务
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=cpu_intensive_task,
                args=(i+1,),
                name=f"CPUTask{i+1}"
            )
            threads.append(thread)
            
        print("启动CPU密集型任务...")
        
        # 启动任务并监控
        for thread in threads:
            thread.start()
            time.sleep(1)  # 间隔启动
            self.monitor.print_current_status()
            
        # 等待任务完成
        for thread in threads:
            thread.join()
            
        time.sleep(2)  # 等待最后的监控数据
        
        # 停止监控并显示报告
        self.monitor.stop_monitoring()
        
        print("\n" + self.monitor.create_report())
        
    def demo_memory_monitoring(self):
        """内存监控演示"""
        print("\n=== 内存使用监控演示 ===")
        
        self.monitor = PerformanceMonitor(interval=0.3)
        self.monitor.start_monitoring()
        
        def memory_intensive_task(task_id: int):
            """内存密集型任务"""
            print(f"[MemTask{task_id}] 开始内存密集型操作")
            
            # 创建大量数据
            data = []
            for i in range(100000):
                data.append(f"数据项_{task_id}_{i}")
                if i % 20000 == 0:
                    print(f"[MemTask{task_id}] 已创建 {i} 项数据")
                    time.sleep(0.1)
                    
            print(f"[MemTask{task_id}] 内存操作完成，数据量: {len(data)}")
            
            # 清理数据
            del data
            
        # 创建内存密集型任务
        threads = []
        for i in range(2):
            thread = threading.Thread(
                target=memory_intensive_task,
                args=(i+1,),
                name=f"MemoryTask{i+1}"
            )
            threads.append(thread)
            
        print("启动内存密集型任务...")
        
        # 启动任务
        for thread in threads:
            thread.start()
            
        # 定期显示状态
        for i in range(8):
            time.sleep(1)
            self.monitor.print_current_status()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        # 停止监控
        self.monitor.stop_monitoring()
        
        print("\n" + self.monitor.create_report())
        
    def run_all_demos(self):
        """运行所有监控演示"""
        print("开始性能监控演示...")
        
        try:
            self.demo_basic_monitoring()
            time.sleep(2)
            
            self.demo_memory_monitoring()
            
        except KeyboardInterrupt:
            print("\n监控演示被用户中断")
        except Exception as e:
            print(f"\n监控演示出错: {e}")
        finally:
            if hasattr(self, 'monitor'):
                self.monitor.stop_monitoring()
            print("\n性能监控演示结束")


def main():
    """主函数"""
    demo = MonitoringDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()