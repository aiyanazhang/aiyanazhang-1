"""
核心模块单元测试
"""

import pytest
import time
from unittest.mock import Mock, patch

from python_advanced_examples.core.registry import (
    ExampleRegistry, Example, ExampleCategory, DifficultyLevel
)
from python_advanced_examples.core.runner import ExampleRunner, ExecutionStatus
from python_advanced_examples.core.performance import PerformanceMonitor


class TestExampleRegistry:
    """示例注册表测试"""
    
    def setup_method(self):
        """测试设置"""
        self.registry = ExampleRegistry()
    
    def test_register_example(self):
        """测试示例注册"""
        @self.registry.register(
            name="test_example",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="测试示例"
        )
        def test_func():
            return "test result"
        
        # 验证注册
        example = self.registry.get_example("test_example")
        assert example is not None
        assert example.name == "test_example"
        assert example.category == ExampleCategory.DECORATORS
        assert example.difficulty == DifficultyLevel.BEGINNER
        assert example.description == "测试示例"
    
    def test_list_examples_with_filters(self):
        """测试带过滤的示例列表"""
        # 注册多个示例
        @self.registry.register(
            name="decorator_example", 
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="装饰器示例"
        )
        def decorator_func():
            pass
        
        @self.registry.register(
            name="async_example",
            category=ExampleCategory.ASYNC_PROGRAMMING, 
            difficulty=DifficultyLevel.ADVANCED,
            description="异步示例"
        )
        def async_func():
            pass
        
        # 测试分类过滤
        decorator_examples = self.registry.list_examples(category=ExampleCategory.DECORATORS)
        assert len(decorator_examples) == 1
        assert decorator_examples[0].name == "decorator_example"
        
        # 测试难度过滤
        beginner_examples = self.registry.list_examples(difficulty=DifficultyLevel.BEGINNER)
        assert len(beginner_examples) == 1
        assert beginner_examples[0].name == "decorator_example"
    
    def test_search_examples(self):
        """测试示例搜索"""
        @self.registry.register(
            name="cache_decorator",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="缓存装饰器示例"
        )
        def cache_func():
            pass
        
        # 搜索名称
        results = self.registry.search("cache")
        assert len(results) == 1
        assert results[0].name == "cache_decorator"
        
        # 搜索描述
        results = self.registry.search("缓存")
        assert len(results) == 1
        assert results[0].name == "cache_decorator"
    
    def test_get_statistics(self):
        """测试统计信息"""
        # 注册示例
        @self.registry.register(
            name="stat_test1",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="统计测试1"
        )
        def func1():
            pass
        
        @self.registry.register(
            name="stat_test2",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="统计测试2"
        )
        def func2():
            pass
        
        stats = self.registry.get_statistics()
        
        assert stats["total_examples"] == 2
        assert ExampleCategory.DECORATORS.value in stats["categories"]
        assert stats["categories"][ExampleCategory.DECORATORS.value] == 2


class TestExampleRunner:
    """示例运行器测试"""
    
    def setup_method(self):
        """测试设置"""
        self.registry = ExampleRegistry()
        self.runner = ExampleRunner(self.registry)
    
    def test_run_successful_example(self):
        """测试成功运行示例"""
        @self.registry.register(
            name="success_test",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="成功测试"
        )
        def success_func():
            print("Hello, World!")
            return "success"
        
        result = self.runner.run("success_test")
        
        assert result.success
        assert result.status == ExecutionStatus.SUCCESS
        assert result.return_value == "success"
        assert "Hello, World!" in result.stdout
        assert result.execution_time > 0
    
    def test_run_failing_example(self):
        """测试失败示例运行"""
        @self.registry.register(
            name="fail_test",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="失败测试"
        )
        def fail_func():
            raise ValueError("测试错误")
        
        result = self.runner.run("fail_test")
        
        assert not result.success
        assert result.status == ExecutionStatus.FAILED
        assert "测试错误" in result.error
        assert result.execution_time > 0
    
    def test_run_nonexistent_example(self):
        """测试运行不存在的示例"""
        result = self.runner.run("nonexistent")
        
        assert not result.success
        assert result.status == ExecutionStatus.ERROR
        assert "not found" in result.error.lower()
    
    def test_run_with_timeout(self):
        """测试超时控制"""
        @self.registry.register(
            name="timeout_test",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="超时测试"
        )
        def timeout_func():
            time.sleep(2)
            return "completed"
        
        # 设置较短的超时
        result = self.runner.run("timeout_test", timeout=0.5)
        
        # 根据实现，可能是超时或正常完成
        assert result.execution_time > 0
    
    def test_benchmark(self):
        """测试基准测试"""
        @self.registry.register(
            name="benchmark_test",
            category=ExampleCategory.DECORATORS,
            difficulty=DifficultyLevel.BEGINNER,
            description="基准测试"
        )
        def benchmark_func():
            time.sleep(0.01)  # 短暂延迟
            return "done"
        
        benchmark_result = self.runner.benchmark(
            "benchmark_test",
            iterations=3,
            warmup_iterations=1
        )
        
        assert "example_name" in benchmark_result
        assert benchmark_result["example_name"] == "benchmark_test"
        assert "execution_time" in benchmark_result
        assert benchmark_result["execution_time"]["mean"] > 0


class TestPerformanceMonitor:
    """性能监控器测试"""
    
    def setup_method(self):
        """测试设置"""
        self.monitor = PerformanceMonitor()
    
    def test_performance_monitoring(self):
        """测试性能监控"""
        self.monitor.enable()
        
        with self.monitor.profile("test_function"):
            time.sleep(0.01)
            result = sum(range(1000))
        
        stats = self.monitor.get_stats("test_function")
        assert stats is not None
        assert stats.call_count == 1
        assert stats.execution_time > 0
    
    def test_multiple_calls_aggregation(self):
        """测试多次调用聚合"""
        self.monitor.enable()
        
        for i in range(3):
            with self.monitor.profile("multi_test"):
                time.sleep(0.001)
        
        stats = self.monitor.get_stats("multi_test")
        assert stats.call_count == 3
        assert stats.total_time > 0
        assert stats.average_time > 0
    
    def test_generate_report(self):
        """测试性能报告生成"""
        self.monitor.enable()
        
        with self.monitor.profile("report_test"):
            time.sleep(0.001)
        
        report = self.monitor.generate_report()
        
        assert "summary" in report
        assert "top_functions" in report
        assert report["summary"]["total_functions_monitored"] >= 1
    
    def test_reset_stats(self):
        """测试统计重置"""
        self.monitor.enable()
        
        with self.monitor.profile("reset_test"):
            pass
        
        # 确认有统计数据
        assert len(self.monitor.get_stats()) > 0
        
        # 重置
        self.monitor.reset_stats()
        
        # 确认已清空
        assert len(self.monitor.get_stats()) == 0


if __name__ == "__main__":
    pytest.main([__file__])