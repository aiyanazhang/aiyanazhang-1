"""
多线程编程示例

展示Python多线程编程的高级用法，包括线程池、锁机制、生产者消费者等模式。
"""

import threading
import time
import queue
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Dict, Optional
from dataclasses import dataclass
import logging
from contextlib import contextmanager

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

logger = logging.getLogger(__name__)


@dataclass
class ThreadResult:
    """线程执行结果"""
    thread_id: str
    result: Any
    execution_time: float
    success: bool
    error: Optional[str] = None


class ThreadSafeCounter:
    """线程安全计数器"""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
    
    def increment(self, amount: int = 1) -> int:
        """增加计数"""
        with self._lock:
            self._value += amount
            self._condition.notify_all()
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """减少计数"""
        with self._lock:
            self._value -= amount
            self._condition.notify_all()
            return self._value
    
    def get_value(self) -> int:
        """获取当前值"""
        with self._lock:
            return self._value
    
    def wait_for_value(self, target: int, timeout: Optional[float] = None) -> bool:
        """等待值达到目标"""
        with self._condition:
            return self._condition.wait_for(
                lambda: self._value >= target, 
                timeout=timeout
            )
    
    def reset(self):
        """重置计数器"""
        with self._lock:
            self._value = 0
            self._condition.notify_all()


class ThreadPoolManager:
    """线程池管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.submitted_tasks = {}
        self.completed_tasks = []
        self.lock = threading.Lock()
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> None:
        """提交任务"""
        future = self.executor.submit(self._execute_task, task_id, func, *args, **kwargs)
        
        with self.lock:
            self.submitted_tasks[task_id] = future
    
    def _execute_task(self, task_id: str, func: Callable, *args, **kwargs) -> ThreadResult:
        """执行任务"""
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            thread_result = ThreadResult(
                thread_id=task_id,
                result=result,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            thread_result = ThreadResult(
                thread_id=task_id,
                result=None,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
        
        with self.lock:
            self.completed_tasks.append(thread_result)
        
        return thread_result
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> List[ThreadResult]:
        """等待所有任务完成"""
        results = []
        
        for task_id, future in self.submitted_tasks.items():
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except Exception as e:
                # 创建错误结果
                error_result = ThreadResult(
                    thread_id=task_id,
                    result=None,
                    execution_time=0,
                    success=False,
                    error=str(e)
                )
                results.append(error_result)
        
        return results
    
    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        with self.lock:
            total_tasks = len(self.submitted_tasks)
            completed_tasks = len(self.completed_tasks)
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": total_tasks - completed_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            }
    
    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        self.executor.shutdown(wait=wait)


class ProducerConsumer:
    """生产者消费者模式"""
    
    def __init__(self, buffer_size: int = 10):
        self.buffer = queue.Queue(maxsize=buffer_size)
        self.producers_active = threading.Event()
        self.consumers_active = threading.Event()
        self.total_produced = ThreadSafeCounter()
        self.total_consumed = ThreadSafeCounter()
    
    def producer(self, producer_id: str, items_to_produce: int, production_delay: float = 0.1):
        """生产者函数"""
        self.producers_active.set()
        
        for i in range(items_to_produce):
            item = f"Producer-{producer_id}-Item-{i}"
            
            try:
                self.buffer.put(item, timeout=1.0)
                self.total_produced.increment()
                
                logger.info(f"Producer {producer_id} produced: {item}")
                time.sleep(production_delay)
                
            except queue.Full:
                logger.warning(f"Producer {producer_id} failed to produce {item} - buffer full")
                break
        
        logger.info(f"Producer {producer_id} finished")
    
    def consumer(self, consumer_id: str, max_items: Optional[int] = None, consumption_delay: float = 0.2):
        """消费者函数"""
        self.consumers_active.set()
        consumed_count = 0
        
        while True:
            try:
                item = self.buffer.get(timeout=0.5)
                
                # 模拟处理时间
                time.sleep(consumption_delay)
                
                self.total_consumed.increment()
                consumed_count += 1
                
                logger.info(f"Consumer {consumer_id} consumed: {item}")
                
                # 标记任务完成
                self.buffer.task_done()
                
                # 检查是否达到最大消费数量
                if max_items and consumed_count >= max_items:
                    break
                    
            except queue.Empty:
                # 如果没有生产者活跃且队列为空，退出
                if not self.producers_active.is_set():
                    break
                continue
        
        logger.info(f"Consumer {consumer_id} finished, consumed {consumed_count} items")
    
    def start_production(self, num_producers: int = 2, items_per_producer: int = 5):
        """启动生产者"""
        self.producers_active.set()
        
        threads = []
        for i in range(num_producers):
            thread = threading.Thread(
                target=self.producer,
                args=(f"P{i}", items_per_producer),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # 等待所有生产者完成
        for thread in threads:
            thread.join()
        
        self.producers_active.clear()
    
    def start_consumption(self, num_consumers: int = 3, max_items_per_consumer: Optional[int] = None):
        """启动消费者"""
        self.consumers_active.set()
        
        threads = []
        for i in range(num_consumers):
            thread = threading.Thread(
                target=self.consumer,
                args=(f"C{i}", max_items_per_consumer),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        return threads
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_produced": self.total_produced.get_value(),
            "total_consumed": self.total_consumed.get_value(),
            "buffer_size": self.buffer.qsize(),
            "producers_active": self.producers_active.is_set(),
            "consumers_active": self.consumers_active.is_set()
        }


@contextmanager
def thread_local_storage():
    """线程本地存储上下文管理器"""
    thread_local = threading.local()
    thread_local.data = {}
    thread_local.start_time = time.time()
    
    try:
        yield thread_local
    finally:
        execution_time = time.time() - thread_local.start_time
        logger.info(f"Thread {threading.current_thread().name} executed for {execution_time:.3f}s")


def cpu_intensive_task(task_id: str, complexity: int) -> Dict[str, Any]:
    """CPU密集型任务"""
    start_time = time.time()
    
    # 模拟CPU密集型计算
    result = sum(i * i for i in range(complexity))
    
    execution_time = time.time() - start_time
    
    return {
        "task_id": task_id,
        "result": result,
        "complexity": complexity,
        "execution_time": execution_time,
        "thread_name": threading.current_thread().name
    }


def io_intensive_task(task_id: str, delay: float) -> Dict[str, Any]:
    """I/O密集型任务模拟"""
    start_time = time.time()
    
    # 模拟I/O等待
    time.sleep(delay)
    
    execution_time = time.time() - start_time
    
    return {
        "task_id": task_id,
        "delay": delay,
        "execution_time": execution_time,
        "thread_name": threading.current_thread().name
    }


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="threading_basic_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.BEGINNER,
    description="基础多线程编程示例",
    tags=["threading", "basic", "concurrency"]
)
@demo(title="基础多线程编程示例")
def threading_basic_example():
    """展示基础多线程编程概念"""
    
    def worker_function(worker_id: int, work_time: float):
        """工作函数"""
        print(f"Worker {worker_id} 开始工作 (线程: {threading.current_thread().name})")
        time.sleep(work_time)
        print(f"Worker {worker_id} 完成工作")
        return f"Worker {worker_id} 结果"
    
    print("顺序执行示例：")
    start_time = time.time()
    
    for i in range(3):
        worker_function(i, 1.0)
    
    sequential_time = time.time() - start_time
    print(f"顺序执行耗时: {sequential_time:.2f}s")
    
    print("\n多线程执行示例：")
    start_time = time.time()
    
    threads = []
    for i in range(3):
        thread = threading.Thread(
            target=worker_function,
            args=(i, 1.0),
            name=f"Worker-Thread-{i}"
        )
        thread.start()
        threads.append(thread)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    threaded_time = time.time() - start_time
    print(f"多线程执行耗时: {threaded_time:.2f}s")
    print(f"性能提升: {sequential_time/threaded_time:.1f}x")


@example(
    name="thread_safe_counter_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="线程安全计数器示例",
    tags=["threading", "thread-safety", "synchronization"]
)
@demo(title="线程安全计数器示例")
def thread_safe_counter_example():
    """展示线程安全编程"""
    
    def increment_worker(counter: ThreadSafeCounter, increments: int, worker_id: str):
        """增加计数的工作函数"""
        for i in range(increments):
            value = counter.increment()
            print(f"Worker {worker_id}: 增加到 {value}")
            time.sleep(0.01)  # 短暂延迟以增加竞争条件
    
    def decrement_worker(counter: ThreadSafeCounter, decrements: int, worker_id: str):
        """减少计数的工作函数"""
        for i in range(decrements):
            value = counter.decrement()
            print(f"Worker {worker_id}: 减少到 {value}")
            time.sleep(0.01)
    
    print("线程安全计数器示例")
    
    counter = ThreadSafeCounter(0)
    
    print(f"初始值: {counter.get_value()}")
    
    # 创建多个线程同时操作计数器
    threads = []
    
    # 增加线程
    for i in range(2):
        thread = threading.Thread(
            target=increment_worker,
            args=(counter, 5, f"Inc-{i}")
        )
        threads.append(thread)
    
    # 减少线程
    for i in range(2):
        thread = threading.Thread(
            target=decrement_worker,
            args=(counter, 3, f"Dec-{i}")
        )
        threads.append(thread)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    final_value = counter.get_value()
    expected_value = (2 * 5) - (2 * 3)  # 10 - 6 = 4
    
    print(f"\n最终值: {final_value}")
    print(f"期望值: {expected_value}")
    print(f"结果正确: {final_value == expected_value}")


@example(
    name="thread_pool_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="线程池管理器示例",
    tags=["threading", "thread-pool", "task-management"]
)
@demo(title="线程池管理器示例")
def thread_pool_example():
    """展示线程池的使用"""
    
    print("线程池管理器示例")
    
    manager = ThreadPoolManager(max_workers=3)
    
    # 提交CPU密集型任务
    print("\n提交CPU密集型任务...")
    for i in range(5):
        manager.submit_task(
            f"cpu_task_{i}",
            cpu_intensive_task,
            f"CPU_{i}",
            10000 + i * 5000
        )
    
    # 提交I/O密集型任务
    print("提交I/O密集型任务...")
    for i in range(3):
        manager.submit_task(
            f"io_task_{i}",
            io_intensive_task,
            f"IO_{i}",
            random.uniform(0.5, 1.5)
        )
    
    # 监控进度
    print("\n监控执行进度...")
    while True:
        progress = manager.get_progress()
        print(f"进度: {progress['completed_tasks']}/{progress['total_tasks']} "
              f"({progress['completion_rate']:.1%})")
        
        if progress['completion_rate'] >= 1.0:
            break
        
        time.sleep(0.5)
    
    # 等待所有任务完成
    results = manager.wait_for_completion()
    
    print(f"\n所有任务完成！")
    print(f"成功任务: {sum(1 for r in results if r.success)}")
    print(f"失败任务: {sum(1 for r in results if not r.success)}")
    
    # 显示部分结果
    print("\n任务结果 (前5个):")
    for result in results[:5]:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.thread_id}: {result.execution_time:.3f}s")
    
    manager.shutdown()


@example(
    name="producer_consumer_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.ADVANCED,
    description="生产者消费者模式示例",
    tags=["threading", "producer-consumer", "queue"]
)
@demo(title="生产者消费者模式示例")
def producer_consumer_example():
    """展示生产者消费者模式"""
    
    print("生产者消费者模式示例")
    
    pc = ProducerConsumer(buffer_size=5)
    
    print("\n启动生产者和消费者...")
    
    # 在单独线程中启动生产者
    producer_thread = threading.Thread(
        target=pc.start_production,
        args=(2, 8),  # 2个生产者，每个生产8个项目
        daemon=True
    )
    producer_thread.start()
    
    # 启动消费者
    consumer_threads = pc.start_consumption(
        num_consumers=3,
        max_items_per_consumer=6
    )
    
    # 监控进度
    print("\n监控生产消费进度...")
    monitor_count = 0
    while producer_thread.is_alive() or any(t.is_alive() for t in consumer_threads):
        stats = pc.get_statistics()
        print(f"生产: {stats['total_produced']}, "
              f"消费: {stats['total_consumed']}, "
              f"缓冲区: {stats['buffer_size']}")
        
        time.sleep(1)
        monitor_count += 1
        
        # 防止无限监控
        if monitor_count > 20:
            break
    
    # 等待生产者完成
    producer_thread.join(timeout=5)
    
    # 等待消费者完成
    for thread in consumer_threads:
        thread.join(timeout=2)
    
    # 最终统计
    final_stats = pc.get_statistics()
    print(f"\n最终统计:")
    print(f"总生产: {final_stats['total_produced']}")
    print(f"总消费: {final_stats['total_consumed']}")
    print(f"剩余缓冲区: {final_stats['buffer_size']}")


@example(
    name="thread_local_storage_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="线程本地存储示例",
    tags=["threading", "thread-local", "isolation"]
)
@demo(title="线程本地存储示例")
def thread_local_storage_example():
    """展示线程本地存储的使用"""
    
    def worker_with_local_storage(worker_id: str, iterations: int):
        """使用线程本地存储的工作函数"""
        with thread_local_storage() as local:
            local.data['worker_id'] = worker_id
            local.data['counter'] = 0
            
            print(f"Worker {worker_id} 开始工作 (线程: {threading.current_thread().name})")
            
            for i in range(iterations):
                local.data['counter'] += 1
                local.data['last_iteration'] = i
                
                print(f"Worker {worker_id}: 迭代 {i}, 计数器 = {local.data['counter']}")
                time.sleep(0.1)
            
            print(f"Worker {worker_id} 完成，最终计数器: {local.data['counter']}")
            
            return {
                'worker_id': worker_id,
                'final_counter': local.data['counter'],
                'thread_name': threading.current_thread().name
            }
    
    print("线程本地存储示例")
    
    # 创建多个线程，每个都有独立的本地存储
    threads = []
    results = {}
    
    def worker_wrapper(worker_id: str, iterations: int):
        result = worker_with_local_storage(worker_id, iterations)
        results[worker_id] = result
    
    # 启动多个工作线程
    for i in range(3):
        thread = threading.Thread(
            target=worker_wrapper,
            args=(f"Worker-{i}", 5),
            name=f"Thread-{i}"
        )
        thread.start()
        threads.append(thread)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print(f"\n所有线程完成！")
    print("各线程的独立计数器值:")
    for worker_id, result in results.items():
        print(f"  {worker_id}: {result['final_counter']} (线程: {result['thread_name']})")


# 导出的类和函数
__all__ = [
    "ThreadSafeCounter",
    "ThreadPoolManager",
    "ProducerConsumer",
    "thread_local_storage",
    "cpu_intensive_task",
    "io_intensive_task",
    "threading_basic_example",
    "thread_safe_counter_example",
    "thread_pool_example",
    "producer_consumer_example",
    "thread_local_storage_example"
]