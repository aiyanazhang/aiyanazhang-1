"""
Python高级用法示例系统

本包提供了Python高级编程特性的综合示例，包括：
- 高级装饰器和元编程技术
- 异步编程和并发处理
- 性能优化和内存管理
- 设计模式和架构实践
- 数据处理和函数式编程

主要模块：
    core: 核心框架和基础设施
    language_features: Python语言特性示例
    concurrency: 并发编程示例
    performance: 性能优化技术
    metaprogramming: 元编程和反射
    data_processing: 数据处理和流式计算
    interfaces: 用户接口（CLI、Web等）
"""

__version__ = "1.0.0"
__author__ = "Python Advanced Examples Team"
__email__ = "team@example.com"

# 导出主要的公共接口
from .core.registry import ExampleRegistry
from .core.runner import ExampleRunner
from .core.performance import PerformanceMonitor

# 创建全局实例
registry = ExampleRegistry()
runner = ExampleRunner(registry)
monitor = PerformanceMonitor()

__all__ = [
    "ExampleRegistry",
    "ExampleRunner", 
    "PerformanceMonitor",
    "registry",
    "runner",
    "monitor",
]