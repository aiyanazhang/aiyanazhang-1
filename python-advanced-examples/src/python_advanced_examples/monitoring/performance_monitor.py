"""
性能监控系统

实时监控系统和应用性能：
- CPU使用率监控
- 内存使用监控
- 磁盘I/O监控
- 网络I/O监控
- 应用级性能指标
"""

import psutil
import threading
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
from abc import ABC, abstractmethod
import logging
import json
from datetime import datetime
import weakref

@dataclass
class PerformanceSnapshot:
    """性能快照数据"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_usage_percent: float
    disk_read_bytes: int
    disk_write_bytes: int
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    thread_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'memory': {
                'percent': self.memory_percent,
                'used': self.memory_used,
                'available': self.memory_available
            },
            'disk': {
                'usage_percent': self.disk_usage_percent,
                'read_bytes': self.disk_read_bytes,
                'write_bytes': self.disk_write_bytes
            },
            'network': {
                'bytes_sent': self.network_bytes_sent,
                'bytes_recv': self.network_bytes_recv
            },
            'processes': {
                'process_count': self.process_count,
                'thread_count': self.thread_count
            }
        }

@dataclass
class ApplicationMetrics:
    """应用程序指标"""
    request_count: int = 0
    response_time_ms: float = 0.0
    error_count: int = 0
    active_connections: int = 0
    cache_hit_rate: float = 0.0
    queue_size: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'request_count': self.request_count,
            'response_time_ms': self.response_time_ms,
            'error_count': self.error_count,
            'active_connections': self.active_connections,
            'cache_hit_rate': self.cache_hit_rate,
            'queue_size': self.queue_size,
            'custom_metrics': self.custom_metrics
        }

class PerformanceMonitor:
    """性能监控器基类"""
    
    def __init__(self, interval: float = 1.0, max_history: int = 1000):
        self.interval = interval
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self.is_monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        self.callbacks = []
        
    def add_callback(self, callback: Callable[[PerformanceSnapshot], None]):
        """添加监控回调函数"""
        self.callbacks.append(callback)
    
    def start(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("性能监控已启动")
    
    def stop(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                snapshot = self._collect_metrics()
                self.history.append(snapshot)
                
                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(snapshot)
                    except Exception as e:
                        self.logger.error(f"监控回调错误: {e}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(self.interval)
    
    def _collect_metrics(self) -> PerformanceSnapshot:
        """收集性能指标"""
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # 网络信息
            network_io = psutil.net_io_counters()
            
            # 进程信息
            process_count = len(psutil.pids())
            
            # 线程数（当前进程）
            current_process = psutil.Process()
            thread_count = current_process.num_threads()
            
            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_available=memory.available,
                disk_usage_percent=disk_usage.percent,
                disk_read_bytes=disk_io.read_bytes if disk_io else 0,
                disk_write_bytes=disk_io.write_bytes if disk_io else 0,
                network_bytes_sent=network_io.bytes_sent if network_io else 0,
                network_bytes_recv=network_io.bytes_recv if network_io else 0,
                process_count=process_count,
                thread_count=thread_count
            )
            
        except Exception as e:
            self.logger.error(f"收集性能指标错误: {e}")
            # 返回空指标
            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used=0,
                memory_available=0,
                disk_usage_percent=0.0,
                disk_read_bytes=0,
                disk_write_bytes=0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                process_count=0,
                thread_count=0
            )
    
    def get_current_metrics(self) -> Optional[PerformanceSnapshot]:
        """获取当前性能指标"""
        if self.history:
            return self.history[-1]
        return None
    
    def get_history(self, limit: int = None) -> List[PerformanceSnapshot]:
        """获取历史记录"""
        if limit:
            return list(self.history)[-limit:]
        return list(self.history)
    
    def get_average_metrics(self, duration_seconds: int = 60) -> Dict[str, float]:
        """获取指定时间段的平均指标"""
        cutoff_time = time.time() - duration_seconds
        recent_snapshots = [
            s for s in self.history 
            if s.timestamp >= cutoff_time
        ]
        
        if not recent_snapshots:
            return {}
        
        count = len(recent_snapshots)
        return {
            'avg_cpu_percent': sum(s.cpu_percent for s in recent_snapshots) / count,
            'avg_memory_percent': sum(s.memory_percent for s in recent_snapshots) / count,
            'avg_disk_usage_percent': sum(s.disk_usage_percent for s in recent_snapshots) / count,
            'count': count
        }

class SystemMonitor(PerformanceMonitor):
    """系统级性能监控"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process_monitor = {}
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0
        }
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """设置警报阈值"""
        self.alert_thresholds[metric] = threshold
    
    def _monitor_loop(self):
        """重写监控循环以添加警报功能"""
        while self.is_monitoring:
            try:
                snapshot = self._collect_metrics()
                self.history.append(snapshot)
                
                # 检查警报
                self._check_alerts(snapshot)
                
                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(snapshot)
                    except Exception as e:
                        self.logger.error(f"监控回调错误: {e}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(self.interval)
    
    def _check_alerts(self, snapshot: PerformanceSnapshot):
        """检查警报条件"""
        alerts = []
        
        if snapshot.cpu_percent > self.alert_thresholds.get('cpu_percent', 100):
            alerts.append(f"CPU使用率过高: {snapshot.cpu_percent:.1f}%")
        
        if snapshot.memory_percent > self.alert_thresholds.get('memory_percent', 100):
            alerts.append(f"内存使用率过高: {snapshot.memory_percent:.1f}%")
        
        if snapshot.disk_usage_percent > self.alert_thresholds.get('disk_usage_percent', 100):
            alerts.append(f"磁盘使用率过高: {snapshot.disk_usage_percent:.1f}%")
        
        for alert in alerts:
            self.logger.warning(f"性能警报: {alert}")
    
    def get_top_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取TOP进程信息"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] is not None and info['cpu_percent'] > 0:
                        processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
            
        except Exception as e:
            self.logger.error(f"获取进程信息错误: {e}")
            return []

class ApplicationMonitor:
    """应用程序性能监控"""
    
    def __init__(self):
        self.metrics = ApplicationMetrics()
        self.request_times = deque(maxlen=1000)
        self.error_log = deque(maxlen=100)
        self.custom_counters = defaultdict(int)
        self.custom_timers = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_request(self, response_time_ms: float, success: bool = True):
        """记录请求"""
        with self.lock:
            self.metrics.request_count += 1
            self.request_times.append(response_time_ms)
            
            if self.request_times:
                self.metrics.response_time_ms = sum(self.request_times) / len(self.request_times)
            
            if not success:
                self.metrics.error_count += 1
    
    def record_error(self, error_msg: str):
        """记录错误"""
        with self.lock:
            self.error_log.append({
                'timestamp': time.time(),
                'message': error_msg
            })
    
    def update_connections(self, count: int):
        """更新活跃连接数"""
        self.metrics.active_connections = count
    
    def update_cache_hit_rate(self, hit_rate: float):
        """更新缓存命中率"""
        self.metrics.cache_hit_rate = hit_rate
    
    def update_queue_size(self, size: int):
        """更新队列大小"""
        self.metrics.queue_size = size
    
    def increment_counter(self, name: str, value: int = 1):
        """增加自定义计数器"""
        with self.lock:
            self.custom_counters[name] += value
            self.metrics.custom_metrics[name] = self.custom_counters[name]
    
    def record_timer(self, name: str, duration_ms: float):
        """记录自定义计时器"""
        with self.lock:
            self.custom_timers[name].append(duration_ms)
            # 保留最近100个记录
            if len(self.custom_timers[name]) > 100:
                self.custom_timers[name] = self.custom_timers[name][-100:]
            
            # 计算平均值
            avg_time = sum(self.custom_timers[name]) / len(self.custom_timers[name])
            self.metrics.custom_metrics[f"{name}_avg_ms"] = avg_time
    
    def get_metrics(self) -> ApplicationMetrics:
        """获取当前指标"""
        return self.metrics
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的错误"""
        with self.lock:
            return list(self.error_log)[-limit:]

class RealTimeMonitor:
    """实时监控器 - 支持WebSocket推送"""
    
    def __init__(self, system_monitor: SystemMonitor, app_monitor: ApplicationMonitor):
        self.system_monitor = system_monitor
        self.app_monitor = app_monitor
        self.websocket_clients = weakref.WeakSet()
        self.is_broadcasting = False
        self.broadcast_thread = None
        
        # 注册系统监控回调
        self.system_monitor.add_callback(self._on_system_metrics)
    
    def add_websocket_client(self, websocket):
        """添加WebSocket客户端"""
        self.websocket_clients.add(websocket)
    
    def remove_websocket_client(self, websocket):
        """移除WebSocket客户端"""
        self.websocket_clients.discard(websocket)
    
    def start_broadcasting(self):
        """开始广播实时数据"""
        if self.is_broadcasting:
            return
        
        self.is_broadcasting = True
        self.broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.broadcast_thread.start()
    
    def stop_broadcasting(self):
        """停止广播"""
        self.is_broadcasting = False
        if self.broadcast_thread:
            self.broadcast_thread.join(timeout=2.0)
    
    def _on_system_metrics(self, snapshot: PerformanceSnapshot):
        """系统指标回调"""
        # 可以在这里处理实时系统指标
        pass
    
    def _broadcast_loop(self):
        """广播循环"""
        while self.is_broadcasting:
            try:
                # 收集当前数据
                data = self._collect_realtime_data()
                
                # 广播给所有WebSocket客户端
                self._broadcast_data(data)
                
                time.sleep(1.0)  # 每秒广播一次
                
            except Exception as e:
                logging.error(f"广播循环错误: {e}")
                time.sleep(1.0)
    
    def _collect_realtime_data(self) -> Dict[str, Any]:
        """收集实时数据"""
        system_metrics = self.system_monitor.get_current_metrics()
        app_metrics = self.app_monitor.get_metrics()
        
        return {
            'timestamp': time.time(),
            'system': system_metrics.to_dict() if system_metrics else {},
            'application': app_metrics.to_dict(),
            'system_averages': self.system_monitor.get_average_metrics(60),
            'top_processes': self.system_monitor.get_top_processes(5)
        }
    
    def _broadcast_data(self, data: Dict[str, Any]):
        """广播数据到WebSocket客户端"""
        if not self.websocket_clients:
            return
        
        message = json.dumps(data)
        disconnected_clients = []
        
        for client in self.websocket_clients:
            try:
                # 这里应该调用WebSocket发送方法
                # client.send(message)
                pass
            except Exception as e:
                disconnected_clients.append(client)
        
        # 清理断开的客户端
        for client in disconnected_clients:
            self.websocket_clients.discard(client)

# 监控管理器
class MonitoringManager:
    """监控管理器 - 统一管理所有监控组件"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor(interval=1.0)
        self.app_monitor = ApplicationMonitor()
        self.realtime_monitor = RealTimeMonitor(self.system_monitor, self.app_monitor)
        self.is_started = False
    
    def start(self):
        """启动所有监控"""
        if self.is_started:
            return
        
        self.system_monitor.start()
        self.realtime_monitor.start_broadcasting()
        self.is_started = True
        logging.info("监控系统已启动")
    
    def stop(self):
        """停止所有监控"""
        if not self.is_started:
            return
        
        self.system_monitor.stop()
        self.realtime_monitor.stop_broadcasting()
        self.is_started = False
        logging.info("监控系统已停止")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        return {
            'system': self.system_monitor.get_current_metrics(),
            'application': self.app_monitor.get_metrics(),
            'system_averages': self.system_monitor.get_average_metrics(300),  # 5分钟平均
            'top_processes': self.system_monitor.get_top_processes(10),
            'recent_errors': self.app_monitor.get_recent_errors(10)
        }

# 全局监控实例
_global_monitor = None

def get_global_monitor() -> MonitoringManager:
    """获取全局监控实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MonitoringManager()
    return _global_monitor

# 监控装饰器
def monitor_performance(monitor_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        name = monitor_name or f"{func.__module__}.{func.__name__}"
        
        def wrapper(*args, **kwargs):
            start_time = time.time()
            monitor = get_global_monitor()
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                monitor.app_monitor.record_error(f"{name}: {str(e)}")
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                monitor.app_monitor.record_request(duration_ms, success)
                monitor.app_monitor.record_timer(name, duration_ms)
            
            return result
        
        return wrapper
    return decorator

# 使用示例
def demonstrate_monitoring():
    """演示监控功能"""
    print("=== 性能监控示例 ===\n")
    
    # 创建监控管理器
    monitor_manager = MonitoringManager()
    
    # 启动监控
    monitor_manager.start()
    
    # 模拟一些应用活动
    for i in range(10):
        # 模拟请求
        response_time = 50 + (i * 10)  # 模拟递增的响应时间
        success = i < 8  # 前8个请求成功
        monitor_manager.app_monitor.record_request(response_time, success)
        
        # 模拟错误
        if not success:
            monitor_manager.app_monitor.record_error(f"模拟错误 {i}")
        
        time.sleep(0.1)
    
    # 获取仪表板数据
    dashboard_data = monitor_manager.get_dashboard_data()
    
    print("仪表板数据:")
    print(f"系统CPU: {dashboard_data['system'].cpu_percent:.1f}%" if dashboard_data['system'] else "系统CPU: 无数据")
    print(f"应用请求数: {dashboard_data['application'].request_count}")
    print(f"应用错误数: {dashboard_data['application'].error_count}")
    print(f"平均响应时间: {dashboard_data['application'].response_time_ms:.1f}ms")
    
    # 停止监控
    monitor_manager.stop()

if __name__ == "__main__":
    demonstrate_monitoring()