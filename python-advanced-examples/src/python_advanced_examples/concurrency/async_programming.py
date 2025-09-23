"""
asyncio异步编程

展示Python异步编程的高级用法，包括异步任务管理、上下文管理器、生成器等。
"""

import asyncio
import aiohttp
import time
from typing import AsyncGenerator, AsyncIterator, List, Optional, Callable, Any, Dict
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
import random
from concurrent.futures import ThreadPoolExecutor

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    result: Any
    execution_time: float
    success: bool
    error: Optional[str] = None


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.running_tasks = set()
        self.completed_tasks = []
    
    async def submit_task(self, task_id: str, coro: Callable, *args, **kwargs) -> TaskResult:
        """提交异步任务"""
        async with self.semaphore:
            start_time = time.time()
            try:
                result = await coro(*args, **kwargs)
                execution_time = time.time() - start_time
                
                task_result = TaskResult(
                    task_id=task_id,
                    result=result,
                    execution_time=execution_time,
                    success=True
                )
                
                self.completed_tasks.append(task_result)
                return task_result
                
            except Exception as e:
                execution_time = time.time() - start_time
                task_result = TaskResult(
                    task_id=task_id,
                    result=None,
                    execution_time=execution_time,
                    success=False,
                    error=str(e)
                )
                
                self.completed_tasks.append(task_result)
                return task_result
    
    async def submit_batch(self, tasks: List[tuple]) -> List[TaskResult]:
        """批量提交任务"""
        coroutines = [
            self.submit_task(task_id, coro, *args, **kwargs)
            for task_id, coro, args, kwargs in tasks
        ]
        
        return await asyncio.gather(*coroutines, return_exceptions=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_tasks = len(self.completed_tasks)
        successful_tasks = sum(1 for task in self.completed_tasks if task.success)
        
        if total_tasks == 0:
            return {"total": 0, "success_rate": 0, "average_time": 0}
        
        total_time = sum(task.execution_time for task in self.completed_tasks)
        average_time = total_time / total_tasks
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "success_rate": successful_tasks / total_tasks,
            "average_execution_time": average_time,
            "total_execution_time": total_time
        }


class AsyncContextManager:
    """异步上下文管理器"""
    
    def __init__(self, resource_name: str, setup_time: float = 0.1):
        self.resource_name = resource_name
        self.setup_time = setup_time
        self.resource = None
    
    async def __aenter__(self):
        """异步进入上下文"""
        logger.info(f"Setting up async resource: {self.resource_name}")
        await asyncio.sleep(self.setup_time)  # 模拟异步设置
        
        self.resource = f"AsyncResource-{self.resource_name}-{int(time.time())}"
        logger.info(f"Async resource ready: {self.resource}")
        return self.resource
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文"""
        if self.resource:
            logger.info(f"Cleaning up async resource: {self.resource}")
            await asyncio.sleep(0.05)  # 模拟异步清理
            self.resource = None
            
        if exc_type:
            logger.warning(f"Async context exited with exception: {exc_type.__name__}")
        
        return False  # 不抑制异常


class AsyncGenerator:
    """异步生成器示例"""
    
    @staticmethod
    async def async_range(start: int, stop: int, delay: float = 0.1) -> AsyncGenerator[int, None]:
        """异步范围生成器"""
        for i in range(start, stop):
            await asyncio.sleep(delay)
            yield i
    
    @staticmethod
    async def async_fetch_data(urls: List[str]) -> AsyncGenerator[Dict[str, Any], None]:
        """异步数据获取生成器"""
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    # 模拟HTTP请求
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                    # 模拟响应数据
                    data = {
                        "url": url,
                        "status": 200,
                        "data": f"Content from {url}",
                        "timestamp": time.time()
                    }
                    
                    yield data
                    
                except Exception as e:
                    yield {
                        "url": url,
                        "status": 500,
                        "error": str(e),
                        "timestamp": time.time()
                    }


class AsyncPool:
    """异步连接池"""
    
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.connections = asyncio.Queue(maxsize=pool_size)
        self.created_connections = 0
        self.lock = asyncio.Lock()
    
    async def _create_connection(self) -> str:
        """创建新连接"""
        await asyncio.sleep(0.1)  # 模拟连接创建时间
        connection_id = f"conn_{self.created_connections}"
        self.created_connections += 1
        logger.info(f"Created new connection: {connection_id}")
        return connection_id
    
    async def get_connection(self) -> str:
        """获取连接"""
        try:
            # 尝试从池中获取现有连接
            connection = self.connections.get_nowait()
            logger.info(f"Reused connection: {connection}")
            return connection
        except asyncio.QueueEmpty:
            # 池中没有可用连接，创建新的
            async with self.lock:
                if self.created_connections < self.pool_size:
                    return await self._create_connection()
                else:
                    # 等待连接归还
                    logger.info("Waiting for connection to be returned...")
                    return await self.connections.get()
    
    async def return_connection(self, connection: str):
        """归还连接"""
        try:
            self.connections.put_nowait(connection)
            logger.info(f"Returned connection: {connection}")
        except asyncio.QueueFull:
            logger.warning(f"Connection pool full, discarding: {connection}")


async def async_http_client(urls: List[str], max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """异步HTTP客户端"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_url(session, url):
        async with semaphore:
            try:
                # 模拟HTTP请求
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                return {
                    "url": url,
                    "status": 200,
                    "content_length": random.randint(1000, 5000),
                    "response_time": random.uniform(0.1, 0.3)
                }
                
            except Exception as e:
                return {
                    "url": url,
                    "status": 500,
                    "error": str(e)
                }
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)


