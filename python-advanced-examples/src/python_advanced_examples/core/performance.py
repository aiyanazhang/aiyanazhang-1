"""
性能监控模块

提供详细的性能分析、监控和基准测试功能。
"""

import cProfile
import functools
import io
import logging
import pstats
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
import threading
import psutil
import tracemalloc
from contextlib import contextmanager
import weakref

logger = logging.getLogger(__name__)


@dataclass
class PerformanceData:
    """性能数据"""
    function_name: str
    execution_time: float
    memory_usage: float  # MB
    cpu_usage: float  # 百分比
    call_count: int = 1
    max_memory: float = 0.0
    min_memory: float = float('inf')
    total_time: float = 0.0
    last_call_time: float = field(default_factory=time.time)
    memory_peak: float = 0.0
    memory_allocations: int = 0
    memory_deallocations: int = 0
    
    def update(self, other: 'PerformanceData'):
        """更新性能数据"""
        self.call_count += other.call_count
        self.total_time += other.execution_time
        self.max_memory = max(self.max_memory, other.memory_usage)
        self.min_memory = min(self.min_memory, other.memory_usage)
        self.memory_peak = max(self.memory_peak, other.memory_peak)
        self.last_call_time = other.last_call_time
        self.memory_allocations += other.memory_allocations
        self.memory_deallocations += other.memory_deallocations
    
    @property
    def average_time(self) -> float:
        """平均执行时间"""
        return self.total_time / self.call_count if self.call_count > 0 else 0
    
    @property
    def average_memory(self) -> float:
        """平均内存使用"""
        return (self.max_memory + self.min_memory) / 2 if self.min_memory != float('inf') else 0


class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.tracing = False
        self.snapshots = []
        self.baseline = None
    
    def start_tracing(self):
        """开始内存跟踪"""
        if not self.tracing:
            tracemalloc.start()
            self.tracing = True
            self.baseline = tracemalloc.take_snapshot()
    
    def stop_tracing(self):
        """停止内存跟踪"""
        if self.tracing:
            tracemalloc.stop()
            self.tracing = False
    
    def take_snapshot(self) -> Optional[tracemalloc.Snapshot]:
        """获取内存快照"""
        if self.tracing:
            snapshot = tracemalloc.take_snapshot()
            self.snapshots.append(snapshot)
            return snapshot
        return None
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """获取当前内存使用情况"""
        if not self.tracing:
            return {}
        
        current = tracemalloc.take_snapshot()
        if self.baseline:
            top_stats = current.compare_to(self.baseline, 'lineno')
        else:
            top_stats = current.statistics('lineno')
        
        total_size = sum(stat.size for stat in top_stats)
        total_count = sum(stat.count for stat in top_stats)
        
        return {
            "total_size_mb": total_size / 1024 / 1024,
            "total_blocks": total_count,
            "top_allocations": [
                {
                    "file": stat.traceback.format()[-1] if stat.traceback else "unknown",
                    "size_mb": stat.size / 1024 / 1024,
                    "count": stat.count
                }
                for stat in top_stats[:10]
            ]
        }


class CPUProfiler:
    """CPU分析器"""
    
    def __init__(self):
        self.profiler = None
        self.profile_data = None
    
    def start_profiling(self):
        """开始CPU分析"""
        self.profiler = cProfile.Profile()
        self.profiler.enable()
    
    def stop_profiling(self):
        """停止CPU分析"""
        if self.profiler:
            self.profiler.disable()
            self.profile_data = self.profiler
    
    def get_stats(self, sort_by: str = 'cumulative') -> str:
        """获取分析统计"""
        if not self.profile_data:
            return ""
        
        stream = io.StringIO()
        stats = pstats.Stats(self.profile_data, stream=stream)
        stats.sort_stats(sort_by)
        stats.print_stats(20)  # 显示前20个函数
        
        return stream.getvalue()
    
    def get_function_stats(self) -> List[Dict[str, Any]]:
        """获取函数级别的统计信息"""
        if not self.profile_data:
            return []
        
        stats = pstats.Stats(self.profile_data)
        function_stats = []
        
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            function_stats.append({
                "function": f"{func[0]}:{func[1]}({func[2]})",
                "call_count": cc,
                "total_time": tt,
                "cumulative_time": ct,
                "per_call_time": tt / cc if cc > 0 else 0,
                "per_call_cumulative": ct / cc if cc > 0 else 0
            })
        
        return sorted(function_stats, key=lambda x: x["cumulative_time"], reverse=True)


class RealTimeMonitor:
    """实时监控器"""
    
    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.monitoring = False
        self.data_points = deque(maxlen=1000)  # 保留最近1000个数据点
        self.monitor_thread = None
        self.process = psutil.Process()
    
    def start(self):
        """开始实时监控"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop(self):
        """停止实时监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = self.process.cpu_percent()
                
                # 内存使用
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # 记录数据点
                data_point = {
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_mb,
                    "num_threads": self.process.num_threads(),
                }
                
                self.data_points.append(data_point)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            
            time.sleep(self.interval)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        if not self.data_points:
            return {}
        
        recent_points = list(self.data_points)[-100:]  # 最近100个点
        
        cpu_values = [p["cpu_percent"] for p in recent_points]
        memory_values = [p["memory_mb"] for p in recent_points]
        
        return {
            "current_cpu": cpu_values[-1] if cpu_values else 0,
            "average_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "peak_cpu": max(cpu_values) if cpu_values else 0,
            "current_memory": memory_values[-1] if memory_values else 0,
            "average_memory": sum(memory_values) / len(memory_values) if memory_values else 0,
            "peak_memory": max(memory_values) if memory_values else 0,
            "data_points": len(self.data_points)
        }
    
    def get_time_series(self, duration_seconds: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取时间序列数据"""
        data_points = list(self.data_points)
        
        if duration_seconds and data_points:
            cutoff_time = time.time() - duration_seconds
            data_points = [p for p in data_points if p["timestamp"] >= cutoff_time]
        
        return data_points


class PerformanceMonitor:
    """性能监控器主类"""
    
    def __init__(self):
        self.performance_data: Dict[str, PerformanceData] = {}
        self.memory_profiler = MemoryProfiler()
        self.cpu_profiler = CPUProfiler()
        self.realtime_monitor = RealTimeMonitor()
        self.enabled = True
        self._monitored_functions = weakref.WeakSet()
    
    def enable(self):
        """启用性能监控"""
        self.enabled = True
        self.memory_profiler.start_tracing()
        self.realtime_monitor.start()
    
    def disable(self):
        """禁用性能监控"""
        self.enabled = False
        self.memory_profiler.stop_tracing()
        self.realtime_monitor.stop()
    
    @contextmanager
    def profile(self, name: str):
        """性能分析上下文管理器"""
        if not self.enabled:
            yield
            return
        
        # 记录开始状态
        start_time = time.time()
        start_memory = self._get_current_memory()
        start_cpu = psutil.cpu_percent()
        
        # 内存快照
        memory_snapshot_before = self.memory_profiler.take_snapshot()
        
        try:
            yield
        finally:
            # 记录结束状态
            end_time = time.time()
            end_memory = self._get_current_memory()
            end_cpu = psutil.cpu_percent()
            
            # 计算指标
            execution_time = end_time - start_time
            memory_usage = max(end_memory - start_memory, 0)
            cpu_usage = (end_cpu + start_cpu) / 2
            
            # 内存分配信息
            memory_snapshot_after = self.memory_profiler.take_snapshot()
            memory_allocations = 0
            memory_deallocations = 0
            
            if memory_snapshot_before and memory_snapshot_after:
                memory_diff = memory_snapshot_after.compare_to(memory_snapshot_before, 'lineno')
                memory_allocations = sum(1 for stat in memory_diff if stat.size_diff > 0)
                memory_deallocations = sum(1 for stat in memory_diff if stat.size_diff < 0)
            
            # 创建性能数据
            perf_data = PerformanceData(
                function_name=name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                memory_peak=end_memory,
                memory_allocations=memory_allocations,
                memory_deallocations=memory_deallocations
            )
            
            # 更新统计
            self._update_performance_data(name, perf_data)
    
    def _get_current_memory(self) -> float:
        """获取当前内存使用（MB）"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def _update_performance_data(self, name: str, new_data: PerformanceData):
        """更新性能数据"""
        if name in self.performance_data:
            self.performance_data[name].update(new_data)
        else:
            self.performance_data[name] = new_data
    
    def get_stats(self, function_name: Optional[str] = None) -> Union[PerformanceData, Dict[str, PerformanceData]]:
        """获取性能统计"""
        if function_name:
            return self.performance_data.get(function_name)
        return self.performance_data.copy()
    
    def get_top_functions(self, metric: str = "total_time", limit: int = 10) -> List[PerformanceData]:
        """获取性能排行榜"""
        valid_metrics = ["total_time", "call_count", "average_time", "max_memory", "memory_peak"]
        
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric: {metric}. Valid options: {valid_metrics}")
        
        sorted_data = sorted(
            self.performance_data.values(),
            key=lambda x: getattr(x, metric),
            reverse=True
        )
        
        return sorted_data[:limit]
    
    def generate_report(self, include_realtime: bool = True) -> Dict[str, Any]:
        """生成性能报告"""
        report = {
            "summary": {
                "total_functions_monitored": len(self.performance_data),
                "total_calls": sum(data.call_count for data in self.performance_data.values()),
                "total_execution_time": sum(data.total_time for data in self.performance_data.values()),
            },
            "top_functions": {
                "by_time": [
                    {
                        "name": data.function_name,
                        "total_time": data.total_time,
                        "call_count": data.call_count,
                        "average_time": data.average_time
                    }
                    for data in self.get_top_functions("total_time", 5)
                ],
                "by_memory": [
                    {
                        "name": data.function_name,
                        "peak_memory": data.memory_peak,
                        "max_memory": data.max_memory,
                        "average_memory": data.average_memory
                    }
                    for data in self.get_top_functions("memory_peak", 5)
                ],
                "by_calls": [
                    {
                        "name": data.function_name,
                        "call_count": data.call_count,
                        "total_time": data.total_time,
                        "average_time": data.average_time
                    }
                    for data in self.get_top_functions("call_count", 5)
                ]
            },
            "memory_analysis": self.memory_profiler.get_memory_usage(),
        }
        
        if include_realtime:
            report["realtime_stats"] = self.realtime_monitor.get_current_stats()
        
        # CPU分析统计
        if self.cpu_profiler.profile_data:
            report["cpu_analysis"] = {
                "function_stats": self.cpu_profiler.get_function_stats()[:10],
                "detailed_stats": self.cpu_profiler.get_stats()
            }
        
        return report
    
    def reset_stats(self):
        """重置所有统计数据"""
        self.performance_data.clear()
        self.memory_profiler.snapshots.clear()
        self.cpu_profiler.profile_data = None
    
    def start_cpu_profiling(self):
        """开始CPU分析"""
        self.cpu_profiler.start_profiling()
    
    def stop_cpu_profiling(self):
        """停止CPU分析"""
        self.cpu_profiler.stop_profiling()
    
    def export_data(self, filename: str, format: str = "json"):
        """导出性能数据"""
        import json
        
        data = {
            "performance_data": {
                name: {
                    "function_name": perf.function_name,
                    "execution_time": perf.execution_time,
                    "memory_usage": perf.memory_usage,
                    "cpu_usage": perf.cpu_usage,
                    "call_count": perf.call_count,
                    "total_time": perf.total_time,
                    "average_time": perf.average_time,
                    "max_memory": perf.max_memory,
                    "memory_peak": perf.memory_peak,
                    "last_call_time": perf.last_call_time
                }
                for name, perf in self.performance_data.items()
            },
            "realtime_data": self.realtime_monitor.get_time_series(3600),  # 最近1小时
            "memory_analysis": self.memory_profiler.get_memory_usage(),
            "report": self.generate_report(include_realtime=False)
        }
        
        if format.lower() == "json":
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")


# 装饰器函数
def monitor_performance(name: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        func_name = name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 使用全局监控器实例
            from . import monitor
            
            with monitor.profile(func_name):
                return func(*args, **kwargs)
        
        return wrapper
    
    if callable(name):
        # 直接使用 @monitor_performance（无参数）
        func = name
        return decorator(func)
    else:
        # 使用 @monitor_performance("name")（有参数）
        return decorator


def benchmark(iterations: int = 10, warmup: int = 3):
    """基准测试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from . import monitor
            
            func_name = f"{func.__module__}.{func.__name__}_benchmark"
            
            # 预热
            for _ in range(warmup):
                func(*args, **kwargs)
            
            # 基准测试
            results = []
            for _ in range(iterations):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                results.append({
                    "result": result,
                    "execution_time": end_time - start_time
                })
            
            # 计算统计
            times = [r["execution_time"] for r in results]
            stats = {
                "iterations": iterations,
                "total_time": sum(times),
                "average_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "std_dev": (sum((t - sum(times) / len(times)) ** 2 for t in times) / len(times)) ** 0.5,
                "results": results
            }
            
            logger.info(f"Benchmark {func_name}: {stats['average_time']:.6f}s avg, {stats['std_dev']:.6f}s std")
            
            return stats
        
        return wrapper
    
    return decorator