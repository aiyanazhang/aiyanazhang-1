"""
管道模式实现

展示管道模式的高级用法：
- 可组合的处理阶段
- 异步管道
- 并行管道
- 错误处理和重试
- 管道监控和指标
"""

import asyncio
import threading
import time
from typing import (
    Any, Callable, TypeVar, Generic, List, Dict, Optional, 
    Union, Tuple, Iterator, AsyncIterator
)
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging
from functools import wraps

T = TypeVar('T')
U = TypeVar('U')

class PipelineStageStatus(Enum):
    """管道阶段状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PipelineContext:
    """管道上下文"""
    stage_name: str
    input_data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: PipelineStageStatus = PipelineStageStatus.PENDING
    error: Optional[Exception] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.end_time:
            return self.end_time - self.start_time
        return None

class PipelineStage(Generic[T, U], ABC):
    """管道阶段抽象基类"""
    
    def __init__(self, name: str, retry_count: int = 0, timeout: Optional[float] = None):
        self.name = name
        self.retry_count = retry_count
        self.timeout = timeout
        self.metrics = defaultdict(int)
    
    @abstractmethod
    def process(self, data: T, context: PipelineContext) -> U:
        """处理数据"""
        pass
    
    def pre_process(self, data: T, context: PipelineContext) -> T:
        """预处理钩子"""
        return data
    
    def post_process(self, result: U, context: PipelineContext) -> U:
        """后处理钩子"""
        return result
    
    def handle_error(self, error: Exception, context: PipelineContext) -> Optional[U]:
        """错误处理"""
        context.error = error
        context.status = PipelineStageStatus.FAILED
        self.metrics['errors'] += 1
        raise error
    
    def should_skip(self, data: T, context: PipelineContext) -> bool:
        """是否跳过该阶段"""
        return False
    
    def execute(self, data: T, context: PipelineContext) -> U:
        """执行阶段处理"""
        context.stage_name = self.name
        context.status = PipelineStageStatus.RUNNING
        self.metrics['total'] += 1
        
        try:
            if self.should_skip(data, context):
                context.status = PipelineStageStatus.SKIPPED
                self.metrics['skipped'] += 1
                return data
            
            # 预处理
            processed_data = self.pre_process(data, context)
            
            # 主处理逻辑
            for attempt in range(self.retry_count + 1):
                try:
                    result = self.process(processed_data, context)
                    break
                except Exception as e:
                    if attempt == self.retry_count:
                        return self.handle_error(e, context)
                    self.metrics['retries'] += 1
                    time.sleep(0.1 * (attempt + 1))  # 指数退避
            
            # 后处理
            final_result = self.post_process(result, context)
            
            context.status = PipelineStageStatus.COMPLETED
            context.end_time = time.time()
            self.metrics['success'] += 1
            
            return final_result
            
        except Exception as e:
            return self.handle_error(e, context)

class MapStage(PipelineStage[T, U]):
    """映射阶段"""
    
    def __init__(self, name: str, transform_func: Callable[[T], U], **kwargs):
        super().__init__(name, **kwargs)
        self.transform_func = transform_func
    
    def process(self, data: T, context: PipelineContext) -> U:
        return self.transform_func(data)

class FilterStage(PipelineStage[T, T]):
    """过滤阶段"""
    
    def __init__(self, name: str, predicate: Callable[[T], bool], **kwargs):
        super().__init__(name, **kwargs)
        self.predicate = predicate
    
    def process(self, data: T, context: PipelineContext) -> T:
        return data
    
    def should_skip(self, data: T, context: PipelineContext) -> bool:
        return not self.predicate(data)

class ReduceStage(PipelineStage[List[T], U]):
    """归约阶段"""
    
    def __init__(self, name: str, reduce_func: Callable[[List[T]], U], **kwargs):
        super().__init__(name, **kwargs)
        self.reduce_func = reduce_func
    
    def process(self, data: List[T], context: PipelineContext) -> U:
        return self.reduce_func(data)

class BatchStage(PipelineStage[T, List[T]]):
    """批处理阶段"""
    
    def __init__(self, name: str, batch_size: int, **kwargs):
        super().__init__(name, **kwargs)
        self.batch_size = batch_size
        self.batch_buffer = []
    
    def process(self, data: T, context: PipelineContext) -> List[T]:
        self.batch_buffer.append(data)
        if len(self.batch_buffer) >= self.batch_size:
            batch = self.batch_buffer.copy()
            self.batch_buffer.clear()
            return batch
        return []
    
    def get_remaining_batch(self) -> List[T]:
        """获取剩余的批次数据"""
        if self.batch_buffer:
            batch = self.batch_buffer.copy()
            self.batch_buffer.clear()
            return batch
        return []

class Pipeline(Generic[T, U]):
    """管道处理器"""
    
    def __init__(self, name: str = "Pipeline"):
        self.name = name
        self.stages: List[PipelineStage] = []
        self.metrics = defaultdict(int)
        self.logger = logging.getLogger(f"Pipeline.{name}")
    
    def add_stage(self, stage: PipelineStage) -> 'Pipeline':
        """添加处理阶段"""
        self.stages.append(stage)
        return self
    
    def map(self, name: str, transform_func: Callable, **kwargs) -> 'Pipeline':
        """添加映射阶段"""
        return self.add_stage(MapStage(name, transform_func, **kwargs))
    
    def filter(self, name: str, predicate: Callable[[T], bool], **kwargs) -> 'Pipeline':
        """添加过滤阶段"""
        return self.add_stage(FilterStage(name, predicate, **kwargs))
    
    def reduce(self, name: str, reduce_func: Callable, **kwargs) -> 'Pipeline':
        """添加归约阶段"""
        return self.add_stage(ReduceStage(name, reduce_func, **kwargs))
    
    def batch(self, name: str, batch_size: int, **kwargs) -> 'Pipeline':
        """添加批处理阶段"""
        return self.add_stage(BatchStage(name, batch_size, **kwargs))
    
    def process(self, data: T) -> U:
        """处理单个数据项"""
        context = PipelineContext("Pipeline", data)
        current_data = data
        
        for stage in self.stages:
            stage_context = PipelineContext(stage.name, current_data)
            current_data = stage.execute(current_data, stage_context)
            
            # 记录指标
            self.metrics[f"{stage.name}_duration"] = stage_context.duration or 0
            self.metrics[f"{stage.name}_status"] = stage_context.status.value
        
        return current_data
    
    def process_stream(self, data_stream: Iterator[T]) -> Iterator[U]:
        """处理数据流"""
        for item in data_stream:
            try:
                result = self.process(item)
                if result is not None:  # 过滤掉None结果
                    yield result
            except Exception as e:
                self.logger.error(f"Pipeline error processing item: {e}")
                self.metrics['stream_errors'] += 1
    
    def process_batch(self, data_list: List[T]) -> List[U]:
        """批量处理"""
        results = []
        for item in data_list:
            try:
                result = self.process(item)
                if result is not None:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Batch processing error: {e}")
                self.metrics['batch_errors'] += 1
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取管道指标"""
        stage_metrics = {}
        for stage in self.stages:
            stage_metrics[stage.name] = dict(stage.metrics)
        
        return {
            'pipeline_metrics': dict(self.metrics),
            'stage_metrics': stage_metrics
        }

