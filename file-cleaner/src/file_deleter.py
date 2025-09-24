#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除执行器模块
安全执行文件删除操作，支持原子操作和进度显示
"""

import os
import time
import shutil
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from config_manager import get_config
from file_matcher import FileInfo
from backup_manager import BackupManager


class DeleteResult(Enum):
    """删除结果枚举"""
    SUCCESS = "success"          # 成功
    FAILED = "failed"            # 失败
    SKIPPED = "skipped"          # 跳过
    PERMISSION_DENIED = "permission_denied"  # 权限不足
    NOT_FOUND = "not_found"      # 文件不存在


@dataclass
class FileDeleteResult:
    """单个文件删除结果"""
    file_info: FileInfo          # 文件信息
    result: DeleteResult         # 删除结果
    error_message: str = ""      # 错误信息
    execution_time: float = 0.0  # 执行时间


@dataclass
class BatchDeleteResult:
    """批量删除结果"""
    total_files: int             # 总文件数
    successful: List[FileDeleteResult]  # 成功删除的文件
    failed: List[FileDeleteResult]      # 删除失败的文件
    skipped: List[FileDeleteResult]     # 跳过的文件
    backup_id: Optional[str] = None     # 备份ID
    total_time: float = 0.0            # 总执行时间
    total_size_deleted: int = 0        # 删除的总大小


class FileDeleter:
    """文件删除器"""
    
    def __init__(self, enable_backup: bool = True, dry_run: bool = False):
        """
        初始化删除器
        
        Args:
            enable_backup: 是否启用备份
            dry_run: 是否为模拟运行
        """
        self.config = get_config()
        self.enable_backup = enable_backup and self.config.get_bool('ENABLE_BACKUP', True)
        self.dry_run = dry_run
        
        # 初始化备份管理器
        if self.enable_backup:
            self.backup_manager = BackupManager()
        else:
            self.backup_manager = None
        
        # 进度回调函数
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """
        设置进度回调函数
        
        Args:
            callback: 回调函数 (current, total, message)
        """
        self.progress_callback = callback
    
    def delete_files(self, files: List[FileInfo], 
                    description: str = "文件清理") -> BatchDeleteResult:
        """
        批量删除文件
        
        Args:
            files: 要删除的文件列表
            description: 操作描述
            
        Returns:
            批量删除结果
        """
        start_time = time.time()
        
        # 初始化结果
        result = BatchDeleteResult(
            total_files=len(files),
            successful=[],
            failed=[],
            skipped=[]
        )
        
        if not files:
            return result
        
        # 创建备份
        backup_id = None
        if self.enable_backup and not self.dry_run:
            self._report_progress(0, len(files), "创建备份...")
            backup_id = self.backup_manager.create_backup(files, description)
            if backup_id:
                result.backup_id = backup_id
                print(f"✅ 备份已创建: {backup_id}")
            else:
                print("⚠️  备份创建失败，继续删除操作")
        
        # 执行删除操作
        for i, file_info in enumerate(files):
            self._report_progress(i + 1, len(files), f"删除: {file_info.name}")
            
            delete_result = self._delete_single_file(file_info)
            
            # 分类结果
            if delete_result.result == DeleteResult.SUCCESS:
                result.successful.append(delete_result)
                result.total_size_deleted += file_info.size
            elif delete_result.result == DeleteResult.SKIPPED:
                result.skipped.append(delete_result)
            else:
                result.failed.append(delete_result)
        
        result.total_time = time.time() - start_time
        
        # 显示结果摘要
        self._show_result_summary(result)
        
        return result
    
    def _delete_single_file(self, file_info: FileInfo) -> FileDeleteResult:
        """
        删除单个文件
        
        Args:
            file_info: 文件信息
            
        Returns:
            删除结果
        """
        start_time = time.time()
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_info.path):
                return FileDeleteResult(
                    file_info=file_info,
                    result=DeleteResult.NOT_FOUND,
                    error_message="文件不存在",
                    execution_time=time.time() - start_time
                )
            
            # 模拟运行模式
            if self.dry_run:
                # 模拟延迟
                time.sleep(0.01)
                return FileDeleteResult(
                    file_info=file_info,
                    result=DeleteResult.SKIPPED,
                    error_message="模拟运行模式",
                    execution_time=time.time() - start_time
                )
            
            # 检查文件权限
            if not os.access(file_info.path, os.W_OK):
                return FileDeleteResult(
                    file_info=file_info,
                    result=DeleteResult.PERMISSION_DENIED,
                    error_message="权限不足",
                    execution_time=time.time() - start_time
                )
            
            # 执行删除
            if file_info.is_dir:
                # 删除目录
                if os.path.islink(file_info.path):
                    os.unlink(file_info.path)
                else:
                    shutil.rmtree(file_info.path)
            else:
                # 删除文件
                os.remove(file_info.path)
            
            return FileDeleteResult(
                file_info=file_info,
                result=DeleteResult.SUCCESS,
                execution_time=time.time() - start_time
            )
            
        except PermissionError:
            return FileDeleteResult(
                file_info=file_info,
                result=DeleteResult.PERMISSION_DENIED,
                error_message="权限不足",
                execution_time=time.time() - start_time
            )
        except FileNotFoundError:
            return FileDeleteResult(
                file_info=file_info,
                result=DeleteResult.NOT_FOUND,
                error_message="文件不存在",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return FileDeleteResult(
                file_info=file_info,
                result=DeleteResult.FAILED,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _report_progress(self, current: int, total: int, message: str):
        """
        报告进度
        
        Args:
            current: 当前进度
            total: 总数
            message: 消息
        """
        if self.progress_callback:
            self.progress_callback(current, total, message)
        else:
            # 默认进度显示
            if total > 0:
                percentage = (current / total) * 100
                print(f"\r进度: {current}/{total} ({percentage:.1f}%) - {message}", end='', flush=True)
                if current == total:
                    print()  # 换行
    
    def _show_result_summary(self, result: BatchDeleteResult):
        """
        显示结果摘要
        
        Args:
            result: 批量删除结果
        """
        print(f"\n{'='*60}")
        print(f"🗑️  删除操作完成")
        print(f"{'='*60}")
        
        # 统计信息
        success_count = len(result.successful)
        failed_count = len(result.failed)
        skipped_count = len(result.skipped)
        
        print(f"📊 操作统计:")
        print(f"   ✅ 成功删除: {success_count} 个文件")
        print(f"   ❌ 删除失败: {failed_count} 个文件")
        print(f"   ⏭️  跳过文件: {skipped_count} 个文件")
        print(f"   💾 释放空间: {self._format_size(result.total_size_deleted)}")
        print(f"   ⏱️  耗时: {result.total_time:.2f} 秒")
        
        if result.backup_id:
            print(f"   🛡️  备份ID: {result.backup_id}")
        
        # 显示失败的文件
        if result.failed:
            print(f"\n❌ 删除失败的文件:")
            for delete_result in result.failed:
                file_info = delete_result.file_info
                print(f"   - {file_info.name}: {delete_result.error_message}")
        
        # 显示权限问题的文件
        permission_denied = [r for r in result.failed 
                           if r.result == DeleteResult.PERMISSION_DENIED]
        if permission_denied:
            print(f"\n🔒 权限不足的文件 (可尝试使用 sudo):")
            for delete_result in permission_denied:
                print(f"   - {delete_result.file_info.name}")
    
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
    
    def can_delete_file(self, file_path: str) -> Tuple[bool, str]:
        """
        检查是否可以删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否可以删除, 原因)
        """
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        if not os.access(file_path, os.W_OK):
            return False, "权限不足"
        
        # 检查是否为系统关键文件
        abs_path = os.path.abspath(file_path)
        system_dirs = ['/bin', '/usr', '/etc', '/var', '/lib']
        
        for sys_dir in system_dirs:
            if abs_path.startswith(sys_dir):
                return False, "系统文件"
        
        return True, "可以删除"
    
    def estimate_delete_time(self, files: List[FileInfo]) -> float:
        """
        估算删除时间
        
        Args:
            files: 文件列表
            
        Returns:
            估算时间（秒）
        """
        # 基于文件数量和大小的简单估算
        base_time = len(files) * 0.01  # 每个文件基础时间
        
        # 大文件需要更多时间
        large_files = sum(1 for f in files if f.size > 10 * 1024 * 1024)  # >10MB
        large_file_time = large_files * 0.1
        
        # 备份时间
        backup_time = 0
        if self.enable_backup:
            total_size = sum(f.size for f in files)
            backup_time = total_size / (10 * 1024 * 1024)  # 假设10MB/s压缩速度
        
        return base_time + large_file_time + backup_time


class ProgressDisplay:
    """进度显示器"""
    
    def __init__(self, show_details: bool = True):
        """
        初始化进度显示器
        
        Args:
            show_details: 是否显示详细信息
        """
        self.show_details = show_details
        self.start_time = None
    
    def start(self, total: int):
        """开始进度显示"""
        self.start_time = time.time()
    
    def update(self, current: int, total: int, message: str):
        """更新进度"""
        if total == 0:
            return
        
        percentage = (current / total) * 100
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # 估算剩余时间
        if current > 0:
            eta = (elapsed / current) * (total - current)
            eta_str = f" (剩余: {eta:.1f}s)"
        else:
            eta_str = ""
        
        # 进度条
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        if self.show_details:
            print(f"\r[{bar}] {percentage:5.1f}% ({current}/{total}){eta_str} - {message}", 
                  end='', flush=True)
        else:
            print(f"\r[{bar}] {percentage:5.1f}%", end='', flush=True)
        
        if current == total:
            print()  # 换行


def delete_files_with_backup(files: List[FileInfo], 
                           description: str = "文件清理",
                           dry_run: bool = False,
                           show_progress: bool = True) -> BatchDeleteResult:
    """
    删除文件并创建备份的便捷函数
    
    Args:
        files: 要删除的文件列表
        description: 操作描述
        dry_run: 是否为模拟运行
        show_progress: 是否显示进度
        
    Returns:
        删除结果
    """
    deleter = FileDeleter(enable_backup=True, dry_run=dry_run)
    
    # 设置进度显示
    if show_progress:
        progress = ProgressDisplay()
        deleter.set_progress_callback(progress.update)
        progress.start(len(files))
    
    return deleter.delete_files(files, description)


if __name__ == '__main__':
    # 测试删除器
    from file_matcher import FileMatchEngine
    
    print("=== 删除执行器测试 ===")
    
    # 创建测试删除器（模拟模式）
    deleter = FileDeleter(enable_backup=True, dry_run=True)
    
    # 测试估算时间
    engine = FileMatchEngine(".")
    result = engine.find_files("*.py", recursive=False)
    
    if result.files:
        estimated_time = deleter.estimate_delete_time(result.files)
        print(f"估算删除时间: {estimated_time:.2f} 秒")
        
        # 执行模拟删除
        print(f"执行模拟删除 {len(result.files)} 个文件...")
        delete_result = deleter.delete_files(result.files, "测试删除")
        
        print(f"模拟删除完成: {len(delete_result.skipped)} 个文件被跳过")
    else:
        print("未找到测试文件")
