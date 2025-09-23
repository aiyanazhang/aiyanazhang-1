"""
线程生命周期管理模块

演示线程从创建到销毁的完整生命周期管理
"""

import threading
import time
import signal
import atexit
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ThreadState(Enum):
    """线程状态枚举"""
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"
    ERROR = "error"


@dataclass
class ManagedThread:
    """托管线程信息"""
    thread: threading.Thread
    state: ThreadState
    created_time: datetime
    started_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None
    cleanup_func: Optional[Callable] = None
    priority: int = 5  # 1-10, 10最高
    
    def get_runtime(self) -> Optional[float]:
        """获取运行时间"""
        if self.started_time and self.finished_time:
            return (self.finished_time - self.started_time).total_seconds()
        elif self.started_time:
            return (datetime.now() - self.started_time).total_seconds()
        return None


class ThreadLifecycleManager:
    """线程生命周期管理器"""
    
    def __init__(self):
        self.managed_threads: Dict[str, ManagedThread] = {}
        self.shutdown_event = threading.Event()
        self.lock = threading.Lock()
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.shutdown_all)
        
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        print(f"\n接收到信号 {signum}，开始优雅关闭...")
        self.shutdown_all()
        
    def create_thread(self, name: str, target: Callable, args: tuple = (), 
                     cleanup_func: Optional[Callable] = None, 
                     priority: int = 5) -> threading.Thread:
        """创建托管线程"""
        thread = threading.Thread(target=self._wrapped_target, 
                                 args=(name, target, args), name=name)
        
        managed_thread = ManagedThread(
            thread=thread,
            state=ThreadState.CREATED,
            created_time=datetime.now(),
            cleanup_func=cleanup_func,
            priority=priority
        )
        
        with self.lock:
            self.managed_threads[name] = managed_thread
            
        print(f"线程 '{name}' 已创建")
        return thread
        
    def _wrapped_target(self, name: str, target: Callable, args: tuple):
        """包装的目标函数"""
        with self.lock:
            if name in self.managed_threads:
                self.managed_threads[name].state = ThreadState.RUNNING
                self.managed_threads[name].started_time = datetime.now()
                
        try:
            print(f"[{name}] 开始执行")
            target(*args)
            
            with self.lock:
                if name in self.managed_threads:
                    self.managed_threads[name].state = ThreadState.TERMINATED
                    self.managed_threads[name].finished_time = datetime.now()
                    
        except Exception as e:
            print(f"[{name}] 执行异常: {e}")
            with self.lock:
                if name in self.managed_threads:
                    self.managed_threads[name].state = ThreadState.ERROR
                    self.managed_threads[name].finished_time = datetime.now()
        finally:
            # 执行清理函数
            self._cleanup_thread(name)
            
    def _cleanup_thread(self, name: str):
        """清理线程资源"""
        with self.lock:
            if name in self.managed_threads:
                managed_thread = self.managed_threads[name]
                if managed_thread.cleanup_func:
                    try:
                        print(f"[{name}] 执行清理函数")
                        managed_thread.cleanup_func()
                    except Exception as e:
                        print(f"[{name}] 清理函数执行失败: {e}")
                        
    def start_thread(self, name: str) -> bool:
        """启动线程"""
        with self.lock:
            if name not in self.managed_threads:
                print(f"线程 '{name}' 不存在")
                return False
                
            managed_thread = self.managed_threads[name]
            if managed_thread.state != ThreadState.CREATED:
                print(f"线程 '{name}' 状态不正确: {managed_thread.state}")
                return False
                
            managed_thread.state = ThreadState.READY
            
        try:
            managed_thread.thread.start()
            print(f"线程 '{name}' 已启动")
            return True
        except Exception as e:
            print(f"启动线程 '{name}' 失败: {e}")
            return False
            
    def wait_for_thread(self, name: str, timeout: Optional[float] = None) -> bool:
        """等待线程完成"""
        with self.lock:
            if name not in self.managed_threads:
                return False
            thread = self.managed_threads[name].thread
            
        try:
            thread.join(timeout)
            return not thread.is_alive()
        except Exception:
            return False
            
    def get_thread_status(self, name: str) -> Optional[Dict[str, Any]]:
        """获取线程状态"""
        with self.lock:
            if name not in self.managed_threads:
                return None
                
            managed_thread = self.managed_threads[name]
            return {
                'name': name,
                'state': managed_thread.state.value,
                'is_alive': managed_thread.thread.is_alive(),
                'created_time': managed_thread.created_time.isoformat(),
                'started_time': managed_thread.started_time.isoformat() if managed_thread.started_time else None,
                'finished_time': managed_thread.finished_time.isoformat() if managed_thread.finished_time else None,
                'runtime': managed_thread.get_runtime(),
                'priority': managed_thread.priority
            }
            
    def list_all_threads(self) -> List[Dict[str, Any]]:
        """列出所有托管线程"""
        with self.lock:
            return [self.get_thread_status(name) for name in self.managed_threads.keys()]
            
    def shutdown_all(self):
        """关闭所有线程"""
        print("开始关闭所有托管线程...")
        self.shutdown_event.set()
        
        # 按优先级排序，优先级高的先关闭
        with self.lock:
            sorted_threads = sorted(
                self.managed_threads.items(),
                key=lambda x: x[1].priority,
                reverse=True
            )
            
        for name, managed_thread in sorted_threads:
            if managed_thread.thread.is_alive():
                print(f"等待线程 '{name}' 完成...")
                managed_thread.thread.join(timeout=3)
                if managed_thread.thread.is_alive():
                    print(f"线程 '{name}' 未能及时完成")
                    
        print("所有托管线程已关闭")


class LifecycleDemo:
    """生命周期管理演示"""
    
    def __init__(self):
        self.manager = ThreadLifecycleManager()
        
    def sample_task(self, name: str, duration: int):
        """示例任务"""
        for i in range(duration):
            if self.manager.shutdown_event.is_set():
                print(f"[{name}] 收到关闭信号，提前退出")
                break
            print(f"[{name}] 执行步骤 {i+1}/{duration}")
            time.sleep(1)
            
    def resource_cleanup(self):
        """资源清理函数"""
        print("执行资源清理...")
        time.sleep(0.5)
        print("资源清理完成")
        
    def demo_basic_lifecycle(self):
        """演示基础生命周期管理"""
        print("\n=== 基础生命周期管理演示 ===")
        
        # 创建线程
        thread1 = self.manager.create_thread(
            "LifecycleWorker1", 
            self.sample_task, 
            ("Worker1", 3),
            cleanup_func=self.resource_cleanup,
            priority=7
        )
        
        thread2 = self.manager.create_thread(
            "LifecycleWorker2",
            self.sample_task,
            ("Worker2", 2),
            priority=5
        )
        
        # 显示创建后状态
        print("\n创建后状态:")
        for status in self.manager.list_all_threads():
            print(f"  {status['name']}: {status['state']}")
            
        # 启动线程
        self.manager.start_thread("LifecycleWorker1")
        self.manager.start_thread("LifecycleWorker2")
        
        # 监控状态变化
        for i in range(5):
            time.sleep(1)
            print(f"\n状态检查 {i+1}:")
            for status in self.manager.list_all_threads():
                runtime = status['runtime']
                runtime_str = f"{runtime:.1f}s" if runtime else "N/A"
                print(f"  {status['name']}: {status['state']} (运行时间: {runtime_str})")
                
        # 等待完成
        self.manager.wait_for_thread("LifecycleWorker1")
        self.manager.wait_for_thread("LifecycleWorker2")
        
        print("\n最终状态:")
        for status in self.manager.list_all_threads():
            runtime = status['runtime']
            runtime_str = f"{runtime:.1f}s" if runtime else "N/A"
            print(f"  {status['name']}: {status['state']} (总运行时间: {runtime_str})")
            
    def demo_graceful_shutdown(self):
        """演示优雅关闭"""
        print("\n=== 优雅关闭演示 ===")
        
        # 创建长时间运行的线程
        for i in range(3):
            self.manager.create_thread(
                f"LongRunningWorker{i+1}",
                self.sample_task,
                (f"LongWorker{i+1}", 10),  # 10秒任务
                priority=i+1
            )
            
        # 启动所有线程
        for i in range(3):
            self.manager.start_thread(f"LongRunningWorker{i+1}")
            
        print("启动了3个长时间运行的线程")
        print("3秒后将触发优雅关闭...")
        
        time.sleep(3)
        print("\n触发优雅关闭...")
        self.manager.shutdown_all()
        
    def run_all_demos(self):
        """运行所有演示"""
        try:
            self.demo_basic_lifecycle()
            time.sleep(1)
            self.demo_graceful_shutdown()
        except KeyboardInterrupt:
            print("\n演示被中断")
        finally:
            self.manager.shutdown_all()


def main():
    """主函数"""
    demo = LifecycleDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()