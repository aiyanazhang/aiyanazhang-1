"""
内存优化技术

展示各种Python内存优化技术，包括__slots__、对象池、弱引用等。
"""

import gc
import sys
import time
import weakref
from typing import Any, Dict, List, Optional, Set, Type, TypeVar
from dataclasses import dataclass
import psutil
import os
from collections import defaultdict
import threading

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

T = TypeVar('T')


class MemoryOptimizedClass:
    """内存优化的类示例"""
    
    # 使用__slots__限制实例属性，减少内存占用
    __slots__ = ['_id', '_name', '_value', '_cache']
    
    def __init__(self, id: int, name: str, value: float):
        self._id = id
        self._name = name
        self._value = value
        self._cache = {}
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def value(self) -> float:
        return self._value
    
    def compute_expensive_operation(self, x: float) -> float:
        """昂贵的计算操作（带缓存）"""
        if x not in self._cache:
            # 模拟复杂计算
            time.sleep(0.001)
            self._cache[x] = self._value * x ** 2 + x
        
        return self._cache[x]
    
    def __repr__(self) -> str:
        return f"MemoryOptimizedClass(id={self._id}, name='{self._name}', value={self._value})"


class RegularClass:
    """常规类（用于对比）"""
    
    def __init__(self, id: int, name: str, value: float):
        self.id = id
        self.name = name
        self.value = value
        self.cache = {}
    
    def compute_expensive_operation(self, x: float) -> float:
        """昂贵的计算操作（带缓存）"""
        if x not in self.cache:
            time.sleep(0.001)
            self.cache[x] = self.value * x ** 2 + x
        
        return self.cache[x]
    
    def __repr__(self) -> str:
        return f"RegularClass(id={self.id}, name='{self.name}', value={self.value})"


class ObjectPool:
    """对象池实现"""
    
    def __init__(self, factory: Type[T], max_size: int = 100):
        self.factory = factory
        self.max_size = max_size
        self.pool: List[T] = []
        self.created_count = 0
        self.reused_count = 0
        self.lock = threading.Lock()
    
    def acquire(self, *args, **kwargs) -> T:
        """获取对象"""
        with self.lock:
            if self.pool:
                obj = self.pool.pop()
                self.reused_count += 1
                
                # 重新初始化对象
                if hasattr(obj, 'reinitialize'):
                    obj.reinitialize(*args, **kwargs)
                
                return obj
            else:
                # 创建新对象
                self.created_count += 1
                return self.factory(*args, **kwargs)
    
    def release(self, obj: T) -> None:
        """释放对象"""
        with self.lock:
            if len(self.pool) < self.max_size:
                # 清理对象状态
                if hasattr(obj, 'cleanup'):
                    obj.cleanup()
                
                self.pool.append(obj)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return {
                "pool_size": len(self.pool),
                "max_size": self.max_size,
                "created_count": self.created_count,
                "reused_count": self.reused_count,
                "reuse_rate": self.reused_count / (self.created_count + self.reused_count) if (self.created_count + self.reused_count) > 0 else 0
            }
    
    def clear(self) -> None:
        """清空对象池"""
        with self.lock:
            self.pool.clear()


class PooledObject:
    """可池化的对象"""
    
    def __init__(self, data: str = ""):
        self.data = data
        self.created_at = time.time()
        self.usage_count = 0
    
    def process(self, input_data: str) -> str:
        """处理数据"""
        self.usage_count += 1
        return f"Processed: {input_data} by {self.data}"
    
    def reinitialize(self, data: str = ""):
        """重新初始化"""
        self.data = data
        self.usage_count = 0
    
    def cleanup(self):
        """清理状态"""
        # 清理敏感数据或重置状态
        pass


