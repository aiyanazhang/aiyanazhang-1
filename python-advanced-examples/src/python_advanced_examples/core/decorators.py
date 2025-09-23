"""
核心装饰器模块

提供系统使用的基础装饰器，包括示例注册、性能监控、基准测试等。
"""

import functools
import logging
from typing import Callable, Optional, Any, Union, List

from .registry import ExampleRegistry, ExampleCategory, DifficultyLevel
from .performance import monitor_performance as _monitor_performance, benchmark as _benchmark

logger = logging.getLogger(__name__)


def example(
    name: str,
    category: Union[ExampleCategory, str],
    difficulty: Union[DifficultyLevel, str] = DifficultyLevel.INTERMEDIATE,
    description: str = "",
    tags: Optional[List[str]] = None,
    **kwargs
) -> Callable:
    """示例注册装饰器
    
    将函数注册为可运行的示例。
    
    Args:
        name: 示例名称，用于标识和运行
        category: 示例分类
        difficulty: 难度级别
        description: 示例描述
        tags: 标签列表，用于搜索和分类
        **kwargs: 其他示例属性
    
    Example:
        @example("basic_decorator", "decorators", "beginner", "基础装饰器示例")
        def basic_decorator_example():
            pass
    """
    def decorator(func: Callable) -> Callable:
        # 使用全局注册表
        from . import registry
        
        # 注册示例
        registry_decorator = registry.register(
            name=name,
            category=category,
            difficulty=difficulty,
            description=description,
            tags=tags,
            **kwargs
        )
        
        # 应用注册装饰器
        registered_func = registry_decorator(func)
        
        # 添加便捷方法
        registered_func.example_name = name
        registered_func.example_category = category
        registered_func.example_difficulty = difficulty
        
        return registered_func
    
    return decorator


def monitor_performance(name: Optional[str] = None):
    """性能监控装饰器的封装"""
    return _monitor_performance(name)


def benchmark(iterations: int = 10, warmup: int = 3):
    """基准测试装饰器的封装"""
    return _benchmark(iterations, warmup)


def demo(
    title: str = "",
    description: str = "",
    auto_run: bool = False
) -> Callable:
    """演示装饰器
    
    标记函数为演示用途，提供额外的展示信息。
    
    Args:
        title: 演示标题
        description: 演示描述
        auto_run: 是否自动运行（用于Web界面）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if title:
                print(f"\n🎯 {title}")
                print("=" * (len(title) + 4))
            
            if description:
                print(f"📝 {description}\n")
            
            try:
                result = func(*args, **kwargs)
                
                if title:
                    print(f"\n✅ {title} 完成")
                
                return result
            
            except Exception as e:
                if title:
                    print(f"\n❌ {title} 失败: {e}")
                raise
        
        # 添加演示元数据
        wrapper._demo_metadata = {
            "title": title or func.__name__,
            "description": description,
            "auto_run": auto_run
        }
        
        return wrapper
    
    return decorator


def safe_execution(
    catch_exceptions: bool = True,
    log_errors: bool = True,
    default_return: Any = None,
    reraise: bool = False
) -> Callable:
    """安全执行装饰器
    
    为函数提供异常处理和错误恢复机制。
    
    Args:
        catch_exceptions: 是否捕获异常
        log_errors: 是否记录错误日志
        default_return: 异常时的默认返回值
        reraise: 是否重新抛出异常
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                
                if reraise:
                    raise
                
                if catch_exceptions:
                    return default_return
                else:
                    raise
        
        return wrapper
    
    return decorator


