#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件匹配引擎
根据用户输入的模式查找匹配的文件列表
"""

import os
import re
import glob
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from input_validator import InputType, InputValidator


class MatchStrategy(Enum):
    """匹配策略枚举"""
    EXACT = "exact"              # 精确匹配
    WILDCARD = "wildcard"        # 通配符匹配
    REGEX = "regex"              # 正则表达式匹配
    FUZZY = "fuzzy"              # 模糊匹配


@dataclass
class FileInfo:
    """文件信息类"""
    path: str                    # 文件路径
    name: str                    # 文件名
    size: int                    # 文件大小
    modified_time: float         # 修改时间
    is_hidden: bool              # 是否隐藏文件
    is_dir: bool                 # 是否目录
    extension: str               # 文件扩展名
    relative_path: str           # 相对路径


@dataclass
class MatchResult:
    """匹配结果类"""
    files: List[FileInfo]        # 匹配的文件列表
    total_count: int             # 总匹配数量
    total_size: int              # 总文件大小
    directories: Set[str]        # 涉及的目录
    pattern: str                 # 使用的模式
    strategy: MatchStrategy      # 匹配策略


class FileMatchEngine:
    """文件匹配引擎"""
    
    def __init__(self, base_dir: str = "."):
        """
        初始化文件匹配引擎
        
        Args:
            base_dir: 基础搜索目录
        """
        self.base_dir = os.path.abspath(base_dir)
        self.validator = InputValidator()
        
        # 默认跳过的目录
        self.skip_dirs = {
            '.git', '.svn', '.hg', '__pycache__', 
            'node_modules', '.vscode', '.idea',
            '.DS_Store', 'Thumbs.db'
        }
        
        # 最大搜索文件数限制
        self.max_files = 10000
        
        # 最大搜索深度
        self.max_depth = 10
    
    def find_files(self, pattern: str, recursive: bool = False, 
                   max_depth: Optional[int] = None) -> MatchResult:
        """
        根据模式查找文件
        
        Args:
            pattern: 搜索模式
            recursive: 是否递归搜索
            max_depth: 最大搜索深度
            
        Returns:
            匹配结果
        """
        # 验证输入
        validation_result = self.validator.validate_input(pattern)
        if not validation_result.is_valid:
            return MatchResult([], 0, 0, set(), pattern, MatchStrategy.EXACT)
        
        # 确定匹配策略
        strategy = self._determine_strategy(validation_result.input_type)
        
        # 设置搜索深度
        search_depth = max_depth or (self.max_depth if recursive else 1)
        
        # 执行搜索
        files = self._search_files(pattern, strategy, recursive, search_depth)
        
        # 计算统计信息
        total_size = sum(f.size for f in files)
        directories = {os.path.dirname(f.path) for f in files}
        
        return MatchResult(
            files=files,
            total_count=len(files),
            total_size=total_size,
            directories=directories,
            pattern=pattern,
            strategy=strategy
        )
    
    def _determine_strategy(self, input_type: InputType) -> MatchStrategy:
        """
        确定匹配策略
        
        Args:
            input_type: 输入类型
            
        Returns:
            匹配策略
        """
        strategy_map = {
            InputType.EXACT_FILE: MatchStrategy.EXACT,
            InputType.WILDCARD: MatchStrategy.WILDCARD,
            InputType.REGEX: MatchStrategy.REGEX,
            InputType.DANGEROUS: MatchStrategy.EXACT  # 危险输入按精确处理
        }
        return strategy_map.get(input_type, MatchStrategy.EXACT)
    
    def _search_files(self, pattern: str, strategy: MatchStrategy, 
                     recursive: bool, max_depth: int) -> List[FileInfo]:
        """
        执行文件搜索
        
        Args:
            pattern: 搜索模式
            strategy: 匹配策略
            recursive: 是否递归
            max_depth: 最大深度
            
        Returns:
            文件信息列表
        """
        files = []
        
        if strategy == MatchStrategy.EXACT:
            files = self._exact_match(pattern)
        elif strategy == MatchStrategy.WILDCARD:
            files = self._wildcard_match(pattern, recursive, max_depth)
        elif strategy == MatchStrategy.REGEX:
            files = self._regex_match(pattern, recursive, max_depth)
        
        # 应用文件数量限制
        if len(files) > self.max_files:
            files = files[:self.max_files]
        
        return files
    
    def _exact_match(self, filename: str) -> List[FileInfo]:
        """
        精确文件名匹配
        
        Args:
            filename: 文件名
            
        Returns:
            匹配的文件列表
        """
        files = []
        
        # 检查当前目录
        file_path = os.path.join(self.base_dir, filename)
        if os.path.exists(file_path):
            file_info = self._create_file_info(file_path)
            if file_info:
                files.append(file_info)
        
        # 如果是相对路径或绝对路径
        if '/' in filename:
            if os.path.isabs(filename):
                # 绝对路径
                if os.path.exists(filename):
                    file_info = self._create_file_info(filename)
                    if file_info:
                        files.append(file_info)
            else:
                # 相对路径
                full_path = os.path.join(self.base_dir, filename)
                if os.path.exists(full_path):
                    file_info = self._create_file_info(full_path)
                    if file_info:
                        files.append(file_info)
        
        return files
    
    def _wildcard_match(self, pattern: str, recursive: bool, max_depth: int) -> List[FileInfo]:
        """
        通配符模式匹配
        
        Args:
            pattern: 通配符模式
            recursive: 是否递归
            max_depth: 最大深度
            
        Returns:
            匹配的文件列表
        """
        files = []
        
        if recursive:
            # 递归搜索
            for root, dirs, filenames in os.walk(self.base_dir):
                # 计算当前深度
                depth = root[len(self.base_dir):].count(os.sep)
                if depth >= max_depth:
                    dirs.clear()  # 不再深入
                    continue
                
                # 跳过特定目录
                dirs[:] = [d for d in dirs if d not in self.skip_dirs]
                
                # 匹配文件
                for filename in filenames:
                    if fnmatch.fnmatch(filename, pattern):
                        file_path = os.path.join(root, filename)
                        file_info = self._create_file_info(file_path)
                        if file_info:
                            files.append(file_info)
                        
                        # 检查文件数量限制
                        if len(files) >= self.max_files:
                            return files
        else:
            # 非递归搜索，使用glob
            try:
                search_pattern = os.path.join(self.base_dir, pattern)
                matched_paths = glob.glob(search_pattern)
                
                for file_path in matched_paths:
                    if os.path.isfile(file_path):
                        file_info = self._create_file_info(file_path)
                        if file_info:
                            files.append(file_info)
            except Exception as e:
                print(f"通配符匹配错误: {e}")
        
        return files
    
    def _regex_match(self, pattern: str, recursive: bool, max_depth: int) -> List[FileInfo]:
        """
        正则表达式匹配
        
        Args:
            pattern: 正则表达式模式
            recursive: 是否递归
            max_depth: 最大深度
            
        Returns:
            匹配的文件列表
        """
        files = []
        
        try:
            # 编译正则表达式
            regex = re.compile(pattern)
            
            if recursive:
                # 递归搜索
                for root, dirs, filenames in os.walk(self.base_dir):
                    # 计算深度
                    depth = root[len(self.base_dir):].count(os.sep)
                    if depth >= max_depth:
                        dirs.clear()
                        continue
                    
                    # 跳过特定目录
                    dirs[:] = [d for d in dirs if d not in self.skip_dirs]
                    
                    # 正则匹配
                    for filename in filenames:
                        if regex.search(filename):
                            file_path = os.path.join(root, filename)
                            file_info = self._create_file_info(file_path)
                            if file_info:
                                files.append(file_info)
                            
                            if len(files) >= self.max_files:
                                return files
            else:
                # 当前目录搜索
                try:
                    for item in os.listdir(self.base_dir):
                        item_path = os.path.join(self.base_dir, item)
                        if os.path.isfile(item_path) and regex.search(item):
                            file_info = self._create_file_info(item_path)
                            if file_info:
                                files.append(file_info)
                except PermissionError:
                    pass
        
        except re.error as e:
            print(f"正则表达式错误: {e}")
        
        return files
    
    def _create_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        创建文件信息对象
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息对象
        """
        try:
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            # 获取文件扩展名
            _, ext = os.path.splitext(filename)
            extension = ext[1:] if ext else ""  # 去掉点号
            
            # 计算相对路径
            try:
                relative_path = os.path.relpath(file_path, self.base_dir)
            except ValueError:
                relative_path = file_path
            
            return FileInfo(
                path=file_path,
                name=filename,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                is_hidden=filename.startswith('.'),
                is_dir=os.path.isdir(file_path),
                extension=extension,
                relative_path=relative_path
            )
        
        except (OSError, IOError):
            # 文件不存在或无权限访问
            return None
    
    def filter_files(self, files: List[FileInfo], 
                    min_size: Optional[int] = None,
                    max_size: Optional[int] = None,
                    extensions: Optional[List[str]] = None,
                    exclude_extensions: Optional[List[str]] = None,
                    modified_after: Optional[float] = None,
                    modified_before: Optional[float] = None,
                    include_hidden: bool = True) -> List[FileInfo]:
        """
        过滤文件列表
        
        Args:
            files: 文件列表
            min_size: 最小文件大小
            max_size: 最大文件大小
            extensions: 包含的扩展名
            exclude_extensions: 排除的扩展名
            modified_after: 修改时间晚于
            modified_before: 修改时间早于
            include_hidden: 是否包含隐藏文件
            
        Returns:
            过滤后的文件列表
        """
        filtered_files = []
        
        for file_info in files:
            # 大小过滤
            if min_size is not None and file_info.size < min_size:
                continue
            if max_size is not None and file_info.size > max_size:
                continue
            
            # 扩展名过滤
            if extensions and file_info.extension not in extensions:
                continue
            if exclude_extensions and file_info.extension in exclude_extensions:
                continue
            
            # 修改时间过滤
            if modified_after is not None and file_info.modified_time <= modified_after:
                continue
            if modified_before is not None and file_info.modified_time >= modified_before:
                continue
            
            # 隐藏文件过滤
            if not include_hidden and file_info.is_hidden:
                continue
            
            filtered_files.append(file_info)
        
        return filtered_files
    
    def sort_files(self, files: List[FileInfo], 
                  sort_by: str = "name", reverse: bool = False) -> List[FileInfo]:
        """
        排序文件列表
        
        Args:
            files: 文件列表
            sort_by: 排序字段 (name, size, modified_time)
            reverse: 是否倒序
            
        Returns:
            排序后的文件列表
        """
        sort_key_map = {
            "name": lambda f: f.name.lower(),
            "size": lambda f: f.size,
            "modified_time": lambda f: f.modified_time,
            "extension": lambda f: f.extension.lower()
        }
        
        if sort_by not in sort_key_map:
            sort_by = "name"
        
        return sorted(files, key=sort_key_map[sort_by], reverse=reverse)
    
    def get_file_statistics(self, files: List[FileInfo]) -> Dict[str, any]:
        """
        获取文件统计信息
        
        Args:
            files: 文件列表
            
        Returns:
            统计信息字典
        """
        if not files:
            return {
                "total_count": 0,
                "total_size": 0,
                "avg_size": 0,
                "extensions": {},
                "directories": set(),
                "hidden_count": 0,
                "largest_file": None,
                "newest_file": None,
                "oldest_file": None
            }
        
        total_size = sum(f.size for f in files)
        extensions = {}
        directories = set()
        hidden_count = 0
        
        largest_file = max(files, key=lambda f: f.size)
        newest_file = max(files, key=lambda f: f.modified_time)
        oldest_file = min(files, key=lambda f: f.modified_time)
        
        for file_info in files:
            # 扩展名统计
            ext = file_info.extension or "无扩展名"
            extensions[ext] = extensions.get(ext, 0) + 1
            
            # 目录统计
            directories.add(os.path.dirname(file_info.path))
            
            # 隐藏文件统计
            if file_info.is_hidden:
                hidden_count += 1
        
        return {
            "total_count": len(files),
            "total_size": total_size,
            "avg_size": total_size // len(files) if files else 0,
            "extensions": extensions,
            "directories": directories,
            "hidden_count": hidden_count,
            "largest_file": largest_file,
            "newest_file": newest_file,
            "oldest_file": oldest_file
        }


