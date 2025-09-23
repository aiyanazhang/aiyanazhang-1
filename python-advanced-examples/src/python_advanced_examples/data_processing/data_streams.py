"""
数据流处理示例

展示现代数据流处理的高级概念：
- 流式数据处理
- 背压控制
- 窗口操作
- 并行流处理
- 流聚合和状态管理
"""

import asyncio
import threading
import time
from typing import (
    Any, Callable, TypeVar, Generic, Iterator, List, Dict, 
    Optional, Union, Tuple, AsyncIterator
)
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import heapq
from dataclasses import dataclass
from enum import Enum

T = TypeVar('T')
U = TypeVar('U')

class StreamState(Enum):
    """流状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class StreamEvent:
    """流事件数据类"""
    data: Any
    timestamp: float
    event_type: str = "data"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BackpressureStrategy(Enum):
    """背压策略"""
    DROP = "drop"           # 丢弃新数据
    BUFFER = "buffer"       # 缓冲数据
    BLOCK = "block"         # 阻塞生产者
    ERROR = "error"         # 抛出异常

class DataStream(Generic[T]):
    """数据流基础类"""
    
    def __init__(self, 
                 source: Iterator[T] = None,
                 buffer_size: int = 1000,
                 backpressure_strategy: BackpressureStrategy = BackpressureStrategy.BUFFER):
        self._source = source or iter([])
        self._buffer = deque(maxlen=buffer_size if backpressure_strategy == BackpressureStrategy.BUFFER else None)
        self._backpressure_strategy = backpressure_strategy
        self._state = StreamState.CREATED
        self._subscribers = []
        self._error_handlers = []
        self._completion_handlers = []
        self._lock = threading.Lock()
        
    def map(self, transform: Callable[[T], U]) -> 'DataStream[U]':
        """映射转换"""
        def mapped_source():
            for item in self._source:
                yield transform(item)
        
        return DataStream(mapped_source())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'DataStream[T]':
        """过滤操作"""
        def filtered_source():
            for item in self._source:
                if predicate(item):
                    yield item
        
        return DataStream(filtered_source())
    
    def take(self, count: int) -> 'DataStream[T]':
        """取前N个元素"""
        def taken_source():
            taken = 0
            for item in self._source:
                if taken >= count:
                    break
                yield item
                taken += 1
        
        return DataStream(taken_source())
    
    def skip(self, count: int) -> 'DataStream[T]':
        """跳过前N个元素"""
        def skipped_source():
            skipped = 0
            for item in self._source:
                if skipped < count:
                    skipped += 1
                    continue
                yield item
        
        return DataStream(skipped_source())
    
    def batch(self, size: int) -> 'DataStream[List[T]]':
        """批处理"""
        def batched_source():
            batch = []
            for item in self._source:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:  # 处理剩余数据
                yield batch
        
        return DataStream(batched_source())
    
    def subscribe(self, 
                 on_next: Callable[[T], None],
                 on_error: Callable[[Exception], None] = None,
                 on_complete: Callable[[], None] = None):
        """订阅流"""
        self._subscribers.append(on_next)
        if on_error:
            self._error_handlers.append(on_error)
        if on_complete:
            self._completion_handlers.append(on_complete)
    
    def emit(self, item: T):
        """发射数据项"""
        with self._lock:
            if self._state != StreamState.RUNNING:
                return
            
            # 处理背压
            if len(self._buffer) >= self._buffer.maxlen and self._backpressure_strategy == BackpressureStrategy.DROP:
                return  # 丢弃新数据
            elif self._backpressure_strategy == BackpressureStrategy.ERROR and len(self._buffer) >= self._buffer.maxlen:
                raise Exception("Buffer overflow")
            
            self._buffer.append(item)
            
            # 通知订阅者
            for subscriber in self._subscribers:
                try:
                    subscriber(item)
                except Exception as e:
                    for error_handler in self._error_handlers:
                        error_handler(e)
    
    def start(self):
        """启动流处理"""
        self._state = StreamState.RUNNING
        try:
            for item in self._source:
                self.emit(item)
            
            self._state = StreamState.COMPLETED
            for handler in self._completion_handlers:
                handler()
                
        except Exception as e:
            self._state = StreamState.ERROR
            for error_handler in self._error_handlers:
                error_handler(e)
    
    def to_list(self) -> List[T]:
        """收集所有元素到列表"""
        return list(self._source)

class WindowedStream(DataStream[T]):
    """窗口流处理"""
    
    def __init__(self, source: Iterator[T], window_size: int, slide_size: int = None):
        super().__init__(source)
        self._window_size = window_size
        self._slide_size = slide_size or window_size
        self._window_buffer = deque(maxlen=window_size)
    
    def tumbling_window(self) -> 'DataStream[List[T]]':
        """滚动窗口（不重叠）"""
        def windowed_source():
            window = []
            for item in self._source:
                window.append(item)
                if len(window) >= self._window_size:
                    yield window.copy()
                    window.clear()
            if window:  # 处理剩余数据
                yield window
        
        return DataStream(windowed_source())
    
    def sliding_window(self) -> 'DataStream[List[T]]':
        """滑动窗口"""
        def windowed_source():
            window = deque(maxlen=self._window_size)
            count = 0
            
            for item in self._source:
                window.append(item)
                count += 1
                
                if len(window) == self._window_size and count % self._slide_size == 0:
                    yield list(window)
        
        return DataStream(windowed_source())
    
    def time_window(self, duration_seconds: float) -> 'DataStream[List[StreamEvent]]':
        """时间窗口"""
        def time_windowed_source():
            window = []
            window_start = time.time()
            
            for item in self._source:
                current_time = time.time()
                event = StreamEvent(item, current_time)
                
                # 检查是否需要输出窗口
                if current_time - window_start >= duration_seconds:
                    if window:
                        yield window.copy()
                    window.clear()
                    window_start = current_time
                
                window.append(event)
            
            if window:  # 处理剩余数据
                yield window
        
        return DataStream(time_windowed_source())

class ParallelStream(DataStream[T]):
    """并行流处理"""
    
    def __init__(self, source: Iterator[T], num_workers: int = 4):
        super().__init__(source)
        self._num_workers = num_workers
        self._executor = ThreadPoolExecutor(max_workers=num_workers)
    
    def parallel_map(self, transform: Callable[[T], U]) -> 'DataStream[U]':
        """并行映射"""
        def parallel_mapped_source():
            # 将源数据分批
            items = list(self._source)
            chunk_size = max(1, len(items) // self._num_workers)
            chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
            
            # 并行处理
            futures = []
            for chunk in chunks:
                future = self._executor.submit(lambda c: [transform(item) for item in c], chunk)
                futures.append(future)
            
            # 收集结果
            for future in as_completed(futures):
                for result in future.result():
                    yield result
        
        return DataStream(parallel_mapped_source())
    
    def parallel_filter(self, predicate: Callable[[T], bool]) -> 'DataStream[T]':
        """并行过滤"""
        def parallel_filtered_source():
            items = list(self._source)
            chunk_size = max(1, len(items) // self._num_workers)
            chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
            
            futures = []
            for chunk in chunks:
                future = self._executor.submit(
                    lambda c: [item for item in c if predicate(item)], 
                    chunk
                )
                futures.append(future)
            
            for future in as_completed(futures):
                for result in future.result():
                    yield result
        
        return DataStream(parallel_filtered_source())
    
    def __del__(self):
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=True)

class StreamProcessor:
    """流处理器"""
    
    @staticmethod
    def merge(*streams: DataStream) -> DataStream:
        """合并多个流"""
        def merged_source():
            iterators = [iter(stream._source) for stream in streams]
            while iterators:
                for i, iterator in enumerate(iterators[:]):
                    try:
                        yield next(iterator)
                    except StopIteration:
                        iterators.remove(iterator)
        
        return DataStream(merged_source())
    
    @staticmethod
    def zip(*streams: DataStream) -> DataStream[Tuple]:
        """压缩多个流"""
        def zipped_source():
            iterators = [iter(stream._source) for stream in streams]
            while True:
                try:
                    values = [next(iterator) for iterator in iterators]
                    yield tuple(values)
                except StopIteration:
                    break
        
        return DataStream(zipped_source())
    
    @staticmethod
    def reduce(stream: DataStream[T], 
              reducer: Callable[[U, T], U], 
              initial: U = None) -> U:
        """归约操作"""
        result = initial
        for item in stream._source:
            if result is None:
                result = item
            else:
                result = reducer(result, item)
        return result
    
    @staticmethod
    def group_by(stream: DataStream[T], 
                key_func: Callable[[T], Any]) -> Dict[Any, List[T]]:
        """分组操作"""
        groups = defaultdict(list)
        for item in stream._source:
            key = key_func(item)
            groups[key].append(item)
        return dict(groups)

class AsyncDataStream(Generic[T]):
    """异步数据流"""
    
    def __init__(self, source: AsyncIterator[T] = None):
        self._source = source
        self._subscribers = []
        self._state = StreamState.CREATED
    
    async def map(self, transform: Callable[[T], U]) -> 'AsyncDataStream[U]':
        """异步映射"""
        async def async_mapped_source():
            async for item in self._source:
                yield transform(item)
        
        return AsyncDataStream(async_mapped_source())
    
    async def filter(self, predicate: Callable[[T], bool]) -> 'AsyncDataStream[T]':
        """异步过滤"""
        async def async_filtered_source():
            async for item in self._source:
                if predicate(item):
                    yield item
        
        return AsyncDataStream(async_filtered_source())
    
    async def collect(self) -> List[T]:
        """收集所有元素"""
        result = []
        async for item in self._source:
            result.append(item)
        return result
    
    def subscribe(self, on_next: Callable[[T], None]):
        """订阅异步流"""
        self._subscribers.append(on_next)
    
    async def emit(self, item: T):
        """发射数据项"""
        for subscriber in self._subscribers:
            subscriber(item)

# 流处理示例
class StreamExamples:
    """流处理示例"""
    
    @staticmethod
    def basic_stream_example():
        """基础流示例"""
        # 创建数据源
        numbers = range(1, 21)
        stream = DataStream(iter(numbers))
        
        # 链式操作
        result = (stream
                 .filter(lambda x: x % 2 == 0)  # 过滤偶数
                 .map(lambda x: x ** 2)         # 平方
                 .take(5)                       # 取前5个
                 .to_list())
        
        return result
    
    @staticmethod
    def windowed_stream_example():
        """窗口流示例"""
        numbers = range(1, 16)
        windowed = WindowedStream(iter(numbers), window_size=3, slide_size=2)
        
        # 滑动窗口
        sliding_result = windowed.sliding_window().to_list()
        
        # 滚动窗口
        windowed2 = WindowedStream(iter(numbers), window_size=4)
        tumbling_result = windowed2.tumbling_window().to_list()
        
        return {
            'sliding_windows': sliding_result,
            'tumbling_windows': tumbling_result
        }
    
    @staticmethod
    def parallel_stream_example():
        """并行流示例"""
        numbers = range(1, 101)
        parallel = ParallelStream(iter(numbers), num_workers=4)
        
        # 并行计算平方
        squares = parallel.parallel_map(lambda x: x ** 2).to_list()
        
        # 并行过滤
        parallel2 = ParallelStream(iter(numbers), num_workers=4)
        evens = parallel2.parallel_filter(lambda x: x % 2 == 0).to_list()
        
        return {
            'parallel_squares': squares[:10],  # 显示前10个
            'parallel_evens': evens[:10]       # 显示前10个
        }
    
    @staticmethod
    def stream_aggregation_example():
        """流聚合示例"""
        numbers = range(1, 11)
        stream = DataStream(iter(numbers))
        
        # 求和
        total = StreamProcessor.reduce(stream, lambda a, b: a + b, 0)
        
        # 分组
        numbers2 = range(1, 21)
        stream2 = DataStream(iter(numbers2))
        groups = StreamProcessor.group_by(
            stream2, 
            lambda x: "even" if x % 2 == 0 else "odd"
        )
        
        return {
            'sum': total,
            'groups': {k: v[:5] for k, v in groups.items()}  # 限制输出
        }

# 使用示例
def demonstrate_data_streams():
    """演示数据流处理"""
    print("=== 数据流处理示例 ===\n")
    
    # 1. 基础流操作
    print("1. 基础流操作:")
    basic_result = StreamExamples.basic_stream_example()
    print(f"偶数平方前5个: {basic_result}")
    
    # 2. 窗口操作
    print("\n2. 窗口操作:")
    window_result = StreamExamples.windowed_stream_example()
    print(f"滑动窗口: {window_result['sliding_windows']}")
    print(f"滚动窗口: {window_result['tumbling_windows']}")
    
    # 3. 并行处理
    print("\n3. 并行处理:")
    parallel_result = StreamExamples.parallel_stream_example()
    print(f"并行平方: {parallel_result['parallel_squares']}")
    print(f"并行过滤: {parallel_result['parallel_evens']}")
    
    # 4. 流聚合
    print("\n4. 流聚合:")
    agg_result = StreamExamples.stream_aggregation_example()
    print(f"求和: {agg_result['sum']}")
    print(f"分组: {agg_result['groups']}")

if __name__ == "__main__":
    demonstrate_data_streams()