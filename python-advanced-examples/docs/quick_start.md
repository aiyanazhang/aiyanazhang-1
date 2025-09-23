# Python高级用法示例系统 - 快速上手指南

## 🚀 快速开始

### 1. 环境准备

确保您的系统满足以下要求：
- Python 3.9+
- pip包管理器

### 2. 安装依赖

```bash
cd python-advanced-examples
pip install -e .
```

如果需要开发环境或Web功能：
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装Web依赖
pip install -e ".[web]"

# 安装所有依赖
pip install -e ".[dev,web,docs]"
```

### 3. 验证安装

运行快速启动脚本：
```bash
python examples/quick_start.py
```

### 4. 使用命令行工具

```bash
# 查看帮助
python-advanced --help

# 列出所有示例
python-advanced list

# 运行特定示例
python-advanced run caching_decorator_basic

# 运行性能基准测试
python-advanced benchmark --category decorators

# 启动Web界面
python-advanced web
```

## 📁 项目结构

```
python-advanced-examples/
├── src/python_advanced_examples/     # 源代码
│   ├── core/                        # 核心框架
│   │   ├── registry.py              # 示例注册中心
│   │   ├── runner.py                # 示例执行引擎
│   │   ├── performance.py           # 性能监控
│   │   └── decorators.py            # 核心装饰器
│   ├── language_features/           # 语言特性模块
│   │   ├── advanced_decorators.py   # 高级装饰器
│   │   ├── context_managers.py      # 上下文管理器
│   │   ├── generators.py            # 生成器和迭代器
│   │   └── type_hints.py            # 类型提示
│   └── interfaces/                  # 用户接口
│       ├── cli.py                   # 命令行接口
│       └── web_interface.py         # Web界面
├── tests/                           # 测试文件
├── examples/                        # 示例脚本
├── docs/                           # 文档
└── pyproject.toml                  # 项目配置
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试模块
pytest tests/unit/test_core.py

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行性能测试
pytest -m performance
```

## 🌟 主要功能

### 1. 示例管理系统
- 自动注册和发现示例
- 分类和标签管理
- 搜索和过滤功能

### 2. 执行引擎
- 安全的示例执行环境
- 超时和内存限制
- 异常处理和恢复

### 3. 性能监控
- 实时性能分析
- 内存使用跟踪
- 基准测试功能

### 4. 多种接口
- 命令行工具
- Web演示界面
- API接口

## 📚 示例分类

### 装饰器 (Decorators)
- 缓存装饰器
- 重试装饰器
- 限流装饰器
- 类型检查装饰器

### 上下文管理器 (Context Managers)
- 资源管理器
- 状态管理器
- 临时目录管理

### 生成器 (Generators)
- 无限序列生成器
- 批处理迭代器
- 惰性求值器
- 滑动窗口

### 类型提示 (Type Hints)
- 泛型容器
- 协议定义
- 字面量类型
- 函数重载

## 🔧 开发指南

### 添加新示例

1. 在相应模块中创建函数
2. 使用 `@example` 装饰器注册
3. 添加适当的测试
4. 更新文档

示例代码：
```python
from python_advanced_examples.core.decorators import example
from python_advanced_examples.core.registry import ExampleCategory, DifficultyLevel

@example(
    name="my_new_example",
    category=ExampleCategory.DECORATORS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="我的新示例",
    tags=["demo", "tutorial"]
)
def my_new_example():
    """新示例函数"""
    print("Hello, World!")
    return "success"
```

### 代码规范

项目使用以下工具维护代码质量：
- `black`: 代码格式化
- `ruff`: 代码检查
- `mypy`: 类型检查

运行代码检查：
```bash
black src/
ruff check src/
mypy src/
```

## 🌐 Web界面

启动Web服务器：
```bash
python-advanced web --host 0.0.0.0 --port 8000
```

然后访问 `http://localhost:8000` 查看Web界面。

### API端点

- `GET /api/examples` - 获取所有示例
- `GET /api/examples/{name}` - 获取特定示例
- `POST /api/run` - 运行示例
- `GET /api/categories` - 获取分类列表
- `GET /api/stats` - 获取统计信息
- `GET /api/search?q=<query>` - 搜索示例

## 🐛 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保正确安装
   pip install -e .
   ```

2. **权限错误**
   ```bash
   # 使用虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

3. **依赖缺失**
   ```bash
   # 安装所有依赖
   pip install -e ".[dev,web,docs]"
   ```

### 调试模式

启用详细输出：
```bash
python-advanced --verbose list
python-advanced run example_name --profile
```

## 📈 性能监控

系统内置完整的性能监控功能：

```python
from python_advanced_examples.core.performance import monitor_performance

@monitor_performance
def my_function():
    # 你的代码
    pass

# 查看性能报告
python-advanced stats
```

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

请确保：
- 添加适当的测试
- 更新文档
- 遵循代码规范

## 📄 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

---

🎉 **开始探索Python的高级世界吧！**