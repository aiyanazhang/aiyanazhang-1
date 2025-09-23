"""
静态资源处理

管理Web界面的静态文件：
- CSS样式
- JavaScript脚本
- 图像资源
- 字体文件
"""

from pathlib import Path
from typing import Dict, Any
import json

class StaticFileHandler:
    """静态文件处理器"""
    
    def __init__(self, static_dir: Path = None):
        self.static_dir = static_dir or Path(__file__).parent / "static"
        self.static_dir.mkdir(exist_ok=True)
        self._initialize_static_files()
    
    def _initialize_static_files(self):
        """初始化静态文件"""
        # 创建CSS文件
        self._create_css_files()
        # 创建JavaScript文件
        self._create_js_files()
        # 创建配置文件
        self._create_config_files()
    
    def _create_css_files(self):
        """创建CSS样式文件"""
        css_dir = self.static_dir / "css"
        css_dir.mkdir(exist_ok=True)
        
        # 主样式文件
        main_css = """
/* 主样式文件 */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-family);
    line-height: 1.6;
    color: var(--dark-color);
    background-color: #ffffff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* 导航栏 */
.navbar {
    background-color: var(--dark-color);
    color: white;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
    text-decoration: none;
    color: white;
}

.navbar-nav {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.navbar-nav a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}

.navbar-nav a:hover {
    color: var(--primary-color);
}

/* 主要内容区域 */
.main-content {
    min-height: calc(100vh - 120px);
    padding: 2rem 0;
}

.section {
    margin: 2rem 0;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-title {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: var(--dark-color);
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.5rem;
}

/* 按钮样式 */
.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    text-align: center;
    transition: all 0.3s;
    margin: 0.25rem;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
}

.btn-secondary {
    background-color: var(--secondary-color);
    color: white;
}

.btn-success {
    background-color: var(--success-color);
    color: white;
}

.btn-danger {
    background-color: var(--danger-color);
    color: white;
}

/* 表单样式 */
.form-group {
    margin-bottom: 1rem;
}

.form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* 代码块样式 */
.code-block {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9rem;
    overflow-x: auto;
    margin: 1rem 0;
}

.code-editor {
    background-color: #2d3748;
    color: #e2e8f0;
    border: 1px solid #4a5568;
    border-radius: 4px;
    padding: 1rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9rem;
    resize: vertical;
    min-height: 200px;
}

/* 结果显示 */
.result-panel {
    background-color: #f8f9fa;
    border-left: 4px solid var(--success-color);
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 4px 4px 0;
}

.error-panel {
    background-color: #f8d7da;
    border-left: 4px solid var(--danger-color);
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 4px 4px 0;
    color: #721c24;
}

/* 网格布局 */
.grid {
    display: grid;
    gap: 2rem;
}

.grid-2 {
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
}

.grid-3 {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 0 15px;
    }
    
    .section {
        padding: 1rem;
    }
    
    .navbar-nav {
        gap: 1rem;
    }
    
    .grid-2,
    .grid-3 {
        grid-template-columns: 1fr;
    }
}

/* 动画效果 */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 工具提示 */
.tooltip {
    position: relative;
    cursor: help;
}

.tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    background-color: var(--dark-color);
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s;
}

.tooltip:hover::after {
    opacity: 1;
    visibility: visible;
}
"""
        
        with open(css_dir / "main.css", "w", encoding="utf-8") as f:
            f.write(main_css)
    
    def _create_js_files(self):
        """创建JavaScript文件"""
        js_dir = self.static_dir / "js"
        js_dir.mkdir(exist_ok=True)
        
        # 主JavaScript文件
        main_js = """
// 主JavaScript文件
class PythonExamplesApp {
    constructor() {
        this.apiBase = '/api';
        this.currentCategory = null;
        this.currentExample = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadCategories();
    }
    
    setupEventListeners() {
        // 代码执行按钮
        const executeBtn = document.getElementById('execute-code');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => this.executeCode());
        }
        
        // 示例运行按钮
        const runExampleBtn = document.getElementById('run-example');
        if (runExampleBtn) {
            runExampleBtn.addEventListener('click', () => this.runExample());
        }
        
        // 性能测试按钮
        const benchmarkBtn = document.getElementById('run-benchmark');
        if (benchmarkBtn) {
            benchmarkBtn.addEventListener('click', () => this.runBenchmark());
        }
    }
    
    async loadCategories() {
        try {
            const response = await fetch(`${this.apiBase}/examples/categories`);
            const data = await response.json();
            this.displayCategories(data.categories);
        } catch (error) {
            console.error('加载分类失败:', error);
            this.showError('加载示例分类失败');
        }
    }
    
    displayCategories(categories) {
        const container = document.getElementById('categories-container');
        if (!container) return;
        
        container.innerHTML = categories.map(category => `
            <div class="category-card" data-category="${category.name}">
                <h3>${category.title}</h3>
                <p>${category.description}</p>
                <div class="examples-list">
                    ${category.examples.map(example => `
                        <button class="btn btn-secondary example-btn" 
                                data-category="${category.name}" 
                                data-example="${example}">
                            ${example.replace(/_/g, ' ')}
                        </button>
                    `).join('')}
                </div>
            </div>
        `).join('');
        
        // 添加示例按钮事件监听
        container.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                const example = e.target.dataset.example;
                this.selectExample(category, example);
            });
        });
    }
    
    selectExample(category, example) {
        this.currentCategory = category;
        this.currentExample = example;
        
        // 更新UI
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });
        
        const selectedBtn = document.querySelector(
            `[data-category="${category}"][data-example="${example}"]`
        );
        if (selectedBtn) {
            selectedBtn.classList.remove('btn-secondary');
            selectedBtn.classList.add('btn-primary');
        }
        
        // 显示示例信息
        this.showExampleInfo(category, example);
    }
    
    showExampleInfo(category, example) {
        const infoContainer = document.getElementById('example-info');
        if (!infoContainer) return;
        
        infoContainer.innerHTML = `
            <h4>选中示例</h4>
            <p><strong>分类:</strong> ${category}</p>
            <p><strong>示例:</strong> ${example}</p>
            <button id="run-selected-example" class="btn btn-success">
                运行此示例
            </button>
        `;
        
        document.getElementById('run-selected-example').addEventListener('click', () => {
            this.runSelectedExample();
        });
    }
    
    async executeCode() {
        const codeInput = document.getElementById('code-input');
        const resultContainer = document.getElementById('execution-result');
        
        if (!codeInput || !resultContainer) return;
        
        const code = codeInput.value.trim();
        if (!code) {
            this.showError('请输入要执行的代码');
            return;
        }
        
        this.showLoading(resultContainer);
        
        try {
            const response = await fetch(`${this.apiBase}/code/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    timeout: 30
                })
            });
            
            const result = await response.json();
            this.displayExecutionResult(result, resultContainer);
            
        } catch (error) {
            console.error('代码执行失败:', error);
            this.showError('代码执行失败', resultContainer);
        }
    }
    
    async runSelectedExample() {
        if (!this.currentCategory || !this.currentExample) {
            this.showError('请先选择一个示例');
            return;
        }
        
        const resultContainer = document.getElementById('example-result');
        if (!resultContainer) return;
        
        this.showLoading(resultContainer);
        
        try {
            const response = await fetch(`${this.apiBase}/examples/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    category: this.currentCategory,
                    name: this.currentExample,
                    parameters: {}
                })
            });
            
            const result = await response.json();
            this.displayExecutionResult(result, resultContainer);
            
        } catch (error) {
            console.error('示例运行失败:', error);
            this.showError('示例运行失败', resultContainer);
        }
    }
    
    async runBenchmark() {
        const testType = document.getElementById('benchmark-type')?.value || 'list_comprehension';
        const iterations = parseInt(document.getElementById('iterations')?.value || '1000');
        const dataSize = parseInt(document.getElementById('data-size')?.value || '1000');
        const resultContainer = document.getElementById('benchmark-result');
        
        if (!resultContainer) return;
        
        this.showLoading(resultContainer);
        
        try {
            const response = await fetch(`${this.apiBase}/performance/benchmark`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    test_type: testType,
                    iterations: iterations,
                    data_size: dataSize
                })
            });
            
            const result = await response.json();
            this.displayBenchmarkResult(result, resultContainer);
            
        } catch (error) {
            console.error('性能测试失败:', error);
            this.showError('性能测试失败', resultContainer);
        }
    }
    
    displayExecutionResult(result, container) {
        const isSuccess = result.success;
        const panelClass = isSuccess ? 'result-panel' : 'error-panel';
        
        let content = `
            <div class="${panelClass}">
                <h4>${isSuccess ? '执行成功' : '执行失败'}</h4>
                <p><strong>执行时间:</strong> ${result.execution_time.toFixed(4)}秒</p>
        `;
        
        if (result.result) {
            content += `<p><strong>结果:</strong></p><pre>${result.result}</pre>`;
        }
        
        if (result.stdout) {
            content += `<p><strong>输出:</strong></p><pre>${result.stdout}</pre>`;
        }
        
        if (result.error) {
            content += `<p><strong>错误:</strong></p><pre>${result.error}</pre>`;
        }
        
        if (result.stderr) {
            content += `<p><strong>错误输出:</strong></p><pre>${result.stderr}</pre>`;
        }
        
        content += '</div>';
        container.innerHTML = content;
    }
    
    displayBenchmarkResult(result, container) {
        container.innerHTML = `
            <div class="result-panel">
                <h4>性能测试结果</h4>
                <p><strong>测试类型:</strong> ${result.test_type}</p>
                <p><strong>迭代次数:</strong> ${result.iterations}</p>
                <p><strong>数据大小:</strong> ${result.data_size}</p>
                <p><strong>总执行时间:</strong> ${result.total_time.toFixed(4)}秒</p>
                <p><strong>平均每次执行时间:</strong> ${result.avg_time_per_iteration.toFixed(6)}秒</p>
                <p><strong>每秒操作数:</strong> ${result.operations_per_second.toFixed(2)}</p>
            </div>
        `;
    }
    
    showLoading(container) {
        container.innerHTML = `
            <div class="text-center">
                <div class="loading"></div>
                <p>执行中...</p>
            </div>
        `;
    }
    
    showError(message, container = null) {
        const content = `
            <div class="error-panel">
                <h4>错误</h4>
                <p>${message}</p>
            </div>
        `;
        
        if (container) {
            container.innerHTML = content;
        } else {
            // 创建临时错误提示
            const errorDiv = document.createElement('div');
            errorDiv.innerHTML = content;
            errorDiv.style.position = 'fixed';
            errorDiv.style.top = '20px';
            errorDiv.style.right = '20px';
            errorDiv.style.zIndex = '9999';
            document.body.appendChild(errorDiv);
            
            setTimeout(() => {
                document.body.removeChild(errorDiv);
            }, 5000);
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PythonExamplesApp();
});

// 工具函数
function formatCode(code) {
    // 简单的代码格式化
    return code
        .replace(/\\t/g, '    ')
        .replace(/;\\s*/g, ';\\n')
        .trim();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('复制成功');
    }).catch(err => {
        console.error('复制失败:', err);
    });
}
"""
        
        with open(js_dir / "main.js", "w", encoding="utf-8") as f:
            f.write(main_js)
    
    def _create_config_files(self):
        """创建配置文件"""
        config_dir = self.static_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # API配置
        api_config = {
            "endpoints": {
                "examples": "/api/examples",
                "code_execution": "/api/code/execute",
                "performance": "/api/performance",
                "monitoring": "/api/monitor"
            },
            "ui": {
                "theme": "default",
                "language": "zh-CN",
                "code_editor": {
                    "theme": "dark",
                    "font_size": 14,
                    "tab_size": 4
                }
            }
        }
        
        with open(config_dir / "api.json", "w", encoding="utf-8") as f:
            json.dump(api_config, f, indent=2, ensure_ascii=False)

def get_static_files() -> Dict[str, str]:
    """获取静态文件映射"""
    handler = StaticFileHandler()
    static_files = {}
    
    # 扫描静态文件目录
    for file_path in handler.static_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(handler.static_dir)
            static_files[str(relative_path)] = str(file_path)
    
    return static_files

# 初始化静态文件
def initialize_static_resources():
    """初始化静态资源"""
    handler = StaticFileHandler()
    print(f"静态文件已初始化到: {handler.static_dir}")
    return handler

if __name__ == "__main__":
    initialize_static_resources()