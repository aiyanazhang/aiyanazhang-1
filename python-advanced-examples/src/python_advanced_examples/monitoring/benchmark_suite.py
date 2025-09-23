"""
基准测试套件

提供全面的性能基准测试功能：
- 函数执行时间测试
- 内存使用测试
- 并发性能测试
- 算法复杂度分析
- 对比测试
"""

import time
import timeit
import tracemalloc
import statistics
import threading
import asyncio
from typing import (
    Any, Callable, Dict, List, Optional, Union, Tuple, 
    TypeVar, Generic, Iterator
)
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import gc
import sys
import psutil
import functools
import inspect

T = TypeVar('T')
R = TypeVar('R')

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    execution_time: float
    memory_usage: Optional[float] = None
    iterations: int = 1
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def avg_time_per_iteration(self) -> float:
        """平均每次迭代时间"""
        return self.execution_time / self.iterations if self.iterations > 0 else 0
    
    @property
    def operations_per_second(self) -> float:
        """每秒操作数"""
        return self.iterations / self.execution_time if self.execution_time > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'iterations': self.iterations,
            'avg_time_per_iteration': self.avg_time_per_iteration,
            'operations_per_second': self.operations_per_second,
            'success': self.success,
            'error': self.error,
            'metadata': self.metadata
        }

@dataclass
class ComparisonResult:
    """对比测试结果"""
    results: List[BenchmarkResult]
    baseline: Optional[str] = None
    
    def get_fastest(self) -> Optional[BenchmarkResult]:
        """获取最快的结果"""
        successful_results = [r for r in self.results if r.success]
        if not successful_results:
            return None
        return min(successful_results, key=lambda r: r.execution_time)
    
    def get_slowest(self) -> Optional[BenchmarkResult]:
        """获取最慢的结果"""
        successful_results = [r for r in self.results if r.success]
        if not successful_results:
            return None
        return max(successful_results, key=lambda r: r.execution_time)
    
    def get_relative_performance(self) -> Dict[str, float]:
        """获取相对性能（相对于基线或最快的）"""
        baseline_result = None
        
        if self.baseline:
            baseline_result = next((r for r in self.results if r.name == self.baseline), None)
        
        if not baseline_result:
            baseline_result = self.get_fastest()
        
        if not baseline_result:
            return {}
        
        baseline_time = baseline_result.execution_time
        return {
            r.name: r.execution_time / baseline_time 
            for r in self.results if r.success
        }

class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self, 
                 warmup_iterations: int = 3,
                 test_iterations: int = 10,
                 timeout: float = 300.0):
        self.warmup_iterations = warmup_iterations
        self.test_iterations = test_iterations
        self.timeout = timeout
    
    def run_single(self, 
                   func: Callable,
                   name: str = None,
                   iterations: int = None,
                   args: Tuple = (),
                   kwargs: Dict[str, Any] = None,
                   measure_memory: bool = True) -> BenchmarkResult:
        """运行单个函数的基准测试"""
        if kwargs is None:
            kwargs = {}
        
        test_name = name or getattr(func, '__name__', 'unnamed_function')
        test_iterations = iterations or self.test_iterations
        
        try:
            # 预热
            for _ in range(self.warmup_iterations):
                func(*args, **kwargs)
            
            # 强制垃圾回收
            gc.collect()
            
            # 内存测试
            memory_usage = None
            if measure_memory:
                memory_usage = self._measure_memory(func, args, kwargs)
            
            # 时间测试
            start_time = time.perf_counter()
            
            for _ in range(test_iterations):
                func(*args, **kwargs)
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            return BenchmarkResult(
                name=test_name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                iterations=test_iterations,
                success=True
            )
            
        except Exception as e:
            return BenchmarkResult(
                name=test_name,
                execution_time=0.0,
                iterations=test_iterations,
                success=False,
                error=str(e)
            )
    
    def run_comparison(self, 
                      functions: Dict[str, Callable],
                      args: Tuple = (),
                      kwargs: Dict[str, Any] = None,
                      baseline: str = None) -> ComparisonResult:
        """运行对比测试"""
        if kwargs is None:
            kwargs = {}
        
        results = []
        for name, func in functions.items():
            result = self.run_single(func, name, args=args, kwargs=kwargs)
            results.append(result)
        
        return ComparisonResult(results=results, baseline=baseline)
    
    def run_timeit(self, 
                   stmt: str,
                   setup: str = "",
                   number: int = 1000000,
                   globals_dict: Dict[str, Any] = None) -> BenchmarkResult:
        """使用timeit运行基准测试"""
        try:
            execution_time = timeit.timeit(
                stmt=stmt,
                setup=setup,
                number=number,
                globals=globals_dict
            )
            
            return BenchmarkResult(
                name=f"timeit: {stmt[:50]}...",
                execution_time=execution_time,
                iterations=number,
                success=True
            )
            
        except Exception as e:
            return BenchmarkResult(
                name=f"timeit: {stmt[:50]}...",
                execution_time=0.0,
                iterations=number,
                success=False,
                error=str(e)
            )
    
    def _measure_memory(self, 
                       func: Callable, 
                       args: Tuple, 
                       kwargs: Dict[str, Any]) -> Optional[float]:
        """测量内存使用"""
        try:
            tracemalloc.start()
            
            # 执行函数
            func(*args, **kwargs)
            
            # 获取内存使用情况
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return peak / 1024 / 1024  # 转换为MB
            
        except Exception:
            tracemalloc.stop()
            return None

