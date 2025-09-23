"""
线程异常处理模块

演示多线程环境下的异常处理策略
"""

import threading
import time
import traceback
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import queue


@dataclass
class ThreadException:
    """线程异常信息"""
    thread_name: str
    exception_type: str
    exception_message: str
    traceback_info: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'thread_name': self.thread_name,
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'traceback_info': self.traceback_info,
            'timestamp': self.timestamp.isoformat()
        }


class ThreadExceptionHandler:
    """线程异常处理器"""
    
    def __init__(self):
        self.exceptions: List[ThreadException] = []
        self.exception_queue = queue.Queue()
        self.lock = threading.Lock()
        self.exception_callbacks: List[Callable] = []
        
    def handle_exception(self, thread_name: str, exception: Exception) -> None:
        """处理线程异常"""
        thread_exception = ThreadException(
            thread_name=thread_name,
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            traceback_info=traceback.format_exc(),
            timestamp=datetime.now()
        )
        
        with self.lock:
            self.exceptions.append(thread_exception)
            
        # 放入队列供监控线程处理
        self.exception_queue.put(thread_exception)
        
        # 调用回调函数
        for callback in self.exception_callbacks:
            try:
                callback(thread_exception)
            except Exception as e:
                print(f"异常回调函数执行失败: {e}")
                
        print(f"[异常处理器] 记录线程 '{thread_name}' 异常: {exception}")
        
    def add_exception_callback(self, callback: Callable) -> None:
        """添加异常回调函数"""
        self.exception_callbacks.append(callback)
        
    def get_exceptions(self) -> List[ThreadException]:
        """获取所有异常记录"""
        with self.lock:
            return self.exceptions.copy()
            
    def get_exception_summary(self) -> Dict[str, Any]:
        """获取异常统计摘要"""
        with self.lock:
            total_exceptions = len(self.exceptions)
            exception_types = {}
            thread_exceptions = {}
            
            for exc in self.exceptions:
                # 统计异常类型
                exc_type = exc.exception_type
                exception_types[exc_type] = exception_types.get(exc_type, 0) + 1
                
                # 统计线程异常
                thread_name = exc.thread_name
                thread_exceptions[thread_name] = thread_exceptions.get(thread_name, 0) + 1
                
            return {
                'total_exceptions': total_exceptions,
                'exception_types': exception_types,
                'thread_exceptions': thread_exceptions,
                'latest_exception': self.exceptions[-1].to_dict() if self.exceptions else None
            }


def safe_thread_wrapper(func: Callable, exception_handler: ThreadExceptionHandler):
    """安全线程包装器"""
    def wrapper(*args, **kwargs):
        thread_name = threading.current_thread().name
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exception_handler.handle_exception(thread_name, e)
            # 根据需要决定是否重新抛出异常
            # raise  # 取消注释此行以重新抛出异常
    return wrapper


