"""
线程池演示模块
展示concurrent.futures模块的ThreadPoolExecutor使用
"""

import concurrent.futures
import threading
import time
import random
import math
from datetime import datetime
from typing import List, Any, Dict, Callable, Optional
import os

# 可选的psutil导入
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    # psutil的简单替代品
    class MockPsutil:
        @staticmethod
        def cpu_percent(interval=None):
            return 0.0
        
        @staticmethod
        def virtual_memory():
            class MemInfo:
                percent = 0.0
                used = 0
                total = 8 * 1024 * 1024 * 1024  # 8GB
            return MemInfo()
        
        @staticmethod
        def Process():
            class ProcessInfo:
                def memory_info(self):
                    class MemInfo:
                        rss = 100 * 1024 * 1024  # 100MB
                    return MemInfo()
                
                def cpu_percent(self):
                    return 0.0
            return ProcessInfo()
    
    psutil = MockPsutil()


class ThreadPoolDemo:
    """线程池使用演示类"""
    
    def __init__(self):
        self.cpu_count = os.cpu_count()
        print(f"🖥️  检测到CPU核心数: {self.cpu_count}")
    
    def batch_processing(self) -> None:
        """批量任务处理演示"""
        print(f"\n{'='*50}")
        print("📦 批量任务处理演示")
        print(f"{'='*50}")
        
        def cpu_intensive_task(n: int) -> Dict[str, Any]:
            """CPU密集型任务：计算素数"""
            start_time = time.time()
            
            def is_prime(num):
                if num < 2:
                    return False
                for i in range(2, int(math.sqrt(num)) + 1):
                    if num % i == 0:
                        return False
                return True
            
            # 查找前n个素数
            primes = []
            num = 2
            while len(primes) < n:
                if is_prime(num):
                    primes.append(num)
                num += 1
            
            end_time = time.time()
            
            return {
                'task_id': f"Task-{n}",
                'count': n,
                'largest_prime': primes[-1],
                'execution_time': end_time - start_time,
                'thread_id': threading.get_ident()
            }
        
        # 定义任务列表
        tasks = [100, 200, 300, 400, 500]
        
        print(f"📋 待处理任务: {tasks}")
        
        # 串行处理（对比）
        print(f"\n🔄 串行处理:")
        start_time = time.time()
        serial_results = []
        for task in tasks:
            result = cpu_intensive_task(task)
            serial_results.append(result)
            print(f"  ✅ {result['task_id']} 完成，耗时: {result['execution_time']:.2f}秒")
        
        serial_time = time.time() - start_time
        print(f"串行总耗时: {serial_time:.2f}秒")
        
        # 线程池并行处理
        print(f"\n⚡ 线程池并行处理 (max_workers={self.cpu_count}):")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(cpu_intensive_task, task): task 
                for task in tasks
            }
            
            parallel_results = []
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    parallel_results.append(result)
                    print(f"  ✅ {result['task_id']} 完成，耗时: {result['execution_time']:.2f}秒")
                except Exception as e:
                    print(f"  ❌ Task-{task} 失败: {e}")
        
        parallel_time = time.time() - start_time
        print(f"并行总耗时: {parallel_time:.2f}秒")
        
        # 性能对比
        speedup = serial_time / parallel_time
        print(f"\n📊 性能对比:")
        print(f"  串行耗时: {serial_time:.2f}秒")
        print(f"  并行耗时: {parallel_time:.2f}秒")
        print(f"  加速比: {speedup:.2f}x")
        print(f"  效率: {(speedup / self.cpu_count) * 100:.1f}%")
    
    def result_collection(self) -> List[Dict[str, Any]]:
        """结果收集和异常处理演示"""
        print(f"\n{'='*50}")
        print("🎯 结果收集和异常处理演示")
        print(f"{'='*50}")
        
        def unreliable_task(task_id: int) -> Dict[str, Any]:
            """不稳定的任务（可能失败）"""
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
            
            # 30%的概率失败
            if random.random() < 0.3:
                raise Exception(f"Task {task_id} 随机失败")
            
            return {
                'task_id': task_id,
                'result': random.randint(1, 100),
                'execution_time': delay,
                'status': 'success'
            }
        
        tasks = list(range(1, 11))  # 10个任务
        results = []
        errors = []
        
        print(f"📋 提交 {len(tasks)} 个任务到线程池...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # 提交所有任务并获取Future对象
            future_to_task = {
                executor.submit(unreliable_task, task_id): task_id 
                for task_id in tasks
            }
            
            # 使用as_completed获取完成的任务
            for future in concurrent.futures.as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result(timeout=5)  # 5秒超时
                    results.append(result)
                    print(f"  ✅ Task-{task_id}: 结果={result['result']}, 耗时={result['execution_time']:.2f}秒")
                except concurrent.futures.TimeoutError:
                    error_info = {'task_id': task_id, 'error': 'Timeout', 'type': 'TimeoutError'}
                    errors.append(error_info)
                    print(f"  ⏰ Task-{task_id}: 超时")
                except Exception as e:
                    error_info = {'task_id': task_id, 'error': str(e), 'type': type(e).__name__}
                    errors.append(error_info)
                    print(f"  ❌ Task-{task_id}: {e}")
        
        # 统计结果
        print(f"\n📊 执行统计:")
        print(f"  总任务数: {len(tasks)}")
        print(f"  成功任务: {len(results)}")
        print(f"  失败任务: {len(errors)}")
        print(f"  成功率: {(len(results) / len(tasks)) * 100:.1f}%")
        
        if results:
            avg_result = sum(r['result'] for r in results) / len(results)
            avg_time = sum(r['execution_time'] for r in results) / len(results)
            print(f"  平均结果: {avg_result:.1f}")
            print(f"  平均耗时: {avg_time:.2f}秒")
        
        return results
    
    def dynamic_pool_sizing(self) -> None:
        """动态线程池大小演示"""
        print(f"\n{'='*50}")
        print("📈 动态线程池大小演示")
        print(f"{'='*50}")
        
        def io_bound_task(task_id: int, delay: float) -> Dict[str, Any]:
            """IO密集型任务模拟"""
            start_time = time.time()
            time.sleep(delay)  # 模拟IO等待
            end_time = time.time()
            
            return {
                'task_id': task_id,
                'delay': delay,
                'actual_time': end_time - start_time,
                'thread_id': threading.get_ident()
            }
        
        # 测试不同的线程池大小
        pool_sizes = [1, 2, 4, 8, 16]
        task_count = 20
        task_delay = 0.5  # 每个任务0.5秒延迟
        
        results_summary = []
        
        for pool_size in pool_sizes:
            print(f"\n🔧 测试线程池大小: {pool_size}")
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
                futures = [
                    executor.submit(io_bound_task, i, task_delay)
                    for i in range(1, task_count + 1)
                ]
                
                results = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        print(f"  ❌ 任务失败: {e}")
            
            total_time = time.time() - start_time
            
            # 分析线程使用情况
            unique_threads = len(set(r['thread_id'] for r in results))
            
            results_summary.append({
                'pool_size': pool_size,
                'total_time': total_time,
                'unique_threads': unique_threads,
                'theoretical_min_time': (task_count * task_delay) / pool_size,
                'efficiency': ((task_count * task_delay) / pool_size) / total_time
            })
            
            print(f"  ⏱️  总耗时: {total_time:.2f}秒")
            print(f"  🧵 实际使用线程数: {unique_threads}")
            print(f"  📊 效率: {results_summary[-1]['efficiency']:.1%}")
        
        # 性能分析
        print(f"\n📊 性能分析汇总:")
        print(f"{'线程池大小':>8} {'总耗时(秒)':>10} {'使用线程':>8} {'理论最小耗时':>12} {'效率':>8}")
        print("-" * 55)
        
        for summary in results_summary:
            print(f"{summary['pool_size']:>8} "
                  f"{summary['total_time']:>10.2f} "
                  f"{summary['unique_threads']:>8} "
                  f"{summary['theoretical_min_time']:>12.2f} "
                  f"{summary['efficiency']:>8.1%}")
        
        # 找出最优配置
        best_config = max(results_summary, key=lambda x: x['efficiency'])
        print(f"\n🏆 最优配置: 线程池大小 {best_config['pool_size']}, "
              f"效率 {best_config['efficiency']:.1%}")
    
    def monitor_thread_pool(self) -> None:
        """线程池监控演示"""
        print(f"\n{'='*50}")
        print("📊 线程池监控演示")
        print(f"{'='*50}")
        
        def monitored_task(task_id: int) -> Dict[str, Any]:
            """被监控的任务"""
            start_time = time.time()
            
            # 模拟不同类型的工作负载
            if task_id % 3 == 0:
                # CPU密集型
                total = sum(i * i for i in range(10000))
            elif task_id % 3 == 1:
                # IO密集型
                time.sleep(random.uniform(0.5, 1.5))
            else:
                # 混合型
                time.sleep(random.uniform(0.1, 0.3))
                total = sum(i for i in range(5000))
            
            end_time = time.time()
            
            return {
                'task_id': task_id,
                'execution_time': end_time - start_time,
                'thread_id': threading.get_ident(),
                'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
            }
        
        def print_system_stats():
            """打印系统统计信息"""
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            active_threads = threading.active_count()
            
            print(f"  📊 CPU使用率: {cpu_percent:.1f}%")
            print(f"  🧠 内存使用: {memory.percent:.1f}% ({memory.used / 1024 / 1024 / 1024:.1f}GB)")
            print(f"  🧵 活跃线程数: {active_threads}")
        
        print("🔍 开始监控线程池执行...")
        print_system_stats()
        
        start_time = time.time()
        completed_tasks = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # 提交任务
            futures = [
                executor.submit(monitored_task, i)
                for i in range(1, 21)  # 20个任务
            ]
            
            # 监控执行过程
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    completed_tasks += 1
                    
                    if completed_tasks % 5 == 0:  # 每完成5个任务打印一次状态
                        elapsed = time.time() - start_time
                        print(f"\n⏳ 进度: {completed_tasks}/20 任务完成 (耗时: {elapsed:.1f}秒)")
                        print_system_stats()
                        
                        # 显示最近完成的任务信息
                        print(f"  🎯 最新任务 Task-{result['task_id']}: "
                              f"耗时 {result['execution_time']:.2f}秒, "
                              f"内存 {result['memory_usage']:.1f}MB")
                
                except Exception as e:
                    print(f"❌ 任务失败: {e}")
        
        total_time = time.time() - start_time
        print(f"\n✅ 所有任务完成，总耗时: {total_time:.2f}秒")
        print_system_stats()
    
    def run_all_demos(self) -> None:
        """运行所有线程池演示"""
        print("🚀 开始线程池演示")
        print("=" * 60)
        
        try:
            self.batch_processing()
            self.result_collection()
            self.dynamic_pool_sizing()
            self.monitor_thread_pool()
            
            print(f"\n{'='*60}")
            print("✅ 线程池演示完成")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")


def main():
    """主函数"""
    demo = ThreadPoolDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()