class ConcurrencyBenchmark:
    """并发性能基准测试"""
    
    def __init__(self, runner: BenchmarkRunner = None):
        self.runner = runner or BenchmarkRunner()
    
    def benchmark_threading(self,
                           func: Callable,
                           worker_counts: List[int],
                           total_tasks: int = 1000,
                           args: Tuple = (),
                           kwargs: Dict[str, Any] = None) -> Dict[int, BenchmarkResult]:
        """基准测试多线程性能"""
        if kwargs is None:
            kwargs = {}
        
        results = {}
        
        for worker_count in worker_counts:
            try:
                start_time = time.perf_counter()
                
                with ThreadPoolExecutor(max_workers=worker_count) as executor:
                    futures = [
                        executor.submit(func, *args, **kwargs)
                        for _ in range(total_tasks)
                    ]
                    
                    # 等待所有任务完成
                    for future in as_completed(futures):
                        future.result()  # 获取结果，如果有异常会抛出
                
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                
                results[worker_count] = BenchmarkResult(
                    name=f"threading_{worker_count}_workers",
                    execution_time=execution_time,
                    iterations=total_tasks,
                    success=True,
                    metadata={'worker_count': worker_count, 'total_tasks': total_tasks}
                )
                
            except Exception as e:
                results[worker_count] = BenchmarkResult(
                    name=f"threading_{worker_count}_workers",
                    execution_time=0.0,
                    iterations=total_tasks,
                    success=False,
                    error=str(e),
                    metadata={'worker_count': worker_count, 'total_tasks': total_tasks}
                )
        
        return results
    
    async def benchmark_asyncio(self,
                               async_func: Callable,
                               concurrency_levels: List[int],
                               total_tasks: int = 1000,
                               args: Tuple = (),
                               kwargs: Dict[str, Any] = None) -> Dict[int, BenchmarkResult]:
        """基准测试asyncio性能"""
        if kwargs is None:
            kwargs = {}
        
        results = {}
        
        for concurrency in concurrency_levels:
            try:
                start_time = time.perf_counter()
                
                # 创建信号量限制并发数
                semaphore = asyncio.Semaphore(concurrency)
                
                async def limited_func():
                    async with semaphore:
                        return await async_func(*args, **kwargs)
                
                # 创建所有任务
                tasks = [limited_func() for _ in range(total_tasks)]
                
                # 等待所有任务完成
                await asyncio.gather(*tasks)
                
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                
                results[concurrency] = BenchmarkResult(
                    name=f"asyncio_{concurrency}_concurrent",
                    execution_time=execution_time,
                    iterations=total_tasks,
                    success=True,
                    metadata={'concurrency': concurrency, 'total_tasks': total_tasks}
                )
                
            except Exception as e:
                results[concurrency] = BenchmarkResult(
                    name=f"asyncio_{concurrency}_concurrent",
                    execution_time=0.0,
                    iterations=total_tasks,
                    success=False,
                    error=str(e),
                    metadata={'concurrency': concurrency, 'total_tasks': total_tasks}
                )
        
        return results