@asynccontextmanager
async def async_transaction():
    """异步事务上下文管理器"""
    transaction_id = f"txn_{int(time.time())}"
    logger.info(f"Starting transaction: {transaction_id}")
    
    try:
        await asyncio.sleep(0.01)  # 模拟事务开始
        yield transaction_id
        
        # 模拟提交
        await asyncio.sleep(0.01)
        logger.info(f"Transaction committed: {transaction_id}")
        
    except Exception as e:
        # 模拟回滚
        await asyncio.sleep(0.01)
        logger.error(f"Transaction rolled back: {transaction_id}, error: {e}")
        raise


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="async_example_basic",
    category=ExampleCategory.ASYNC_PROGRAMMING,
    difficulty=DifficultyLevel.BEGINNER,
    description="基础异步编程示例",
    tags=["asyncio", "basic", "coroutines"]
)
@demo(title="基础异步编程示例")
def async_example_basic():
    """展示基础异步编程概念"""
    
    async def simple_async_function(name: str, delay: float) -> str:
        """简单的异步函数"""
        print(f"开始执行 {name}")
        await asyncio.sleep(delay)
        print(f"完成执行 {name}")
        return f"结果：{name}"
    
    async def main():
        print("顺序执行示例：")
        start_time = time.time()
        
        result1 = await simple_async_function("任务1", 1.0)
        result2 = await simple_async_function("任务2", 0.5)
        
        sequential_time = time.time() - start_time
        print(f"顺序执行耗时: {sequential_time:.2f}s")
        print(f"结果: {result1}, {result2}")
        
        print("\n并发执行示例：")
        start_time = time.time()
        
        # 并发执行
        results = await asyncio.gather(
            simple_async_function("任务A", 1.0),
            simple_async_function("任务B", 0.5),
            simple_async_function("任务C", 0.3)
        )
        
        concurrent_time = time.time() - start_time
        print(f"并发执行耗时: {concurrent_time:.2f}s")
        print(f"结果: {results}")
        
        print(f"\n性能提升: {sequential_time/concurrent_time:.1f}x")
    
    # 运行异步主函数
    asyncio.run(main())


