"""
高级装饰器实现

展示各种高级装饰器模式，包括缓存、重试、限流、类型检查、性能监控等实用装饰器。
"""

import asyncio
import functools
import hashlib
import logging
import random
import threading
import time
import weakref
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Type
import inspect
from dataclasses import dataclass, field

from ..core.decorators import example, demo, monitor_performance
from ..core.registry import ExampleCategory, DifficultyLevel

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


# ============================================================================
# 缓存装饰器系统
# ============================================================================

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> tuple[bool, Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                # 移动到末尾（最近使用）
                value = self.cache.pop(key)
                self.cache[key] = value
                return True, value
            return False, None
    
    def put(self, key: str, value: Any) -> None:
        """存储缓存值"""
        with self.lock:
            if key in self.cache:
                # 更新现有值
                self.cache.pop(key)
            elif len(self.cache) >= self.maxsize:
                # 删除最少使用的项
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        with self.lock:
            return {
                "size": len(self.cache),
                "maxsize": self.maxsize,
                "hits": getattr(self, '_hits', 0),
                "misses": getattr(self, '_misses', 0)
            }


@dataclass
class TTLCacheItem:
    """TTL缓存项"""
    value: Any
    expire_time: float
    
    def is_expired(self) -> bool:
        return time.time() > self.expire_time


class TTLCache:
    """带过期时间的缓存"""
    
    def __init__(self, maxsize: int = 128, ttl: float = 300):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: Dict[str, TTLCacheItem] = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> tuple[bool, Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if not item.is_expired():
                    return True, item.value
                else:
                    # 删除过期项
                    del self.cache[key]
            return False, None
    
    def put(self, key: str, value: Any) -> None:
        """存储缓存值"""
        with self.lock:
            # 清理过期项
            self._cleanup_expired()
            
            if len(self.cache) >= self.maxsize and key not in self.cache:
                # 删除一个随机项以腾出空间
                random_key = random.choice(list(self.cache.keys()))
                del self.cache[random_key]
            
            expire_time = time.time() + self.ttl
            self.cache[key] = TTLCacheItem(value, expire_time)
    
    def _cleanup_expired(self) -> None:
        """清理过期项"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if item.expire_time <= current_time
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()


class CachingDecorator:
    """高级缓存装饰器"""
    
    def __init__(
        self,
        cache_type: str = "lru",
        maxsize: int = 128,
        ttl: Optional[float] = None,
        key_func: Optional[Callable] = None,
        cache_condition: Optional[Callable] = None
    ):
        self.cache_type = cache_type
        self.maxsize = maxsize
        self.ttl = ttl
        self.key_func = key_func or self._default_key_func
        self.cache_condition = cache_condition
        
        # 创建缓存实例
        if cache_type == "lru":
            self.cache = LRUCache(maxsize)
        elif cache_type == "ttl":
            self.cache = TTLCache(maxsize, ttl or 300)
        else:
            raise ValueError(f"Unsupported cache type: {cache_type}")
        
        # 统计信息
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()
    
    def _default_key_func(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """默认的key生成函数"""
        # 创建参数的字符串表示
        key_parts = [func.__name__]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        key_str = "|".join(key_parts)
        # 使用hash确保key长度可控
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查缓存条件
            if self.cache_condition and not self.cache_condition(*args, **kwargs):
                return func(*args, **kwargs)
            
            # 生成缓存key
            cache_key = self.key_func(func, args, kwargs)
            
            # 尝试从缓存获取
            found, value = self.cache.get(cache_key)
            
            with self.lock:
                if found:
                    self.hits += 1
                    return value
                else:
                    self.misses += 1
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            self.cache.put(cache_key, result)
            
            return result
        
        # 添加缓存管理方法
        wrapper.cache_clear = self.cache.clear
        wrapper.cache_info = self.get_cache_info
        wrapper._cache_decorator = self
        
        return wrapper
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        cache_info = self.cache.info()
        cache_info.update({
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        })
        return cache_info


# ============================================================================
# 重试装饰器系统
# ============================================================================

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 60.0
    jitter: bool = True
    exceptions: tuple = (Exception,)
    on_retry: Optional[Callable] = None
    on_failure: Optional[Callable] = None


class RetryDecorator:
    """智能重试装饰器"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ):
        self.config = RetryConfig(
            max_attempts=max_attempts,
            delay=delay,
            backoff_factor=backoff_factor,
            max_delay=max_delay,
            jitter=jitter,
            exceptions=exceptions,
            on_retry=on_retry,
            on_failure=on_failure
        )
    
    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.config.max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except self.config.exceptions as e:
                    last_exception = e
                    
                    if attempt == self.config.max_attempts - 1:
                        # 最后一次尝试失败
                        if self.config.on_failure:
                            self.config.on_failure(func, attempt + 1, e)
                        raise
                    
                    # 计算延迟时间
                    delay = self.config.delay * (self.config.backoff_factor ** attempt)
                    delay = min(delay, self.config.max_delay)
                    
                    if self.config.jitter:
                        delay *= (0.5 + random.random() * 0.5)  # 添加50%的随机性
                    
                    # 回调函数
                    if self.config.on_retry:
                        self.config.on_retry(func, attempt + 1, e, delay)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            # 理论上不会到达这里
            raise last_exception
        
        wrapper._retry_config = self.config
        return wrapper


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="caching_decorator_basic",
    category=ExampleCategory.DECORATORS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="基础缓存装饰器使用示例",
    tags=["caching", "lru", "performance"]
)
@demo(title="基础缓存装饰器示例")
def caching_decorator_basic():
    """展示LRU缓存装饰器的基本用法"""
    
    @CachingDecorator(cache_type="lru", maxsize=3)
    def fibonacci(n: int) -> int:
        """计算斐波那契数列（递归实现）"""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print("计算斐波那契数列：")
    
    # 第一次计算
    start = time.time()
    result1 = fibonacci(10)
    time1 = time.time() - start
    print(f"fibonacci(10) = {result1}, 耗时: {time1:.4f}s")
    
    # 第二次计算（应该从缓存获取）
    start = time.time()
    result2 = fibonacci(10)
    time2 = time.time() - start
    print(f"fibonacci(10) = {result2}, 耗时: {time2:.4f}s (cached)")
    
    # 显示缓存信息
    cache_info = fibonacci.cache_info()
    print(f"缓存信息: {cache_info}")
    
    print(f"性能提升: {time1/time2:.1f}x" if time2 > 0 else "无限倍提升")


@example(
    name="retry_decorator_example",
    category=ExampleCategory.DECORATORS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="重试装饰器使用示例",
    tags=["retry", "resilience", "error-handling"]
)
@demo(title="重试装饰器示例")
def retry_decorator_example():
    """展示重试装饰器的用法"""
    
    # 定义重试回调
    def on_retry(func, attempt, exception, delay):
        print(f"  重试第 {attempt} 次失败: {exception}, {delay:.1f}秒后重试")
    
    def on_failure(func, attempts, exception):
        print(f"  所有 {attempts} 次尝试都失败了: {exception}")
    
    @RetryDecorator(
        max_attempts=3,
        delay=0.5,
        backoff_factor=2.0,
        exceptions=(ValueError, ConnectionError),
        on_retry=on_retry,
        on_failure=on_failure
    )
    def unreliable_network_call(success_rate: float = 0.3) -> str:
        """模拟不稳定的网络调用"""
        if random.random() > success_rate:
            raise ConnectionError("网络连接失败")
        return "网络请求成功!"
    
    print("重试装饰器示例：")
    
    # 成功的例子
    try:
        result = unreliable_network_call(success_rate=0.8)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ 最终失败: {e}")
    
    print("\n低成功率示例:")
    # 失败的例子
    try:
        result = unreliable_network_call(success_rate=0.1)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ 最终失败: {e}")