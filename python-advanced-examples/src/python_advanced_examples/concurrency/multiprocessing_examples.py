"""
多进程编程示例

展示Python多进程编程的高级用法，包括进程池、进程间通信、共享内存等。
"""

import multiprocessing as mp
import time
import os
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import pickle
import signal

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """进程执行结果"""
    process_id: str
    pid: int
    result: Any
    execution_time: float
    success: bool
    error: Optional[str] = None


class ProcessPoolManager:
    """进程池管理器"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self.submitted_tasks = {}
        self.completed_tasks = []
    
    def submit_task(self, task_id: str, func, *args, **kwargs) -> None:
        """提交任务到进程池"""
        future = self.executor.submit(self._execute_task, task_id, func, *args, **kwargs)
        self.submitted_tasks[task_id] = future
    
    @staticmethod
    def _execute_task(task_id: str, func, *args, **kwargs) -> ProcessResult:
        """在子进程中执行任务"""
        start_time = time.time()
        pid = os.getpid()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            return ProcessResult(
                process_id=task_id,
                pid=pid,
                result=result,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ProcessResult(
                process_id=task_id,
                pid=pid,
                result=None,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> List[ProcessResult]:
        """等待所有任务完成"""
        results = []
        
        for task_id, future in self.submitted_tasks.items():
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except Exception as e:
                error_result = ProcessResult(
                    process_id=task_id,
                    pid=0,
                    result=None,
                    execution_time=0,
                    success=False,
                    error=str(e)
                )
                results.append(error_result)
        
        return results
    
    def shutdown(self, wait: bool = True):
        """关闭进程池"""
        self.executor.shutdown(wait=wait)


class SharedMemoryExample:
    """共享内存示例"""
    
    def __init__(self, array_size: int = 1000):
        self.array_size = array_size
        self.shared_array = mp.Array('i', array_size)  # 整数数组
        self.shared_value = mp.Value('d', 0.0)  # 双精度浮点数
        self.lock = mp.Lock()
    
    def worker_process(self, worker_id: int, start_idx: int, end_idx: int):
        """工作进程函数"""
        pid = os.getpid()
        print(f"Worker {worker_id} (PID: {pid}) 处理索引 {start_idx} 到 {end_idx}")
        
        # 在指定范围内填充数组
        for i in range(start_idx, end_idx):
            with self.lock:
                self.shared_array[i] = worker_id * 1000 + i
        
        # 更新共享值
        with self.lock:
            self.shared_value.value += (end_idx - start_idx)
        
        print(f"Worker {worker_id} 完成")
        return f"Worker {worker_id} processed {end_idx - start_idx} items"
    
    def run_parallel_processing(self, num_workers: int = 4):
        """运行并行处理"""
        chunk_size = self.array_size // num_workers
        processes = []
        
        print(f"启动 {num_workers} 个工作进程...")
        
        for i in range(num_workers):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size
            
            # 最后一个进程处理剩余的元素
            if i == num_workers - 1:
                end_idx = self.array_size
            
            process = mp.Process(
                target=self.worker_process,
                args=(i, start_idx, end_idx)
            )
            process.start()
            processes.append(process)
        
        # 等待所有进程完成
        for process in processes:
            process.join()
        
        print(f"所有进程完成，共享值: {self.shared_value.value}")
        
        # 验证结果
        return self.verify_results()
    
    def verify_results(self) -> Dict[str, Any]:
        """验证处理结果"""
        total_sum = sum(self.shared_array[:])
        non_zero_count = sum(1 for x in self.shared_array[:] if x != 0)
        
        return {
            "array_size": self.array_size,
            "total_sum": total_sum,
            "non_zero_count": non_zero_count,
            "shared_value": self.shared_value.value,
            "verification_passed": non_zero_count == self.shared_value.value
        }


class ProcessCommunication:
    """进程间通信示例"""
    
    @staticmethod
    def producer_process(queue: mp.Queue, num_items: int, producer_id: str):
        """生产者进程"""
        pid = os.getpid()
        print(f"Producer {producer_id} (PID: {pid}) 开始生产...")
        
        for i in range(num_items):
            item = {
                "producer_id": producer_id,
                "item_id": i,
                "data": f"Data-{producer_id}-{i}",
                "timestamp": time.time(),
                "pid": pid
            }
            
            queue.put(item)
            print(f"Producer {producer_id} 生产: {item['data']}")
            time.sleep(random.uniform(0.1, 0.3))
        
        # 发送结束信号
        queue.put(None)
        print(f"Producer {producer_id} 完成生产")
    
    @staticmethod
    def consumer_process(queue: mp.Queue, results_queue: mp.Queue, consumer_id: str):
        """消费者进程"""
        pid = os.getpid()
        print(f"Consumer {consumer_id} (PID: {pid}) 开始消费...")
        
        consumed_items = []
        
        while True:
            try:
                item = queue.get(timeout=2)
                
                if item is None:  # 结束信号
                    queue.put(None)  # 传递给其他消费者
                    break
                
                # 处理项目
                processed_item = {
                    "original": item,
                    "consumer_id": consumer_id,
                    "consumer_pid": pid,
                    "processed_at": time.time()
                }
                
                consumed_items.append(processed_item)
                print(f"Consumer {consumer_id} 消费: {item['data']}")
                
                time.sleep(random.uniform(0.05, 0.15))
                
            except Exception as e:
                print(f"Consumer {consumer_id} 异常: {e}")
                break
        
        # 返回结果
        results_queue.put({
            "consumer_id": consumer_id,
            "consumed_count": len(consumed_items),
            "items": consumed_items
        })
        
        print(f"Consumer {consumer_id} 完成，处理了 {len(consumed_items)} 个项目")
    
    def run_producer_consumer(self, num_producers: int = 2, num_consumers: int = 3, items_per_producer: int = 5):
        """运行生产者消费者示例"""
        # 创建队列
        task_queue = mp.Queue()
        results_queue = mp.Queue()
        
        processes = []
        
        # 启动生产者进程
        for i in range(num_producers):
            producer = mp.Process(
                target=self.producer_process,
                args=(task_queue, items_per_producer, f"P{i}")
            )
            producer.start()
            processes.append(producer)
        
        # 启动消费者进程
        for i in range(num_consumers):
            consumer = mp.Process(
                target=self.consumer_process,
                args=(task_queue, results_queue, f"C{i}")
            )
            consumer.start()
            processes.append(consumer)
        
        # 等待所有进程完成
        for process in processes:
            process.join()
        
        # 收集结果
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        return results


def cpu_intensive_calculation(n: int) -> Dict[str, Any]:
    """CPU密集型计算任务"""
    pid = os.getpid()
    start_time = time.time()
    
    # 计算质数
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
    
    primes = [i for i in range(2, n) if is_prime(i)]
    
    execution_time = time.time() - start_time
    
    return {
        "pid": pid,
        "range": n,
        "prime_count": len(primes),
        "largest_prime": max(primes) if primes else None,
        "execution_time": execution_time
    }


def parallel_calculation_worker(data_chunk: List[int]) -> Dict[str, Any]:
    """并行计算工作函数"""
    pid = os.getpid()
    start_time = time.time()
    
    # 对数据块进行处理
    results = {
        "sum": sum(data_chunk),
        "count": len(data_chunk),
        "min": min(data_chunk) if data_chunk else None,
        "max": max(data_chunk) if data_chunk else None,
        "avg": sum(data_chunk) / len(data_chunk) if data_chunk else 0
    }
    
    execution_time = time.time() - start_time
    
    return {
        "pid": pid,
        "chunk_size": len(data_chunk),
        "results": results,
        "execution_time": execution_time
    }


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="multiprocessing_basic_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.BEGINNER,
    description="基础多进程编程示例",
    tags=["multiprocessing", "basic", "parallel"]
)
@demo(title="基础多进程编程示例")
def multiprocessing_basic_example():
    """展示基础多进程编程概念"""
    
    def worker_function(worker_id: int, work_duration: float):
        """工作函数"""
        pid = os.getpid()
        print(f"Worker {worker_id} 开始工作 (PID: {pid})")
        time.sleep(work_duration)
        print(f"Worker {worker_id} 完成工作 (PID: {pid})")
        return f"Worker {worker_id} 结果 (PID: {pid})"
    
    print("多进程编程基础示例")
    print(f"主进程 PID: {os.getpid()}")
    print(f"CPU 核心数: {mp.cpu_count()}")
    
    print("\n顺序执行示例：")
    start_time = time.time()
    
    sequential_results = []
    for i in range(3):
        result = worker_function(i, 1.0)
        sequential_results.append(result)
    
    sequential_time = time.time() - start_time
    print(f"顺序执行耗时: {sequential_time:.2f}s")
    
    print("\n多进程执行示例：")
    start_time = time.time()
    
    with mp.Pool(processes=3) as pool:
        # 准备参数
        args = [(i, 1.0) for i in range(3)]
        
        # 并行执行
        parallel_results = pool.starmap(worker_function, args)
    
    parallel_time = time.time() - start_time
    print(f"多进程执行耗时: {parallel_time:.2f}s")
    print(f"性能提升: {sequential_time/parallel_time:.1f}x")
    
    print(f"\n结果:")
    for result in parallel_results:
        print(f"  {result}")


@example(
    name="process_pool_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="进程池管理器示例",
    tags=["multiprocessing", "process-pool", "cpu-intensive"]
)
@demo(title="进程池管理器示例")
def process_pool_example():
    """展示进程池的使用"""
    
    print("进程池管理器示例")
    print(f"使用 {mp.cpu_count()} 个进程")
    
    manager = ProcessPoolManager(max_workers=mp.cpu_count())
    
    # 提交CPU密集型任务
    print("\n提交CPU密集型任务...")
    task_ranges = [1000, 2000, 3000, 5000, 8000]
    
    for i, n in enumerate(task_ranges):
        manager.submit_task(
            f"prime_task_{i}",
            cpu_intensive_calculation,
            n
        )
    
    print("等待任务完成...")
    start_time = time.time()
    
    results = manager.wait_for_completion(timeout=30)
    
    total_time = time.time() - start_time
    
    print(f"\n所有任务完成，总耗时: {total_time:.2f}s")
    print(f"成功任务: {sum(1 for r in results if r.success)}")
    print(f"失败任务: {sum(1 for r in results if not r.success)}")
    
    # 显示结果详情
    print("\n任务结果详情:")
    for result in results:
        if result.success:
            data = result.result
            print(f"✅ {result.process_id} (PID: {result.pid}): "
                  f"范围={data['range']}, 质数数量={data['prime_count']}, "
                  f"最大质数={data['largest_prime']}, "
                  f"耗时={result.execution_time:.3f}s")
        else:
            print(f"❌ {result.process_id}: {result.error}")
    
    manager.shutdown()


@example(
    name="shared_memory_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="共享内存示例",
    tags=["multiprocessing", "shared-memory", "synchronization"]
)
@demo(title="共享内存示例")
def shared_memory_example():
    """展示共享内存的使用"""
    
    print("共享内存示例")
    
    # 创建共享内存示例
    array_size = 1000
    num_workers = 4
    
    shared_mem = SharedMemoryExample(array_size)
    
    print(f"数组大小: {array_size}")
    print(f"工作进程数: {num_workers}")
    
    start_time = time.time()
    
    # 运行并行处理
    verification_result = shared_mem.run_parallel_processing(num_workers)
    
    execution_time = time.time() - start_time
    
    print(f"\n并行处理完成，耗时: {execution_time:.2f}s")
    print(f"验证结果:")
    print(f"  数组大小: {verification_result['array_size']}")
    print(f"  总和: {verification_result['total_sum']}")
    print(f"  非零元素: {verification_result['non_zero_count']}")
    print(f"  共享值: {verification_result['shared_value']}")
    print(f"  验证通过: {verification_result['verification_passed']}")


@example(
    name="process_communication_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.ADVANCED,
    description="进程间通信示例",
    tags=["multiprocessing", "ipc", "queue", "producer-consumer"]
)
@demo(title="进程间通信示例")
def process_communication_example():
    """展示进程间通信"""
    
    print("进程间通信示例")
    
    comm = ProcessCommunication()
    
    # 运行生产者消费者模式
    print("\n启动生产者消费者进程...")
    
    start_time = time.time()
    
    results = comm.run_producer_consumer(
        num_producers=2,
        num_consumers=3,
        items_per_producer=8
    )
    
    execution_time = time.time() - start_time
    
    print(f"\n所有进程完成，耗时: {execution_time:.2f}s")
    
    # 分析结果
    total_consumed = sum(r['consumed_count'] for r in results)
    
    print(f"\n结果统计:")
    print(f"消费者数量: {len(results)}")
    print(f"总消费项目: {total_consumed}")
    
    print(f"\n各消费者详情:")
    for result in results:
        print(f"  {result['consumer_id']}: 处理了 {result['consumed_count']} 个项目")


@example(
    name="parallel_data_processing_example",
    category=ExampleCategory.CONCURRENCY,
    difficulty=DifficultyLevel.ADVANCED,
    description="并行数据处理示例",
    tags=["multiprocessing", "data-processing", "map-reduce"]
)
@demo(title="并行数据处理示例")
def parallel_data_processing_example():
    """展示并行数据处理"""
    
    print("并行数据处理示例")
    
    # 生成大数据集
    data_size = 10000
    data = list(range(1, data_size + 1))
    
    print(f"数据集大小: {len(data)}")
    
    # 将数据分块
    num_processes = mp.cpu_count()
    chunk_size = len(data) // num_processes
    
    data_chunks = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        
        # 最后一个块包含剩余数据
        if i == num_processes - 1:
            end_idx = len(data)
        
        data_chunks.append(data[start_idx:end_idx])
    
    print(f"分成 {len(data_chunks)} 个数据块")
    
    # 顺序处理（对比基准）
    print("\n顺序处理...")
    start_time = time.time()
    
    sequential_result = parallel_calculation_worker(data)
    
    sequential_time = time.time() - start_time
    print(f"顺序处理耗时: {sequential_time:.3f}s")
    
    # 并行处理
    print("\n并行处理...")
    start_time = time.time()
    
    with mp.Pool(processes=num_processes) as pool:
        chunk_results = pool.map(parallel_calculation_worker, data_chunks)
    
    parallel_time = time.time() - start_time
    
    # 聚合结果
    total_sum = sum(r['results']['sum'] for r in chunk_results)
    total_count = sum(r['results']['count'] for r in chunk_results)
    overall_min = min(r['results']['min'] for r in chunk_results if r['results']['min'] is not None)
    overall_max = max(r['results']['max'] for r in chunk_results if r['results']['max'] is not None)
    overall_avg = total_sum / total_count if total_count > 0 else 0
    
    print(f"并行处理耗时: {parallel_time:.3f}s")
    print(f"性能提升: {sequential_time/parallel_time:.1f}x")
    
    print(f"\n处理结果:")
    print(f"  总和: {total_sum}")
    print(f"  数量: {total_count}")
    print(f"  最小值: {overall_min}")
    print(f"  最大值: {overall_max}")
    print(f"  平均值: {overall_avg:.2f}")
    
    print(f"\n各进程详情:")
    for i, result in enumerate(chunk_results):
        print(f"  进程 {i} (PID: {result['pid']}): "
              f"处理 {result['chunk_size']} 项, "
              f"耗时 {result['execution_time']:.3f}s")


# 导出的类和函数
__all__ = [
    "ProcessPoolManager",
    "SharedMemoryExample",
    "ProcessCommunication",
    "cpu_intensive_calculation",
    "parallel_calculation_worker",
    "multiprocessing_basic_example",
    "process_pool_example",
    "shared_memory_example",
    "process_communication_example",
    "parallel_data_processing_example"
]