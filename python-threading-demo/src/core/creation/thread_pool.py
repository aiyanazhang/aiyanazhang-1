"""
线程池演示模块

演示如何使用ThreadPoolExecutor管理线程池
"""

import concurrent.futures
import threading
import time
import random
import math
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, Future


class ThreadPoolDemo:
    """线程池演示类"""
    
    def __init__(self):
        self.results: List[Any] = []
        
    def cpu_intensive_task(self, task_id: int, iterations: int) -> Dict[str, Any]:
        """CPU密集型任务示例"""
        thread_name = threading.current_thread().name
        print(f"[{thread_name}] 开始执行CPU密集型任务 {task_id}")
        
        start_time = time.time()
        
        # 计算质数
        primes = []
        for num in range(2, iterations):
            if self.is_prime(num):
                primes.append(num)
                
        end_time = time.time()
        execution_time = end_time - start_time
        
        result = {
            'task_id': task_id,
            'thread_name': thread_name,
            'iterations': iterations,
            'primes_found': len(primes),
            'execution_time': execution_time
        }
        
        print(f"[{thread_name}] 任务 {task_id} 完成，找到 {len(primes)} 个质数")
        return result
        
    def io_intensive_task(self, task_id: int, delay: float) -> Dict[str, Any]:
        """IO密集型任务示例（模拟网络请求或文件操作）"""
        thread_name = threading.current_thread().name
        print(f"[{thread_name}] 开始执行IO密集型任务 {task_id}")
        
        start_time = time.time()
        
        # 模拟IO操作
        time.sleep(delay)
        
        # 模拟处理结果
        data_size = random.randint(1000, 10000)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        result = {
            'task_id': task_id,
            'thread_name': thread_name,
            'delay': delay,
            'data_size': data_size,
            'execution_time': execution_time
        }
        
        print(f"[{thread_name}] 任务 {task_id} 完成，处理了 {data_size} 字节数据")
        return result
        
    def task_with_exception(self, task_id: int, should_fail: bool = False) -> Dict[str, Any]:
        """可能抛出异常的任务"""
        thread_name = threading.current_thread().name
        print(f"[{thread_name}] 开始执行任务 {task_id}")
        
        if should_fail:
            raise ValueError(f"任务 {task_id} 故意失败")
            
        time.sleep(random.uniform(0.5, 1.5))
        
        return {
            'task_id': task_id,
            'thread_name': thread_name,
            'status': 'success'
        }
        
    def is_prime(self, n: int) -> bool:
        """检查是否为质数"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
        
    def demo_basic_thread_pool(self) -> None:
        """演示基础线程池使用"""
        print("\n=== 基础线程池演示 ===")
        print("演示ThreadPoolExecutor的基本用法")
        
        # 创建线程池
        max_workers = 3
        print(f"创建线程池，最大工作线程数: {max_workers}")
        
        with ThreadPoolExecutor(max_workers=max_workers, 
                               thread_name_prefix="PoolWorker") as executor:
            
            # 提交多个任务
            tasks = []
            for i in range(5):
                future = executor.submit(self.io_intensive_task, i+1, random.uniform(1, 3))
                tasks.append(future)
                
            print(f"提交了 {len(tasks)} 个任务到线程池")
            
            # 等待任务完成并获取结果
            print("\n等待任务完成...")
            for i, future in enumerate(tasks):
                try:
                    result = future.result()  # 获取结果，会阻塞直到完成
                    print(f"任务 {i+1} 结果: 线程={result['thread_name']}, "
                          f"耗时={result['execution_time']:.2f}秒")
                except Exception as e:
                    print(f"任务 {i+1} 失败: {e}")
                    
        print("线程池自动关闭")
        
    def demo_map_method(self) -> None:
        """演示使用map方法批量执行任务"""
        print("\n=== 线程池map方法演示 ===")
        print("演示使用executor.map批量执行相同类型的任务")
        
        # 准备任务参数
        task_params = [(i+1, 1000 + i*500) for i in range(4)]
        
        print(f"准备执行 {len(task_params)} 个CPU密集型任务")
        
        with ThreadPoolExecutor(max_workers=2, 
                               thread_name_prefix="MapWorker") as executor:
            
            start_time = time.time()
            
            # 使用map方法执行任务
            results = list(executor.map(
                lambda params: self.cpu_intensive_task(*params),
                task_params
            ))
            
            end_time = time.time()
            total_time = end_time - start_time
            
        print(f"\n所有任务完成，总耗时: {total_time:.2f}秒")
        print("任务结果:")
        for result in results:
            print(f"  - 任务 {result['task_id']}: 找到 {result['primes_found']} 个质数, "
                  f"耗时 {result['execution_time']:.2f}秒")
                  
    def demo_as_completed(self) -> None:
        """演示使用as_completed处理完成的任务"""
        print("\n=== as_completed演示 ===")
        print("演示使用as_completed按完成顺序处理任务结果")
        
        with ThreadPoolExecutor(max_workers=3, 
                               thread_name_prefix="CompletedWorker") as executor:
            
            # 提交不同执行时间的任务
            futures = []
            delays = [3, 1, 2, 0.5, 2.5]
            
            for i, delay in enumerate(delays):
                future = executor.submit(self.io_intensive_task, i+1, delay)
                futures.append(future)
                
            print(f"提交了 {len(futures)} 个不同延时的任务")
            print("按完成顺序处理结果:")
            
            # 按完成顺序处理结果
            completed_count = 0
            for future in as_completed(futures):
                completed_count += 1
                try:
                    result = future.result()
                    print(f"  [{completed_count}] 任务 {result['task_id']} 完成 "
                          f"(延时: {result['delay']}秒, 实际耗时: {result['execution_time']:.2f}秒)")
                except Exception as e:
                    print(f"  [{completed_count}] 任务失败: {e}")
                    
    def demo_exception_handling(self) -> None:
        """演示线程池中的异常处理"""
        print("\n=== 异常处理演示 ===")
        print("演示线程池中如何处理任务异常")
        
        with ThreadPoolExecutor(max_workers=2, 
                               thread_name_prefix="ExceptionWorker") as executor:
            
            # 提交一些会失败的任务和正常任务
            futures = []
            for i in range(5):
                should_fail = (i % 2 == 1)  # 奇数任务会失败
                future = executor.submit(self.task_with_exception, i+1, should_fail)
                futures.append((future, should_fail))
                
            print(f"提交了 {len(futures)} 个任务（其中一些会失败）")
            
            # 处理结果和异常
            success_count = 0
            failed_count = 0
            
            for future, expected_to_fail in futures:
                try:
                    result = future.result(timeout=5)  # 设置超时
                    success_count += 1
                    print(f"  ✓ 任务 {result['task_id']} 成功: {result['status']}")
                except Exception as e:
                    failed_count += 1
                    print(f"  ✗ 任务失败: {e}")
                    
            print(f"\n结果统计: 成功 {success_count} 个，失败 {failed_count} 个")
            
    def demo_thread_pool_with_timeout(self) -> None:
        """演示带超时的线程池操作"""
        print("\n=== 超时处理演示 ===")
        print("演示如何处理任务超时")
        
        with ThreadPoolExecutor(max_workers=2, 
                               thread_name_prefix="TimeoutWorker") as executor:
            
            # 提交一些长时间运行的任务
            futures = []
            delays = [1, 5, 2, 8, 3]  # 有些任务会超时
            
            for i, delay in enumerate(delays):
                future = executor.submit(self.io_intensive_task, i+1, delay)
                futures.append((future, delay))
                
            print(f"提交了 {len(futures)} 个不同延时的任务")
            
            # 设置超时时间
            timeout = 4
            print(f"设置超时时间: {timeout}秒")
            
            for future, delay in futures:
                try:
                    result = future.result(timeout=timeout)
                    print(f"  ✓ 任务 {result['task_id']} 在时限内完成 "
                          f"(延时: {delay}秒)")
                except concurrent.futures.TimeoutError:
                    print(f"  ⏰ 任务超时 (预期延时: {delay}秒)")
                    # 注意：超时的任务仍在后台运行
                except Exception as e:
                    print(f"  ✗ 任务失败: {e}")
                    
    def demo_dynamic_thread_pool(self) -> None:
        """演示动态调整线程池大小"""
        print("\n=== 动态线程池演示 ===")
        print("演示不同线程池大小对性能的影响")
        
        # 测试不同的线程池大小
        pool_sizes = [1, 2, 4, 8]
        task_count = 8
        
        for pool_size in pool_sizes:
            print(f"\n测试线程池大小: {pool_size}")
            
            with ThreadPoolExecutor(max_workers=pool_size, 
                                   thread_name_prefix=f"DynamicWorker{pool_size}") as executor:
                
                start_time = time.time()
                
                # 提交相同的任务
                futures = []
                for i in range(task_count):
                    future = executor.submit(self.io_intensive_task, i+1, 1.5)
                    futures.append(future)
                    
                # 等待所有任务完成
                for future in futures:
                    future.result()
                    
                end_time = time.time()
                total_time = end_time - start_time
                
                print(f"  线程池大小 {pool_size}: 总耗时 {total_time:.2f}秒")
                
    def run_all_demos(self) -> None:
        """运行所有线程池演示"""
        print("开始线程池演示...")
        
        try:
            self.demo_basic_thread_pool()
            time.sleep(1)
            
            self.demo_map_method()
            time.sleep(1)
            
            self.demo_as_completed()
            time.sleep(1)
            
            self.demo_exception_handling()
            time.sleep(1)
            
            self.demo_thread_pool_with_timeout()
            time.sleep(1)
            
            self.demo_dynamic_thread_pool()
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")
        finally:
            print("\n线程池演示结束")


def main():
    """主函数，用于测试"""
    demo = ThreadPoolDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()