class AlgorithmBenchmark:
    """算法性能基准测试"""
    
    def __init__(self, runner: BenchmarkRunner = None):
        self.runner = runner or BenchmarkRunner()
    
    def benchmark_complexity(self,
                           func: Callable,
                           data_generator: Callable[[int], Any],
                           sizes: List[int],
                           name: str = "algorithm") -> Dict[int, BenchmarkResult]:
        """测试算法复杂度"""
        results = {}
        
        for size in sizes:
            try:
                # 生成测试数据
                test_data = data_generator(size)
                
                # 运行基准测试
                result = self.runner.run_single(
                    func=func,
                    name=f"{name}_size_{size}",
                    args=(test_data,),
                    iterations=max(1, 100 // (size // 100 + 1))  # 大数据集减少迭代次数
                )
                
                result.metadata['data_size'] = size
                results[size] = result
                
            except Exception as e:
                results[size] = BenchmarkResult(
                    name=f"{name}_size_{size}",
                    execution_time=0.0,
                    iterations=1,
                    success=False,
                    error=str(e),
                    metadata={'data_size': size}
                )
        
        return results
    
    def compare_sorting_algorithms(self, sizes: List[int] = None) -> Dict[str, Dict[int, BenchmarkResult]]:
        """比较排序算法性能"""
        if sizes is None:
            sizes = [100, 1000, 5000, 10000]
        
        # 排序算法实现
        def bubble_sort(arr):
            arr = arr.copy()
            n = len(arr)
            for i in range(n):
                for j in range(0, n - i - 1):
                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
            return arr
        
        def quick_sort(arr):
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if x < pivot]
            middle = [x for x in arr if x == pivot]
            right = [x for x in arr if x > pivot]
            return quick_sort(left) + middle + quick_sort(right)
        
        def merge_sort(arr):
            if len(arr) <= 1:
                return arr
            
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            
            return merge(left, right)
        
        def merge(left, right):
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        # 数据生成器
        import random
        def generate_random_list(size):
            return [random.randint(1, 1000) for _ in range(size)]
        
        algorithms = {
            'bubble_sort': bubble_sort,
            'quick_sort': quick_sort,
            'merge_sort': merge_sort,
            'python_sorted': sorted
        }
        
        results = {}
        for name, algorithm in algorithms.items():
            results[name] = self.benchmark_complexity(
                func=algorithm,
                data_generator=generate_random_list,
                sizes=sizes,
                name=name
            )
        
        return results