class WeakReferenceCache:
    """弱引用缓存"""
    
    def __init__(self):
        self._cache: Dict[str, weakref.ref] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "expired": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            obj = self._cache[key]()  # 调用弱引用
            
            if obj is not None:
                self._stats["hits"] += 1
                return obj
            else:
                # 对象已被垃圾回收
                del self._cache[key]
                self._stats["expired"] += 1
        
        self._stats["misses"] += 1
        return None
    
    def put(self, key: str, obj: Any) -> None:
        """存储对象的弱引用"""
        def cleanup_callback(ref):
            # 对象被回收时的清理回调
            if key in self._cache and self._cache[key] is ref:
                del self._cache[key]
        
        self._cache[key] = weakref.ref(obj, cleanup_callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        
        return {
            "cache_size": len(self._cache),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "expired": self._stats["expired"],
            "hit_rate": self._stats["hits"] / total_requests if total_requests > 0 else 0
        }
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._stats = {"hits": 0, "misses": 0, "expired": 0}


class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.snapshots = []
    
    def take_snapshot(self, label: str = "") -> Dict[str, Any]:
        """获取内存快照"""
        gc.collect()  # 强制垃圾回收
        
        memory_info = self.process.memory_info()
        
        snapshot = {
            "label": label,
            "timestamp": time.time(),
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "gc_counts": gc.get_count(),
            "object_count": len(gc.get_objects())
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def compare_snapshots(self, start_label: str, end_label: str) -> Dict[str, Any]:
        """比较两个快照"""
        start_snapshot = next((s for s in self.snapshots if s["label"] == start_label), None)
        end_snapshot = next((s for s in self.snapshots if s["label"] == end_label), None)
        
        if not start_snapshot or not end_snapshot:
            return {"error": "Snapshot not found"}
        
        return {
            "memory_diff_mb": end_snapshot["rss"] - start_snapshot["rss"],
            "object_count_diff": end_snapshot["object_count"] - start_snapshot["object_count"],
            "time_diff": end_snapshot["timestamp"] - start_snapshot["timestamp"],
            "start_memory": start_snapshot["rss"],
            "end_memory": end_snapshot["rss"]
        }
    
    def get_memory_report(self) -> Dict[str, Any]:
        """获取内存报告"""
        if not self.snapshots:
            return {"error": "No snapshots available"}
        
        current_memory = self.snapshots[-1]["rss"]
        peak_memory = max(s["rss"] for s in self.snapshots)
        min_memory = min(s["rss"] for s in self.snapshots)
        
        return {
            "current_memory_mb": current_memory,
            "peak_memory_mb": peak_memory,
            "min_memory_mb": min_memory,
            "memory_range_mb": peak_memory - min_memory,
            "snapshot_count": len(self.snapshots)
        }


def measure_memory_usage(func, *args, **kwargs) -> Dict[str, Any]:
    """测量函数的内存使用"""
    # 获取开始时的内存
    process = psutil.Process()
    gc.collect()
    start_memory = process.memory_info().rss / 1024 / 1024
    
    # 执行函数
    start_time = time.time()
    result = func(*args, **kwargs)
    execution_time = time.time() - start_time
    
    # 获取结束时的内存
    gc.collect()
    end_memory = process.memory_info().rss / 1024 / 1024
    
    return {
        "result": result,
        "execution_time": execution_time,
        "start_memory_mb": start_memory,
        "end_memory_mb": end_memory,
        "memory_diff_mb": end_memory - start_memory
    }


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="memory_optimization_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="内存优化技术对比示例",
    tags=["memory", "optimization", "slots", "performance"]
)
@demo(title="内存优化技术对比示例")
def memory_optimization_example():
    """展示内存优化技术的效果"""
    
    def create_regular_objects(count: int) -> List[RegularClass]:
        """创建常规对象"""
        return [RegularClass(i, f"obj_{i}", i * 1.5) for i in range(count)]
    
    def create_optimized_objects(count: int) -> List[MemoryOptimizedClass]:
        """创建优化对象"""
        return [MemoryOptimizedClass(i, f"obj_{i}", i * 1.5) for i in range(count)]
    
    print("内存优化技术对比")
    
    profiler = MemoryProfiler()
    object_count = 10000
    
    print(f"\n创建 {object_count} 个对象进行测试...")
    
    # 测试常规类
    print("\n1. 常规类内存使用:")
    profiler.take_snapshot("before_regular")
    
    regular_result = measure_memory_usage(create_regular_objects, object_count)
    
    profiler.take_snapshot("after_regular")
    
    print(f"   执行时间: {regular_result['execution_time']:.3f}s")
    print(f"   内存使用: {regular_result['memory_diff_mb']:.2f}MB")
    
    # 清理
    del regular_result
    gc.collect()
    
    # 测试优化类
    print("\n2. 优化类内存使用 (使用__slots__):")
    profiler.take_snapshot("before_optimized")
    
    optimized_result = measure_memory_usage(create_optimized_objects, object_count)
    
    profiler.take_snapshot("after_optimized")
    
    print(f"   执行时间: {optimized_result['execution_time']:.3f}s")
    print(f"   内存使用: {optimized_result['memory_diff_mb']:.2f}MB")
    
    # 比较结果
    regular_memory = profiler.compare_snapshots("before_regular", "after_regular")["memory_diff_mb"]
    optimized_memory = profiler.compare_snapshots("before_optimized", "after_optimized")["memory_diff_mb"]
    
    print(f"\n内存优化效果:")
    print(f"   常规类内存使用: {regular_memory:.2f}MB")
    print(f"   优化类内存使用: {optimized_memory:.2f}MB")
    
    if regular_memory > 0:
        memory_savings = (regular_memory - optimized_memory) / regular_memory * 100
        print(f"   内存节省: {memory_savings:.1f}%")
    
    # 单个对象大小比较
    print(f"\n单个对象内存占用:")
    regular_obj = RegularClass(1, "test", 1.0)
    optimized_obj = MemoryOptimizedClass(1, "test", 1.0)
    
    regular_size = sys.getsizeof(regular_obj) + sys.getsizeof(regular_obj.__dict__)
    optimized_size = sys.getsizeof(optimized_obj)
    
    print(f"   常规对象: {regular_size} bytes")
    print(f"   优化对象: {optimized_size} bytes")
    print(f"   节省: {(regular_size - optimized_size) / regular_size * 100:.1f}%")


@example(
    name="object_pool_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="对象池模式示例",
    tags=["object-pool", "reuse", "performance", "memory"]
)
@demo(title="对象池模式示例")
def object_pool_example():
    """展示对象池的使用"""
    
    print("对象池模式示例")
    
    # 创建对象池
    pool = ObjectPool(PooledObject, max_size=5)
    
    print(f"对象池最大容量: {pool.max_size}")
    
    # 模拟对象使用
    print("\n模拟对象获取和释放:")
    
    objects = []
    
    # 获取多个对象
    for i in range(8):
        obj = pool.acquire(f"data_{i}")
        result = obj.process(f"input_{i}")
        objects.append(obj)
        
        stats = pool.get_statistics()
        print(f"获取对象 {i}: {result}")
        print(f"   池统计: 创建={stats['created_count']}, 复用={stats['reused_count']}, "
              f"复用率={stats['reuse_rate']:.1%}")
    
    print(f"\n释放对象:")
    
    # 释放对象
    for i, obj in enumerate(objects):
        pool.release(obj)
        stats = pool.get_statistics()
        print(f"释放对象 {i}: 池大小={stats['pool_size']}")
    
    print(f"\n再次获取对象 (应该复用池中的对象):")
    
    # 再次获取对象，应该复用
    for i in range(3):
        obj = pool.acquire(f"reused_data_{i}")
        result = obj.process(f"reused_input_{i}")
        pool.release(obj)
        
        stats = pool.get_statistics()
        print(f"复用对象 {i}: {result}")
        print(f"   使用次数: {obj.usage_count}")
    
    # 最终统计
    final_stats = pool.get_statistics()
    print(f"\n最终统计:")
    print(f"   总创建对象: {final_stats['created_count']}")
    print(f"   总复用次数: {final_stats['reused_count']}")
    print(f"   复用率: {final_stats['reuse_rate']:.1%}")
    print(f"   池中剩余: {final_stats['pool_size']}")


@example(
    name="weak_reference_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.ADVANCED,
    description="弱引用缓存示例",
    tags=["weak-reference", "cache", "gc", "memory-management"]
)
@demo(title="弱引用缓存示例")
def weak_reference_example():
    """展示弱引用缓存的使用"""
    
    class CacheableObject:
        """可缓存的对象"""
        def __init__(self, id: int, data: str):
            self.id = id
            self.data = data
            print(f"创建对象: CacheableObject(id={id})")
        
        def __del__(self):
            print(f"销毁对象: CacheableObject(id={self.id})")
    
    print("弱引用缓存示例")
    
    cache = WeakReferenceCache()
    
    print("\n1. 创建对象并存储到弱引用缓存:")
    
    # 创建对象并缓存
    obj1 = CacheableObject(1, "data1")
    obj2 = CacheableObject(2, "data2")
    obj3 = CacheableObject(3, "data3")
    
    cache.put("obj1", obj1)
    cache.put("obj2", obj2)
    cache.put("obj3", obj3)
    
    stats = cache.get_statistics()
    print(f"缓存统计: {stats}")
    
    print("\n2. 从缓存获取对象:")
    
    # 从缓存获取
    cached_obj1 = cache.get("obj1")
    cached_obj2 = cache.get("obj2")
    
    print(f"获取 obj1: {cached_obj1.data if cached_obj1 else 'None'}")
    print(f"获取 obj2: {cached_obj2.data if cached_obj2 else 'None'}")
    
    stats = cache.get_statistics()
    print(f"缓存统计: {stats}")
    
    print("\n3. 删除强引用，触发垃圾回收:")
    
    # 删除部分强引用
    del obj1
    del obj2
    
    # 强制垃圾回收
    gc.collect()
    time.sleep(0.1)  # 给回调时间执行
    
    print("\n4. 再次尝试从缓存获取:")
    
    cached_obj1_after_gc = cache.get("obj1")
    cached_obj2_after_gc = cache.get("obj2")
    cached_obj3_after_gc = cache.get("obj3")
    
    print(f"获取 obj1 (GC后): {cached_obj1_after_gc.data if cached_obj1_after_gc else 'None'}")
    print(f"获取 obj2 (GC后): {cached_obj2_after_gc.data if cached_obj2_after_gc else 'None'}")
    print(f"获取 obj3 (GC后): {cached_obj3_after_gc.data if cached_obj3_after_gc else 'None'}")
    
    final_stats = cache.get_statistics()
    print(f"\n最终缓存统计: {final_stats}")
    
    print("\n弱引用缓存的优势:")
    print("- 自动清理不再使用的对象")
    print("- 避免内存泄漏")
    print("- 减少手动缓存管理")


@example(
    name="memory_profiling_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.ADVANCED,
    description="内存分析和监控示例",
    tags=["memory-profiling", "monitoring", "gc", "analysis"]
)
@demo(title="内存分析和监控示例")
def memory_profiling_example():
    """展示内存分析和监控"""
    
    def memory_intensive_operation(size: int) -> List[List[int]]:
        """内存密集型操作"""
        data = []
        for i in range(size):
            # 创建嵌套列表
            inner_list = list(range(i, i + 100))
            data.append(inner_list)
        return data
    
    print("内存分析和监控示例")
    
    profiler = MemoryProfiler()
    
    # 基线快照
    profiler.take_snapshot("baseline")
    print("已获取基线内存快照")
    
    # 第一次内存分配
    print("\n执行第一次内存分配...")
    profiler.take_snapshot("before_allocation_1")
    
    data1 = memory_intensive_operation(1000)
    
    profiler.take_snapshot("after_allocation_1")
    
    allocation1_diff = profiler.compare_snapshots("before_allocation_1", "after_allocation_1")
    print(f"第一次分配内存变化: {allocation1_diff['memory_diff_mb']:.2f}MB")
    print(f"对象数量变化: {allocation1_diff['object_count_diff']}")
    
    # 第二次内存分配
    print("\n执行第二次内存分配...")
    profiler.take_snapshot("before_allocation_2")
    
    data2 = memory_intensive_operation(1500)
    
    profiler.take_snapshot("after_allocation_2")
    
    allocation2_diff = profiler.compare_snapshots("before_allocation_2", "after_allocation_2")
    print(f"第二次分配内存变化: {allocation2_diff['memory_diff_mb']:.2f}MB")
    print(f"对象数量变化: {allocation2_diff['object_count_diff']}")
    
    # 释放内存
    print("\n释放第一部分数据...")
    profiler.take_snapshot("before_cleanup")
    
    del data1
    gc.collect()
    
    profiler.take_snapshot("after_cleanup")
    
    cleanup_diff = profiler.compare_snapshots("before_cleanup", "after_cleanup")
    print(f"清理后内存变化: {cleanup_diff['memory_diff_mb']:.2f}MB")
    print(f"对象数量变化: {cleanup_diff['object_count_diff']}")
    
    # 生成内存报告
    print("\n内存分析报告:")
    report = profiler.get_memory_report()
    
    print(f"   当前内存使用: {report['current_memory_mb']:.2f}MB")
    print(f"   峰值内存使用: {report['peak_memory_mb']:.2f}MB")
    print(f"   最小内存使用: {report['min_memory_mb']:.2f}MB")
    print(f"   内存使用范围: {report['memory_range_mb']:.2f}MB")
    print(f"   快照数量: {report['snapshot_count']}")
    
    # 总体变化
    total_diff = profiler.compare_snapshots("baseline", "after_cleanup")
    print(f"\n相比基线的总体变化:")
    print(f"   内存变化: {total_diff['memory_diff_mb']:.2f}MB")
    print(f"   对象数量变化: {total_diff['object_count_diff']}")


# 导出的类和函数
__all__ = [
    "MemoryOptimizedClass",
    "RegularClass",
    "ObjectPool",
    "PooledObject",
    "WeakReferenceCache",
    "MemoryProfiler",
    "measure_memory_usage",
    "memory_optimization_example",
    "object_pool_example", 
    "weak_reference_example",
    "memory_profiling_example"
]