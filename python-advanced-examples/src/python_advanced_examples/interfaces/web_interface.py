"""
Web演示界面

提供基于FastAPI的Web界面，用于在浏览器中运行和展示示例。
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

from .. import registry, runner
from ..core.registry import ExampleCategory, DifficultyLevel

# 数据模型
class ExampleInfo(BaseModel):
    name: str
    category: str
    difficulty: str
    description: str
    tags: List[str]
    source_code: Optional[str] = None


class RunRequest(BaseModel):
    example_name: str
    timeout: Optional[float] = None
    memory_limit_mb: Optional[int] = None


class RunResponse(BaseModel):
    success: bool
    status: str
    output: str
    error: Optional[str] = None
    execution_time: float
    memory_usage: float


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title="Python高级用法示例系统",
        description="在浏览器中运行和学习Python高级特性",
        version="1.0.0"
    )
    
    # 静态文件目录（如果存在）
    static_dir = Path(__file__).parent.parent.parent.parent / "web" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # 模板目录
    template_dir = Path(__file__).parent.parent.parent.parent / "web" / "templates"
    if template_dir.exists():
        templates = Jinja2Templates(directory=str(template_dir))
    else:
        templates = None
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """主页"""
        if templates:
            return templates.TemplateResponse("index.html", {"request": request})
        else:
            # 简单的HTML页面
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Python高级用法示例系统</title>
                <meta charset="utf-8">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        max-width: 1200px; 
                        margin: 0 auto; 
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .header { 
                        text-align: center; 
                        color: #2c3e50;
                        margin-bottom: 30px;
                    }
                    .card {
                        background: white;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .examples-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px;
                    }
                    .example-card {
                        border-left: 4px solid #3498db;
                        transition: transform 0.2s;
                    }
                    .example-card:hover {
                        transform: translateY(-2px);
                    }
                    .example-title {
                        color: #2c3e50;
                        margin: 0 0 10px 0;
                    }
                    .example-meta {
                        color: #7f8c8d;
                        font-size: 0.9em;
                        margin: 5px 0;
                    }
                    .run-button {
                        background: #3498db;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        cursor: pointer;
                        margin-top: 10px;
                    }
                    .run-button:hover {
                        background: #2980b9;
                    }
                    .output-area {
                        background: #2c3e50;
                        color: #ecf0f1;
                        padding: 20px;
                        border-radius: 4px;
                        font-family: 'Courier New', monospace;
                        white-space: pre-wrap;
                        margin-top: 20px;
                        display: none;
                    }
                    .loading {
                        color: #f39c12;
                    }
                    .success {
                        color: #27ae60;
                    }
                    .error {
                        color: #e74c3c;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🐍 Python高级用法示例系统</h1>
                    <p>在浏览器中运行和学习Python高级特性</p>
                </div>
                
                <div class="card">
                    <h2>API端点</h2>
                    <ul>
                        <li><a href="/api/examples">GET /api/examples</a> - 获取所有示例</li>
                        <li><a href="/api/categories">GET /api/categories</a> - 获取分类列表</li>
                        <li><a href="/api/stats">GET /api/stats</a> - 获取统计信息</li>
                        <li>POST /api/run - 运行示例</li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>可用示例</h2>
                    <div id="examples-container">
                        <p>加载中...</p>
                    </div>
                </div>
                
                <div id="output-panel" class="card output-area">
                    <h3>执行输出</h3>
                    <div id="output-content"></div>
                </div>
                
                <script>
                    // 加载示例列表
                    fetch('/api/examples')
                        .then(response => response.json())
                        .then(examples => {
                            const container = document.getElementById('examples-container');
                            if (examples.length === 0) {
                                container.innerHTML = '<p>没有可用的示例</p>';
                                return;
                            }
                            
                            const grid = document.createElement('div');
                            grid.className = 'examples-grid';
                            
                            examples.forEach(example => {
                                const card = document.createElement('div');
                                card.className = 'card example-card';
                                card.innerHTML = `
                                    <h3 class="example-title">${example.name}</h3>
                                    <div class="example-meta">分类: ${example.category}</div>
                                    <div class="example-meta">难度: ${example.difficulty}</div>
                                    <div class="example-meta">标签: ${example.tags.join(', ') || '无'}</div>
                                    <p>${example.description}</p>
                                    <button class="run-button" onclick="runExample('${example.name}')">
                                        运行示例
                                    </button>
                                `;
                                grid.appendChild(card);
                            });
                            
                            container.innerHTML = '';
                            container.appendChild(grid);
                        })
                        .catch(error => {
                            console.error('加载示例失败:', error);
                            document.getElementById('examples-container').innerHTML = 
                                '<p class="error">加载示例失败</p>';
                        });
                    
                    // 运行示例
                    function runExample(exampleName) {
                        const outputPanel = document.getElementById('output-panel');
                        const outputContent = document.getElementById('output-content');
                        
                        outputPanel.style.display = 'block';
                        outputContent.innerHTML = '<span class="loading">运行中...</span>';
                        
                        fetch('/api/run', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                example_name: exampleName
                            })
                        })
                        .then(response => response.json())
                        .then(result => {
                            const statusClass = result.success ? 'success' : 'error';
                            let output = `<span class="${statusClass}">[${result.status}]</span> ${exampleName}\\n`;
                            output += `执行时间: ${result.execution_time.toFixed(3)}s\\n`;
                            output += `内存使用: ${result.memory_usage.toFixed(1)}MB\\n\\n`;
                            
                            if (result.success && result.output) {
                                output += result.output;
                            } else if (result.error) {
                                output += `<span class="error">错误: ${result.error}</span>`;
                            }
                            
                            outputContent.innerHTML = output;
                        })
                        .catch(error => {
                            console.error('运行示例失败:', error);
                            outputContent.innerHTML = `<span class="error">运行失败: ${error}</span>`;
                        });
                    }
                </script>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
    
    @app.get("/api/examples", response_model=List[ExampleInfo])
    async def get_examples():
        """获取所有示例"""
        try:
            # 导入示例模块以确保示例已注册
            from ..language_features import advanced_decorators, context_managers, generators, type_hints
        except ImportError:
            pass
        
        examples = registry.list_examples()
        
        return [
            ExampleInfo(
                name=example.name,
                category=example.category.value,
                difficulty=example.difficulty.value,
                description=example.description,
                tags=list(example.tags),
                source_code=example.get_source_code()
            )
            for example in examples
        ]
    
    @app.get("/api/examples/{example_name}", response_model=ExampleInfo)
    async def get_example(example_name: str):
        """获取单个示例详情"""
        example = registry.get_example(example_name)
        if not example:
            raise HTTPException(status_code=404, detail="示例未找到")
        
        return ExampleInfo(
            name=example.name,
            category=example.category.value,
            difficulty=example.difficulty.value,
            description=example.description,
            tags=list(example.tags),
            source_code=example.get_source_code()
        )
    
    @app.post("/api/run", response_model=RunResponse)
    async def run_example(request: RunRequest):
        """运行示例"""
        if not registry.get_example(request.example_name):
            raise HTTPException(status_code=404, detail="示例未找到")
        
        result = runner.run(
            request.example_name,
            timeout=request.timeout,
            memory_limit_mb=request.memory_limit_mb,
            capture_output=True
        )
        
        return RunResponse(
            success=result.success,
            status=result.status.value,
            output=result.stdout or "",
            error=result.error,
            execution_time=result.execution_time,
            memory_usage=result.memory_usage
        )
    
    @app.get("/api/categories")
    async def get_categories():
        """获取所有分类"""
        categories = registry.get_categories()
        return [{"name": cat.value, "display_name": cat.value} for cat in categories]
    
    @app.get("/api/stats")
    async def get_stats():
        """获取统计信息"""
        return registry.get_statistics()
    
    @app.get("/api/search")
    async def search_examples(q: str, limit: int = 10):
        """搜索示例"""
        results = registry.search(q)[:limit]
        
        return [
            {
                "name": example.name,
                "category": example.category.value,
                "difficulty": example.difficulty.value,
                "description": example.description,
                "tags": list(example.tags)
            }
            for example in results
        ]
    
    return app


# 如果直接运行此文件
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)