@example(
    name="async_task_manager_example",
    category=ExampleCategory.ASYNC_PROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="异步任务管理器示例",
    tags=["asyncio", "task-management", "concurrency"]
)
@demo(title="异步任务管理器示例")
def async_task_manager_example():
    """展示异步任务管理器的用法"""
    
    async def cpu_bound_task(task_id: str, complexity: int) -> str:
        """CPU密集型任务模拟"""
        await asyncio.sleep(0.1)  # 模拟一些异步操作
        
        # 在线程池中执行CPU密集型计算
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                lambda: sum(i * i for i in range(complexity))
            )
        
        return f"任务{task_id}完成，结果: {result}"
    
    async def io_bound_task(task_id: str, delay: float) -> str:
        """I/O密集型任务模拟"""
        await asyncio.sleep(delay)
        return f"任务{task_id}完成，延迟: {delay}s"
    
    async def main():
        print("异步任务管理器示例")
        
        manager = AsyncTaskManager(max_concurrent=3)
        
        # 准备任务列表
        tasks = []
        
        # 添加CPU密集型任务
        for i in range(3):
            tasks.append((
                f"cpu_{i}",
                cpu_bound_task,
                (f"CPU_{i}", 1000 + i * 500),
                {}
            ))
        
        # 添加I/O密集型任务
        for i in range(5):
            tasks.append((
                f"io_{i}",
                io_bound_task,
                (f"IO_{i}", random.uniform(0.5, 1.5)),
                {}
            ))
        
        print(f"提交 {len(tasks)} 个任务...")
        start_time = time.time()
        
        results = await manager.submit_batch(tasks)
        
        total_time = time.time() - start_time
        print(f"所有任务完成，总耗时: {total_time:.2f}s")
        
        # 显示结果
        print("\n任务结果:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.task_id}: {result.result or result.error} "
                  f"({result.execution_time:.3f}s)")
        
        # 显示统计信息
        stats = manager.get_statistics()
        print(f"\n统计信息:")
        print(f"总任务数: {stats['total_tasks']}")
        print(f"成功率: {stats['success_rate']:.1%}")
        print(f"平均执行时间: {stats['average_execution_time']:.3f}s")
    
    asyncio.run(main())


@example(
    name="async_context_manager_example",
    category=ExampleCategory.ASYNC_PROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="异步上下文管理器示例",
    tags=["asyncio", "context-managers", "resources"]
)
@demo(title="异步上下文管理器示例")
def async_context_manager_example():
    """展示异步上下文管理器的用法"""
    
    async def main():
        print("异步上下文管理器示例")
        
        # 基本异步上下文管理器
        print("\n1. 基本异步上下文管理器:")
        async with AsyncContextManager("database") as resource:
            print(f"使用资源: {resource}")
            await asyncio.sleep(0.2)  # 模拟使用资源
        
        # 异步事务示例
        print("\n2. 异步事务示例:")
        try:
            async with async_transaction() as txn_id:
                print(f"在事务中执行操作: {txn_id}")
                await asyncio.sleep(0.1)
                # raise Exception("模拟错误")  # 取消注释以测试回滚
                print("事务操作完成")
        except Exception as e:
            print(f"事务失败: {e}")
        
        # 嵌套异步上下文管理器
        print("\n3. 嵌套异步上下文管理器:")
        async with AsyncContextManager("connection_pool") as pool:
            async with AsyncContextManager("session") as session:
                print(f"使用连接池: {pool}")
                print(f"使用会话: {session}")
                await asyncio.sleep(0.1)
    
    asyncio.run(main())


@example(
    name="async_generator_example",
    category=ExampleCategory.ASYNC_PROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="异步生成器示例",
    tags=["asyncio", "generators", "streaming"]
)
@demo(title="异步生成器示例")
def async_generator_example():
    """展示异步生成器的用法"""
    
    async def main():
        print("异步生成器示例")
        
        # 异步范围生成器
        print("\n1. 异步范围生成器:")
        async for num in AsyncGenerator.async_range(1, 6, 0.2):
            print(f"生成数字: {num}")
        
        # 异步数据获取生成器
        print("\n2. 异步数据获取生成器:")
        urls = [
            "https://api.example.com/users",
            "https://api.example.com/posts", 
            "https://api.example.com/comments"
        ]
        
        async for response in AsyncGenerator.async_fetch_data(urls):
            if response.get("status") == 200:
                print(f"✅ {response['url']}: {response['data']}")
            else:
                print(f"❌ {response['url']}: {response.get('error', 'Unknown error')}")
        
        # 异步生成器推导
        print("\n3. 异步生成器推导:")
        async def async_squares(n):
            for i in range(n):
                await asyncio.sleep(0.1)
                yield i * i
        
        squares = [x async for x in async_squares(5)]
        print(f"异步生成的平方数: {squares}")
    
    asyncio.run(main())


