"""
示例执行引擎

提供安全的示例执行环境，包括超时控制、内存限制、异常处理和结果收集。
"""

import asyncio
import contextlib
import io
import logging
import multiprocessing
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import psutil
import os
import signal
from pathlib import Path

from .registry import Example, ExampleRegistry
from .performance import PerformanceData

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """执行状态"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class ExecutionResult:
    """执行结果"""
    example_name: str
    status: ExecutionStatus
    output: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: float = 0.0  # MB
    return_value: Any = None
    performance_data: Optional[PerformanceData] = None
    stdout: str = ""
    stderr: str = ""
    exception_info: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    def __post_init__(self):
        if self.end_time is None:
            self.end_time = time.time()
    
    @property
    def success(self) -> bool:
        """是否执行成功"""
        return self.status == ExecutionStatus.SUCCESS
    
    def get_summary(self) -> str:
        """获取执行摘要"""
        status_emoji = {
            ExecutionStatus.SUCCESS: "✅",
            ExecutionStatus.FAILED: "❌", 
            ExecutionStatus.TIMEOUT: "⏰",
            ExecutionStatus.MEMORY_EXCEEDED: "💾",
            ExecutionStatus.CANCELLED: "🚫",
            ExecutionStatus.ERROR: "💥",
        }
        
        emoji = status_emoji.get(self.status, "❓")
        summary = f"{emoji} {self.example_name}: {self.status.value}"
        
        if self.execution_time > 0:
            summary += f" ({self.execution_time:.3f}s"
            if self.memory_usage > 0:
                summary += f", {self.memory_usage:.1f}MB"
            summary += ")"
        
        return summary


class ResourceMonitor:
    """资源监控器"""
    
    def __init__(self, memory_limit_mb: int = 512):
        self.memory_limit_mb = memory_limit_mb
        self.process = psutil.Process()
        self.peak_memory = 0.0
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self.peak_memory = 0.0
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
    
    def check_memory(self) -> float:
        """检查当前内存使用"""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if self.monitoring:
                self.peak_memory = max(self.peak_memory, memory_mb)
                
                if memory_mb > self.memory_limit_mb:
                    raise MemoryError(f"Memory usage {memory_mb:.1f}MB exceeds limit {self.memory_limit_mb}MB")
            
            return memory_mb
        except psutil.NoSuchProcess:
            return 0.0
    
    def get_peak_memory(self) -> float:
        """获取峰值内存使用"""
        return self.peak_memory


class ExecutionContext:
    """执行上下文"""
    
    def __init__(
        self,
        example: Example,
        timeout: Optional[float] = None,
        memory_limit_mb: Optional[int] = None,
        capture_output: bool = True,
        isolated: bool = False
    ):
        self.example = example
        self.timeout = timeout or example.execution_time_limit
        self.memory_limit_mb = memory_limit_mb or example.memory_limit
        self.capture_output = capture_output
        self.isolated = isolated
        
        self.monitor = ResourceMonitor(self.memory_limit_mb)
        self.stdout_capture = io.StringIO() if capture_output else None
        self.stderr_capture = io.StringIO() if capture_output else None
        self.original_stdout = None
        self.original_stderr = None
    
    def __enter__(self):
        # 开始资源监控
        self.monitor.start_monitoring()
        
        # 重定向输出
        if self.capture_output:
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
            sys.stdout = self.stdout_capture
            sys.stderr = self.stderr_capture
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 停止资源监控
        self.monitor.stop_monitoring()
        
        # 恢复输出
        if self.capture_output and self.original_stdout and self.original_stderr:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
    
    def get_captured_output(self) -> tuple[str, str]:
        """获取捕获的输出"""
        stdout = self.stdout_capture.getvalue() if self.stdout_capture else ""
        stderr = self.stderr_capture.getvalue() if self.stderr_capture else ""
        return stdout, stderr


def _execute_function_with_timeout(func: Callable, args: tuple, kwargs: dict, timeout: float) -> Any:
    """在子进程中执行函数，支持超时"""
    def target(result_queue, error_queue):
        try:
            result = func(*args, **kwargs)
            result_queue.put(result)
        except Exception as e:
            error_queue.put((type(e).__name__, str(e), traceback.format_exc()))
    
    result_queue = multiprocessing.Queue()
    error_queue = multiprocessing.Queue()
    
    process = multiprocessing.Process(target=target, args=(result_queue, error_queue))
    process.start()
    process.join(timeout=timeout)
    
    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Function execution exceeded {timeout}s timeout")
    
    if not error_queue.empty():
        exc_type, exc_msg, exc_traceback = error_queue.get()
        raise RuntimeError(f"{exc_type}: {exc_msg}\n{exc_traceback}")
    
    if not result_queue.empty():
        return result_queue.get()
    
    return None


class ExampleRunner:
    """示例执行器"""
    
    def __init__(self, registry: ExampleRegistry):
        self.registry = registry
        self.thread_executor = ThreadPoolExecutor(max_workers=4)
        self.process_executor = ProcessPoolExecutor(max_workers=2)
    
    def run(
        self,
        example_name: str,
        *args,
        timeout: Optional[float] = None,
        memory_limit_mb: Optional[int] = None,
        capture_output: bool = True,
        isolated: bool = False,
        **kwargs
    ) -> ExecutionResult:
        """运行单个示例
        
        Args:
            example_name: 示例名称
            *args: 传递给示例函数的位置参数
            timeout: 超时时间（秒）
            memory_limit_mb: 内存限制（MB）
            capture_output: 是否捕获输出
            isolated: 是否在隔离环境中运行
            **kwargs: 传递给示例函数的关键字参数
        """
        # 获取示例
        example = self.registry.get_example(example_name)
        if example is None:
            return ExecutionResult(
                example_name=example_name,
                status=ExecutionStatus.ERROR,
                error=f"Example '{example_name}' not found"
            )
        
        start_time = time.time()
        
        try:
            # 执行设置代码
            if example.setup_code:
                exec(example.setup_code)
            
            # 创建执行上下文
            with ExecutionContext(
                example=example,
                timeout=timeout,
                memory_limit_mb=memory_limit_mb,
                capture_output=capture_output,
                isolated=isolated
            ) as ctx:
                
                if isolated:
                    # 在隔离进程中执行
                    result = self._run_isolated(example.func, args, kwargs, ctx.timeout)
                else:
                    # 在当前进程中执行
                    result = self._run_in_process(example.func, args, kwargs, ctx)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # 获取输出和内存使用
                stdout, stderr = ctx.get_captured_output()
                peak_memory = ctx.monitor.get_peak_memory()
                
                # 创建成功结果
                execution_result = ExecutionResult(
                    example_name=example_name,
                    status=ExecutionStatus.SUCCESS,
                    return_value=result,
                    execution_time=execution_time,
                    memory_usage=peak_memory,
                    stdout=stdout,
                    stderr=stderr,
                    start_time=start_time,
                    end_time=end_time
                )
                
        except TimeoutError as e:
            execution_result = ExecutionResult(
                example_name=example_name,
                status=ExecutionStatus.TIMEOUT,
                error=str(e),
                execution_time=time.time() - start_time,
                exception_info=traceback.format_exc()
            )
            
        except MemoryError as e:
            execution_result = ExecutionResult(
                example_name=example_name,
                status=ExecutionStatus.MEMORY_EXCEEDED,
                error=str(e),
                execution_time=time.time() - start_time,
                exception_info=traceback.format_exc()
            )
            
        except Exception as e:
            execution_result = ExecutionResult(
                example_name=example_name,
                status=ExecutionStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time,
                exception_info=traceback.format_exc()
            )
        
        finally:
            # 执行清理代码
            if example and example.cleanup_code:
                try:
                    exec(example.cleanup_code)
                except Exception as e:
                    logger.warning(f"Cleanup code failed for {example_name}: {e}")
        
        return execution_result
    
    def _run_in_process(self, func: Callable, args: tuple, kwargs: dict, ctx: ExecutionContext) -> Any:
        """在当前进程中运行"""
        # 设置超时
        if ctx.timeout > 0:
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function execution exceeded {ctx.timeout}s timeout")
            
            # 设置信号处理器（仅在Unix系统上）
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(ctx.timeout))
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            return result
        finally:
            # 取消超时
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
    
    def _run_isolated(self, func: Callable, args: tuple, kwargs: dict, timeout: float) -> Any:
        """在隔离进程中运行"""
        future = self.process_executor.submit(_execute_function_with_timeout, func, args, kwargs, timeout)
        return future.result(timeout=timeout + 1)  # 留出额外的1秒缓冲
    
    async def run_async(
        self,
        example_name: str,
        *args,
        **kwargs
    ) -> ExecutionResult:
        """异步运行示例"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_executor,
            self.run,
            example_name,
            *args,
            **kwargs
        )
    
    def run_batch(
        self,
        example_names: List[str],
        parallel: bool = True,
        max_workers: Optional[int] = None,
        **common_kwargs
    ) -> List[ExecutionResult]:
        """批量运行示例
        
        Args:
            example_names: 示例名称列表
            parallel: 是否并行执行
            max_workers: 最大工作线程数
            **common_kwargs: 传递给所有示例的公共参数
        """
        if not parallel:
            # 顺序执行
            return [self.run(name, **common_kwargs) for name in example_names]
        
        # 并行执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.run, name, **common_kwargs)
                for name in example_names
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # 创建错误结果
                    error_result = ExecutionResult(
                        example_name="unknown",
                        status=ExecutionStatus.ERROR,
                        error=str(e),
                        exception_info=traceback.format_exc()
                    )
                    results.append(error_result)
            
            return results
    
    async def run_batch_async(
        self,
        example_names: List[str],
        max_concurrent: int = 4,
        **common_kwargs
    ) -> List[ExecutionResult]:
        """异步批量运行示例"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_semaphore(name):
            async with semaphore:
                return await self.run_async(name, **common_kwargs)
        
        tasks = [run_with_semaphore(name) for name in example_names]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def run_by_category(
        self,
        category: Union[str, 'ExampleCategory'],
        **kwargs
    ) -> List[ExecutionResult]:
        """按分类运行所有示例"""
        examples = self.registry.get_by_category(category)
        example_names = [ex.name for ex in examples]
        return self.run_batch(example_names, **kwargs)
    
    def run_by_difficulty(
        self,
        difficulty: Union[str, 'DifficultyLevel'],
        **kwargs
    ) -> List[ExecutionResult]:
        """按难度运行所有示例"""
        examples = self.registry.get_by_difficulty(difficulty)
        example_names = [ex.name for ex in examples]
        return self.run_batch(example_names, **kwargs)
    
    def benchmark(
        self,
        example_name: str,
        iterations: int = 10,
        warmup_iterations: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """对示例进行基准测试
        
        Args:
            example_name: 示例名称
            iterations: 测试迭代次数
            warmup_iterations: 预热迭代次数
            **kwargs: 传递给示例的参数
        """
        # 预热
        for _ in range(warmup_iterations):
            self.run(example_name, capture_output=False, **kwargs)
        
        # 正式测试
        results = []
        for _ in range(iterations):
            result = self.run(example_name, **kwargs)
            if result.success:
                results.append(result)
        
        if not results:
            return {"error": "No successful runs"}
        
        # 计算统计信息
        execution_times = [r.execution_time for r in results]
        memory_usages = [r.memory_usage for r in results]
        
        return {
            "example_name": example_name,
            "iterations": len(results),
            "execution_time": {
                "mean": sum(execution_times) / len(execution_times),
                "min": min(execution_times),
                "max": max(execution_times),
                "std": (sum((t - sum(execution_times) / len(execution_times)) ** 2 for t in execution_times) / len(execution_times)) ** 0.5
            },
            "memory_usage": {
                "mean": sum(memory_usages) / len(memory_usages),
                "min": min(memory_usages),
                "max": max(memory_usages),
                "std": (sum((m - sum(memory_usages) / len(memory_usages)) ** 2 for m in memory_usages) / len(memory_usages)) ** 0.5
            },
            "success_rate": len(results) / (iterations + warmup_iterations)
        }
    
    def get_execution_report(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """生成执行报告"""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        
        status_counts = {}
        for result in results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if successful > 0:
            successful_results = [r for r in results if r.success]
            avg_execution_time = sum(r.execution_time for r in successful_results) / len(successful_results)
            avg_memory_usage = sum(r.memory_usage for r in successful_results) / len(successful_results)
        else:
            avg_execution_time = 0
            avg_memory_usage = 0
        
        return {
            "total_examples": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 0,
            "status_breakdown": status_counts,
            "average_execution_time": avg_execution_time,
            "average_memory_usage": avg_memory_usage,
            "results": [
                {
                    "name": r.example_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "memory_usage": r.memory_usage,
                    "error": r.error
                }
                for r in results
            ]
        }
    
    def __del__(self):
        """清理资源"""
        try:
            self.thread_executor.shutdown(wait=False)
            self.process_executor.shutdown(wait=False)
        except Exception:
            pass