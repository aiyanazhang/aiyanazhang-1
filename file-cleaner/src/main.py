#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地目录文件清理脚本系统 - 主程序入口
提供命令行接口和交互模式
"""

import argparse
import sys
import os
import time
from pathlib import Path
from typing import List, Optional

# 添加src目录到Python路径
script_dir = Path(__file__).parent
if script_dir.name != 'src':
    src_dir = script_dir / 'src'
    sys.path.insert(0, str(src_dir))

from config_manager import init_config, get_config
from input_validator import validate_user_input, RiskLevel
from file_matcher import FileMatchEngine
from safety_checker import SafetyChecker
from confirmation_ui import get_user_confirmation, ConfirmationUI
from backup_manager import BackupManager
from file_deleter import FileDeleter
from logger import get_logger, init_logger
from rollback_manager import RollbackManager


class FileCleanerApp:
    """文件清理应用主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化应用
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化配置和日志
        self.config = init_config(config_path)
        self.logger = init_logger()
        
        # 初始化组件
        self.validator = None
        self.matcher = None
        self.safety_checker = None
        self.ui = None
        self.backup_manager = None
        self.file_deleter = None
        self.rollback_manager = None
        
        # 应用设置  
        self.dry_run = False
        self.verbose = False
        self.base_dir = "."
        
    def _init_components(self):
        """延迟初始化组件"""
        if self.matcher is None:
            self.matcher = FileMatchEngine(self.base_dir)
        if self.safety_checker is None:
            self.safety_checker = SafetyChecker()
        if self.ui is None:
            use_colors = self.config.get_bool('USE_COLORS', True)
            self.ui = ConfirmationUI(use_colors)
    
    def run_interactive(self):
        """运行交互模式"""
        self._init_components()
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    文件清理工具                                ║")
        print("║                   交互式模式                                   ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print("欢迎使用文件清理工具！")
        print("输入 'help' 查看帮助，输入 'quit' 退出程序")
        print()
        
        while True:
            try:
                # 获取用户输入
                user_input = input("clean> ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                elif user_input.lower() in ['help', 'h']:
                    self._show_help()
                elif user_input.lower() in ['config', 'settings']:
                    self._show_config()
                elif user_input.lower().startswith('cd '):
                    self._change_directory(user_input[3:].strip())
                elif user_input.lower() == 'pwd':
                    print(f"当前目录: {os.path.abspath(self.base_dir)}")
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                else:
                    # 执行文件搜索和清理
                    self._process_pattern(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n操作已取消")
                break
            except EOFError:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
    
    def run_command_line(self, args):
        """
        运行命令行模式
        
        Args:
            args: 命令行参数
        """
        self._init_components()
        
        # 设置选项
        self.dry_run = args.dry_run
        self.verbose = args.verbose
        
        if args.directory:
            self.base_dir = args.directory
            self.matcher = FileMatchEngine(self.base_dir)
        
        # 执行相应操作
        if args.list_backups:
            self._list_backups()
        elif args.restore:
            self._restore_files(args.restore)
        elif args.pattern:
            # 设置文件删除器
            self.file_deleter.dry_run = self.dry_run
            self._process_pattern(args.pattern, args.recursive)
        else:
            print("请指定要搜索的文件模式，使用 --help 查看帮助")
    
    def _process_pattern(self, pattern: str, recursive: bool = False):
        """
        处理文件模式
        
        Args:
            pattern: 搜索模式
            recursive: 是否递归搜索
        """
        print(f"\n搜索模式: '{pattern}'")
        if recursive:
            print("递归搜索子目录")
        print(f"搜索目录: {os.path.abspath(self.base_dir)}")
        print("-" * 60)
        
        # 1. 验证输入
        validation_result = validate_user_input(pattern)
        if not validation_result.is_valid:
            print(f"❌ 输入验证失败: {validation_result.message}")
            return
        
        # 显示验证结果
        risk_color = self._get_risk_color(validation_result.risk_level)
        print(f"输入类型: {validation_result.input_type.value}")
        print(f"风险等级: {self.ui._colorize(validation_result.risk_level.value, risk_color)}")
        if validation_result.message:
            print(f"说明: {validation_result.message}")
        
        # 2. 搜索文件
        print(f"\n🔍 搜索匹配文件...")
        match_result = self.matcher.find_files(pattern, recursive)
        
        if not match_result.files:
            print("未找到匹配的文件")
            return
        
        print(f"找到 {match_result.total_count} 个文件，总大小 {self._format_size(match_result.total_size)}")
        
        # 3. 安全检查
        print(f"\n🛡️  执行安全检查...")
        file_risks = self.safety_checker.check_files_batch(match_result.files)
        
        # 4. 显示结果和获取确认
        if self.dry_run:
            print(f"\n{self.ui._colorize('📋 预览模式 - 不会实际删除文件', 'BLUE')}")
            self.ui.show_file_list(file_risks)
            self.ui.show_summary(file_risks)
        else:
            # 获取用户确认
            confirmation = get_user_confirmation(file_risks, self.config.get_bool('USE_COLORS', True))
            
            if confirmation.cancelled:
                print("操作已取消")
                return
            
            if not confirmation.confirmed_files:
                print("没有文件被确认删除")
                return
            
            # 执行删除（现在集成实际的删除功能）
            print(f"\n🗑️  准备删除 {len(confirmation.confirmed_files)} 个文件...")
            
            # 使用文件删除器执行删除
            delete_result = self.file_deleter.delete_files(
                confirmation.confirmed_files, 
                f"清理操作: {pattern}"
            )
            
            # 记录操作日志
            from logger import OperationLog
            operation_log = OperationLog(
                session_id=self.logger.session_id,
                timestamp=time.time(),
                operation_type="file_cleanup",
                pattern=pattern,
                files_found=len(match_result.files),
                files_deleted=len(delete_result.successful),
                files_failed=len(delete_result.failed),
                total_size=sum(f.size for f in match_result.files),
                backup_id=delete_result.backup_id,
                execution_time=delete_result.total_time,
                status="completed" if delete_result.successful else "failed",
                details={
                    "recursive": recursive,
                    "confirmation_type": confirmation.confirmation_type.value
                }
            )
            
            self.logger.log_batch_deletion(operation_log)
    
    def _get_risk_color(self, risk_level) -> str:
        """获取风险等级对应的颜色"""
        color_map = {
            RiskLevel.LOW: 'GREEN',
            RiskLevel.MEDIUM: 'CYAN', 
            RiskLevel.HIGH: 'YELLOW',
            RiskLevel.EXTREME: 'RED'
        }
        return getattr(self.ui, f'_colorize', lambda x, y: x)('', getattr(self.ui, color_map.get(risk_level, 'RESET'), ''))
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f}MB"
        else:
            return f"{size/(1024*1024*1024):.1f}GB"
    
    def _show_help(self):
        """显示帮助信息"""
        print("""
=== 文件清理工具帮助 ===

交互模式命令:
  help, h          - 显示此帮助信息
  quit, exit, q    - 退出程序
  config           - 显示当前配置
  cd <目录>        - 切换工作目录
  pwd              - 显示当前目录
  clear            - 清屏
  history, log     - 查看操作历史
  backups, backup  - 查看备份列表
  restore, rollback - 交互式恢复文件

文件模式示例:
  *.tmp            - 删除所有临时文件
  *.log            - 删除所有日志文件
  temp*            - 删除以temp开头的文件
  backup_*         - 删除以backup_开头的文件
  specific.txt     - 删除特定文件

安全提示:
  🟢 绿色 - 安全文件，可以放心删除
  🔵 蓝色 - 谨慎文件，建议确认后删除  
  🟡 黄色 - 警告文件，删除前请仔细检查
  🔴 红色 - 危险文件，删除可能影响系统
  ⚫ 灰色 - 被保护文件，无法删除

输入任何文件模式开始搜索...
        """)
    
    def _show_config(self):
        """显示当前配置"""
        print("\n=== 当前配置 ===")
        print(f"工作目录: {os.path.abspath(self.base_dir)}")
        print(f"备份目录: {self.config.get('DEFAULT_BACKUP_DIR')}")
        print(f"启用备份: {self.config.get_bool('ENABLE_BACKUP')}")
        print(f"需要确认: {self.config.get_bool('REQUIRE_CONFIRMATION')}")
        print(f"使用颜色: {self.config.get_bool('USE_COLORS')}")
        print(f"日志级别: {self.config.get('LOG_LEVEL')}")
        print(f"大文件阈值: {self.config.get('LARGE_FILE_THRESHOLD')}MB")
    
    def _change_directory(self, path: str):
        """切换工作目录"""
        try:
            if path.startswith('~'):
                path = os.path.expanduser(path)
            
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                self.base_dir = abs_path
                self.matcher = FileMatchEngine(self.base_dir)
                print(f"已切换到: {abs_path}")
            else:
                print(f"目录不存在: {path}")
        except Exception as e:
            print(f"切换目录失败: {e}")
    
    def _list_backups(self):
        """列出备份"""
        print("📅 列出所有备份:")
        self.backup_manager.show_backup_list()
    
    def _restore_files(self, backup_id: str):
        """恢复文件"""
        print(f"🔄 恢复备份: {backup_id}")
        result = self.rollback_manager.restore_backup(backup_id, "interactive")
        
        if result.successful:
            print(f"✅ 恢复成功: {len(result.successful)} 个文件")
        else:
            print("❌ 恢复失败")
    
    def _show_operation_history(self):
        """显示操作历史"""
        self.logger.show_recent_operations(10)
    
    def _show_backups(self):
        """显示备份列表"""
        self.backup_manager.show_backup_list()
    
    def _interactive_restore(self):
        """交互式恢复"""
        self.rollback_manager.interactive_restore()


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="本地目录文件清理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                           # 启动交互模式
  %(prog)s -p "*.tmp"                # 删除临时文件
  %(prog)s -p "*.log" -r             # 递归删除日志文件
  %(prog)s -p "backup_*" -d          # 预览模式，不实际删除
  %(prog)s --list-backups            # 列出所有备份
  %(prog)s --restore backup_id       # 恢复指定备份

安全提示:
  - 本工具会在删除前进行安全检查
  - 重要文件会被自动保护
  - 默认会创建备份以便恢复
  - 使用 -d 参数可以预览而不实际删除
        """
    )
    
    # 基本选项
    parser.add_argument('-p', '--pattern', 
                       help='要搜索的文件模式 (如: *.tmp, temp*, specific.txt)')
    
    parser.add_argument('-d', '--directory',
                       help='指定搜索目录 (默认: 当前目录)')
    
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='递归搜索子目录')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，显示将要删除的文件但不实际删除')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出模式')
    
    # 配置选项
    parser.add_argument('-c', '--config',
                       help='指定配置文件路径')
    
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份 (危险选项)')
    
    parser.add_argument('--no-confirm', action='store_true',
                       help='跳过确认步骤 (危险选项)')
    
    # 备份和恢复
    parser.add_argument('--list-backups', action='store_true',
                       help='列出所有可用备份')
    
    parser.add_argument('--restore',
                       help='从指定备份恢复文件')
    
    return parser


def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # 创建应用实例
        app = FileCleanerApp(args.config if hasattr(args, 'config') else None)
        
        # 根据参数决定运行模式
        if len(sys.argv) == 1:
            # 无参数，启动交互模式
            app.run_interactive()
        else:
            # 有参数，运行命令行模式
            app.run_command_line(args)
            
    except KeyboardInterrupt:
        print("\n程序已中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序错误: {e}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