class ParallelPipeline(Pipeline[T, U]):
    """并行管道"""
    
    def __init__(self, name: str = "ParallelPipeline", num_workers: int = 4):
        super().__init__(name)
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
    
    def process_parallel(self, data_list: List[T]) -> List[U]:
        """并行处理数据列表"""
        if not data_list:
            return []
        
        # 将数据分块
        chunk_size = max(1, len(data_list) // self.num_workers)
        chunks = [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]
        
        # 并行处理
        futures = []
        for chunk in chunks:
            future = self.executor.submit(self.process_batch, chunk)
            futures.append(future)
        
        # 收集结果
        results = []
        for future in as_completed(futures):
            try:
                chunk_results = future.result()
                results.extend(chunk_results)
            except Exception as e:
                self.logger.error(f"Parallel processing error: {e}")
                self.metrics['parallel_errors'] += 1
        
        return results
    
    def __del__(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)

class AsyncPipeline(Generic[T, U]):
    """异步管道"""
    
    def __init__(self, name: str = "AsyncPipeline"):
        self.name = name
        self.stages: List[Callable] = []
        self.metrics = defaultdict(int)
        self.logger = logging.getLogger(f"AsyncPipeline.{name}")
    
    def add_async_stage(self, name: str, stage_func: Callable) -> 'AsyncPipeline':
        """添加异步处理阶段"""
        async def wrapped_stage(data):
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(stage_func):
                    result = await stage_func(data)
                else:
                    result = stage_func(data)
                
                self.metrics[f"{name}_success"] += 1
                return result
                
            except Exception as e:
                self.logger.error(f"Async stage {name} error: {e}")
                self.metrics[f"{name}_errors"] += 1
                raise
            finally:
                duration = time.time() - start_time
                self.metrics[f"{name}_duration"] = duration
        
        wrapped_stage.__name__ = name
        self.stages.append(wrapped_stage)
        return self
    
    async def process_async(self, data: T) -> U:
        """异步处理单个数据项"""
        current_data = data
        
        for stage in self.stages:
            current_data = await stage(current_data)
        
        return current_data
    
    async def process_stream_async(self, data_stream: AsyncIterator[T]) -> AsyncIterator[U]:
        """异步处理数据流"""
        async for item in data_stream:
            try:
                result = await self.process_async(item)
                if result is not None:
                    yield result
            except Exception as e:
                self.logger.error(f"Async stream processing error: {e}")
                self.metrics['async_stream_errors'] += 1

# 管道示例
class PipelineExamples:
    """管道使用示例"""
    
    @staticmethod
    def basic_pipeline_example():
        """基础管道示例"""
        # 创建数据处理管道
        pipeline = (Pipeline("DataProcessor")
                   .map("square", lambda x: x ** 2)
                   .filter("even_only", lambda x: x % 2 == 0)
                   .map("add_prefix", lambda x: f"result_{x}")
                   .map("to_upper", lambda s: s.upper()))
        
        # 处理数据
        test_data = list(range(1, 11))
        results = []
        
        for item in test_data:
            try:
                result = pipeline.process(item)
                if result:  # 过滤阶段可能返回None
                    results.append(result)
            except Exception:
                pass  # 跳过错误项
        
        return {
            'input': test_data,
            'output': results,
            'metrics': pipeline.get_metrics()
        }
    
    @staticmethod
    def parallel_pipeline_example():
        """并行管道示例"""
        # 创建并行管道
        pipeline = (ParallelPipeline("ParallelProcessor", num_workers=4)
                   .map("heavy_compute", lambda x: x ** 3 + x ** 2 + x)  # 模拟重计算
                   .filter("large_only", lambda x: x > 100)
                   .map("normalize", lambda x: x / 1000))
        
        # 处理大量数据
        test_data = list(range(1, 101))
        results = pipeline.process_parallel(test_data)
        
        return {
            'processed_count': len(results),
            'sample_results': results[:10],
            'metrics': pipeline.get_metrics()
        }
    
    @staticmethod
    async def async_pipeline_example():
        """异步管道示例"""
        # 创建异步管道
        pipeline = AsyncPipeline("AsyncProcessor")
        
        # 添加异步处理阶段
        async def async_fetch(data):
            await asyncio.sleep(0.01)  # 模拟异步IO
            return data * 2
        
        def sync_transform(data):
            return f"processed_{data}"
        
        pipeline.add_async_stage("fetch", async_fetch)
        pipeline.add_async_stage("transform", sync_transform)
        
        # 处理数据
        test_data = [1, 2, 3, 4, 5]
        results = []
        
        for item in test_data:
            result = await pipeline.process_async(item)
            results.append(result)
        
        return {
            'input': test_data,
            'output': results,
            'metrics': dict(pipeline.metrics)
        }
    
    @staticmethod
    def complex_pipeline_example():
        """复杂管道示例"""
        # 多阶段数据处理管道
        pipeline = Pipeline("ComplexProcessor")
        
        # 数据验证阶段
        def validate_data(data):
            if not isinstance(data, dict) or 'value' not in data:
                raise ValueError("Invalid data format")
            return data
        
        # 数据清洗阶段
        def clean_data(data):
            return {
                'value': max(0, data['value']),  # 确保非负
                'metadata': data.get('metadata', {}),
                'processed': True
            }
        
        # 数据增强阶段
        def enrich_data(data):
            data['enriched'] = {
                'doubled': data['value'] * 2,
                'squared': data['value'] ** 2,
                'timestamp': time.time()
            }
            return data
        
        # 构建管道
        (pipeline
         .map("validate", validate_data, retry_count=2)
         .map("clean", clean_data)
         .filter("positive_only", lambda d: d['value'] > 0)
         .map("enrich", enrich_data))
        
        # 测试数据
        test_data = [
            {'value': 10, 'metadata': {'source': 'A'}},
            {'value': -5, 'metadata': {'source': 'B'}},
            {'value': 0, 'metadata': {'source': 'C'}},
            {'value': 25, 'metadata': {'source': 'D'}},
        ]
        
        results = pipeline.process_batch(test_data)
        
        return {
            'processed_count': len(results),
            'results': results,
            'metrics': pipeline.get_metrics()
        }

# 使用示例
def demonstrate_pipelines():
    """演示管道模式"""
    print("=== 管道模式示例 ===\n")
    
    # 1. 基础管道
    print("1. 基础管道:")
    basic_result = PipelineExamples.basic_pipeline_example()
    print(f"输入: {basic_result['input']}")
    print(f"输出: {basic_result['output']}")
    
    # 2. 并行管道
    print("\n2. 并行管道:")
    parallel_result = PipelineExamples.parallel_pipeline_example()
    print(f"处理数量: {parallel_result['processed_count']}")
    print(f"示例结果: {parallel_result['sample_results']}")
    
    # 3. 复杂管道
    print("\n3. 复杂管道:")
    complex_result = PipelineExamples.complex_pipeline_example()
    print(f"处理数量: {complex_result['processed_count']}")
    print(f"结果示例: {complex_result['results'][0] if complex_result['results'] else 'None'}")

async def demonstrate_async_pipeline():
    """演示异步管道"""
    print("\n4. 异步管道:")
    async_result = await PipelineExamples.async_pipeline_example()
    print(f"输入: {async_result['input']}")
    print(f"输出: {async_result['output']}")

if __name__ == "__main__":
    demonstrate_pipelines()
    
    # 运行异步示例
    asyncio.run(demonstrate_async_pipeline())