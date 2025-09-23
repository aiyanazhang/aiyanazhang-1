"""性能优化模块初始化"""

from .memory_optimization import *
from .caching_strategies import *
from .algorithm_optimization import *

__all__ = [
    # 内存优化
    "MemoryOptimizedClass",
    "ObjectPool",
    "WeakReferenceCache",
    "MemoryProfiler",
    "memory_optimization_example",
    "object_pool_example",
    "weak_reference_example",
    
    # 缓存策略
    "LRUCache",
    "LFUCache", 
    "TTLCache",
    "TieredCache",
    "CachePerformanceComparison",
    "lru_cache_example",
    "cache_comparison_example",
    
    # 算法优化
    "AlgorithmOptimizer",
    "DataStructureComparison",
    "SearchAlgorithms",
    "SortingAlgorithms",
    "algorithm_optimization_example",
    "data_structure_comparison_example",
]