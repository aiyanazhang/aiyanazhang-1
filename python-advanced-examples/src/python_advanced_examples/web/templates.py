"""
模板管理器

管理Web界面的HTML模板：
- 页面模板
- 组件模板
- 动态内容渲染
"""

from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
import json

class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        self._initialize_templates()
    
    def _initialize_templates(self):
        """初始化模板文件"""
        self._create_base_template()
        self._create_page_templates()
        self._create_component_templates()
    
    def _create_base_template(self):
        """创建基础模板"""
        base_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Python高级用法示例系统{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="container">
            <a href="/" class="navbar-brand">Python Advanced Examples</a>
            <ul class="navbar-nav">
                <li><a href="/">首页</a></li>
                <li><a href="/examples">示例</a></li>
                <li><a href="/playground">代码运行场</a></li>
                <li><a href="/performance">性能测试</a></li>
                <li><a href="/monitor">监控</a></li>
                <li><a href="/docs">API文档</a></li>
            </ul>
        </div>
    </nav>

    <!-- 主要内容 -->
    <main class="main-content">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 Python高级用法示例系统. All rights reserved.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="/static/js/main.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""
        
        with open(self.templates_dir / "base.html", "w", encoding="utf-8") as f:
            f.write(base_template)
    
    def _create_page_templates(self):
        """创建页面模板"""
        
        # 首页模板
        index_template = """
{% extends "base.html" %}

{% block title %}首页 - Python高级用法示例系统{% endblock %}

{% block content %}
<div class="section fade-in">
    <h1>Python高级用法示例系统</h1>
    <p class="lead">探索现代Python开发中的核心概念、设计模式和最佳实践</p>
</div>

<div class="grid grid-3">
    <div class="section">
        <h3>🚀 语言特性</h3>
        <p>深入了解Python的高级语言特性：装饰器、上下文管理器、生成器、类型提示等。</p>
        <a href="/examples?category=language_features" class="btn btn-primary">探索特性</a>
    </div>
    
    <div class="section">
        <h3>⚡ 并发编程</h3>
        <p>掌握异步编程、多线程和多进程处理技术，提升应用性能。</p>
        <a href="/examples?category=concurrency" class="btn btn-primary">学习并发</a>
    </div>
    
    <div class="section">
        <h3>🔧 数据处理</h3>
        <p>学习函数式编程、数据流处理和响应式编程的高级技术。</p>
        <a href="/examples?category=data_processing" class="btn btn-primary">处理数据</a>
    </div>
    
    <div class="section">
        <h3>🎭 元编程</h3>
        <p>探索元类、描述符和动态编程的强大功能。</p>
        <a href="/examples?category=metaprogramming" class="btn btn-primary">元编程</a>
    </div>
    
    <div class="section">
        <h3>📈 性能优化</h3>
        <p>了解内存优化、缓存策略和算法优化技术。</p>
        <a href="/examples?category=performance" class="btn btn-primary">优化性能</a>
    </div>
    
    <div class="section">
        <h3>🎮 在线体验</h3>
        <p>在浏览器中直接运行和测试Python代码。</p>
        <a href="/playground" class="btn btn-success">立即尝试</a>
    </div>
</div>

<div class="section">
    <h2>快速开始</h2>
    <div class="grid grid-2">
        <div>
            <h4>选择示例分类</h4>
            <p>从左侧导航栏选择您感兴趣的示例分类，每个分类包含多个实用示例。</p>
        </div>
        <div>
            <h4>运行代码</h4>
            <p>点击任何示例都可以看到完整的代码和运行结果，还可以修改参数进行实验。</p>
        </div>
        <div>
            <h4>性能测试</h4>
            <p>使用内置的性能测试工具比较不同实现方式的效率。</p>
        </div>
        <div>
            <h4>在线编辑</h4>
            <p>在代码运行场中编写和测试您自己的Python代码。</p>
        </div>
    </div>
</div>
{% endblock %}
"""
        
        with open(self.templates_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_template)
        
        # 示例页面模板
        examples_template = """
{% extends "base.html" %}

{% block title %}示例 - Python高级用法示例系统{% endblock %}

{% block content %}
<div class="section">
    <h1>Python高级用法示例</h1>
    <p>选择一个分类来探索相关的示例代码</p>
</div>

<div class="grid grid-2">
    <div class="section">
        <h2>示例分类</h2>
        <div id="categories-container">
            <!-- 分类将通过JavaScript动态加载 -->
            <div class="loading"></div>
            <p>加载示例分类中...</p>
        </div>
    </div>
    
    <div class="section">
        <h2>示例信息</h2>
        <div id="example-info">
            <p>请从左侧选择一个示例来查看详细信息。</p>
        </div>
        
        <h3>运行结果</h3>
        <div id="example-result">
            <p>选择并运行示例后，结果将在这里显示。</p>
        </div>
    </div>
</div>

<style>
.category-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    background: white;
}

.category-card h3 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.examples-list {
    margin-top: 1rem;
}

.example-btn {
    display: block;
    width: 100%;
    margin-bottom: 0.5rem;
    text-align: left;
}
</style>
{% endblock %}
"""
        
        with open(self.templates_dir / "examples.html", "w", encoding="utf-8") as f:
            f.write(examples_template)
        
        # 代码运行场模板
        playground_template = """
{% extends "base.html" %}

{% block title %}代码运行场 - Python高级用法示例系统{% endblock %}

{% block content %}
<div class="section">
    <h1>Python代码运行场</h1>
    <p>在浏览器中直接编写和运行Python代码</p>
</div>

<div class="grid grid-2">
    <div class="section">
        <h2>代码编辑器</h2>
        <div class="form-group">
            <label for="code-input" class="form-label">输入Python代码:</label>
            <textarea id="code-input" class="form-control code-editor" rows="15" placeholder="# 在这里输入您的Python代码
print('Hello, Python!')

# 示例：计算斐波那契数列
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f'fibonacci({i}) = {fibonacci(i)}')"></textarea>
        </div>
        
        <div class="form-group">
            <button id="execute-code" class="btn btn-primary">
                🚀 运行代码
            </button>
            <button onclick="document.getElementById('code-input').value=''" class="btn btn-secondary">
                🗑️ 清空
            </button>
        </div>
    </div>
    
    <div class="section">
        <h2>执行结果</h2>
        <div id="execution-result">
            <p>点击"运行代码"按钮来执行您的代码。</p>
        </div>
    </div>
</div>

<div class="section">
    <h2>代码示例</h2>
    <div class="grid grid-3">
        <div class="code-example">
            <h4>列表推导式</h4>
            <div class="code-block">
# 生成偶数平方
squares = [x**2 for x in range(10) if x % 2 == 0]
print(squares)
            </div>
            <button onclick="loadExample(this)" class="btn btn-secondary btn-sm">加载示例</button>
        </div>
        
        <div class="code-example">
            <h4>装饰器</h4>
            <div class="code-block">
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} took {end-start:.4f}s')
        return result
    return wrapper

@timer
def slow_function():
    import time
    time.sleep(0.1)
    return "Done!"

result = slow_function()
print(result)
            </div>
            <button onclick="loadExample(this)" class="btn btn-secondary btn-sm">加载示例</button>
        </div>
        
        <div class="code-example">
            <h4>生成器</h4>
            <div class="code-block">
def fibonacci_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 获取前10个斐波那契数
fib = fibonacci_generator()
for i in range(10):
    print(next(fib))
            </div>
            <button onclick="loadExample(this)" class="btn btn-secondary btn-sm">加载示例</button>
        </div>
    </div>
</div>

<script>
function loadExample(button) {
    const codeBlock = button.previousElementSibling;
    const code = codeBlock.textContent.trim();
    document.getElementById('code-input').value = code;
}
</script>

<style>
.code-example {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    background: white;
}

.code-example h4 {
    margin-bottom: 0.5rem;
    color: var(--primary-color);
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
}
</style>
{% endblock %}
"""
        
        with open(self.templates_dir / "playground.html", "w", encoding="utf-8") as f:
            f.write(playground_template)
        
        # 性能测试页面模板
        performance_template = """
{% extends "base.html" %}

{% block title %}性能测试 - Python高级用法示例系统{% endblock %}

{% block content %}
<div class="section">
    <h1>性能基准测试</h1>
    <p>比较不同Python实现方式的性能差异</p>
</div>

<div class="grid grid-2">
    <div class="section">
        <h2>测试配置</h2>
        <form id="benchmark-form">
            <div class="form-group">
                <label for="benchmark-type" class="form-label">测试类型:</label>
                <select id="benchmark-type" class="form-control">
                    <option value="list_comprehension">列表推导式</option>
                    <option value="generator_expression">生成器表达式</option>
                    <option value="dictionary_creation">字典创建</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="iterations" class="form-label">迭代次数:</label>
                <input type="number" id="iterations" class="form-control" value="1000" min="1" max="10000">
            </div>
            
            <div class="form-group">
                <label for="data-size" class="form-label">数据大小:</label>
                <input type="number" id="data-size" class="form-control" value="1000" min="1" max="100000">
            </div>
            
            <button type="button" id="run-benchmark" class="btn btn-primary">
                📊 运行基准测试
            </button>
        </form>
    </div>
    
    <div class="section">
        <h2>测试结果</h2>
        <div id="benchmark-result">
            <p>配置测试参数并点击"运行基准测试"来查看结果。</p>
        </div>
    </div>
</div>

<div class="section">
    <h2>性能优化建议</h2>
    <div class="grid grid-2">
        <div>
            <h4>🚀 列表推导式 vs 循环</h4>
            <p>列表推导式通常比传统for循环更快，代码也更简洁。</p>
            <div class="code-block">
# 快速方式
squares = [x**2 for x in range(1000)]

# 慢速方式
squares = []
for x in range(1000):
    squares.append(x**2)
            </div>
        </div>
        
        <div>
            <h4>⚡ 生成器 vs 列表</h4>
            <p>当处理大量数据时，生成器可以节省内存。</p>
            <div class="code-block">
# 内存高效
squares_gen = (x**2 for x in range(1000000))

# 内存消耗大
squares_list = [x**2 for x in range(1000000)]
            </div>
        </div>
        
        <div>
            <h4>🎯 字典推导式</h4>
            <p>字典推导式比传统方法创建字典更快。</p>
            <div class="code-block">
# 快速方式
squares_dict = {x: x**2 for x in range(100)}

# 慢速方式
squares_dict = {}
for x in range(100):
    squares_dict[x] = x**2
            </div>
        </div>
        
        <div>
            <h4>🔧 内置函数优化</h4>
            <p>使用内置函数通常比自定义循环更快。</p>
            <div class="code-block">
# 快速方式
total = sum(range(1000))

# 慢速方式
total = 0
for i in range(1000):
    total += i
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
        
        with open(self.templates_dir / "performance.html", "w", encoding="utf-8") as f:
            f.write(performance_template)
    
    def _create_component_templates(self):
        """创建组件模板"""
        
        # 错误页面组件
        error_template = """
{% extends "base.html" %}

{% block title %}{{ error_code }} - {{ error_message }}{% endblock %}

{% block content %}
<div class="section text-center">
    <h1>{{ error_code }}</h1>
    <h2>{{ error_message }}</h2>
    <p>{{ error_description|default("页面未找到或发生错误") }}</p>
    <a href="/" class="btn btn-primary">返回首页</a>
</div>
{% endblock %}
"""
        
        with open(self.templates_dir / "error.html", "w", encoding="utf-8") as f:
            f.write(error_template)
    
    def render_template(self, template_name: str, **context) -> str:
        """渲染模板"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            # 返回错误页面
            error_template = self.env.get_template("error.html")
            return error_template.render(
                error_code=500,
                error_message="模板渲染错误",
                error_description=str(e)
            )
    
    def get_template(self, template_name: str) -> Template:
        """获取模板对象"""
        return self.env.get_template(template_name)

def render_template(template_name: str, **context) -> str:
    """全局模板渲染函数"""
    manager = TemplateManager()
    return manager.render_template(template_name, **context)

# 初始化模板管理器
def initialize_templates():
    """初始化模板"""
    manager = TemplateManager()
    print(f"模板文件已初始化到: {manager.templates_dir}")
    return manager

if __name__ == "__main__":
    initialize_templates()