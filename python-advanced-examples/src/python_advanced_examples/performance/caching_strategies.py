"""
缓存策略实现

展示各种缓存策略的实现和性能对比，包括LRU、LFU、TTL等。
"""

import time
import threading
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List, Optional, Tuple, Generic, TypeVar
from dataclasses import dataclass
import heapq
import random

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        return 1.0 - self.hit_rate


@dataclass
class CacheItem:
    """缓存项"""
    key: Any
    value: Any
    access_count: int = 0
    last_access: float = 0.0
    created_at: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.last_access == 0.0:
            self.last_access = self.created_at


class LRUCache(Generic[K, V]):
    """LRU (Least Recently Used) 缓存实现"""
    
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self.cache: OrderedDict[K, V] = OrderedDict()
        self.stats = CacheStats(max_size=max_size)
        self.lock = threading.RLock()
    
    def get(self, key: K) -> Optional[V]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                # 移动到末尾（最近使用）
                value = self.cache.pop(key)
                self.cache[key] = value
                self.stats.hits += 1
                return value
            else:
                self.stats.misses += 1
                return None
    
    def put(self, key: K, value: V) -> None:
        """存储缓存值"""
        with self.lock:
            if key in self.cache:
                # 更新现有值并移动到末尾
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # 删除最少使用的项（第一个）
                self.cache.popitem(last=False)
                self.stats.evictions += 1
            
            self.cache[key] = value
            self.stats.size = len(self.cache)
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.stats.size = 0
    
    def get_stats(self) -> CacheStats:
        """获取统计信息"""
        with self.lock:
            self.stats.size = len(self.cache)
            return self.stats


class LFUCache(Generic[K, V]):
    """LFU (Least Frequently Used) 缓存实现"""
    
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self.cache: Dict[K, V] = {}
        self.frequencies: Dict[K, int] = {}
        self.freq_to_keys: defaultdict[int, set] = defaultdict(set)
        self.min_freq = 0
        self.stats = CacheStats(max_size=max_size)
        self.lock = threading.RLock()
    
    def _update_freq(self, key: K) -> None:
        """更新键的频率"""
        freq = self.frequencies[key]
        self.freq_to_keys[freq].remove(key)
        
        # 如果这是最小频率且没有其他键有这个频率，更新最小频率
        if freq == self.min_freq and len(self.freq_to_keys[freq]) == 0:
            self.min_freq += 1
        
        # 增加频率
        self.frequencies[key] = freq + 1
        self.freq_to_keys[freq + 1].add(key)
    
    def get(self, key: K) -> Optional[V]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                self._update_freq(key)
                self.stats.hits += 1
                return self.cache[key]
            else:
                self.stats.misses += 1
                return None
    
    def put(self, key: K, value: V) -> None:
        """存储缓存值"""
        with self.lock:
            if self.max_size <= 0:
                return
            
            if key in self.cache:
                # 更新现有值
                self.cache[key] = value
                self._update_freq(key)
                return
            
            # 如果缓存已满，删除最少使用的键
            if len(self.cache) >= self.max_size:
                # 找到最小频率的键并删除一个
                lfu_key = self.freq_to_keys[self.min_freq].pop()
                del self.cache[lfu_key]
                del self.frequencies[lfu_key]
                self.stats.evictions += 1
            
            # 添加新键
            self.cache[key] = value
            self.frequencies[key] = 1
            self.freq_to_keys[1].add(key)
            self.min_freq = 1
            self.stats.size = len(self.cache)
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.frequencies.clear()
            self.freq_to_keys.clear()
            self.min_freq = 0
            self.stats.size = 0
    
    def get_stats(self) -> CacheStats:
        """获取统计信息"""
        with self.lock:
            self.stats.size = len(self.cache)
            return self.stats


