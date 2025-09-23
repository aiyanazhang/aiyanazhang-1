"""
算法优化示例

展示不同算法和数据结构的性能对比和优化技术。
"""

import time
import random
from typing import List, Dict, Any, Callable
from collections import deque, defaultdict
import bisect

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel


class AlgorithmOptimizer:
    """算法优化器"""
    
    @staticmethod
    def time_algorithm(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """测量算法执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        return {
            "result": result,
            "execution_time": execution_time,
            "algorithm": func.__name__
        }
    
    @staticmethod
    def compare_algorithms(algorithms: List[Callable], test_data: Any) -> Dict[str, Any]:
        """比较多个算法的性能"""
        results = {}
        
        for algo in algorithms:
            result = AlgorithmOptimizer.time_algorithm(algo, test_data)
            results[algo.__name__] = result
        
        # 找出最快的算法
        fastest = min(results.keys(), key=lambda x: results[x]["execution_time"])
        
        return {
            "results": results,
            "fastest": fastest,
            "comparison": {
                name: {
                    "speedup": results[fastest]["execution_time"] / result["execution_time"],
                    "time": result["execution_time"]
                }
                for name, result in results.items()
            }
        }


class SortingAlgorithms:
    """排序算法实现"""
    
    @staticmethod
    def bubble_sort(arr: List[int]) -> List[int]:
        """冒泡排序"""
        arr = arr.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    @staticmethod
    def quick_sort(arr: List[int]) -> List[int]:
        """快速排序"""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return SortingAlgorithms.quick_sort(left) + middle + SortingAlgorithms.quick_sort(right)
    
    @staticmethod
    def merge_sort(arr: List[int]) -> List[int]:
        """归并排序"""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = SortingAlgorithms.merge_sort(arr[:mid])
        right = SortingAlgorithms.merge_sort(arr[mid:])
        
        return SortingAlgorithms._merge(left, right)
    
    @staticmethod
    def _merge(left: List[int], right: List[int]) -> List[int]:
        """归并两个有序数组"""
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
    
    @staticmethod
    def python_sort(arr: List[int]) -> List[int]:
        """Python内置排序"""
        return sorted(arr)


class SearchAlgorithms:
    """搜索算法实现"""
    
    @staticmethod
    def linear_search(arr: List[int], target: int) -> int:
        """线性搜索"""
        for i, value in enumerate(arr):
            if value == target:
                return i
        return -1
    
    @staticmethod
    def binary_search(arr: List[int], target: int) -> int:
        """二分搜索（要求数组已排序）"""
        left, right = 0, len(arr) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    
    @staticmethod
    def bisect_search(arr: List[int], target: int) -> int:
        """使用bisect模块的二分搜索"""
        index = bisect.bisect_left(arr, target)
        if index < len(arr) and arr[index] == target:
            return index
        return -1


class DataStructureComparison:
    """数据结构性能对比"""
    
    @staticmethod
    def list_operations(size: int) -> Dict[str, float]:
        """列表操作性能测试"""
        data = list(range(size))
        
        # 测试追加
        start_time = time.time()
        for i in range(1000):
            data.append(i)
        append_time = time.time() - start_time
        
        # 测试插入
        start_time = time.time()
        for i in range(100):
            data.insert(0, i)
        insert_time = time.time() - start_time
        
        # 测试查找
        start_time = time.time()
        for i in range(1000):
            _ = size // 2 in data
        search_time = time.time() - start_time
        
        return {
            "append_time": append_time,
            "insert_time": insert_time,
            "search_time": search_time
        }
    
    @staticmethod
    def deque_operations(size: int) -> Dict[str, float]:
        """双端队列操作性能测试"""
        data = deque(range(size))
        
        # 测试追加
        start_time = time.time()
        for i in range(1000):
            data.append(i)
        append_time = time.time() - start_time
        
        # 测试左侧插入
        start_time = time.time()
        for i in range(100):
            data.appendleft(i)
        insert_time = time.time() - start_time
        
        # 测试查找
        start_time = time.time()
        for i in range(1000):
            _ = size // 2 in data
        search_time = time.time() - start_time
        
        return {
            "append_time": append_time,
            "insert_time": insert_time,
            "search_time": search_time
        }
    
    @staticmethod
    def set_operations(size: int) -> Dict[str, float]:
        """集合操作性能测试"""
        data = set(range(size))
        
        # 测试添加
        start_time = time.time()
        for i in range(1000):
            data.add(size + i)
        add_time = time.time() - start_time
        
        # 测试查找
        start_time = time.time()
        for i in range(1000):
            _ = size // 2 in data
        search_time = time.time() - start_time
        
        # 测试删除
        start_time = time.time()
        for i in range(100):
            data.discard(i)
        delete_time = time.time() - start_time
        
        return {
            "add_time": add_time,
            "search_time": search_time,
            "delete_time": delete_time
        }


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="algorithm_optimization_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="算法优化对比示例",
    tags=["algorithms", "optimization", "performance", "sorting"]
)
@demo(title="算法优化对比示例")
def algorithm_optimization_example():
    """展示不同算法的性能对比"""
    
    print("算法优化对比示例")
    
    # 生成测试数据
    small_data = [random.randint(1, 1000) for _ in range(100)]
    medium_data = [random.randint(1, 1000) for _ in range(1000)]
    
    print(f"测试数据规模: 小={len(small_data)}, 中={len(medium_data)}")
    
    # 排序算法对比
    print("\n=== 排序算法性能对比 ===")
    
    sorting_algorithms = [
        SortingAlgorithms.bubble_sort,
        SortingAlgorithms.quick_sort,
        SortingAlgorithms.merge_sort,
        SortingAlgorithms.python_sort
    ]
    
    # 小数据集测试
    print(f"\n小数据集 ({len(small_data)} 元素):")
    small_comparison = AlgorithmOptimizer.compare_algorithms(sorting_algorithms, small_data)
    
    for name, data in small_comparison["comparison"].items():
        print(f"  {name}: {data['time']:.6f}s (加速比: {data['speedup']:.1f}x)")
    
    print(f"  最快算法: {small_comparison['fastest']}")
    
    # 中等数据集测试（跳过冒泡排序，太慢了）
    print(f"\n中等数据集 ({len(medium_data)} 元素, 跳过冒泡排序):")
    fast_algorithms = [
        SortingAlgorithms.quick_sort,
        SortingAlgorithms.merge_sort,
        SortingAlgorithms.python_sort
    ]
    
    medium_comparison = AlgorithmOptimizer.compare_algorithms(fast_algorithms, medium_data)
    
    for name, data in medium_comparison["comparison"].items():
        print(f"  {name}: {data['time']:.6f}s (加速比: {data['speedup']:.1f}x)")
    
    print(f"  最快算法: {medium_comparison['fastest']}")
    
    # 搜索算法对比
    print(f"\n=== 搜索算法性能对比 ===")
    
    # 准备有序数据用于二分搜索
    sorted_data = sorted(medium_data)
    target = sorted_data[len(sorted_data) // 2]  # 选择中间的元素作为目标
    
    print(f"搜索目标: {target} (在 {len(sorted_data)} 个有序元素中)")
    
    # 线性搜索
    linear_result = AlgorithmOptimizer.time_algorithm(
        SearchAlgorithms.linear_search, sorted_data, target
    )
    
    # 二分搜索
    binary_result = AlgorithmOptimizer.time_algorithm(
        SearchAlgorithms.binary_search, sorted_data, target
    )
    
    # bisect搜索
    bisect_result = AlgorithmOptimizer.time_algorithm(
        SearchAlgorithms.bisect_search, sorted_data, target
    )
    
    print(f"  线性搜索: {linear_result['execution_time']:.6f}s")
    print(f"  二分搜索: {binary_result['execution_time']:.6f}s")
    print(f"  bisect搜索: {bisect_result['execution_time']:.6f}s")
    
    # 计算加速比
    if linear_result['execution_time'] > 0:
        binary_speedup = linear_result['execution_time'] / binary_result['execution_time']
        bisect_speedup = linear_result['execution_time'] / bisect_result['execution_time']
        
        print(f"  二分搜索加速比: {binary_speedup:.1f}x")
        print(f"  bisect搜索加速比: {bisect_speedup:.1f}x")


@example(
    name="data_structure_comparison_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="数据结构性能对比示例",
    tags=["data-structures", "performance", "comparison", "optimization"]
)
@demo(title="数据结构性能对比示例")
def data_structure_comparison_example():
    """展示不同数据结构的性能对比"""
    
    print("数据结构性能对比示例")
    
    test_size = 10000
    print(f"测试数据规模: {test_size}")
    
    comp = DataStructureComparison()
    
    # 运行性能测试
    print(f"\n运行性能测试...")
    
    list_results = comp.list_operations(test_size)
    deque_results = comp.deque_operations(test_size)
    set_results = comp.set_operations(test_size)
    
    # 显示结果对比
    print(f"\n=== 追加/添加操作对比 ===")
    print(f"  List.append():     {list_results['append_time']:.6f}s")
    print(f"  Deque.append():    {deque_results['append_time']:.6f}s")
    print(f"  Set.add():         {set_results['add_time']:.6f}s")
    
    print(f"\n=== 插入操作对比 ===")
    print(f"  List.insert(0):    {list_results['insert_time']:.6f}s")
    print(f"  Deque.appendleft(): {deque_results['insert_time']:.6f}s")
    print(f"  Set操作无直接对应")
    
    if list_results['insert_time'] > 0:
        deque_speedup = list_results['insert_time'] / deque_results['insert_time']
        print(f"  Deque加速比: {deque_speedup:.1f}x")
    
    print(f"\n=== 查找操作对比 ===")
    print(f"  List 'in' 操作:    {list_results['search_time']:.6f}s")
    print(f"  Deque 'in' 操作:   {deque_results['search_time']:.6f}s")
    print(f"  Set 'in' 操作:     {set_results['search_time']:.6f}s")
    
    if list_results['search_time'] > 0:
        set_speedup = list_results['search_time'] / set_results['search_time']
        print(f"  Set相比List加速比: {set_speedup:.1f}x")
    
    print(f"\n=== 删除操作 ===")
    print(f"  Set.discard():     {set_results['delete_time']:.6f}s")
    
    print(f"\n=== 性能总结 ===")
    print("• List: 适合顺序访问和尾部操作")
    print("• Deque: 适合两端操作，头部插入比List快得多")
    print("• Set: 适合快速查找和去重，查找操作最快")
    print("• 选择数据结构时要考虑主要操作类型")


# 导出的类和函数
__all__ = [
    "AlgorithmOptimizer",
    "SortingAlgorithms",
    "SearchAlgorithms",
    "DataStructureComparison",
    "algorithm_optimization_example",
    "data_structure_comparison_example"
]