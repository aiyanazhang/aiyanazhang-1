"""
响应式编程示例

展示响应式编程的核心概念：
- Observable模式
- 事件流处理
- 操作符组合
- 错误处理和恢复
- 背压和流控制
"""

import asyncio
import threading
import time
from typing import (
    Any, Callable, TypeVar, Generic, List, Dict, Optional, 
    Union, Tuple, Iterator, Set
)
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
import logging

T = TypeVar('T')
U = TypeVar('U')

class EventType(Enum):
    """事件类型"""
    NEXT = "next"
    ERROR = "error"
    COMPLETE = "complete"

@dataclass
class Event(Generic[T]):
    """事件数据类"""
    event_type: EventType
    data: Optional[T] = None
    error: Optional[Exception] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class Observer(Generic[T], ABC):
    """观察者抽象基类"""
    
    @abstractmethod
    def on_next(self, value: T):
        """处理下一个值"""
        pass
    
    @abstractmethod
    def on_error(self, error: Exception):
        """处理错误"""
        pass
    
    @abstractmethod
    def on_complete(self):
        """处理完成事件"""
        pass

class SimpleObserver(Observer[T]):
    """简单观察者实现"""
    
    def __init__(self, 
                 on_next: Callable[[T], None] = None,
                 on_error: Callable[[Exception], None] = None,
                 on_complete: Callable[[], None] = None):
        self._on_next = on_next or (lambda x: None)
        self._on_error = on_error or (lambda e: None)
        self._on_complete = on_complete or (lambda: None)
    
    def on_next(self, value: T):
        self._on_next(value)
    
    def on_error(self, error: Exception):
        self._on_error(error)
    
    def on_complete(self):
        self._on_complete()

class Subscription:
    """订阅对象"""
    
    def __init__(self, observer: Observer, observable: 'Observable'):
        self.observer = observer
        self.observable = observable
        self.is_disposed = False
    
    def dispose(self):
        """取消订阅"""
        if not self.is_disposed:
            self.is_disposed = True
            self.observable._remove_observer(self.observer)

class Observable(Generic[T]):
    """可观察对象基类"""
    
    def __init__(self):
        self._observers: Set[Observer[T]] = set()
        self._is_completed = False
        self._error = None
        self._lock = threading.Lock()
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        """订阅观察者"""
        with self._lock:
            if self._is_completed:
                if self._error:
                    observer.on_error(self._error)
                else:
                    observer.on_complete()
                return Subscription(observer, self)
            
            self._observers.add(observer)
            return Subscription(observer, self)
    
    def _remove_observer(self, observer: Observer[T]):
        """移除观察者"""
        with self._lock:
            self._observers.discard(observer)
    
    def _emit_next(self, value: T):
        """发射下一个值"""
        with self._lock:
            if self._is_completed:
                return
            
            observers_copy = self._observers.copy()
        
        for observer in observers_copy:
            try:
                observer.on_next(value)
            except Exception as e:
                logging.error(f"Observer error: {e}")
    
    def _emit_error(self, error: Exception):
        """发射错误"""
        with self._lock:
            if self._is_completed:
                return
            
            self._is_completed = True
            self._error = error
            observers_copy = self._observers.copy()
            self._observers.clear()
        
        for observer in observers_copy:
            try:
                observer.on_error(error)
            except Exception as e:
                logging.error(f"Observer error handling error: {e}")
    
    def _emit_complete(self):
        """发射完成事件"""
        with self._lock:
            if self._is_completed:
                return
            
            self._is_completed = True
            observers_copy = self._observers.copy()
            self._observers.clear()
        
        for observer in observers_copy:
            try:
                observer.on_complete()
            except Exception as e:
                logging.error(f"Observer error handling completion: {e}")
    
    def map(self, transform: Callable[[T], U]) -> 'Observable[U]':
        """映射操作符"""
        return MapObservable(self, transform)
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Observable[T]':
        """过滤操作符"""
        return FilterObservable(self, predicate)
    
    def take(self, count: int) -> 'Observable[T]':
        """取前N个元素"""
        return TakeObservable(self, count)
    
    def skip(self, count: int) -> 'Observable[T]':
        """跳过前N个元素"""
        return SkipObservable(self, count)
    
    def debounce(self, duration: float) -> 'Observable[T]':
        """防抖操作符"""
        return DebounceObservable(self, duration)
    
    def throttle(self, duration: float) -> 'Observable[T]':
        """节流操作符"""
        return ThrottleObservable(self, duration)
    
    def merge(self, other: 'Observable[T]') -> 'Observable[T]':
        """合并操作符"""
        return MergeObservable([self, other])
    
    def zip(self, other: 'Observable[U]') -> 'Observable[Tuple[T, U]]':
        """压缩操作符"""
        return ZipObservable(self, other)

