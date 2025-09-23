"""
FastAPI Web接口实现

提供Web API接口用于演示各种Python高级用法：
- 示例代码执行
- 性能基准测试
- 实时监控数据
- 交互式演示
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
import asyncio
import json
import time
import traceback
from pathlib import Path
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# 导入示例模块
from ..core.example_manager import ExampleManager, ExampleResult
from ..core.performance_monitor import PerformanceMonitor
from ..language_features.advanced_decorators import (
    CacheDecorator, RateLimitDecorator, RetryDecorator
)
from ..concurrency.async_programming import AsyncTaskManager
from ..data_processing.functional_programming import (
    FunctionalUtils, Maybe, Either
)
from ..data_processing.pipeline import Pipeline

# 数据模型
class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="要执行的Python代码")
    example_type: str = Field("general", description="示例类型")
    timeout: int = Field(30, description="超时时间（秒）")

class CodeExecutionResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    memory_usage: Optional[float] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None

class ExampleRequest(BaseModel):
    category: str = Field(..., description="示例分类")
    name: str = Field(..., description="示例名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="示例参数")

class PerformanceTestRequest(BaseModel):
    test_type: str = Field(..., description="测试类型")
    iterations: int = Field(1000, description="迭代次数")
    data_size: int = Field(1000, description="数据大小")

class MonitoringData(BaseModel):
    timestamp: float
    cpu_usage: float
    memory_usage: float
    active_tasks: int
    request_count: int

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="Python高级用法示例系统",
        description="展示Python高级编程概念和最佳实践的Web演示系统",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 全局变量
    app.state.example_manager = ExampleManager()
    app.state.performance_monitor = PerformanceMonitor()
    app.state.request_count = 0
    
    # 静态文件和模板
    static_dir = Path(__file__).parent / "static"
    templates_dir = Path(__file__).parent / "templates"
    
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    templates = Jinja2Templates(directory=templates_dir if templates_dir.exists() else Path(__file__).parent)
    
    return app

class ExampleAPI:
    """示例API处理器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home():
            """首页"""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Python高级用法示例系统</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                    .code { background: #f5f5f5; padding: 10px; font-family: monospace; border-radius: 3px; }
                    button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 3px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Python高级用法示例系统</h1>
                    <div class="section">
                        <h2>功能概览</h2>
                        <ul>
                            <li><a href="/docs">API文档</a> - 查看完整的API文档</li>
                            <li><a href="/examples">示例列表</a> - 浏览所有可用示例</li>
                            <li><a href="/monitor">性能监控</a> - 实时系统监控</li>
                            <li><a href="/playground">代码运行场</a> - 在线执行Python代码</li>
                        </ul>
                    </div>
                    <div class="section">
                        <h2>快速开始</h2>
                        <p>使用以下API端点开始探索：</p>
                        <div class="code">
                            GET /api/examples/categories - 获取示例分类<br>
                            POST /api/examples/run - 运行示例代码<br>
                            POST /api/code/execute - 执行自定义代码<br>
                            GET /api/performance/benchmark - 性能基准测试
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        
        @self.app.get("/api/examples/categories")
        async def get_example_categories():
            """获取示例分类"""
            return {
                "categories": [
                    {
                        "name": "language_features",
                        "title": "语言特性",
                        "description": "Python高级语言特性示例",
                        "examples": [
                            "advanced_decorators",
                            "context_managers",
                            "generators_iterators",
                            "type_hints"
                        ]
                    },
                    {
                        "name": "concurrency",
                        "title": "并发编程",
                        "description": "异步和并发编程示例",
                        "examples": [
                            "async_programming",
                            "threading_examples",
                            "multiprocessing_examples"
                        ]
                    },
                    {
                        "name": "data_processing",
                        "title": "数据处理",
                        "description": "函数式编程和数据流处理",
                        "examples": [
                            "functional_programming",
                            "data_streams",
                            "pipeline_processing",
                            "reactive_programming"
                        ]
                    },
                    {
                        "name": "metaprogramming",
                        "title": "元编程",
                        "description": "元类、描述符和动态编程",
                        "examples": [
                            "metaclasses",
                            "descriptors",
                            "dynamic_classes"
                        ]
                    },
                    {
                        "name": "performance",
                        "title": "性能优化",
                        "description": "内存优化和性能提升技术",
                        "examples": [
                            "memory_optimization",
                            "caching_strategies",
                            "algorithm_optimization"
                        ]
                    }
                ]
            }
        
        @self.app.post("/api/examples/run", response_model=CodeExecutionResponse)
        async def run_example(request: ExampleRequest):
            """运行指定示例"""
            try:
                start_time = time.time()
                
                # 根据分类和名称执行相应示例
                result = await self._execute_example(
                    request.category, 
                    request.name, 
                    request.parameters
                )
                
                execution_time = time.time() - start_time
                
                return CodeExecutionResponse(
                    success=True,
                    result=str(result),
                    execution_time=execution_time
                )
                
            except Exception as e:
                return CodeExecutionResponse(
                    success=False,
                    error=str(e),
                    execution_time=time.time() - start_time
                )
        
        @self.app.post("/api/code/execute", response_model=CodeExecutionResponse)
        async def execute_code(request: CodeExecutionRequest):
            """执行自定义代码"""
            try:
                start_time = time.time()
                
                # 捕获输出
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                # 创建安全的执行环境
                safe_globals = {
                    '__builtins__': {
                        'print': print,
                        'len': len,
                        'range': range,
                        'list': list,
                        'dict': dict,
                        'tuple': tuple,
                        'set': set,
                        'str': str,
                        'int': int,
                        'float': float,
                        'bool': bool,
                        'enumerate': enumerate,
                        'zip': zip,
                        'map': map,
                        'filter': filter,
                        'sum': sum,
                        'max': max,
                        'min': min,
                        'abs': abs,
                        'round': round,
                    }
                }
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # 使用exec执行代码
                    exec(request.code, safe_globals)
                
                execution_time = time.time() - start_time
                stdout_output = stdout_capture.getvalue()
                stderr_output = stderr_capture.getvalue()
                
                return CodeExecutionResponse(
                    success=True,
                    result="代码执行完成",
                    execution_time=execution_time,
                    stdout=stdout_output if stdout_output else None,
                    stderr=stderr_output if stderr_output else None
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                return CodeExecutionResponse(
                    success=False,
                    error=str(e),
                    execution_time=execution_time,
                    stderr=traceback.format_exc()
                )
    
    async def _execute_example(self, category: str, name: str, parameters: Dict[str, Any]) -> Any:
        """执行具体示例"""
        if category == "language_features":
            return await self._run_language_feature_example(name, parameters)
        elif category == "concurrency":
            return await self._run_concurrency_example(name, parameters)
        elif category == "data_processing":
            return await self._run_data_processing_example(name, parameters)
        elif category == "metaprogramming":
            return await self._run_metaprogramming_example(name, parameters)
        elif category == "performance":
            return await self._run_performance_example(name, parameters)
        else:
            raise ValueError(f"未知的示例分类: {category}")
    
    async def _run_language_feature_example(self, name: str, parameters: Dict[str, Any]) -> Any:
        """运行语言特性示例"""
        if name == "advanced_decorators":
            # 演示高级装饰器
            cache = CacheDecorator()
            
            @cache
            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            
            n = parameters.get("n", 10)
            result = fibonacci(n)
            return {"fibonacci": result, "cache_info": cache.cache_info()}
            
        elif name == "context_managers":
            # 演示上下文管理器
            from ..language_features.context_managers import ResourceManager
            
            with ResourceManager("demo_resource") as resource:
                return resource.get_info()
        
        return f"示例 {name} 执行完成"
    
    async def _run_concurrency_example(self, name: str, parameters: Dict[str, Any]) -> Any:
        """运行并发编程示例"""
        if name == "async_programming":
            # 演示异步编程
            task_manager = AsyncTaskManager()
            
            async def sample_task(task_id: int):
                await asyncio.sleep(0.1)
                return f"Task {task_id} completed"
            
            tasks = [sample_task(i) for i in range(parameters.get("task_count", 5))]
            results = await task_manager.run_tasks(tasks)
            return {"completed_tasks": len(results), "results": results[:3]}
        
        return f"示例 {name} 执行完成"
    
    async def _run_data_processing_example(self, name: str, parameters: Dict[str, Any]) -> Any:
        """运行数据处理示例"""
        if name == "functional_programming":
            # 演示函数式编程
            numbers = list(range(1, parameters.get("count", 11)))
            
            # 使用Maybe Monad
            maybe_result = Maybe.unit(numbers).map(
                lambda lst: [x * 2 for x in lst if x % 2 == 0]
            )
            
            return {"input": numbers, "result": maybe_result.value}
            
        elif name == "pipeline_processing":
            # 演示管道处理
            pipeline = (Pipeline("demo_pipeline")
                       .map("square", lambda x: x ** 2)
                       .filter("even_only", lambda x: x % 2 == 0)
                       .map("add_prefix", lambda x: f"result_{x}"))
            
            test_data = list(range(1, parameters.get("count", 6)))
            results = pipeline.process_batch(test_data)
            
            return {"input": test_data, "results": results}
        
        return f"示例 {name} 执行完成"
    
    async def _run_metaprogramming_example(self, name: str, parameters: Dict[str, Any]) -> Any:
        """运行元编程示例"""
        if name == "metaclasses":
            # 演示元类
            from ..metaprogramming.metaclasses import SingletonMeta
            
            class Config(metaclass=SingletonMeta):
                def __init__(self):
                    self.value = parameters.get("config_value", "default")
            
            config1 = Config()
            config2 = Config()
            
            return {
                "is_singleton": config1 is config2,
                "config_value": config1.value
            }
        
        return f"示例 {name} 执行完成"
    
    async def _run_performance_example(self, name: str, parameters: Dict[str, Any]) -> Any:
        """运行性能优化示例"""
        if name == "caching_strategies":
            # 演示缓存策略
            from ..performance.caching_strategies import LRUCache
            
            cache = LRUCache(maxsize=parameters.get("cache_size", 100))
            
            # 模拟缓存使用
            for i in range(parameters.get("operations", 50)):
                key = f"key_{i % 10}"  # 重复一些键
                cache.set(key, f"value_{i}")
            
            return {
                "cache_size": len(cache),
                "hit_rate": cache.hit_rate(),
                "miss_rate": cache.miss_rate()
            }
        
        return f"示例 {name} 执行完成"

class PerformanceAPI:
    """性能API处理器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """设置性能API路由"""
        
        @self.app.post("/api/performance/benchmark")
        async def run_benchmark(request: PerformanceTestRequest):
            """运行性能基准测试"""
            try:
                start_time = time.time()
                
                if request.test_type == "list_comprehension":
                    # 列表推导式性能测试
                    results = []
                    for _ in range(request.iterations):
                        data = [x ** 2 for x in range(request.data_size)]
                        results.append(len(data))
                    
                elif request.test_type == "generator_expression":
                    # 生成器表达式性能测试
                    results = []
                    for _ in range(request.iterations):
                        data = (x ** 2 for x in range(request.data_size))
                        results.append(sum(1 for _ in data))
                    
                elif request.test_type == "dictionary_creation":
                    # 字典创建性能测试
                    results = []
                    for _ in range(request.iterations):
                        data = {f"key_{i}": i ** 2 for i in range(request.data_size)}
                        results.append(len(data))
                
                else:
                    raise ValueError(f"未知的测试类型: {request.test_type}")
                
                execution_time = time.time() - start_time
                
                return {
                    "test_type": request.test_type,
                    "iterations": request.iterations,
                    "data_size": request.data_size,
                    "total_time": execution_time,
                    "avg_time_per_iteration": execution_time / request.iterations,
                    "operations_per_second": request.iterations / execution_time if execution_time > 0 else 0
                }
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

class MonitoringAPI:
    """监控API处理器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """设置监控API路由"""
        
        @self.app.get("/api/monitor/status")
        async def get_system_status():
            """获取系统状态"""
            import psutil
            
            return {
                "timestamp": time.time(),
                "cpu_usage": psutil.cpu_percent(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "request_count": getattr(self.app.state, 'request_count', 0)
            }
        
        @self.app.get("/api/monitor/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy", "timestamp": time.time()}

def setup_web_app() -> FastAPI:
    """设置完整的Web应用"""
    app = create_app()
    
    # 初始化API处理器
    example_api = ExampleAPI(app)
    performance_api = PerformanceAPI(app)
    monitoring_api = MonitoringAPI(app)
    
    # 中间件：请求计数
    @app.middleware("http")
    async def count_requests(request, call_next):
        app.state.request_count = getattr(app.state, 'request_count', 0) + 1
        response = await call_next(request)
        return response
    
    return app

# 创建应用实例
app = setup_web_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)