#!/usr/bin/env python3
"""
快速启动示例

展示如何使用Python高级用法示例系统。
"""

import sys
from pathlib import Path

# 添加源代码路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """主函数"""
    print("🐍 Python高级用法示例系统 - 快速启动")
    print("=" * 50)
    
    try:
        # 导入核心模块
        from python_advanced_examples import registry, runner
        from python_advanced_examples.core.registry import ExampleCategory, DifficultyLevel
        
        print("✅ 核心模块导入成功")
        
        # 导入示例模块
        from python_advanced_examples.language_features import (
            advanced_decorators, 
            context_managers, 
            generators, 
            type_hints
        )
        
        print("✅ 示例模块导入成功")
        
        # 显示统计信息
        stats = registry.get_statistics()
        print(f"\n📊 系统统计:")
        print(f"   总示例数: {stats['total_examples']}")
        print(f"   分类数: {len(stats['categories'])}")
        print(f"   标签数: {stats['total_tags']}")
        
        # 显示分类信息
        print(f"\n📂 可用分类:")
        for category, count in stats['categories'].items():
            print(f"   {category}: {count} 个示例")
        
        # 列出一些示例
        examples = registry.list_examples()
        if examples:
            print(f"\n📝 示例预览 (显示前5个):")
            for example in examples[:5]:
                print(f"   • {example.name} ({example.category.value}) - {example.description}")
        
        # 运行一个简单的示例
        if examples:
            example_name = examples[0].name
            print(f"\n🚀 运行示例: {example_name}")
            
            result = runner.run(example_name, capture_output=True)
            
            if result.success:
                print(f"✅ 运行成功 (耗时: {result.execution_time:.3f}s)")
                if result.stdout:
                    print(f"📤 输出:")
                    # 限制输出长度
                    output = result.stdout[:500]
                    if len(result.stdout) > 500:
                        output += "..."
                    print("   " + output.replace("\n", "\n   "))
            else:
                print(f"❌ 运行失败: {result.error}")
        
        print(f"\n🎯 使用方法:")
        print("   python -m python_advanced_examples.interfaces.cli --help")
        print("   python-advanced list")
        print("   python-advanced run <example_name>")
        print("   python-advanced web")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已正确安装依赖包")
        return 1
    
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        return 1
    
    print("\n✨ 快速启动完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())