class TTLCache(Generic[K, V]):
    """TTL (Time To Live) 缓存实现"""
    
    def __init__(self, max_size: int = 128, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[K, CacheItem] = {}
        self.stats = CacheStats(max_size=max_size)
        self.lock = threading.RLock()
    
    def _is_expired(self, item: CacheItem) -> bool:
        """检查项是否过期"""
        return time.time() - item.created_at > self.ttl
    
    def _cleanup_expired(self) -> None:
        """清理过期项"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if current_time - item.created_at > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats.evictions += 1
    
    def get(self, key: K) -> Optional[V]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                
                if self._is_expired(item):
                    del self.cache[key]
                    self.stats.misses += 1
                    self.stats.evictions += 1
                    return None
                
                item.last_access = time.time()
                item.access_count += 1
                self.stats.hits += 1
                return item.value
            else:
                self.stats.misses += 1
                return None
    
    def put(self, key: K, value: V) -> None:
        """存储缓存值"""
        with self.lock:
            # 清理过期项
            self._cleanup_expired()
            
            if key in self.cache:
                # 更新现有项
                self.cache[key].value = value
                self.cache[key].created_at = time.time()
                self.cache[key].last_access = time.time()
            else:
                # 如果缓存已满，删除最旧的项
                if len(self.cache) >= self.max_size:
                    oldest_key = min(
                        self.cache.keys(),
                        key=lambda k: self.cache[k].created_at
                    )
                    del self.cache[oldest_key]
                    self.stats.evictions += 1
                
                # 添加新项
                self.cache[key] = CacheItem(key=key, value=value)
            
            self.stats.size = len(self.cache)
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.stats.size = 0
    
    def get_stats(self) -> CacheStats:
        """获取统计信息"""
        with self.lock:
            self.stats.size = len(self.cache)
            return self.stats


class TieredCache:
    """多层缓存"""
    
    def __init__(self, l1_size: int = 64, l2_size: int = 256, ttl: float = 300.0):
        self.l1_cache = LRUCache(l1_size)  # 一级缓存：快速LRU
        self.l2_cache = TTLCache(l2_size, ttl)  # 二级缓存：TTL缓存
        self.stats = CacheStats(max_size=l1_size + l2_size)
        self.lock = threading.RLock()
    
    def get(self, key: K) -> Optional[V]:
        """获取缓存值"""
        with self.lock:
            # 先查L1缓存
            value = self.l1_cache.get(key)
            if value is not None:
                self.stats.hits += 1
                return value
            
            # 再查L2缓存
            value = self.l2_cache.get(key)
            if value is not None:
                # 提升到L1缓存
                self.l1_cache.put(key, value)
                self.stats.hits += 1
                return value
            
            self.stats.misses += 1
            return None
    
    def put(self, key: K, value: V) -> None:
        """存储缓存值"""
        with self.lock:
            # 存储到L1缓存
            self.l1_cache.put(key, value)
            # 也存储到L2缓存（作为备份）
            self.l2_cache.put(key, value)
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.l1_cache.clear()
            self.l2_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            l1_stats = self.l1_cache.get_stats()
            l2_stats = self.l2_cache.get_stats()
            
            return {
                "overall": {
                    "hits": self.stats.hits,
                    "misses": self.stats.misses,
                    "hit_rate": self.stats.hit_rate
                },
                "l1_cache": {
                    "size": l1_stats.size,
                    "max_size": l1_stats.max_size,
                    "hits": l1_stats.hits,
                    "misses": l1_stats.misses,
                    "hit_rate": l1_stats.hit_rate
                },
                "l2_cache": {
                    "size": l2_stats.size,
                    "max_size": l2_stats.max_size,
                    "hits": l2_stats.hits,
                    "misses": l2_stats.misses,
                    "hit_rate": l2_stats.hit_rate
                }
            }


class CachePerformanceComparison:
    """缓存性能对比测试"""
    
    def __init__(self):
        self.caches = {
            "LRU": LRUCache(100),
            "LFU": LFUCache(100),
            "TTL": TTLCache(100, ttl=60.0),
            "Tiered": TieredCache(50, 50, ttl=60.0)
        }
        self.results = {}
    
    def run_workload(self, cache_name: str, workload: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """运行工作负载"""
        cache = self.caches[cache_name]
        start_time = time.time()
        
        for operation, key in workload:
            if operation == "get":
                cache.get(key)
            elif operation == "put":
                cache.put(key, f"value_{key}")
        
        execution_time = time.time() - start_time
        
        if cache_name == "Tiered":
            stats = cache.get_stats()["overall"]
        else:
            stats = cache.get_stats()
        
        return {
            "execution_time": execution_time,
            "hit_rate": stats.hit_rate if hasattr(stats, 'hit_rate') else stats["hit_rate"],
            "operations_per_second": len(workload) / execution_time
        }
    
    def generate_workload(self, size: int, pattern: str = "random") -> List[Tuple[str, Any]]:
        """生成工作负载"""
        workload = []
        
        if pattern == "random":
            # 随机访问模式
            for _ in range(size):
                if random.random() < 0.7:  # 70% 读操作
                    key = random.randint(1, 200)
                    workload.append(("get", key))
                else:  # 30% 写操作
                    key = random.randint(1, 200)
                    workload.append(("put", key))
        
        elif pattern == "sequential":
            # 顺序访问模式
            for i in range(size):
                if i % 4 == 0:  # 每4次操作写一次
                    workload.append(("put", i))
                else:
                    workload.append(("get", i))
        
        elif pattern == "hotspot":
            # 热点访问模式
            hotspot_keys = list(range(1, 21))  # 前20个为热点
            cold_keys = list(range(21, 201))   # 其余为冷数据
            
            for _ in range(size):
                if random.random() < 0.8:  # 80% 访问热点
                    key = random.choice(hotspot_keys)
                else:  # 20% 访问冷数据
                    key = random.choice(cold_keys)
                
                if random.random() < 0.8:  # 80% 读操作
                    workload.append(("get", key))
                else:
                    workload.append(("put", key))
        
        return workload
    
    def compare_all_caches(self, workload_size: int = 10000) -> Dict[str, Dict[str, Any]]:
        """比较所有缓存策略"""
        patterns = ["random", "sequential", "hotspot"]
        results = {}
        
        for pattern in patterns:
            print(f"\n测试模式: {pattern}")
            workload = self.generate_workload(workload_size, pattern)
            pattern_results = {}
            
            for cache_name in self.caches.keys():
                # 清空缓存
                self.caches[cache_name].clear()
                
                # 运行测试
                result = self.run_workload(cache_name, workload)
                pattern_results[cache_name] = result
                
                print(f"  {cache_name}: 命中率={result['hit_rate']:.2%}, "
                      f"OPS={result['operations_per_second']:.0f}")
            
            results[pattern] = pattern_results
        
        return results


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="lru_cache_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="LRU缓存实现示例",
    tags=["cache", "lru", "algorithm", "performance"]
)
@demo(title="LRU缓存实现示例")
def lru_cache_example():
    """展示LRU缓存的使用"""
    
    print("LRU缓存实现示例")
    
    # 创建小容量的LRU缓存便于演示
    cache = LRUCache[str, str](max_size=3)
    
    print(f"缓存容量: {cache.max_size}")
    
    # 存储数据
    print("\n存储数据:")
    test_data = [("key1", "value1"), ("key2", "value2"), ("key3", "value3")]
    
    for key, value in test_data:
        cache.put(key, value)
        print(f"存储 {key}: {value}")
    
    stats = cache.get_stats()
    print(f"缓存大小: {stats.size}/{stats.max_size}")
    
    # 访问数据
    print("\n访问数据:")
    access_keys = ["key1", "key2", "key1", "key4"]
    
    for key in access_keys:
        value = cache.get(key)
        print(f"访问 {key}: {value or 'Not Found'}")
    
    stats = cache.get_stats()
    print(f"命中率: {stats.hit_rate:.2%}")
    
    # 添加新数据，触发LRU淘汰
    print("\n添加新数据 (触发LRU淘汰):")
    cache.put("key4", "value4")
    cache.put("key5", "value5")
    
    print("验证哪些数据被淘汰:")
    all_keys = ["key1", "key2", "key3", "key4", "key5"]
    for key in all_keys:
        value = cache.get(key)
        status = "存在" if value else "已淘汰"
        print(f"  {key}: {status}")
    
    final_stats = cache.get_stats()
    print(f"\n最终统计:")
    print(f"  命中: {final_stats.hits}")
    print(f"  未命中: {final_stats.misses}")
    print(f"  淘汰: {final_stats.evictions}")
    print(f"  命中率: {final_stats.hit_rate:.2%}")


@example(
    name="cache_comparison_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.ADVANCED,
    description="缓存策略性能对比示例",
    tags=["cache", "performance", "comparison", "benchmark"]
)
@demo(title="缓存策略性能对比示例")
def cache_comparison_example():
    """展示不同缓存策略的性能对比"""
    
    print("缓存策略性能对比")
    
    # 创建性能比较器
    comparator = CachePerformanceComparison()
    
    print("测试配置:")
    print("  - 工作负载大小: 5000 操作")
    print("  - 缓存大小: 100")
    print("  - 测试模式: 随机、顺序、热点")
    
    # 运行比较测试
    results = comparator.compare_all_caches(workload_size=5000)
    
    print("\n=== 性能对比总结 ===")
    
    # 计算每个缓存在不同模式下的平均性能
    cache_names = ["LRU", "LFU", "TTL", "Tiered"]
    patterns = ["random", "sequential", "hotspot"]
    
    print(f"\n{'策略':<10} {'随机命中率':<12} {'顺序命中率':<12} {'热点命中率':<12} {'平均OPS':<10}")
    print("-" * 60)
    
    for cache_name in cache_names:
        hit_rates = []
        ops_rates = []
        
        for pattern in patterns:
            result = results[pattern][cache_name]
            hit_rates.append(result['hit_rate'])
            ops_rates.append(result['operations_per_second'])
        
        avg_ops = sum(ops_rates) / len(ops_rates)
        
        print(f"{cache_name:<10} {hit_rates[0]:<11.1%} {hit_rates[1]:<11.1%} "
              f"{hit_rates[2]:<11.1%} {avg_ops:<10.0f}")
    
    # 找出最佳策略
    print(f"\n=== 推荐策略 ===")
    
    for pattern in patterns:
        pattern_results = results[pattern]
        best_cache = max(pattern_results.keys(), 
                        key=lambda x: pattern_results[x]['hit_rate'])
        best_hit_rate = pattern_results[best_cache]['hit_rate']
        
        print(f"{pattern.capitalize():>8} 模式: {best_cache} "
              f"(命中率 {best_hit_rate:.1%})")


@example(
    name="tiered_cache_example",
    category=ExampleCategory.PERFORMANCE,
    difficulty=DifficultyLevel.ADVANCED,
    description="多层缓存示例",
    tags=["cache", "tiered", "multi-level", "optimization"]
)
@demo(title="多层缓存示例")
def tiered_cache_example():
    """展示多层缓存的使用"""
    
    print("多层缓存示例")
    
    # 创建多层缓存
    cache = TieredCache(l1_size=5, l2_size=10, ttl=30.0)
    
    print("缓存配置:")
    print("  L1缓存 (LRU): 5 项")
    print("  L2缓存 (TTL): 10 项, 30秒过期")
    
    # 存储数据
    print("\n存储数据到缓存:")
    for i in range(8):
        key = f"key_{i}"
        value = f"value_{i}"
        cache.put(key, value)
        print(f"存储 {key}: {value}")
    
    # 查看初始状态
    stats = cache.get_stats()
    print(f"\n初始缓存状态:")
    print(f"  L1缓存: {stats['l1_cache']['size']}/{stats['l1_cache']['max_size']}")
    print(f"  L2缓存: {stats['l2_cache']['size']}/{stats['l2_cache']['max_size']}")
    
    # 访问数据，观察缓存提升
    print(f"\n访问数据 (观察L1/L2命中情况):")
    
    access_pattern = ["key_2", "key_5", "key_7", "key_2", "key_1", "key_5"]
    
    for key in access_pattern:
        # 记录访问前的统计
        before_stats = cache.get_stats()
        
        value = cache.get(key)
        
        # 记录访问后的统计
        after_stats = cache.get_stats()
        
        # 判断命中的缓存层级
        l1_hits_increased = after_stats['l1_cache']['hits'] > before_stats['l1_cache']['hits']
        l2_hits_increased = after_stats['l2_cache']['hits'] > before_stats['l2_cache']['hits']
        
        if l1_hits_increased:
            hit_level = "L1"
        elif l2_hits_increased:
            hit_level = "L2→L1"  # L2命中并提升到L1
        else:
            hit_level = "Miss"
        
        print(f"访问 {key}: {value or 'Not Found'} [{hit_level}]")
    
    # 显示最终统计
    final_stats = cache.get_stats()
    print(f"\n最终统计:")
    print(f"  总体命中率: {final_stats['overall']['hit_rate']:.1%}")
    print(f"  L1缓存:")
    print(f"    大小: {final_stats['l1_cache']['size']}/{final_stats['l1_cache']['max_size']}")
    print(f"    命中率: {final_stats['l1_cache']['hit_rate']:.1%}")
    print(f"  L2缓存:")
    print(f"    大小: {final_stats['l2_cache']['size']}/{final_stats['l2_cache']['max_size']}")
    print(f"    命中率: {final_stats['l2_cache']['hit_rate']:.1%}")
    
    print(f"\n多层缓存的优势:")
    print("  - L1提供极快的访问速度")
    print("  - L2提供更大的存储容量")
    print("  - 热点数据自动提升到L1")
    print("  - 整体命中率更高")


# 导出的类和函数
__all__ = [
    "CacheStats",
    "CacheItem",
    "LRUCache",
    "LFUCache",
    "TTLCache",
    "TieredCache",
    "CachePerformanceComparison",
    "lru_cache_example",
    "cache_comparison_example",
    "tiered_cache_example"
]