class BenchmarkSuite:
    """基准测试套件"""
    
    def __init__(self):
        self.runner = BenchmarkRunner()
        self.concurrency_benchmark = ConcurrencyBenchmark(self.runner)
        self.algorithm_benchmark = AlgorithmBenchmark(self.runner)
        self.results_history = []
    
    def run_python_features_benchmark(self) -> Dict[str, BenchmarkResult]:
        """运行Python特性基准测试"""
        results = {}
        
        # 列表推导式 vs 循环
        def list_comprehension():
            return [x ** 2 for x in range(1000)]
        
        def for_loop():
            result = []
            for x in range(1000):
                result.append(x ** 2)
            return result
        
        comparison = self.runner.run_comparison({
            'list_comprehension': list_comprehension,
            'for_loop': for_loop
        })
        results.update({r.name: r for r in comparison.results})
        
        # 字典推导式 vs 循环
        def dict_comprehension():
            return {x: x ** 2 for x in range(1000)}
        
        def dict_loop():
            result = {}
            for x in range(1000):
                result[x] = x ** 2
            return result
        
        comparison = self.runner.run_comparison({
            'dict_comprehension': dict_comprehension,
            'dict_loop': dict_loop
        })
        results.update({r.name: r for r in comparison.results})
        
        # 生成器 vs 列表
        def generator_sum():
            return sum(x ** 2 for x in range(10000))
        
        def list_sum():
            return sum([x ** 2 for x in range(10000)])
        
        comparison = self.runner.run_comparison({
            'generator_sum': generator_sum,
            'list_sum': list_sum
        })
        results.update({r.name: r for r in comparison.results})
        
        return results
    
    def run_data_structure_benchmark(self) -> Dict[str, BenchmarkResult]:
        """运行数据结构基准测试"""
        results = {}
        
        # 列表 vs 元组
        test_data = list(range(10000))
        
        def list_iteration():
            total = 0
            for x in test_data:
                total += x
            return total
        
        test_tuple = tuple(test_data)
        
        def tuple_iteration():
            total = 0
            for x in test_tuple:
                total += x
            return total
        
        comparison = self.runner.run_comparison({
            'list_iteration': list_iteration,
            'tuple_iteration': tuple_iteration
        })
        results.update({r.name: r for r in comparison.results})
        
        # 集合操作
        set1 = set(range(1000))
        set2 = set(range(500, 1500))
        
        def set_intersection():
            return set1 & set2
        
        def list_intersection():
            return list(set(test_data[:1000]) & set(test_data[500:1500]))
        
        comparison = self.runner.run_comparison({
            'set_intersection': set_intersection,
            'list_intersection': list_intersection
        })
        results.update({r.name: r for r in comparison.results})
        
        return results
    
    def generate_report(self, results: Dict[str, BenchmarkResult]) -> str:
        """生成基准测试报告"""
        report = ["基准测试报告", "=" * 50, ""]
        
        successful_results = {k: v for k, v in results.items() if v.success}
        failed_results = {k: v for k, v in results.items() if not v.success}
        
        if successful_results:
            report.append("成功的测试:")
            report.append("-" * 20)
            
            # 按执行时间排序
            sorted_results = sorted(
                successful_results.items(),
                key=lambda x: x[1].execution_time
            )
            
            for name, result in sorted_results:
                report.append(f"测试名称: {name}")
                report.append(f"  执行时间: {result.execution_time:.6f}秒")
                report.append(f"  迭代次数: {result.iterations}")
                report.append(f"  平均时间: {result.avg_time_per_iteration:.9f}秒/次")
                report.append(f"  操作/秒: {result.operations_per_second:.2f}")
                if result.memory_usage:
                    report.append(f"  内存使用: {result.memory_usage:.2f}MB")
                report.append("")
        
        if failed_results:
            report.append("失败的测试:")
            report.append("-" * 20)
            
            for name, result in failed_results.items():
                report.append(f"测试名称: {name}")
                report.append(f"  错误: {result.error}")
                report.append("")
        
        return "\\n".join(report)

# 使用示例
def demonstrate_benchmarks():
    """演示基准测试功能"""
    print("=== 基准测试示例 ===\\n")
    
    # 创建测试套件
    suite = BenchmarkSuite()
    
    # 运行Python特性基准测试
    print("1. Python特性基准测试:")
    python_results = suite.run_python_features_benchmark()
    
    fastest = min(python_results.values(), key=lambda r: r.execution_time if r.success else float('inf'))
    print(f"最快的测试: {fastest.name} ({fastest.execution_time:.6f}秒)")
    
    # 运行数据结构基准测试
    print("\\n2. 数据结构基准测试:")
    data_results = suite.run_data_structure_benchmark()
    
    # 算法复杂度测试
    print("\\n3. 排序算法比较:")
    sorting_results = suite.algorithm_benchmark.compare_sorting_algorithms([100, 1000])
    
    for algorithm_name, size_results in sorting_results.items():
        for size, result in size_results.items():
            if result.success:
                print(f"{algorithm_name} (size {size}): {result.execution_time:.6f}秒")

if __name__ == "__main__":
    demonstrate_benchmarks()