class ExceptionHandlingDemo:
    """异常处理演示"""
    
    def __init__(self):
        self.exception_handler = ThreadExceptionHandler()
        self.setup_exception_callbacks()
        
    def setup_exception_callbacks(self):
        """设置异常回调"""
        def log_exception(thread_exception: ThreadException):
            """日志异常回调"""
            print(f"[日志] {thread_exception.thread_name}: {thread_exception.exception_message}")
            
        def alert_exception(thread_exception: ThreadException):
            """告警异常回调"""
            if thread_exception.exception_type in ['RuntimeError', 'ValueError']:
                print(f"[告警] 严重异常发生: {thread_exception.thread_name}")
                
        self.exception_handler.add_exception_callback(log_exception)
        self.exception_handler.add_exception_callback(alert_exception)
        
    def task_with_random_exception(self, name: str, should_fail: bool = False):
        """可能出现异常的任务"""
        print(f"[{name}] 开始执行任务")
        
        time.sleep(1)
        
        if should_fail:
            import random
            exception_types = [
                ValueError("数值错误"),
                RuntimeError("运行时错误"),
                TypeError("类型错误"),
                KeyError("键错误")
            ]
            raise random.choice(exception_types)
            
        print(f"[{name}] 任务正常完成")
        
    def task_with_recovery(self, name: str, max_retries: int = 3):
        """带重试机制的任务"""
        for attempt in range(max_retries):
            try:
                print(f"[{name}] 尝试执行 (第{attempt+1}次)")
                
                # 模拟可能失败的操作
                import random
                if random.random() < 0.6:  # 60%概率失败
                    raise ConnectionError("连接失败")
                    
                print(f"[{name}] 执行成功")
                return
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[{name}] 第{attempt+1}次尝试失败: {e}，将重试")
                    time.sleep(1)
                else:
                    print(f"[{name}] 所有重试失败")
                    raise
                    
    def demo_basic_exception_handling(self):
        """演示基础异常处理"""
        print("\n=== 基础异常处理演示 ===")
        
        # 创建混合线程（正常和异常）
        threads = []
        
        for i in range(5):
            should_fail = (i % 2 == 1)  # 奇数线程会失败
            
            target = safe_thread_wrapper(
                self.task_with_random_exception,
                self.exception_handler
            )
            
            thread = threading.Thread(
                target=target,
                args=(f"Worker-{i+1}", should_fail),
                name=f"ExceptionWorker{i+1}"
            )
            threads.append(thread)
            
        print(f"创建了 {len(threads)} 个线程（部分会失败）")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        # 显示异常统计
        print("\n异常处理结果:")
        summary = self.exception_handler.get_exception_summary()
        print(f"总异常数: {summary['total_exceptions']}")
        print(f"异常类型统计: {summary['exception_types']}")
        print(f"线程异常统计: {summary['thread_exceptions']}")
        
    def demo_exception_monitoring(self):
        """演示异常监控"""
        print("\n=== 异常监控演示 ===")
        
        # 异常监控线程
        def exception_monitor():
            """异常监控函数"""
            print("[监控器] 启动异常监控")
            while True:
                try:
                    # 等待异常发生
                    thread_exception = self.exception_handler.exception_queue.get(timeout=5)
                    print(f"[监控器] 检测到异常: {thread_exception.thread_name} - {thread_exception.exception_message}")
                    
                    # 模拟异常处理逻辑
                    if thread_exception.exception_type == "RuntimeError":
                        print("[监控器] 严重异常，记录到告警系统")
                    else:
                        print("[监控器] 一般异常，记录到日志")
                        
                except queue.Empty:
                    print("[监控器] 监控超时，退出监控")
                    break
                except Exception as e:
                    print(f"[监控器] 监控异常: {e}")
                    
        # 启动监控线程
        monitor_thread = threading.Thread(
            target=exception_monitor,
            name="ExceptionMonitor",
            daemon=True
        )
        monitor_thread.start()
        
        # 创建会产生异常的工作线程
        work_threads = []
        for i in range(3):
            target = safe_thread_wrapper(
                self.task_with_random_exception,
                self.exception_handler
            )
            
            thread = threading.Thread(
                target=target,
                args=(f"MonitoredWorker-{i+1}", True),  # 都会失败
                name=f"MonitoredWorker{i+1}"
            )
            work_threads.append(thread)
            
        # 逐个启动，观察监控效果
        for thread in work_threads:
            print(f"启动线程: {thread.name}")
            thread.start()
            time.sleep(2)  # 间隔启动
            
        # 等待工作线程完成
        for thread in work_threads:
            thread.join()
            
        # 等待监控线程处理完异常
        time.sleep(1)
        print("异常监控演示完成")
        
    def demo_recovery_mechanism(self):
        """演示异常恢复机制"""
        print("\n=== 异常恢复机制演示 ===")
        
        # 创建带重试机制的线程
        threads = []
        for i in range(3):
            target = safe_thread_wrapper(
                self.task_with_recovery,
                self.exception_handler
            )
            
            thread = threading.Thread(
                target=target,
                args=(f"RecoveryWorker-{i+1}", 3),
                name=f"RecoveryWorker{i+1}"
            )
            threads.append(thread)
            
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print("\n恢复机制演示完成")
        
        # 显示最终异常统计
        print("\n最终异常统计:")
        for exception in self.exception_handler.get_exceptions():
            print(f"  {exception.thread_name}: {exception.exception_type} - {exception.exception_message}")
            
    def run_all_demos(self):
        """运行所有异常处理演示"""
        print("开始异常处理演示...")
        
        try:
            self.demo_basic_exception_handling()
            time.sleep(1)
            
            self.demo_exception_monitoring()
            time.sleep(1)
            
            self.demo_recovery_mechanism()
            
        except KeyboardInterrupt:
            print("\n异常处理演示被中断")
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")
        finally:
            print("\n异常处理演示结束")


def main():
    """主函数"""
    demo = ExceptionHandlingDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()