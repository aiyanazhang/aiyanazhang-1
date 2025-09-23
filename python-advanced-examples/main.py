#!/usr/bin/env python3
"""
Python高级用法示例系统 - 主入口文件

这是一个综合性的Python高级用法示例系统，展示现代Python开发中的核心概念、
设计模式、性能优化技术和最佳实践。

使用方法:
    python main.py --help              # 显示帮助信息
    python main.py demo                # 运行演示
    python main.py web                 # 启动Web界面
    python main.py cli                 # 启动CLI界面
    python main.py test                # 运行测试
    python main.py benchmark           # 运行基准测试
"""

import sys
import argparse
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from python_advanced_examples.cli.main import main as cli_main
from python_advanced_examples.core.example_manager import ExampleManager
from python_advanced_examples.monitoring.performance_monitor import demonstrate_monitoring
from python_advanced_examples.monitoring.benchmark_suite import demonstrate_benchmarks

def run_demo():
    """运行演示"""
    print("🚀 Python高级用法示例系统演示")
    print("=" * 50)
    
    # 创建示例管理器
    example_manager = ExampleManager()
    
    # 运行各种示例
    print("\\n📚 运行语言特性示例...")
    try:
        from python_advanced_examples.language_features.advanced_decorators import demonstrate_decorators
        demonstrate_decorators()
    except Exception as e:
        print(f"❌ 装饰器示例失败: {e}")
    
    print("\\n⚡ 运行并发编程示例...")
    try:
        from python_advanced_examples.concurrency.async_programming import demonstrate_async_programming
        asyncio.run(demonstrate_async_programming())
    except Exception as e:
        print(f"❌ 异步编程示例失败: {e}")
    
    print("\\n📊 运行数据处理示例...")
    try:
        from python_advanced_examples.data_processing.functional_programming import demonstrate_functional_programming
        demonstrate_functional_programming()
    except Exception as e:
        print(f"❌ 函数式编程示例失败: {e}")
    
    print("\\n🎭 运行元编程示例...")
    try:
        from python_advanced_examples.metaprogramming.metaclasses import demonstrate_metaclasses
        demonstrate_metaclasses()
    except Exception as e:
        print(f"❌ 元编程示例失败: {e}")
    
    print("\\n📈 运行性能优化示例...")
    try:
        from python_advanced_examples.performance.memory_optimization import demonstrate_memory_optimization
        demonstrate_memory_optimization()
    except Exception as e:
        print(f"❌ 性能优化示例失败: {e}")
    
    print("\\n✅ 演示完成！")

def run_web():
    """启动Web界面"""
    print("🌐 启动Web界面...")
    try:
        import uvicorn
        from python_advanced_examples.web.api import app
        
        print("Web界面将在 http://localhost:8000 启动")
        print("API文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except ImportError:
        print("❌ 缺少依赖: pip install uvicorn fastapi")
    except Exception as e:
        print(f"❌ Web服务启动失败: {e}")

def run_cli():
    """启动CLI界面"""
    print("💻 启动CLI界面...")
    try:
        cli_main()
    except Exception as e:
        print(f"❌ CLI启动失败: {e}")

def run_tests():
    """运行测试"""
    print("🧪 运行测试套件...")
    try:
        import pytest
        
        # 运行测试
        test_dir = project_root / "tests"
        if test_dir.exists():
            exit_code = pytest.main([str(test_dir), "-v"])
            sys.exit(exit_code)
        else:
            print("❌ 测试目录不存在")
            
    except ImportError:
        print("❌ 缺少依赖: pip install pytest")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

def run_benchmarks():
    """运行基准测试"""
    print("📊 运行基准测试...")
    try:
        demonstrate_benchmarks()
    except Exception as e:
        print(f"❌ 基准测试失败: {e}")

def run_monitoring():
    """运行监控演示"""
    print("📈 运行监控演示...")
    try:
        demonstrate_monitoring()
    except Exception as e:
        print(f"❌ 监控演示失败: {e}")

def show_project_info():
    """显示项目信息"""
    print("📋 Python高级用法示例系统")
    print("=" * 50)
    print("📁 项目结构:")
    print("  ├── src/python_advanced_examples/")
    print("  │   ├── core/                    # 核心框架")
    print("  │   ├── language_features/       # 语言特性")
    print("  │   ├── concurrency/             # 并发编程")
    print("  │   ├── data_processing/         # 数据处理")
    print("  │   ├── metaprogramming/         # 元编程")
    print("  │   ├── performance/             # 性能优化")
    print("  │   ├── monitoring/              # 性能监控")
    print("  │   ├── web/                     # Web界面")
    print("  │   └── cli/                     # 命令行界面")
    print("  ├── tests/                       # 测试文件")
    print("  ├── docs/                        # 文档")
    print("  └── examples/                    # 示例代码")
    print()
    print("🎯 主要功能:")
    print("  • 高级装饰器和上下文管理器")
    print("  • 异步编程和并发处理")
    print("  • 函数式编程和数据流处理")
    print("  • 元编程技术（元类、描述符）")
    print("  • 性能优化和内存管理")
    print("  • 实时性能监控")
    print("  • Web演示界面")
    print("  • 命令行工具")
    print()
    print("📚 使用方法:")
    print("  python main.py demo              # 运行演示")
    print("  python main.py web               # 启动Web界面")
    print("  python main.py cli               # 启动CLI界面")
    print("  python main.py test              # 运行测试")
    print("  python main.py benchmark         # 运行基准测试")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Python高级用法示例系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py demo              运行完整演示
  python main.py web               启动Web界面 (http://localhost:8000)
  python main.py cli               启动交互式CLI
  python main.py test              运行测试套件
  python main.py benchmark         运行性能基准测试
  python main.py monitor           运行性能监控演示
        """
    )
    
    parser.add_argument(
        "command",
        choices=["demo", "web", "cli", "test", "benchmark", "monitor", "info"],
        help="要执行的命令"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Python Advanced Examples 1.0.0"
    )
    
    args = parser.parse_args()
    
    # 根据命令执行相应功能
    command_map = {
        "demo": run_demo,
        "web": run_web,
        "cli": run_cli,
        "test": run_tests,
        "benchmark": run_benchmarks,
        "monitor": run_monitoring,
        "info": show_project_info
    }
    
    try:
        command_map[args.command]()
    except KeyboardInterrupt:
        print("\\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()