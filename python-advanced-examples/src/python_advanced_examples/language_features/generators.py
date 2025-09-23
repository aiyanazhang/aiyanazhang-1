"""
生成器和迭代器进阶

展示高级生成器和迭代器的实现和应用，包括惰性求值、无限序列、协程等。
"""

import itertools
import random
import time
from typing import Iterator, Generator, Iterable, TypeVar, Any, Callable, Optional
from collections.abc import Iterable as AbcIterable

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

T = TypeVar('T')


class InfiniteSequence:
    """无限序列生成器"""
    
    @staticmethod
    def fibonacci() -> Generator[int, None, None]:
        """斐波那契数列生成器"""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    @staticmethod
    def primes() -> Generator[int, None, None]:
        """质数生成器"""
        def is_prime(n: int) -> bool:
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        n = 2
        while True:
            if is_prime(n):
                yield n
            n += 1
    
    @staticmethod
    def geometric_sequence(start: float = 1, ratio: float = 2) -> Generator[float, None, None]:
        """几何级数生成器"""
        current = start
        while True:
            yield current
            current *= ratio


class BatchProcessor:
    """批处理迭代器"""
    
    def __init__(self, iterable: Iterable[T], batch_size: int):
        self.iterable = iterable
        self.batch_size = batch_size
    
    def __iter__(self) -> Iterator[list[T]]:
        """返回批处理迭代器"""
        iterator = iter(self.iterable)
        while True:
            batch = list(itertools.islice(iterator, self.batch_size))
            if not batch:
                break
            yield batch


class LazyEvaluator:
    """惰性求值器"""
    
    def __init__(self, data: Iterable[T]):
        self.data = data
        self._operations: list[Callable] = []
    
    def map(self, func: Callable[[T], Any]) -> 'LazyEvaluator':
        """添加映射操作"""
        new_evaluator = LazyEvaluator(self.data)
        new_evaluator._operations = self._operations + [lambda it: map(func, it)]
        return new_evaluator
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyEvaluator':
        """添加过滤操作"""
        new_evaluator = LazyEvaluator(self.data)
        new_evaluator._operations = self._operations + [lambda it: filter(predicate, it)]
        return new_evaluator
    
    def take(self, n: int) -> 'LazyEvaluator':
        """添加取前n个元素操作"""
        new_evaluator = LazyEvaluator(self.data)
        new_evaluator._operations = self._operations + [lambda it: itertools.islice(it, n)]
        return new_evaluator
    
    def evaluate(self) -> Iterator[Any]:
        """执行惰性求值"""
        result = iter(self.data)
        for operation in self._operations:
            result = operation(result)
        return result
    
    def to_list(self) -> list[Any]:
        """转换为列表"""
        return list(self.evaluate())


def sliding_window(iterable: Iterable[T], window_size: int) -> Generator[tuple[T, ...], None, None]:
    """滑动窗口生成器"""
    it = iter(iterable)
    window = list(itertools.islice(it, window_size))
    
    if len(window) == window_size:
        yield tuple(window)
    
    for item in it:
        window.pop(0)
        window.append(item)
        yield tuple(window)


def chunk_generator(iterable: Iterable[T], chunk_size: int) -> Generator[list[T], None, None]:
    """分块生成器"""
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if not chunk:
            break
        yield chunk


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="infinite_sequences_example",
    category=ExampleCategory.GENERATORS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="无限序列生成器示例",
    tags=["generators", "infinite", "fibonacci", "primes"]
)
@demo(title="无限序列生成器示例")
def infinite_sequences_example():
    """展示无限序列生成器的用法"""
    
    print("斐波那契数列前10项：")
    fib_gen = InfiniteSequence.fibonacci()
    for i, fib_num in enumerate(fib_gen):
        if i >= 10:
            break
        print(f"F({i}) = {fib_num}")
    
    print("\n前10个质数：")
    prime_gen = InfiniteSequence.primes()
    for i, prime in enumerate(prime_gen):
        if i >= 10:
            break
        print(f"Prime {i+1}: {prime}")
    
    print("\n几何级数前8项（首项=1，公比=2）：")
    geo_gen = InfiniteSequence.geometric_sequence(1, 2)
    for i, value in enumerate(geo_gen):
        if i >= 8:
            break
        print(f"a({i}) = {value}")


