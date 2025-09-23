"""
命令行接口

提供完整的命令行工具，支持运行示例、性能测试、代码生成等功能。
"""

import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# 导入核心模块
from .. import registry, runner, monitor
from ..core.registry import ExampleCategory, DifficultyLevel

console = Console()


def print_banner():
    """打印项目横幅"""
    banner = """
[bold blue]
╔═══════════════════════════════════════════════════════════════╗
║                  Python 高级用法示例系统                      ║
║                                                               ║
║  🐍 展示现代 Python 开发中的核心概念和最佳实践                 ║
║  🚀 包含装饰器、异步编程、性能优化、元编程等高级特性            ║
║  📚 提供完整的学习路径和实践案例                              ║
╚═══════════════════════════════════════════════════════════════╝
[/bold blue]
"""
    console.print(banner)


@click.group()
@click.version_option(version="1.0.0", prog_name="python-advanced")
@click.option('--verbose', '-v', is_flag=True, help='启用详细输出')
@click.pass_context
def cli(ctx, verbose):
    """Python高级用法示例系统 - 探索Python的强大特性"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.option('--category', '-c', 
              type=click.Choice([cat.value for cat in ExampleCategory]), 
              help='按分类过滤')
@click.option('--difficulty', '-d',
              type=click.Choice([diff.value for diff in DifficultyLevel]),
              help='按难度过滤')
@click.option('--tag', '-t', multiple=True, help='按标签过滤')
@click.option('--search', '-s', help='搜索关键词')
@click.option('--detailed', is_flag=True, help='显示详细信息')
def list(category, difficulty, tag, search, detailed):
    """列出所有可用的示例"""
    
    # 获取示例列表
    examples = registry.list_examples(
        category=category,
        difficulty=difficulty,
        tags=list(tag) if tag else None,
        name_pattern=search
    )
    
    if not examples:
        console.print("[yellow]没有找到符合条件的示例[/yellow]")
        return
    
    # 创建表格
    table = Table(title=f"Python高级示例 ({len(examples)} 个)")
    table.add_column("名称", style="cyan", no_wrap=True)
    table.add_column("分类", style="magenta")
    table.add_column("难度", style="green")
    table.add_column("描述", style="white")
    
    if detailed:
        table.add_column("标签", style="blue")
        table.add_column("文件", style="dim")
    
    # 难度排序映射
    difficulty_order = {
        DifficultyLevel.BEGINNER: 1,
        DifficultyLevel.INTERMEDIATE: 2,
        DifficultyLevel.ADVANCED: 3,
        DifficultyLevel.EXPERT: 4
    }
    
    # 按分类和难度排序
    examples.sort(key=lambda x: (x.category.value, difficulty_order.get(x.difficulty, 0)))
    
    for example in examples:
        row = [
            example.name,
            example.category.value,
            example.difficulty.value,
            example.description[:50] + "..." if len(example.description) > 50 else example.description
        ]
        
        if detailed:
            tags = ", ".join(sorted(example.tags)) if example.tags else "无"
            source_file = str(example.source_file.name) if example.source_file else "未知"
            row.extend([tags, source_file])
        
        table.add_row(*row)
    
    console.print(table)
    
    # 显示统计信息
    stats = registry.get_statistics()
    info_panel = Panel(
        f"总示例数: {stats['total_examples']}\n"
        f"分类数: {len(stats['categories'])}\n"
        f"标签数: {stats['total_tags']}",
        title="统计信息",
        style="dim"
    )
    console.print(info_panel)


@cli.command()
@click.argument('example_name')
@click.option('--timeout', '-t', type=float, help='超时时间（秒）')
@click.option('--memory-limit', '-m', type=int, help='内存限制（MB）')
@click.option('--isolated', is_flag=True, help='在隔离进程中运行')
@click.option('--no-output', is_flag=True, help='不捕获输出')
@click.option('--profile', is_flag=True, help='启用性能分析')
@click.pass_context
def run(ctx, example_name, timeout, memory_limit, isolated, no_output, profile):
    """运行指定的示例"""
    
    # 检查示例是否存在
    example = registry.get_example(example_name)
    if not example:
        console.print(f"[red]错误: 示例 '{example_name}' 不存在[/red]")
        
        # 提供相似的建议
        all_examples = registry.list_examples()
        similar = [ex.name for ex in all_examples if example_name.lower() in ex.name.lower()]
        if similar:
            console.print("\n[yellow]您是否要运行以下示例之一？[/yellow]")
            for sim in similar[:5]:
                console.print(f"  • {sim}")
        return
    
    # 显示示例信息
    info_panel = Panel(
        f"[bold]{example.name}[/bold]\n"
        f"分类: {example.category.value}\n"
        f"难度: {example.difficulty.value}\n"
        f"描述: {example.description}\n"
        f"标签: {', '.join(sorted(example.tags)) if example.tags else '无'}",
        title="示例信息",
        style="blue"
    )
    console.print(info_panel)
    
    # 启用性能监控
    if profile:
        monitor.enable()
        monitor.start_cpu_profiling()
    
    # 运行示例
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"运行示例 {example_name}...", total=None)
        
        start_time = time.time()
        result = runner.run(
            example_name,
            timeout=timeout,
            memory_limit_mb=memory_limit,
            capture_output=not no_output,
            isolated=isolated
        )
        end_time = time.time()
        
        progress.remove_task(task)
    
    # 显示结果
    if result.success:
        console.print(f"\n[green]✅ 示例运行成功[/green]")
        
        if result.stdout and not no_output:
            console.print("\n[bold]输出:[/bold]")
            console.print(Panel(result.stdout, style="green"))
        
        if result.return_value is not None:
            console.print(f"\n[bold]返回值:[/bold] {result.return_value}")
    
    else:
        console.print(f"\n[red]❌ 示例运行失败: {result.status.value}[/red]")
        
        if result.error:
            console.print(f"\n[bold]错误信息:[/bold] {result.error}")
        
        if result.stderr and not no_output:
            console.print("\n[bold]错误输出:[/bold]")
            console.print(Panel(result.stderr, style="red"))
        
        if ctx.obj.get('verbose') and result.exception_info:
            console.print("\n[bold]异常详情:[/bold]")
            console.print(Panel(result.exception_info, style="dim"))
    
    # 显示性能信息
    performance_info = []
    performance_info.append(f"执行时间: {result.execution_time:.3f}s")
    performance_info.append(f"内存使用: {result.memory_usage:.1f}MB")
    
    if profile and monitor.enabled:
        monitor.stop_cpu_profiling()
        perf_report = monitor.generate_report()
        if perf_report.get('realtime_stats'):
            stats = perf_report['realtime_stats']
            performance_info.append(f"峰值CPU: {stats.get('peak_cpu', 0):.1f}%")
            performance_info.append(f"峰值内存: {stats.get('peak_memory', 0):.1f}MB")
    
    perf_panel = Panel(
        "\n".join(performance_info),
        title="性能信息",
        style="cyan"
    )
    console.print(perf_panel)


@cli.command()
@click.argument('pattern', required=False)
@click.option('--iterations', '-i', default=10, help='测试迭代次数')
@click.option('--warmup', '-w', default=3, help='预热迭代次数')
@click.option('--category', '-c', 
              type=click.Choice([cat.value for cat in ExampleCategory]),
              help='按分类运行基准测试')
@click.option('--output', '-o', type=click.Path(), help='输出结果到文件')
def benchmark(pattern, iterations, warmup, category, output):
    """运行性能基准测试"""
    
    if category:
        examples = registry.get_by_category(category)
        console.print(f"对分类 '{category}' 运行基准测试...")
    elif pattern:
        examples = [ex for ex in registry.list_examples() if pattern.lower() in ex.name.lower()]
        console.print(f"对模式 '{pattern}' 运行基准测试...")
    else:
        console.print("[red]错误: 请指定测试模式或分类[/red]")
        return
    
    if not examples:
        console.print("[yellow]没有找到符合条件的示例[/yellow]")
        return
    
    results = []
    
    with Progress(console=console) as progress:
        task = progress.add_task("运行基准测试...", total=len(examples))
        
        for example in examples:
            progress.update(task, description=f"测试 {example.name}")
            
            try:
                benchmark_result = runner.benchmark(
                    example.name,
                    iterations=iterations,
                    warmup_iterations=warmup
                )
                results.append(benchmark_result)
                
            except Exception as e:
                console.print(f"[red]基准测试失败 {example.name}: {e}[/red]")
                results.append({"example_name": example.name, "error": str(e)})
            
            progress.advance(task)
    
    # 显示结果表格
    table = Table(title="基准测试结果")
    table.add_column("示例", style="cyan")
    table.add_column("平均时间", style="green")
    table.add_column("最小时间", style="blue")
    table.add_column("最大时间", style="red")
    table.add_column("标准差", style="yellow")
    table.add_column("成功率", style="magenta")
    
    for result in results:
        if "error" in result:
            table.add_row(
                result["example_name"],
                "[red]失败[/red]",
                "[red]--[/red]",
                "[red]--[/red]",
                "[red]--[/red]",
                "[red]0%[/red]"
            )
        else:
            exec_time = result["execution_time"]
            table.add_row(
                result["example_name"],
                f"{exec_time['mean']:.4f}s",
                f"{exec_time['min']:.4f}s",
                f"{exec_time['max']:.4f}s",
                f"{exec_time['std']:.4f}s",
                f"{result['success_rate']*100:.1f}%"
            )
    
    console.print(table)
    
    # 保存结果到文件
    if output:
        import json
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        console.print(f"\n[green]结果已保存到 {output}[/green]")


@cli.command()
@click.option('--category', '-c',
              type=click.Choice([cat.value for cat in ExampleCategory]),
              help='按分类显示统计')
@click.option('--export', '-e', type=click.Path(), help='导出统计到文件')
def stats(category, export):
    """显示示例统计信息"""
    
    stats = registry.get_statistics()
    
    # 总体统计
    console.print(Panel(
        f"总示例数: {stats['total_examples']}\n"
        f"分类数: {len(stats['categories'])}\n"
        f"标签数: {stats['total_tags']}",
        title="总体统计",
        style="blue"
    ))
    
    # 分类统计表格
    cat_table = Table(title="分类统计")
    cat_table.add_column("分类", style="cyan")
    cat_table.add_column("示例数", style="green")
    cat_table.add_column("占比", style="yellow")
    
    total = stats['total_examples']
    for cat_name, count in stats['categories'].items():
        percentage = (count / total * 100) if total > 0 else 0
        cat_table.add_row(cat_name, str(count), f"{percentage:.1f}%")
    
    console.print(cat_table)
    
    # 难度统计表格
    diff_table = Table(title="难度统计")
    diff_table.add_column("难度", style="cyan")
    diff_table.add_column("示例数", style="green")
    diff_table.add_column("占比", style="yellow")
    
    for diff_name, count in stats['difficulty_levels'].items():
        percentage = (count / total * 100) if total > 0 else 0
        diff_table.add_row(diff_name, str(count), f"{percentage:.1f}%")
    
    console.print(diff_table)
    
    # 热门标签
    if stats['most_used_tags']:
        tag_table = Table(title="热门标签 (Top 10)")
        tag_table.add_column("标签", style="cyan")
        tag_table.add_column("使用次数", style="green")
        
        for tag, count in stats['most_used_tags']:
            tag_table.add_row(tag, str(count))
        
        console.print(tag_table)
    
    # 导出统计
    if export:
        import json
        with open(export, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
        console.print(f"\n[green]统计信息已导出到 {export}[/green]")


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='最大结果数')
def search(query, limit):
    """搜索示例"""
    
    results = registry.search(query)
    
    if not results:
        console.print(f"[yellow]没有找到包含 '{query}' 的示例[/yellow]")
        return
    
    # 限制结果数量
    results = results[:limit]
    
    console.print(f"搜索 '{query}' 的结果 ({len(results)} 个):")
    
    for i, example in enumerate(results, 1):
        console.print(f"\n[bold cyan]{i}. {example.name}[/bold cyan]")
        console.print(f"   分类: {example.category.value} | 难度: {example.difficulty.value}")
        console.print(f"   描述: {example.description}")
        if example.tags:
            console.print(f"   标签: {', '.join(sorted(example.tags))}")


@cli.command()
@click.option('--host', default='127.0.0.1', help='服务器主机')
@click.option('--port', default=8000, help='服务器端口')
@click.option('--reload', is_flag=True, help='启用热重载')
def web(host, port, reload):
    """启动Web演示界面"""
    try:
        import uvicorn
        from .web_interface import create_app
        
        console.print(f"启动Web服务器 http://{host}:{port}")
        console.print("按 Ctrl+C 停止服务器")
        
        app = create_app()
        uvicorn.run(app, host=host, port=port, reload=reload)
        
    except ImportError:
        console.print("[red]错误: 未安装Web依赖，请运行: pip install 'python-advanced-examples[web]'[/red]")
    except Exception as e:
        console.print(f"[red]启动Web服务器失败: {e}[/red]")


@cli.command()
def version():
    """显示版本信息"""
    print_banner()
    
    # 显示系统信息
    import platform
    import sys
    
    info_table = Table(title="系统信息")
    info_table.add_column("项目", style="cyan")
    info_table.add_column("值", style="green")
    
    info_table.add_row("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    info_table.add_row("操作系统", platform.system())
    info_table.add_row("架构", platform.machine())
    info_table.add_row("示例总数", str(len(registry._examples)))
    
    console.print(info_table)


def main():
    """主入口函数"""
    # 加载所有示例模块
    try:
        # 导入所有示例模块以注册示例
        from ..language_features import advanced_decorators, context_managers, generators, type_hints
        
        console.print("[dim]已加载语言特性示例模块[/dim]")
        
    except Exception as e:
        console.print(f"[yellow]警告: 加载示例模块时出错: {e}[/yellow]")
    
    # 启动CLI
    cli()


if __name__ == '__main__':
    main()