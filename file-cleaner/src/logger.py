#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志记录器模块
记录所有操作历史，支持审计和故障排查
"""

import os
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from config_manager import get_config


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class OperationLog:
    """操作日志记录"""
    session_id: str              # 会话ID
    timestamp: float             # 时间戳
    operation_type: str          # 操作类型
    pattern: str                 # 搜索模式
    files_found: int             # 找到的文件数
    files_deleted: int           # 删除的文件数
    files_failed: int            # 失败的文件数
    total_size: int              # 总文件大小
    backup_id: Optional[str]     # 备份ID
    execution_time: float        # 执行时间
    status: str                  # 操作状态
    details: Dict[str, Any]      # 详细信息


class CleanerLogger:
    """清理工具日志记录器"""
    
    def __init__(self):
        """初始化日志记录器"""
        self.config = get_config()
        
        # 配置日志文件路径
        self.log_file = Path(self.config.get('LOG_FILE', '~/.clean-script.log')).expanduser()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志级别
        log_level_str = self.config.get('LOG_LEVEL', 'INFO')
        self.log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        
        # 会话ID
        self.session_id = self._generate_session_id()
        
        # 设置日志格式
        self._setup_logging()
        
        # 操作历史文件
        self.history_file = self.log_file.parent / 'operation_history.json'
        self._load_operation_history()
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return f"session_{int(time.time())}_{os.getpid()}"
    
    def _setup_logging(self):
        """设置日志配置"""
        # 创建日志格式器
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(session_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.log_level)
        
        # 创建控制台处理器（可选）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)  # 只显示警告及以上级别
        
        # 配置根日志记录器
        self.logger = logging.getLogger('file_cleaner')
        self.logger.setLevel(self.log_level)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        if self.config.get_bool('LOG_TO_CONSOLE', False):
            self.logger.addHandler(console_handler)
        
        # 添加会话ID到日志记录
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.session_id = self.session_id
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    def _load_operation_history(self):
        """加载操作历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.operation_history = json.load(f)
            except Exception as e:
                self.logger.warning(f"无法加载操作历史: {e}")
                self.operation_history = []
        else:
            self.operation_history = []
    
    def _save_operation_history(self):
        """保存操作历史"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.operation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"无法保存操作历史: {e}")
    
    def log_session_start(self, mode: str = "interactive"):
        """
        记录会话开始
        
        Args:
            mode: 运行模式 (interactive, command_line)
        """
        self.logger.info(f"会话开始 - 模式: {mode}")
        self.logger.info(f"配置文件: {self.config.config_path}")
        self.logger.info(f"日志级别: {self.log_level}")
    
    def log_session_end(self):
        """记录会话结束"""
        self.logger.info("会话结束")
    
    def log_pattern_search(self, pattern: str, recursive: bool, 
                          files_found: int, search_time: float):
        """
        记录模式搜索
        
        Args:
            pattern: 搜索模式
            recursive: 是否递归
            files_found: 找到的文件数
            search_time: 搜索耗时
        """
        self.logger.info(f"搜索完成 - 模式: '{pattern}', 递归: {recursive}, "
                        f"找到: {files_found} 个文件, 耗时: {search_time:.2f}s")
    
    def log_safety_check(self, total_files: int, safe_files: int, 
                        dangerous_files: int, forbidden_files: int):
        """
        记录安全检查结果
        
        Args:
            total_files: 总文件数
            safe_files: 安全文件数
            dangerous_files: 危险文件数
            forbidden_files: 禁止文件数
        """
        self.logger.info(f"安全检查完成 - 总计: {total_files}, 安全: {safe_files}, "
                        f"危险: {dangerous_files}, 禁止: {forbidden_files}")
        
        if dangerous_files > 0:
            self.logger.warning(f"发现 {dangerous_files} 个危险文件")
        
        if forbidden_files > 0:
            self.logger.warning(f"发现 {forbidden_files} 个被禁止删除的文件")
    
    def log_user_confirmation(self, confirmation_type: str, 
                            confirmed_files: int, total_files: int):
        """
        记录用户确认
        
        Args:
            confirmation_type: 确认类型
            confirmed_files: 确认删除的文件数
            total_files: 总文件数
        """
        self.logger.info(f"用户确认 - 类型: {confirmation_type}, "
                        f"确认删除: {confirmed_files}/{total_files} 个文件")
    
    def log_backup_creation(self, backup_id: str, file_count: int, 
                          backup_size: int, backup_time: float):
        """
        记录备份创建
        
        Args:
            backup_id: 备份ID
            file_count: 文件数量
            backup_size: 备份大小
            backup_time: 备份耗时
        """
        self.logger.info(f"备份创建成功 - ID: {backup_id}, 文件: {file_count}, "
                        f"大小: {backup_size} 字节, 耗时: {backup_time:.2f}s")
    
    def log_backup_failure(self, error_message: str):
        """
        记录备份失败
        
        Args:
            error_message: 错误信息
        """
        self.logger.error(f"备份创建失败: {error_message}")
    
    def log_file_deletion(self, file_path: str, file_size: int, 
                         result: str, error_message: str = ""):
        """
        记录单个文件删除
        
        Args:
            file_path: 文件路径
            file_size: 文件大小
            result: 删除结果
            error_message: 错误信息
        """
        if result == "success":
            self.logger.info(f"文件删除成功: {file_path} ({file_size} 字节)")
        elif result == "failed":
            self.logger.error(f"文件删除失败: {file_path} - {error_message}")
        elif result == "permission_denied":
            self.logger.warning(f"文件删除权限不足: {file_path}")
        else:
            self.logger.debug(f"文件删除跳过: {file_path} - {error_message}")
    
    def log_batch_deletion(self, operation_log: OperationLog):
        """
        记录批量删除操作
        
        Args:
            operation_log: 操作日志
        """
        self.logger.info(f"批量删除完成 - 模式: '{operation_log.pattern}', "
                        f"成功: {operation_log.files_deleted}, "
                        f"失败: {operation_log.files_failed}, "
                        f"耗时: {operation_log.execution_time:.2f}s")
        
        # 保存到操作历史
        self.operation_history.append(asdict(operation_log))
        self._save_operation_history()
        
        # 限制历史记录数量
        max_history = 1000
        if len(self.operation_history) > max_history:
            self.operation_history = self.operation_history[-max_history:]
            self._save_operation_history()
    
    def log_restore_operation(self, backup_id: str, restored_files: int, 
                            restore_time: float, success: bool):
        """
        记录恢复操作
        
        Args:
            backup_id: 备份ID
            restored_files: 恢复的文件数
            restore_time: 恢复耗时
            success: 是否成功
        """
        if success:
            self.logger.info(f"文件恢复成功 - 备份ID: {backup_id}, "
                           f"恢复: {restored_files} 个文件, 耗时: {restore_time:.2f}s")
        else:
            self.logger.error(f"文件恢复失败 - 备份ID: {backup_id}")
    
    def log_error(self, error_message: str, exception: Exception = None):
        """
        记录错误
        
        Args:
            error_message: 错误信息
            exception: 异常对象
        """
        if exception:
            self.logger.error(f"{error_message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(error_message)
    
    def log_warning(self, warning_message: str):
        """
        记录警告
        
        Args:
            warning_message: 警告信息
        """
        self.logger.warning(warning_message)
    
    def log_debug(self, debug_message: str):
        """
        记录调试信息
        
        Args:
            debug_message: 调试信息
        """
        self.logger.debug(debug_message)
    
    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取操作历史
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            操作历史列表
        """
        return self.operation_history[-limit:] if limit > 0 else self.operation_history
    
    def get_session_logs(self) -> List[str]:
        """
        获取当前会话的日志
        
        Returns:
            日志行列表
        """
        if not self.log_file.exists():
            return []
        
        session_logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if self.session_id in line:
                        session_logs.append(line.strip())
        except Exception as e:
            self.logger.error(f"读取日志文件失败: {e}")
        
        return session_logs
    
    def cleanup_old_logs(self, max_size_mb: int = 50):
        """
        清理旧日志文件
        
        Args:
            max_size_mb: 最大日志文件大小(MB)
        """
        if not self.log_file.exists():
            return
        
        try:
            file_size = self.log_file.stat().st_size
            max_size = max_size_mb * 1024 * 1024
            
            if file_size > max_size:
                # 保留最后一半的日志
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                keep_lines = lines[len(lines)//2:]
                
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.writelines(keep_lines)
                
                self.logger.info(f"日志文件已清理，保留 {len(keep_lines)} 行")
                
        except Exception as e:
            self.logger.error(f"清理日志文件失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取日志统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_operations": len(self.operation_history),
            "session_id": self.session_id,
            "log_file": str(self.log_file),
            "log_level": self.log_level,
            "total_files_deleted": 0,
            "total_files_failed": 0,
            "total_backups_created": 0
        }
        
        # 统计操作历史
        for op in self.operation_history:
            stats["total_files_deleted"] += op.get("files_deleted", 0)
            stats["total_files_failed"] += op.get("files_failed", 0)
            if op.get("backup_id"):
                stats["total_backups_created"] += 1
        
        # 日志文件大小
        if self.log_file.exists():
            stats["log_file_size"] = self.log_file.stat().st_size
        else:
            stats["log_file_size"] = 0
        
        return stats
    
    def show_recent_operations(self, count: int = 10):
        """
        显示最近的操作
        
        Args:
            count: 显示数量
        """
        recent_ops = self.get_operation_history(count)
        
        if not recent_ops:
            print("📋 没有操作历史记录")
            return
        
        print(f"📋 最近 {len(recent_ops)} 次操作:")
        print("=" * 80)
        
        for i, op in enumerate(reversed(recent_ops), 1):
            timestamp = datetime.fromtimestamp(op['timestamp'])
            print(f"{i:2d}. [{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"模式: '{op['pattern']}'")
            print(f"    状态: {op['status']} | "
                  f"删除: {op['files_deleted']} | "
                  f"失败: {op['files_failed']} | "
                  f"耗时: {op['execution_time']:.2f}s")
            if op.get('backup_id'):
                print(f"    备份: {op['backup_id']}")
            print()


# 全局日志记录器实例
_logger_instance = None


def get_logger() -> CleanerLogger:
    """获取全局日志记录器实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CleanerLogger()
    return _logger_instance


def init_logger() -> CleanerLogger:
    """初始化日志记录器"""
    global _logger_instance
    _logger_instance = CleanerLogger()
    return _logger_instance


if __name__ == '__main__':
    # 测试日志记录器
    logger = CleanerLogger()
    
    print("=== 日志记录器测试 ===")
    
    # 测试各种日志记录
    logger.log_session_start("test")
    logger.log_pattern_search("*.tmp", False, 5, 0.1)
    logger.log_safety_check(5, 3, 1, 1)
    logger.log_user_confirmation("batch", 3, 5)
    logger.log_backup_creation("backup_123", 3, 1024, 0.5)
    logger.log_file_deletion("/tmp/test.txt", 100, "success")
    logger.log_session_end()
    
    # 显示统计信息
    stats = logger.get_statistics()
    print(f"日志统计: {stats}")
    
    # 显示最近操作
    logger.show_recent_operations(3)