@example(
    name="batch_processor_example",
    category=ExampleCategory.GENERATORS,
    difficulty=DifficultyLevel.BEGINNER,
    description="批处理迭代器示例",
    tags=["generators", "batch-processing", "iteration"]
)
@demo(title="批处理迭代器示例")
def batch_processor_example():
    """展示批处理迭代器的用法"""
    
    # 创建一个大数据集
    large_dataset = range(1, 26)  # 1到25的数字
    
    print("原始数据:", list(large_dataset))
    print("\n按批大小为5处理：")
    
    batch_processor = BatchProcessor(large_dataset, batch_size=5)
    
    for batch_num, batch in enumerate(batch_processor, 1):
        print(f"批次 {batch_num}: {batch}")
        # 模拟批处理
        batch_sum = sum(batch)
        print(f"  批次和: {batch_sum}")


@example(
    name="lazy_evaluator_example",
    category=ExampleCategory.GENERATORS,
    difficulty=DifficultyLevel.ADVANCED,
    description="惰性求值器示例",
    tags=["generators", "lazy-evaluation", "functional"]
)
@demo(title="惰性求值器示例")
def lazy_evaluator_example():
    """展示惰性求值器的用法"""
    
    # 创建大数据集
    data = range(1, 1001)  # 1到1000的数字
    print(f"原始数据范围: 1 到 {max(data)}")
    
    # 创建惰性求值链
    result = (LazyEvaluator(data)
              .filter(lambda x: x % 2 == 0)          # 过滤偶数
              .map(lambda x: x ** 2)                  # 平方
              .filter(lambda x: x > 100)              # 大于100
              .take(5))                               # 取前5个
    
    print("\n惰性求值链: 偶数 -> 平方 -> >100 -> 取前5个")
    print("计算结果:", result.to_list())
    
    # 展示惰性特性
    print("\n惰性特性演示:")
    lazy_chain = (LazyEvaluator(range(1, 11))
                  .map(lambda x: print(f"Processing {x}") or x * 2)
                  .take(3))
    
    print("创建惰性链完成（还没有执行任何计算）")
    print("现在开始求值...")
    result_list = lazy_chain.to_list()
    print(f"最终结果: {result_list}")


@example(
    name="sliding_window_example",
    category=ExampleCategory.GENERATORS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="滑动窗口生成器示例",
    tags=["generators", "sliding-window", "data-processing"]
)
@demo(title="滑动窗口生成器示例")
def sliding_window_example():
    """展示滑动窗口生成器的用法"""
    
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    window_size = 3
    
    print(f"原始数据: {data}")
    print(f"窗口大小: {window_size}")
    print("\n滑动窗口:")
    
    for i, window in enumerate(sliding_window(data, window_size)):
        window_sum = sum(window)
        window_avg = window_sum / len(window)
        print(f"窗口 {i+1}: {window} -> 和={window_sum}, 平均={window_avg:.2f}")


@example(
    name="generator_coroutine_example",
    category=ExampleCategory.GENERATORS,
    difficulty=DifficultyLevel.ADVANCED,
    description="生成器协程示例",
    tags=["generators", "coroutines", "communication"]
)
@demo(title="生成器协程示例")
def generator_coroutine_example():
    """展示生成器协程的用法"""
    
    def accumulator():
        """累加器协程"""
        total = 0
        while True:
            value = yield total
            if value is not None:
                total += value
    
    def moving_average(window_size: int):
        """移动平均协程"""
        values = []
        while True:
            value = yield
            if value is not None:
                values.append(value)
                if len(values) > window_size:
                    values.pop(0)
                average = sum(values) / len(values)
                print(f"新值: {value}, 移动平均 (窗口={len(values)}): {average:.2f}")
    
    print("累加器协程示例:")
    acc = accumulator()
    next(acc)  # 启动协程
    
    for i in range(1, 6):
        total = acc.send(i)
        print(f"发送 {i}, 累计总和: {total}")
    
    print("\n移动平均协程示例:")
    ma = moving_average(window_size=3)
    next(ma)  # 启动协程
    
    data_points = [10, 15, 20, 25, 30, 35, 40]
    for point in data_points:
        ma.send(point)


# 导出的类和函数
__all__ = [
    "InfiniteSequence",
    "BatchProcessor",
    "LazyEvaluator",
    "sliding_window",
    "chunk_generator",
    "infinite_sequences_example",
    "batch_processor_example",
    "lazy_evaluator_example", 
    "sliding_window_example",
    "generator_coroutine_example"
]