@example(
    name="async_pool_example",
    category=ExampleCategory.ASYNC_PROGRAMMING,
    difficulty=DifficultyLevel.ADVANCED,
    description="异步连接池示例",
    tags=["asyncio", "connection-pool", "resource-management"]
)
@demo(title="异步连接池示例")
def async_pool_example():
    """展示异步连接池的用法"""
    
    async def worker(worker_id: int, pool: AsyncPool, work_items: int):
        """工作协程"""
        results = []
        
        for i in range(work_items):
            # 获取连接
            connection = await pool.get_connection()
            
            try:
                # 模拟使用连接执行工作
                await asyncio.sleep(random.uniform(0.1, 0.3))
                result = f"Worker{worker_id}-Item{i}-{connection}"
                results.append(result)
                print(f"Worker {worker_id} 完成项目 {i} 使用 {connection}")
                
            finally:
                # 归还连接
                await pool.return_connection(connection)
        
        return results
    
    async def main():
        print("异步连接池示例")
        
        # 创建连接池 (最大5个连接)
        pool = AsyncPool(pool_size=3)
        
        print("\n启动多个工作协程...")
        
        # 创建多个工作协程
        workers = [
            worker(i, pool, 3) for i in range(4)  # 4个工作协程，每个处理3个项目
        ]
        
        start_time = time.time()
        
        # 并发执行所有工作协程
        all_results = await asyncio.gather(*workers)
        
        execution_time = time.time() - start_time
        
        print(f"\n所有工作完成，耗时: {execution_time:.2f}s")
        print(f"总共处理了 {sum(len(results) for results in all_results)} 个项目")
        print(f"连接池创建了 {pool.created_connections} 个连接")
    
    asyncio.run(main())


@example(
    name="async_http_client_example",
    category=ExampleCategory.ASYNC_PROGRAMMING,
    difficulty=DifficultyLevel.ADVANCED,
    description="异步HTTP客户端示例",
    tags=["asyncio", "http", "concurrent-requests"]
)
@demo(title="异步HTTP客户端示例")
def async_http_client_example():
    """展示异步HTTP客户端的用法"""
    
    async def main():
        print("异步HTTP客户端示例")
        
        # 准备URL列表
        urls = [
            f"https://api.example.com/endpoint{i}"
            for i in range(10)
        ]
        
        print(f"准备并发请求 {len(urls)} 个URL...")
        
        start_time = time.time()
        
        # 使用异步HTTP客户端
        results = await async_http_client(urls, max_concurrent=3)
        
        execution_time = time.time() - start_time
        
        print(f"所有请求完成，耗时: {execution_time:.2f}s")
        
        # 统计结果
        successful = sum(1 for r in results if r.get("status") == 200)
        failed = len(results) - successful
        
        print(f"\n请求统计:")
        print(f"成功: {successful}")
        print(f"失败: {failed}")
        print(f"成功率: {successful/len(results):.1%}")
        
        # 显示部分结果
        print(f"\n前5个请求结果:")
        for i, result in enumerate(results[:5]):
            status = "✅" if result.get("status") == 200 else "❌"
            print(f"{status} {result['url']}: "
                  f"状态={result.get('status')}, "
                  f"响应时间={result.get('response_time', 'N/A'):.3f}s")
    
    asyncio.run(main())


# 导出的类和函数
__all__ = [
    "AsyncTaskManager",
    "AsyncContextManager",
    "AsyncGenerator", 
    "AsyncPool",
    "async_http_client",
    "async_transaction",
    "async_example_basic",
    "async_task_manager_example",
    "async_context_manager_example",
    "async_generator_example",
    "async_pool_example",
    "async_http_client_example"
]