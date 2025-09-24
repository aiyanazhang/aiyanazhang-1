#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回滚模块
提供操作回滚功能，恢复误删的文件
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from backup_manager import BackupManager, BackupMetadata
from logger import get_logger
from confirmation_ui import ColorCode


class RestoreResult(Enum):
    """恢复结果枚举"""
    SUCCESS = "success"          # 成功
    FAILED = "failed"            # 失败
    SKIPPED = "skipped"          # 跳过
    CONFLICT = "conflict"        # 路径冲突


@dataclass
class FileRestoreResult:
    """单个文件恢复结果"""
    original_path: str           # 原始路径
    restore_path: str            # 恢复路径
    result: RestoreResult        # 恢复结果
    error_message: str = ""      # 错误信息


@dataclass
class BatchRestoreResult:
    """批量恢复结果"""
    backup_id: str               # 备份ID
    total_files: int             # 总文件数
    successful: List[FileRestoreResult]  # 成功恢复的文件
    failed: List[FileRestoreResult]      # 恢复失败的文件
    skipped: List[FileRestoreResult]     # 跳过的文件
    conflicts: List[FileRestoreResult]   # 冲突的文件
    total_time: float = 0.0            # 总执行时间


class RollbackManager:
    """回滚管理器"""
    
    def __init__(self):
        """初始化回滚管理器"""
        self.backup_manager = BackupManager()
        self.logger = get_logger()
        
        # 冲突处理策略
        self.conflict_strategy = "ask"  # ask, overwrite, skip, rename
    
    def list_available_backups(self) -> List[BackupMetadata]:
        """
        列出可用的备份
        
        Returns:
            备份元数据列表
        """
        return self.backup_manager.list_backups()
    
    def show_backup_details(self, backup_id: str) -> Optional[BackupMetadata]:
        """
        显示备份详细信息
        
        Args:
            backup_id: 备份ID
            
        Returns:
            备份元数据，不存在返回None
        """
        metadata = self.backup_manager.get_backup_info(backup_id)
        if not metadata:
            print(f"❌ 备份不存在: {backup_id}")
            return None
        
        print(f"\n📋 备份详细信息: {backup_id}")
        print("=" * 60)
        print(f"📅 创建时间: {self._format_time(metadata.timestamp)}")
        print(f"📝 描述: {metadata.description}")
        print(f"📁 文件数量: {metadata.file_count}")
        print(f"💾 总大小: {self._format_size(metadata.total_size)}")
        print(f"🗂️  备份路径: {metadata.backup_path}")
        
        print(f"\n📄 包含的文件:")
        for i, file_path in enumerate(metadata.original_paths[:10], 1):
            print(f"  {i:2d}. {os.path.basename(file_path)}")
            print(f"      {file_path}")
        
        if len(metadata.original_paths) > 10:
            remaining = len(metadata.original_paths) - 10
            print(f"  ... 还有 {remaining} 个文件")
        
        return metadata
    
    def check_restore_conflicts(self, backup_id: str) -> Dict[str, List[str]]:
        """
        检查恢复冲突
        
        Args:
            backup_id: 备份ID
            
        Returns:
            冲突信息字典
        """
        metadata = self.backup_manager.get_backup_info(backup_id)
        if not metadata:
            return {"error": ["备份不存在"]}
        
        conflicts = {
            "existing_files": [],      # 已存在的文件
            "permission_issues": [],   # 权限问题
            "missing_directories": [], # 缺失的目录
            "readonly_files": []       # 只读文件
        }
        
        for file_path in metadata.original_paths:
            # 检查文件是否已存在
            if os.path.exists(file_path):
                conflicts["existing_files"].append(file_path)
            
            # 检查目录权限
            parent_dir = os.path.dirname(file_path)
            if not os.path.exists(parent_dir):
                conflicts["missing_directories"].append(parent_dir)
            elif not os.access(parent_dir, os.W_OK):
                conflicts["permission_issues"].append(parent_dir)
            
            # 检查只读文件
            if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
                conflicts["readonly_files"].append(file_path)
        
        return conflicts
    
    def restore_backup(self, backup_id: str, 
                      restore_mode: str = "interactive",
                      target_directory: Optional[str] = None,
                      selected_files: Optional[List[str]] = None) -> BatchRestoreResult:
        """
        恢复备份
        
        Args:
            backup_id: 备份ID
            restore_mode: 恢复模式 (interactive, auto, force)
            target_directory: 目标目录，None表示恢复到原位置
            selected_files: 选择恢复的文件，None表示全部恢复
            
        Returns:
            批量恢复结果
        """
        import time
        start_time = time.time()
        
        # 获取备份信息
        metadata = self.backup_manager.get_backup_info(backup_id)
        if not metadata:
            return BatchRestoreResult(
                backup_id=backup_id,
                total_files=0,
                successful=[],
                failed=[],
                skipped=[],
                conflicts=[]
            )
        
        print(f"🔄 开始恢复备份: {backup_id}")
        
        # 检查冲突
        conflicts_info = self.check_restore_conflicts(backup_id)
        if conflicts_info.get("existing_files") and restore_mode == "interactive":
            if not self._handle_conflicts_interactive(conflicts_info):
                print("❌ 用户取消恢复操作")
                return BatchRestoreResult(
                    backup_id=backup_id,
                    total_files=metadata.file_count,
                    successful=[],
                    failed=[],
                    skipped=[],
                    conflicts=[]
                )
        
        # 执行恢复
        restore_paths = selected_files if selected_files else None
        success = self.backup_manager.restore_backup(
            backup_id, restore_paths, target_directory
        )
        
        # 创建结果（简化版，实际实现需要更详细的跟踪）
        result = BatchRestoreResult(
            backup_id=backup_id,
            total_files=metadata.file_count,
            successful=[],
            failed=[],
            skipped=[],
            conflicts=[],
            total_time=time.time() - start_time
        )
        
        if success:
            # 简化处理，实际应该跟踪每个文件的恢复结果
            for file_path in metadata.original_paths:
                if not selected_files or file_path in selected_files:
                    result.successful.append(FileRestoreResult(
                        original_path=file_path,
                        restore_path=target_directory or file_path,
                        result=RestoreResult.SUCCESS
                    ))
        
        # 记录日志
        self.logger.log_restore_operation(
            backup_id, len(result.successful), result.total_time, success
        )
        
        # 显示结果
        self._show_restore_summary(result)
        
        return result
    
    def _handle_conflicts_interactive(self, conflicts_info: Dict[str, List[str]]) -> bool:
        """
        交互式处理冲突
        
        Args:
            conflicts_info: 冲突信息
            
        Returns:
            是否继续恢复
        """
        if conflicts_info.get("existing_files"):
            existing_files = conflicts_info["existing_files"]
            print(f"\n⚠️  发现 {len(existing_files)} 个文件冲突:")
            
            # 显示前几个冲突文件
            for i, file_path in enumerate(existing_files[:5], 1):
                print(f"  {i}. {file_path}")
            
            if len(existing_files) > 5:
                print(f"  ... 还有 {len(existing_files) - 5} 个文件")
            
            print("\n处理选项:")
            print("1. 覆盖现有文件")
            print("2. 跳过冲突文件")
            print("3. 重命名恢复文件")
            print("4. 取消恢复操作")
            
            while True:
                try:
                    choice = input("\n请选择处理方式 (1-4): ").strip()
                    
                    if choice == '1':
                        self.conflict_strategy = "overwrite"
                        return True
                    elif choice == '2':
                        self.conflict_strategy = "skip"
                        return True
                    elif choice == '3':
                        self.conflict_strategy = "rename"
                        return True
                    elif choice == '4':
                        return False
                    else:
                        print("❌ 无效选择，请输入 1-4")
                        
                except (KeyboardInterrupt, EOFError):
                    return False
        
        return True
    
    def _show_restore_summary(self, result: BatchRestoreResult):
        """
        显示恢复结果摘要
        
        Args:
            result: 恢复结果
        """
        print(f"\n{'='*60}")
        print(f"🔄 恢复操作完成")
        print(f"{'='*60}")
        
        success_count = len(result.successful)
        failed_count = len(result.failed)
        skipped_count = len(result.skipped)
        conflict_count = len(result.conflicts)
        
        print(f"📊 恢复统计:")
        print(f"   ✅ 成功恢复: {success_count} 个文件")
        print(f"   ❌ 恢复失败: {failed_count} 个文件")
        print(f"   ⏭️  跳过文件: {skipped_count} 个文件")
        print(f"   ⚠️  冲突文件: {conflict_count} 个文件")
        print(f"   ⏱️  总耗时: {result.total_time:.2f} 秒")
        
        # 显示失败的文件
        if result.failed:
            print(f"\n❌ 恢复失败的文件:")
            for restore_result in result.failed:
                print(f"   - {os.path.basename(restore_result.original_path)}: "
                      f"{restore_result.error_message}")
    
    def create_rollback_point(self, description: str = "手动创建的回滚点") -> Optional[str]:
        """
        创建回滚点（当前状态的备份）
        
        Args:
            description: 回滚点描述
            
        Returns:
            备份ID，失败返回None
        """
        # 这里可以实现创建当前系统状态的快照
        # 简化实现，实际需要更复杂的逻辑
        print(f"💾 创建回滚点: {description}")
        print("注意: 回滚点功能需要进一步实现")
        return None
    
    def show_rollback_options(self):
        """显示回滚选项"""
        backups = self.list_available_backups()
        
        if not backups:
            print("📋 没有可用的备份进行回滚")
            return
        
        print(f"📋 可用的回滚选项 (共 {len(backups)} 个备份):")
        print("=" * 80)
        
        for i, backup in enumerate(backups, 1):
            age_hours = (self.backup_manager._get_current_time() - backup.timestamp) / 3600
            
            print(f"{i:2d}. {backup.backup_id}")
            print(f"    📅 时间: {self._format_time(backup.timestamp)} "
                  f"({age_hours:.1f}小时前)")
            print(f"    📁 文件: {backup.file_count} 个")
            print(f"    💾 大小: {self._format_size(backup.total_size)}")
            print(f"    📝 描述: {backup.description}")
            print()
    
    def interactive_restore(self):
        """交互式恢复流程"""
        backups = self.list_available_backups()
        
        if not backups:
            print("📋 没有可用的备份")
            return
        
        # 显示备份列表
        self.show_rollback_options()
        
        # 选择备份
        while True:
            try:
                choice = input(f"请选择要恢复的备份 (1-{len(backups)}, q退出): ").strip()
                
                if choice.lower() == 'q':
                    return
                
                backup_index = int(choice) - 1
                if 0 <= backup_index < len(backups):
                    selected_backup = backups[backup_index]
                    break
                else:
                    print(f"❌ 无效选择，请输入 1-{len(backups)}")
                    
            except (ValueError, KeyboardInterrupt, EOFError):
                return
        
        # 显示备份详情
        self.show_backup_details(selected_backup.backup_id)
        
        # 确认恢复
        confirm = input(f"\n确认恢复此备份? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y', '是']:
            print("❌ 恢复操作已取消")
            return
        
        # 执行恢复
        result = self.restore_backup(selected_backup.backup_id, "interactive")
        
        if result.successful:
            print(f"🎉 恢复完成! 成功恢复 {len(result.successful)} 个文件")
        else:
            print("❌ 恢复失败")
    
    def _format_time(self, timestamp: float) -> str:
        """格式化时间"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
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


def interactive_rollback():
    """交互式回滚的便捷函数"""
    manager = RollbackManager()
    manager.interactive_restore()


if __name__ == '__main__':
    # 测试回滚管理器
    manager = RollbackManager()
    
    print("=== 回滚管理器测试 ===")
    
    # 显示可用备份
    manager.show_rollback_options()
    
    # 如果有备份，显示详情
    backups = manager.list_available_backups()
    if backups:
        latest_backup = backups[0]
        print(f"\n测试显示备份详情:")
        manager.show_backup_details(latest_backup.backup_id)
        
        # 检查冲突
        conflicts = manager.check_restore_conflicts(latest_backup.backup_id)
        if any(conflicts.values()):
            print(f"\n发现冲突: {conflicts}")
        else:
            print("\n没有发现冲突")
    else:
        print("没有可用的备份进行测试")