class MapObservable(Observable[U]):
    """映射可观察对象"""
    
    def __init__(self, source: Observable[T], transform: Callable[[T], U]):
        super().__init__()
        self.source = source
        self.transform = transform
        self.subscription = None
    
    def subscribe(self, observer: Observer[U]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if self.subscription is None:
            source_observer = SimpleObserver(
                on_next=lambda value: self._emit_next(self.transform(value)),
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            self.subscription = self.source.subscribe(source_observer)
        
        return subscription

class FilterObservable(Observable[T]):
    """过滤可观察对象"""
    
    def __init__(self, source: Observable[T], predicate: Callable[[T], bool]):
        super().__init__()
        self.source = source
        self.predicate = predicate
        self.subscription = None
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if self.subscription is None:
            def filtered_on_next(value):
                if self.predicate(value):
                    self._emit_next(value)
            
            source_observer = SimpleObserver(
                on_next=filtered_on_next,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            self.subscription = self.source.subscribe(source_observer)
        
        return subscription

class TakeObservable(Observable[T]):
    """取前N个元素的可观察对象"""
    
    def __init__(self, source: Observable[T], count: int):
        super().__init__()
        self.source = source
        self.count = count
        self.taken = 0
        self.subscription = None
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if self.subscription is None:
            def take_on_next(value):
                if self.taken < self.count:
                    self.taken += 1
                    self._emit_next(value)
                    if self.taken >= self.count:
                        self._emit_complete()
            
            source_observer = SimpleObserver(
                on_next=take_on_next,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            self.subscription = self.source.subscribe(source_observer)
        
        return subscription

class SkipObservable(Observable[T]):
    """跳过前N个元素的可观察对象"""
    
    def __init__(self, source: Observable[T], count: int):
        super().__init__()
        self.source = source
        self.count = count
        self.skipped = 0
        self.subscription = None
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if self.subscription is None:
            def skip_on_next(value):
                if self.skipped < self.count:
                    self.skipped += 1
                else:
                    self._emit_next(value)
            
            source_observer = SimpleObserver(
                on_next=skip_on_next,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            self.subscription = self.source.subscribe(source_observer)
        
        return subscription

class DebounceObservable(Observable[T]):
    """防抖可观察对象"""
    
    def __init__(self, source: Observable[T], duration: float):
        super().__init__()
        self.source = source
        self.duration = duration
        self.last_value = None
        self.timer = None
        self.subscription = None
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if self.subscription is None:
            def debounce_on_next(value):
                self.last_value = value
                if self.timer:
                    self.timer.cancel()
                
                self.timer = threading.Timer(
                    self.duration,
                    lambda: self._emit_next(self.last_value)
                )
                self.timer.start()
            
            source_observer = SimpleObserver(
                on_next=debounce_on_next,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            self.subscription = self.source.subscribe(source_observer)
        
        return subscription

class ThrottleObservable(Observable[T]):
    """节流可观察对象"""
    
    def __init__(self, source: Observable[T], duration: float):
        super().__init__()
        self.source = source
        self.duration = duration
        self.last_emit_time = 0
        self.subscription = None
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if self.subscription is None:
            def throttle_on_next(value):
                current_time = time.time()
                if current_time - self.last_emit_time >= self.duration:
                    self.last_emit_time = current_time
                    self._emit_next(value)
            
            source_observer = SimpleObserver(
                on_next=throttle_on_next,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            self.subscription = self.source.subscribe(source_observer)
        
        return subscription

class MergeObservable(Observable[T]):
    """合并可观察对象"""
    
    def __init__(self, sources: List[Observable[T]]):
        super().__init__()
        self.sources = sources
        self.completed_count = 0
        self.subscriptions = []
    
    def subscribe(self, observer: Observer[T]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if not self.subscriptions:
            for source in self.sources:
                def on_complete():
                    self.completed_count += 1
                    if self.completed_count >= len(self.sources):
                        self._emit_complete()
                
                source_observer = SimpleObserver(
                    on_next=self._emit_next,
                    on_error=self._emit_error,
                    on_complete=on_complete
                )
                sub = source.subscribe(source_observer)
                self.subscriptions.append(sub)
        
        return subscription

class ZipObservable(Observable[Tuple[T, U]]):
    """压缩可观察对象"""
    
    def __init__(self, source1: Observable[T], source2: Observable[U]):
        super().__init__()
        self.source1 = source1
        self.source2 = source2
        self.buffer1 = deque()
        self.buffer2 = deque()
        self.subscriptions = []
    
    def subscribe(self, observer: Observer[Tuple[T, U]]) -> Subscription:
        subscription = super().subscribe(observer)
        
        if not self.subscriptions:
            def on_next1(value):
                self.buffer1.append(value)
                self._try_emit()
            
            def on_next2(value):
                self.buffer2.append(value)
                self._try_emit()
            
            observer1 = SimpleObserver(
                on_next=on_next1,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            observer2 = SimpleObserver(
                on_next=on_next2,
                on_error=self._emit_error,
                on_complete=self._emit_complete
            )
            
            self.subscriptions.append(self.source1.subscribe(observer1))
            self.subscriptions.append(self.source2.subscribe(observer2))
        
        return subscription
    
    def _try_emit(self):
        """尝试发射配对的值"""
        while self.buffer1 and self.buffer2:
            value1 = self.buffer1.popleft()
            value2 = self.buffer2.popleft()
            self._emit_next((value1, value2))

class Subject(Observable[T], Observer[T]):
    """主题：既是观察者又是可观察对象"""
    
    def __init__(self):
        super().__init__()
    
    def on_next(self, value: T):
        self._emit_next(value)
    
    def on_error(self, error: Exception):
        self._emit_error(error)
    
    def on_complete(self):
        self._emit_complete()

class EventStream(Observable[T]):
    """事件流"""
    
    def __init__(self):
        super().__init__()
        self.event_queue = deque()
        self.is_processing = False
    
    def emit(self, value: T):
        """手动发射事件"""
        self._emit_next(value)
    
    def emit_async(self, value: T):
        """异步发射事件"""
        threading.Thread(target=lambda: self._emit_next(value)).start()

class ReactiveStream:
    """响应式流处理器"""
    
    @staticmethod
    def from_iterable(iterable: Iterator[T]) -> Observable[T]:
        """从迭代器创建Observable"""
        class IterableObservable(Observable[T]):
            def __init__(self, iterable):
                super().__init__()
                self.iterable = iterable
            
            def subscribe(self, observer: Observer[T]) -> Subscription:
                subscription = super().subscribe(observer)
                
                def emit_items():
                    try:
                        for item in self.iterable:
                            if subscription.is_disposed:
                                break
                            self._emit_next(item)
                        self._emit_complete()
                    except Exception as e:
                        self._emit_error(e)
                
                threading.Thread(target=emit_items).start()
                return subscription
        
        return IterableObservable(iterable)
    
    @staticmethod
    def interval(duration: float) -> Observable[int]:
        """创建定时器Observable"""
        class IntervalObservable(Observable[int]):
            def __init__(self, duration):
                super().__init__()
                self.duration = duration
                self.counter = 0
                self.timer = None
            
            def subscribe(self, observer: Observer[int]) -> Subscription:
                subscription = super().subscribe(observer)
                
                def tick():
                    if not subscription.is_disposed:
                        self._emit_next(self.counter)
                        self.counter += 1
                        self.timer = threading.Timer(self.duration, tick)
                        self.timer.start()
                
                tick()
                return subscription
        
        return IntervalObservable(duration)
    
    @staticmethod
    def timer(delay: float, value: T = None) -> Observable[T]:
        """创建延时Observable"""
        class TimerObservable(Observable[T]):
            def __init__(self, delay, value):
                super().__init__()
                self.delay = delay
                self.value = value
            
            def subscribe(self, observer: Observer[T]) -> Subscription:
                subscription = super().subscribe(observer)
                
                def emit_after_delay():
                    time.sleep(self.delay)
                    if not subscription.is_disposed:
                        self._emit_next(self.value)
                        self._emit_complete()
                
                threading.Thread(target=emit_after_delay).start()
                return subscription
        
        return TimerObservable(delay, value)

# 响应式编程示例
class ReactiveExamples:
    """响应式编程示例"""
    
    @staticmethod
    def basic_observable_example():
        """基础Observable示例"""
        results = []
        
        # 创建Observable
        numbers = ReactiveStream.from_iterable(range(1, 11))
        
        # 链式操作
        processed = (numbers
                    .map(lambda x: x * 2)
                    .filter(lambda x: x > 10)
                    .take(5))
        
        # 订阅
        observer = SimpleObserver(
            on_next=lambda x: results.append(x),
            on_complete=lambda: results.append("COMPLETED")
        )
        
        subscription = processed.subscribe(observer)
        time.sleep(0.1)  # 等待处理完成
        
        return results
    
    @staticmethod
    def subject_example():
        """Subject示例"""
        results = []
        subject = Subject()
        
        # 订阅
        observer = SimpleObserver(on_next=lambda x: results.append(x))
        subscription = subject.subscribe(observer)
        
        # 手动发射数据
        subject.on_next("Hello")
        subject.on_next("World")
        subject.on_complete()
        
        return results
    
    @staticmethod
    def merge_example():
        """合并示例"""
        results = []
        
        # 创建两个Observable
        stream1 = ReactiveStream.from_iterable([1, 3, 5])
        stream2 = ReactiveStream.from_iterable([2, 4, 6])
        
        # 合并
        merged = stream1.merge(stream2)
        
        # 订阅
        observer = SimpleObserver(on_next=lambda x: results.append(x))
        subscription = merged.subscribe(observer)
        
        time.sleep(0.1)  # 等待处理完成
        return sorted(results)  # 排序因为合并顺序不确定
    
    @staticmethod
    def debounce_example():
        """防抖示例"""
        results = []
        event_stream = EventStream()
        
        # 应用防抖
        debounced = event_stream.debounce(0.1)
        
        # 订阅
        observer = SimpleObserver(on_next=lambda x: results.append(x))
        subscription = debounced.subscribe(observer)
        
        # 快速发射多个事件
        event_stream.emit("fast1")
        event_stream.emit("fast2")
        event_stream.emit("fast3")
        
        time.sleep(0.15)  # 等待防抖完成
        return results

# 使用示例
def demonstrate_reactive_programming():
    """演示响应式编程"""
    print("=== 响应式编程示例 ===\n")
    
    # 1. 基础Observable
    print("1. 基础Observable:")
    basic_result = ReactiveExamples.basic_observable_example()
    print(f"处理结果: {basic_result}")
    
    # 2. Subject
    print("\n2. Subject:")
    subject_result = ReactiveExamples.subject_example()
    print(f"Subject结果: {subject_result}")
    
    # 3. 合并
    print("\n3. 流合并:")
    merge_result = ReactiveExamples.merge_example()
    print(f"合并结果: {merge_result}")
    
    # 4. 防抖
    print("\n4. 防抖处理:")
    debounce_result = ReactiveExamples.debounce_example()
    print(f"防抖结果: {debounce_result}")

if __name__ == "__main__":
    demonstrate_reactive_programming()