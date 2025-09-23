"""接口模块

提供多种用户接口，包括命令行接口、Web界面和Jupyter集成。
"""

from .cli import *

__all__ = [
    "main",
    "create_cli_app",
    "run_example_command",
    "list_examples_command",
    "benchmark_command",
]