def validation(
    validate_args: bool = True,
    validate_kwargs: bool = True,
    type_check: bool = False
) -> Callable:
    """参数验证装饰器
    
    为函数提供参数验证功能。
    
    Args:
        validate_args: 是否验证位置参数
        validate_kwargs: 是否验证关键字参数
        type_check: 是否进行类型检查
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if type_check:
                # 简单的类型检查实现
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for param_name, param_value in bound_args.arguments.items():
                    param = sig.parameters[param_name]
                    if param.annotation != inspect.Parameter.empty:
                        expected_type = param.annotation
                        if not isinstance(param_value, expected_type):
                            raise TypeError(
                                f"Parameter '{param_name}' expected {expected_type.__name__}, "
                                f"got {type(param_value).__name__}"
                            )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def deprecated(
    message: str = "",
    version: str = "",
    replacement: str = ""
) -> Callable:
    """弃用警告装饰器
    
    标记函数为已弃用，并提供警告信息。
    
    Args:
        message: 弃用消息
        version: 弃用版本
        replacement: 推荐的替代方案
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            
            warning_msg = f"Function '{func.__name__}' is deprecated"
            
            if version:
                warning_msg += f" since version {version}"
            
            if replacement:
                warning_msg += f". Use '{replacement}' instead"
            
            if message:
                warning_msg += f". {message}"
            
            warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def experimental(
    message: str = "This feature is experimental and may change in future versions"
) -> Callable:
    """实验性功能装饰器
    
    标记函数为实验性功能。
    
    Args:
        message: 实验性功能警告消息
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            
            warning_msg = f"Function '{func.__name__}' is experimental. {message}"
            warnings.warn(warning_msg, UserWarning, stacklevel=2)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def requires_dependencies(*dependencies: str):
    """依赖检查装饰器
    
    检查函数运行所需的依赖是否可用。
    
    Args:
        dependencies: 必需的依赖包名列表
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            missing_deps = []
            
            for dep in dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                raise ImportError(
                    f"Function '{func.__name__}' requires the following dependencies: "
                    f"{', '.join(missing_deps)}. Please install them first."
                )
            
            return func(*args, **kwargs)
        
        # 添加依赖信息到函数
        wrapper._required_dependencies = dependencies
        
        return wrapper
    
    return decorator


def log_calls(
    logger_name: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
    log_duration: bool = True
) -> Callable:
    """函数调用日志装饰器
    
    记录函数调用的详细信息。
    
    Args:
        logger_name: 日志器名称
        log_args: 是否记录参数
        log_result: 是否记录返回值
        log_duration: 是否记录执行时间
    """
    def decorator(func: Callable) -> Callable:
        func_logger = logging.getLogger(logger_name or func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            start_time = time.time()
            
            # 记录调用开始
            call_info = f"Calling {func.__name__}"
            if log_args and (args or kwargs):
                call_info += f" with args={args}, kwargs={kwargs}"
            
            func_logger.debug(call_info)
            
            try:
                result = func(*args, **kwargs)
                
                # 记录调用完成
                end_time = time.time()
                duration = end_time - start_time
                
                complete_info = f"Completed {func.__name__}"
                if log_duration:
                    complete_info += f" in {duration:.3f}s"
                if log_result:
                    complete_info += f" with result={result}"
                
                func_logger.debug(complete_info)
                
                return result
                
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                
                error_info = f"Failed {func.__name__} after {duration:.3f}s with error: {e}"
                func_logger.error(error_info)
                
                raise
        
        return wrapper
    
    return decorator


def memoize(maxsize: int = 128):
    """记忆化装饰器
    
    缓存函数结果以提高性能。
    
    Args:
        maxsize: 缓存的最大大小
    """
    def decorator(func: Callable) -> Callable:
        @functools.lru_cache(maxsize=maxsize)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # lru_cache只支持hashable参数，这里只处理基本情况
            return func(*args, **kwargs)
        
        # 添加缓存管理方法
        wrapper.cache_clear = wrapper.cache_clear
        wrapper.cache_info = wrapper.cache_info
        
        return wrapper
    
    return decorator


def rate_limit(calls_per_second: float = 1.0):
    """速率限制装饰器
    
    限制函数的调用频率。
    
    Args:
        calls_per_second: 每秒允许的调用次数
    """
    def decorator(func: Callable) -> Callable:
        import time
        import threading
        
        lock = threading.Lock()
        last_call_time = [0.0]  # 使用列表以支持修改
        min_interval = 1.0 / calls_per_second
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                current_time = time.time()
                time_since_last_call = current_time - last_call_time[0]
                
                if time_since_last_call < min_interval:
                    sleep_time = min_interval - time_since_last_call
                    time.sleep(sleep_time)
                
                last_call_time[0] = time.time()
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator