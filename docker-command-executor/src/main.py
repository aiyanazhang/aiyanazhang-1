"""
主应用程序入口
整合所有组件，提供统一的命令行接口和API接口
"""

import sys
import argparse
import json
import signal
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from .config_manager import ConfigManager
from .command_parser import CommandParser, ParsedCommand
from .execution_engine import ExecutionEngine, ExecutionResult
from .parameter_validator import ValidationResult


class DockerCommandExecutor:
    """Docker命令执行器主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化执行器"""
        # 初始化配置
        self.config_manager = ConfigManager(config_file)
        self.config_manager.load_from_env()
        
        # 初始化组件
        self.command_parser = CommandParser()
        self.execution_engine = ExecutionEngine(self.config_manager)
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._shutdown = False
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"接收到信号 {signum}，开始清理...")
        self._shutdown = True
        self.cleanup()
        sys.exit(0)
    
    def execute_command(self, command_input: str, mount_path: Optional[str] = None) -> ExecutionResult:
        """执行单个命令"""
        try:
            # 解析命令
            parsed_command = self.command_parser.parse(command_input)
            
            # 记录命令摘要
            command_summary = self.command_parser.get_command_summary(parsed_command)
            self.logger.info(f"执行命令: {command_summary}")
            
            # 执行命令
            result = self.execution_engine.execute(parsed_command, mount_path)
            
            return result
            
        except ValueError as e:
            # 命令解析错误
            self.logger.error(f"命令解析失败: {e}")
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"命令解析失败: {e}",
                execution_time=0.0,
                container_info=None,
                error_message=str(e)
            )
        except Exception as e:
            # 其他错误
            self.logger.error(f"执行失败: {e}")
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"执行失败: {e}",
                execution_time=0.0,
                container_info=None,
                error_message=str(e)
            )
    
    def execute_batch(self, commands: List[str], mount_path: Optional[str] = None) -> List[ExecutionResult]:
        """批量执行命令"""
        results = []
        
        for i, command_input in enumerate(commands):
            self.logger.info(f"执行批量命令 {i+1}/{len(commands)}")
            result = self.execute_command(command_input, mount_path)
            results.append(result)
        
        return results
    
    def validate_command(self, command_input: str) -> ValidationResult:
        """仅验证命令，不执行"""
        try:
            parsed_command = self.command_parser.parse(command_input)
            return self.execution_engine.validate_command_only(parsed_command)
        except ValueError as e:
            # 返回解析错误的验证结果
            return ValidationResult(
                is_valid=False,
                errors=[f"命令解析失败: {e}"],
                warnings=[],
                risk_level='high'
            )
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'health': self.execution_engine.get_health_status(),
            'system_info': self.execution_engine.get_system_info(),
            'metrics': self.execution_engine.get_execution_metrics().__dict__,
            'active_executions': len(self.execution_engine.get_active_executions())
        }
    
    def get_command_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取命令历史"""
        history = self.execution_engine.get_command_history(count)
        return [
            {
                'command': cmd.command,
                'args': cmd.args,
                'raw_input': cmd.raw_input,
                'working_dir': cmd.working_dir,
                'timeout': cmd.timeout
            }
            for cmd in history
        ]
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("开始清理应用程序...")
        
        if hasattr(self, 'execution_engine'):
            self.execution_engine.cleanup()
        
        self.logger.info("应用程序清理完成")


class CLIInterface:
    """命令行接口"""
    
    def __init__(self):
        self.executor: Optional[DockerCommandExecutor] = None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            description='Docker命令执行工具 - 在安全的容器环境中执行系统命令',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s ls -la                    # 执行ls命令
  %(prog)s --mount /tmp cat file.txt # 挂载目录并执行命令
  %(prog)s --validate "rm -rf /"     # 仅验证命令安全性
  %(prog)s --batch commands.txt      # 批量执行命令
  %(prog)s --status                  # 查看系统状态
            """
        )
        
        # 基本参数
        parser.add_argument('command', nargs='*', help='要执行的命令')
        parser.add_argument('--config', '-c', help='配置文件路径')
        parser.add_argument('--mount', '-m', help='要挂载到容器的本地目录')
        parser.add_argument('--workdir', '-w', help='容器工作目录')
        parser.add_argument('--timeout', '-t', type=int, help='命令超时时间（秒）')
        
        # 操作模式
        parser.add_argument('--validate', action='store_true', help='仅验证命令，不执行')
        parser.add_argument('--batch', help='批量执行文件中的命令')
        parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
        
        # 查询操作
        parser.add_argument('--status', action='store_true', help='显示系统状态')
        parser.add_argument('--history', type=int, metavar='N', help='显示最近N条命令历史')
        
        # 输出控制
        parser.add_argument('--output', '-o', choices=['text', 'json'], default='text', help='输出格式')
        parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
        parser.add_argument('--quiet', '-q', action='store_true', help='安静模式')
        
        return parser
    
    def setup_logging(self, verbose: bool, quiet: bool):
        """设置日志级别"""
        if quiet:
            level = logging.ERROR
        elif verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def format_output(self, data: Any, output_format: str) -> str:
        """格式化输出"""
        if output_format == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            return self._format_text_output(data)
    
    def _format_text_output(self, data: Any) -> str:
        """格式化文本输出"""
        if isinstance(data, ExecutionResult):
            output = []
            
            # 状态信息
            status = "✓ 成功" if data.success else "✗ 失败"
            output.append(f"状态: {status}")
            output.append(f"退出码: {data.exit_code}")
            output.append(f"执行时间: {data.execution_time:.2f}s")
            
            # 标准输出
            if data.stdout:
                output.append("\n--- 标准输出 ---")
                output.append(data.stdout.rstrip())
            
            # 错误输出
            if data.stderr:
                output.append("\n--- 错误输出 ---")
                output.append(data.stderr.rstrip())
            
            return '\n'.join(output)
        
        elif isinstance(data, ValidationResult):
            output = []
            
            # 验证状态
            status = "✓ 验证通过" if data.is_valid else "✗ 验证失败"
            output.append(f"状态: {status}")
            output.append(f"风险级别: {data.risk_level}")
            
            # 错误信息
            if data.errors:
                output.append("\n错误:")
                for error in data.errors:
                    output.append(f"  - {error}")
            
            # 警告信息
            if data.warnings:
                output.append("\n警告:")
                for warning in data.warnings:
                    output.append(f"  - {warning}")
            
            return '\n'.join(output)
        
        elif isinstance(data, dict):
            return self._format_dict_output(data)
        
        elif isinstance(data, list):
            return '\n'.join(str(item) for item in data)
        
        else:
            return str(data)
    
    def _format_dict_output(self, data: Dict[str, Any], indent: int = 0) -> str:
        """格式化字典输出"""
        output = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                output.append(f"{prefix}{key}:")
                output.append(self._format_dict_output(value, indent + 1))
            elif isinstance(value, list):
                output.append(f"{prefix}{key}: [{len(value)} 项]")
            else:
                output.append(f"{prefix}{key}: {value}")
        
        return '\n'.join(output)
    
    def run_interactive_mode(self):
        """运行交互模式"""
        print("Docker命令执行工具 - 交互模式")
        print("输入 'exit' 或 'quit' 退出，输入 'help' 获取帮助")
        print()
        
        while True:
            try:
                command_input = input("docker-exec> ").strip()
                
                if not command_input:
                    continue
                
                if command_input.lower() in ['exit', 'quit']:
                    break
                
                if command_input.lower() == 'help':
                    self._show_interactive_help()
                    continue
                
                if command_input.lower() == 'status':
                    status = self.executor.get_status()
                    print(self.format_output(status, 'text'))
                    continue
                
                if command_input.lower().startswith('history'):
                    parts = command_input.split()
                    count = int(parts[1]) if len(parts) > 1 else 10
                    history = self.executor.get_command_history(count)
                    print(self.format_output(history, 'text'))
                    continue
                
                # 执行命令
                result = self.executor.execute_command(command_input)
                print(self.format_output(result, 'text'))
                print()
                
            except KeyboardInterrupt:
                print("\n使用 'exit' 退出")
            except EOFError:
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def _show_interactive_help(self):
        """显示交互模式帮助"""
        help_text = """
交互模式命令:
  <command>        - 执行Docker命令
  status          - 显示系统状态
  history [N]     - 显示最近N条命令历史
  help            - 显示此帮助信息
  exit/quit       - 退出交互模式

示例:
  ls -la
  cat /etc/os-release
  uname -a
        """
        print(help_text)
    
    def run(self, args=None):
        """运行CLI"""
        parser = self.create_parser()
        args = parser.parse_args(args)
        
        # 设置日志
        self.setup_logging(args.verbose, args.quiet)
        
        try:
            # 初始化执行器
            self.executor = DockerCommandExecutor(args.config)
            
            # 处理查询操作
            if args.status:
                status = self.executor.get_status()
                print(self.format_output(status, args.output))
                return 0
            
            if args.history is not None:
                history = self.executor.get_command_history(args.history)
                print(self.format_output(history, args.output))
                return 0
            
            # 处理交互模式
            if args.interactive:
                self.run_interactive_mode()
                return 0
            
            # 处理批量执行
            if args.batch:
                commands = []
                try:
                    with open(args.batch, 'r', encoding='utf-8') as f:
                        commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                except FileNotFoundError:
                    print(f"错误: 找不到批量文件 {args.batch}")
                    return 1
                except Exception as e:
                    print(f"错误: 读取批量文件失败: {e}")
                    return 1
                
                results = self.executor.execute_batch(commands, args.mount)
                for i, result in enumerate(results):
                    print(f"\n=== 命令 {i+1}: {commands[i]} ===")
                    print(self.format_output(result, args.output))
                return 0
            
            # 处理单个命令
            if not args.command:
                parser.print_help()
                return 1
            
            command_input = ' '.join(args.command)
            
            # 添加额外参数
            if args.workdir:
                command_input += f" --workdir {args.workdir}"
            if args.timeout:
                command_input += f" --timeout {args.timeout}"
            
            # 验证模式
            if args.validate:
                result = self.executor.validate_command(command_input)
                print(self.format_output(result, args.output))
                return 0 if result.is_valid else 1
            
            # 执行命令
            result = self.executor.execute_command(command_input, args.mount)
            print(self.format_output(result, args.output))
            
            return 0 if result.success else result.exit_code
            
        except KeyboardInterrupt:
            print("\n操作已取消")
            return 130
        except Exception as e:
            print(f"错误: {e}")
            return 1
        finally:
            if self.executor:
                self.executor.cleanup()


def main():
    """主入口函数"""
    cli = CLIInterface()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())