def search_files(pattern: str, base_dir: str = ".", recursive: bool = False) -> MatchResult:
    """
    搜索文件的便捷函数
    
    Args:
        pattern: 搜索模式
        base_dir: 基础目录
        recursive: 是否递归搜索
        
    Returns:
        匹配结果
    """
    engine = FileMatchEngine(base_dir)
    return engine.find_files(pattern, recursive)


if __name__ == '__main__':
    # 测试文件匹配引擎
    engine = FileMatchEngine(".")
    
    test_patterns = [
        "*.py",           # Python文件
        "test*",          # 以test开头的文件
        "README.md",      # 精确文件名
        ".*",             # 隐藏文件
        r".*\.json$",     # JSON文件 (正则)
    ]
    
    print("=== 文件匹配测试 ===")
    for pattern in test_patterns:
        print(f"\n搜索模式: {pattern}")
        result = engine.find_files(pattern, recursive=False)
        
        print(f"匹配策略: {result.strategy.value}")
        print(f"找到文件: {result.total_count}")
        print(f"总大小: {result.total_size} 字节")
        
        if result.files:
            print("匹配的文件:")
            for file_info in result.files[:5]:  # 只显示前5个
                print(f"  - {file_info.name} ({file_info.size} 字节)")
            
            if len(result.files) > 5:
                print(f"  ... 还有 {len(result.files) - 5} 个文件")
    
    print("\n=== 统计信息测试 ===")
    result = engine.find_files("*.py", recursive=True)
    stats = engine.get_file_statistics(result.files)
    print(f"Python文件统计:")
    print(f"  总数: {stats['total_count']}")
    print(f"  总大小: {stats['total_size']} 字节")
    print(f"  平均大小: {stats['avg_size']} 字节")
    print(f"  最大文件: {stats['largest_file'].name if stats['largest_file'] else 'N/A'}")