#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份模块
提供文件备份和恢复功能，支持操作回滚
"""

import os
import json
import tarfile
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from config_manager import get_config
from file_matcher import FileInfo


@dataclass
class BackupMetadata:
    """备份元数据"""
    backup_id: str                   # 备份ID
    timestamp: float                 # 创建时间戳
    operation_type: str              # 操作类型
    original_paths: List[str]        # 原始文件路径列表
    file_count: int                  # 文件数量
    total_size: int                  # 总文件大小
    backup_path: str                 # 备份文件路径
    description: str                 # 备份描述


class BackupManager:
    """备份管理器"""
    
    def __init__(self):
        """初始化备份管理器"""
        self.config = get_config()
        self.backup_dir = Path(self.config.get('DEFAULT_BACKUP_DIR'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份保留天数
        self.max_backup_age = self.config.get_int('MAX_BACKUP_AGE_DAYS', 30)
        
        # 元数据文件
        self.metadata_file = self.backup_dir / 'backup_index.json'
        
        # 加载备份索引
        self._load_backup_index()
    
    def _load_backup_index(self):
        """加载备份索引"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.backup_index = json.load(f)
            except Exception as e:
                print(f"警告: 无法加载备份索引: {e}")
                self.backup_index = {}
        else:
            self.backup_index = {}
    
    def _save_backup_index(self):
        """保存备份索引"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告: 无法保存备份索引: {e}")
    
    def _generate_backup_id(self) -> str:
        """生成备份ID"""
        timestamp = datetime.now()
        return timestamp.strftime("backup_%Y%m%d_%H%M%S")
    
    def create_backup(self, files: List[FileInfo], 
                     description: str = "文件清理备份") -> Optional[str]:
        """
        创建文件备份
        
        Args:
            files: 要备份的文件列表
            description: 备份描述
            
        Returns:
            备份ID，失败返回None
        """
        if not files:
            return None
        
        backup_id = self._generate_backup_id()
        backup_subdir = self.backup_dir / backup_id
        backup_subdir.mkdir(exist_ok=True)
        
        try:
            # 创建备份压缩文件
            backup_archive = backup_subdir / "files.tar.gz"
            total_size = 0
            
            with tarfile.open(backup_archive, 'w:gz') as tar:
                for file_info in files:
                    if os.path.exists(file_info.path):
                        # 计算相对路径以避免绝对路径问题
                        arcname = os.path.relpath(file_info.path, start=os.path.commonpath([f.path for f in files] + [os.getcwd()]))
                        tar.add(file_info.path, arcname=arcname)
                        total_size += file_info.size
            
            # 创建文件列表
            file_list_path = backup_subdir / "file_list.txt"
            with open(file_list_path, 'w', encoding='utf-8') as f:
                for file_info in files:
                    f.write(f"{file_info.path}\t{file_info.size}\t{file_info.modified_time}\n")
            
            # 创建元数据
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=time.time(),
                operation_type="file_cleanup",
                original_paths=[f.path for f in files],
                file_count=len(files),
                total_size=total_size,
                backup_path=str(backup_archive),
                description=description
            )
            
            # 保存元数据到文件
            metadata_path = backup_subdir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
            
            # 更新备份索引
            self.backup_index[backup_id] = asdict(metadata)
            self._save_backup_index()
            
            print(f"✅ 备份创建成功: {backup_id}")
            print(f"   📁 备份位置: {backup_subdir}")
            print(f"   📊 文件数量: {len(files)}")
            print(f"   💾 总大小: {self._format_size(total_size)}")
            
            return backup_id
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            # 清理失败的备份
            if backup_subdir.exists():
                shutil.rmtree(backup_subdir, ignore_errors=True)
            return None
    
    def list_backups(self) -> List[BackupMetadata]:
        """
        列出所有备份
        
        Returns:
            备份元数据列表
        """
        backups = []
        for backup_id, metadata_dict in self.backup_index.items():
            try:
                metadata = BackupMetadata(**metadata_dict)
                backups.append(metadata)
            except Exception as e:
                print(f"警告: 备份 {backup_id} 元数据损坏: {e}")
        
        # 按时间戳排序（最新的在前）
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def get_backup_info(self, backup_id: str) -> Optional[BackupMetadata]:
        """
        获取备份信息
        
        Args:
            backup_id: 备份ID
            
        Returns:
            备份元数据，不存在返回None
        """
        if backup_id in self.backup_index:
            try:
                return BackupMetadata(**self.backup_index[backup_id])
            except Exception as e:
                print(f"警告: 备份 {backup_id} 元数据损坏: {e}")
        return None
    
    def restore_backup(self, backup_id: str, 
                      restore_paths: Optional[List[str]] = None,
                      target_dir: Optional[str] = None) -> bool:
        """
        恢复备份
        
        Args:
            backup_id: 备份ID
            restore_paths: 要恢复的特定文件路径列表，None表示恢复全部
            target_dir: 恢复目标目录，None表示恢复到原位置
            
        Returns:
            是否成功恢复
        """
        metadata = self.get_backup_info(backup_id)
        if not metadata:
            print(f"❌ 备份不存在: {backup_id}")
            return False
        
        backup_archive = Path(metadata.backup_path)
        if not backup_archive.exists():
            print(f"❌ 备份文件不存在: {backup_archive}")
            return False
        
        try:
            with tarfile.open(backup_archive, 'r:gz') as tar:
                members = tar.getmembers()
                
                # 过滤要恢复的文件
                if restore_paths:
                    # 将绝对路径转换为压缩包内的相对路径
                    restore_names = set()
                    for path in restore_paths:
                        for member in members:
                            if member.name.endswith(os.path.basename(path)):
                                restore_names.add(member.name)
                    
                    members = [m for m in members if m.name in restore_names]
                
                restored_count = 0
                for member in members:
                    try:
                        if target_dir:
                            # 恢复到指定目录
                            extract_path = target_dir
                        else:
                            # 恢复到原位置（当前工作目录）
                            extract_path = "."
                        
                        tar.extract(member, path=extract_path)
                        restored_count += 1
                        print(f"  ✅ 已恢复: {member.name}")
                        
                    except Exception as e:
                        print(f"  ❌ 恢复失败 {member.name}: {e}")
                
                print(f"🎉 恢复完成: {restored_count}/{len(members)} 个文件")
                return restored_count > 0
                
        except Exception as e:
            print(f"❌ 恢复操作失败: {e}")
            return False
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        删除备份
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否成功删除
        """
        if backup_id not in self.backup_index:
            print(f"❌ 备份不存在: {backup_id}")
            return False
        
        try:
            backup_subdir = self.backup_dir / backup_id
            if backup_subdir.exists():
                shutil.rmtree(backup_subdir)
            
            # 从索引中移除
            del self.backup_index[backup_id]
            self._save_backup_index()
            
            print(f"✅ 备份已删除: {backup_id}")
            return True
            
        except Exception as e:
            print(f"❌ 删除备份失败: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        清理过期备份
        
        Returns:
            清理的备份数量
        """
        if self.max_backup_age <= 0:
            return 0
        
        current_time = time.time()
        cutoff_time = current_time - (self.max_backup_age * 24 * 3600)
        
        old_backups = []
        for backup_id, metadata_dict in self.backup_index.items():
            if metadata_dict.get('timestamp', 0) < cutoff_time:
                old_backups.append(backup_id)
        
        cleaned_count = 0
        for backup_id in old_backups:
            if self.delete_backup(backup_id):
                cleaned_count += 1
        
        if cleaned_count > 0:
            print(f"🧹 已清理 {cleaned_count} 个过期备份")
        
        return cleaned_count
    
    def get_backup_statistics(self) -> Dict[str, any]:
        """
        获取备份统计信息
        
        Returns:
            统计信息字典
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                "total_backups": 0,
                "total_files": 0,
                "total_size": 0,
                "oldest_backup": None,
                "newest_backup": None,
                "disk_usage": 0
            }
        
        total_files = sum(b.file_count for b in backups)
        total_size = sum(b.total_size for b in backups)
        
        # 计算磁盘使用量
        disk_usage = 0
        for root, dirs, files in os.walk(self.backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    disk_usage += os.path.getsize(file_path)
                except:
                    pass
        
        return {
            "total_backups": len(backups),
            "total_files": total_files,
            "total_size": total_size,
            "oldest_backup": backups[-1] if backups else None,
            "newest_backup": backups[0] if backups else None,
            "disk_usage": disk_usage
        }
    
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
    
    def _format_time(self, timestamp: float) -> str:
        """格式化时间"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def show_backup_list(self):
        """显示备份列表"""
        backups = self.list_backups()
        
        if not backups:
            print("📋 没有找到备份记录")
            return
        
        print(f"📋 备份列表 (共 {len(backups)} 个备份):")
        print("=" * 80)
        
        for i, backup in enumerate(backups, 1):
            age_hours = (time.time() - backup.timestamp) / 3600
            
            print(f"{i:2d}. {backup.backup_id}")
            print(f"    📅 时间: {self._format_time(backup.timestamp)} ({age_hours:.1f}小时前)")
            print(f"    📁 文件: {backup.file_count} 个")
            print(f"    💾 大小: {self._format_size(backup.total_size)}")
            print(f"    📝 描述: {backup.description}")
            print()
        
        # 显示统计信息
        stats = self.get_backup_statistics()
        print(f"📊 备份统计:")
        print(f"   总备份数: {stats['total_backups']}")
        print(f"   总文件数: {stats['total_files']}")
        print(f"   磁盘占用: {self._format_size(stats['disk_usage'])}")


def create_backup(files: List[FileInfo], description: str = "文件清理备份") -> Optional[str]:
    """
    创建备份的便捷函数
    
    Args:
        files: 要备份的文件列表
        description: 备份描述
        
    Returns:
        备份ID，失败返回None
    """
    manager = BackupManager()
    return manager.create_backup(files, description)


if __name__ == '__main__':
    # 测试备份功能
    manager = BackupManager()
    
    print("=== 备份管理器测试 ===")
    
    # 显示现有备份
    manager.show_backup_list()
    
    # 显示统计信息
    stats = manager.get_backup_statistics()
    print(f"备份统计: {stats}")
    
    # 清理过期备份
    cleaned = manager.cleanup_old_backups()
    if cleaned > 0:
        print(f"清理了 {cleaned} 个过期备份")
