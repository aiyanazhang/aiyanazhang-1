#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全检查模块
对待删除文件进行安全性评估，防止删除重要文件
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from config_manager import get_config
from file_matcher import FileInfo


class SafetyLevel(Enum):
    """安全等级枚举"""
    SAFE = "safe"                    # 安全
    CAUTION = "caution"              # 谨慎
    WARNING = "warning"              # 警告
    DANGER = "danger"                # 危险
    FORBIDDEN = "forbidden"          # 禁止


@dataclass
class SafetyCheck:
    """安全检查结果"""
    level: SafetyLevel               # 安全等级
    reason: str                      # 检查原因
    suggestion: str                  # 建议操作
    auto_approve: bool = False       # 是否可自动批准


@dataclass
class FileRisk:
    """文件风险评估"""
    file_info: FileInfo              # 文件信息
    safety_level: SafetyLevel        # 安全等级
    checks: List[SafetyCheck]        # 检查结果列表
    risk_score: int                  # 风险分数 (0-100)
    can_delete: bool                 # 是否可以删除


class SafetyChecker:
    """安全检查器"""
    
    def __init__(self):
        """初始化安全检查器"""
        self.config = get_config()
        
        # 大文件阈值 (MB)
        self.large_file_threshold = self.config.get_int('LARGE_FILE_THRESHOLD', 100) * 1024 * 1024
        
        # 最近修改阈值 (小时)
        self.recent_threshold = self.config.get_int('RECENT_MODIFIED_THRESHOLD', 24) * 3600
        
        # 系统关键目录
        self.system_dirs = set(self.config.get_protected_dirs())
        
        # 配置文件
        self.config_files = set(self.config.get_config_files())
        
        # 重要扩展名
        self.important_extensions = set(self.config.get_important_extensions())
        
        # 项目文件
        self.project_files = set(self.config.get_project_files())
        
        # 安全扩展名
        self.safe_extensions = {
            'tmp', 'temp', 'log', 'cache', 'bak', 'backup',
            'old', 'orig', 'swp', 'swo', '~', 'pid'
        }
        
        # 危险文件名模式
        self.dangerous_patterns = {
            'passwd', 'shadow', 'sudoers', 'hosts', 'fstab',
            'crontab', 'profile', 'bashrc', 'zshrc'
        }
    
    def check_file_safety(self, file_info: FileInfo) -> FileRisk:
        """
        检查单个文件的安全性
        
        Args:
            file_info: 文件信息
            
        Returns:
            文件风险评估结果
        """
        checks = []
        risk_score = 0
        
        # 执行各项安全检查
        checks.extend(self._check_system_protection(file_info))
        checks.extend(self._check_file_importance(file_info))
        checks.extend(self._check_file_properties(file_info))
        checks.extend(self._check_location_safety(file_info))
        checks.extend(self._check_user_rules(file_info))
        
        # 计算风险分数和安全等级
        risk_score = self._calculate_risk_score(checks)
        safety_level = self._determine_safety_level(risk_score, checks)
        
        # 判断是否可以删除
        can_delete = safety_level != SafetyLevel.FORBIDDEN
        
        return FileRisk(
            file_info=file_info,
            safety_level=safety_level,
            checks=checks,
            risk_score=risk_score,
            can_delete=can_delete
        )
    
    def check_files_batch(self, files: List[FileInfo]) -> List[FileRisk]:
        """
        批量检查文件安全性
        
        Args:
            files: 文件信息列表
            
        Returns:
            文件风险评估列表
        """
        return [self.check_file_safety(file_info) for file_info in files]
    
    def _check_system_protection(self, file_info: FileInfo) -> List[SafetyCheck]:
        """
        检查系统文件保护
        
        Args:
            file_info: 文件信息
            
        Returns:
            检查结果列表
        """
        checks = []
        file_path = os.path.abspath(file_info.path)
        
        # 检查是否在系统目录中
        for sys_dir in self.system_dirs:
            if file_path.startswith(sys_dir + os.sep) or file_path == sys_dir:
                checks.append(SafetyCheck(
                    level=SafetyLevel.FORBIDDEN,
                    reason=f"文件位于系统目录 {sys_dir}",
                    suggestion="系统文件不应被删除",
                    auto_approve=False
                ))
                break
        
        # 检查根目录文件
        if os.path.dirname(file_path) == '/':
            checks.append(SafetyCheck(
                level=SafetyLevel.FORBIDDEN,
                reason="文件位于根目录",
                suggestion="根目录文件不应被删除",
                auto_approve=False
            ))
        
        return checks
    
    def _check_file_importance(self, file_info: FileInfo) -> List[SafetyCheck]:
        """
        检查文件重要性
        
        Args:
            file_info: 文件信息
            
        Returns:
            检查结果列表
        """
        checks = []
        filename = file_info.name.lower()
        extension = file_info.extension.lower()
        
        # 检查配置文件
        if filename in self.config_files or any(pattern in filename for pattern in self.config_files):
            checks.append(SafetyCheck(
                level=SafetyLevel.WARNING,
                reason="这是配置文件",
                suggestion="删除前请确认不再需要此配置",
                auto_approve=False
            ))
        
        # 检查项目文件
        if filename in [pf.lower() for pf in self.project_files]:
            checks.append(SafetyCheck(
                level=SafetyLevel.DANGER,
                reason="这是项目重要文件",
                suggestion="删除可能影响项目功能",
                auto_approve=False
            ))
        
        # 检查重要扩展名
        if extension in self.important_extensions:
            checks.append(SafetyCheck(
                level=SafetyLevel.CAUTION,
                reason=f"文件类型 (.{extension}) 可能包含重要数据",
                suggestion="确认文件内容后再删除",
                auto_approve=False
            ))
        
        # 检查安全扩展名
        if extension in self.safe_extensions:
            checks.append(SafetyCheck(
                level=SafetyLevel.SAFE,
                reason=f"文件类型 (.{extension}) 通常可以安全删除",
                suggestion="这类文件通常是临时文件或备份",
                auto_approve=True
            ))
        
        # 检查危险文件名
        for dangerous in self.dangerous_patterns:
            if dangerous in filename:
                checks.append(SafetyCheck(
                    level=SafetyLevel.FORBIDDEN,
                    reason=f"文件名包含危险模式: {dangerous}",
                    suggestion="这类文件对系统运行至关重要",
                    auto_approve=False
                ))
                break
        
        return checks
    
    def _check_file_properties(self, file_info: FileInfo) -> List[SafetyCheck]:
        """
        检查文件属性
        
        Args:
            file_info: 文件信息
            
        Returns:
            检查结果列表
        """
        checks = []
        current_time = time.time()
        
        # 检查文件大小
        if file_info.size > self.large_file_threshold:
            size_mb = file_info.size / (1024 * 1024)
            checks.append(SafetyCheck(
                level=SafetyLevel.WARNING,
                reason=f"大文件 ({size_mb:.1f} MB)",
                suggestion="确认不再需要此大文件",
                auto_approve=False
            ))
        elif file_info.size == 0:
            checks.append(SafetyCheck(
                level=SafetyLevel.SAFE,
                reason="空文件",
                suggestion="空文件通常可以安全删除",
                auto_approve=True
            ))
        
        # 检查修改时间
        time_diff = current_time - file_info.modified_time
        if time_diff < self.recent_threshold:
            hours = time_diff / 3600
            checks.append(SafetyCheck(
                level=SafetyLevel.CAUTION,
                reason=f"最近修改的文件 ({hours:.1f} 小时前)",
                suggestion="最近修改的文件可能仍在使用",
                auto_approve=False
            ))
        
        # 检查隐藏文件
        if file_info.is_hidden:
            checks.append(SafetyCheck(
                level=SafetyLevel.CAUTION,
                reason="隐藏文件",
                suggestion="隐藏文件可能包含重要配置",
                auto_approve=False
            ))
        
        # 检查可执行文件
        if self._is_executable(file_info):
            checks.append(SafetyCheck(
                level=SafetyLevel.WARNING,
                reason="可执行文件",
                suggestion="删除可执行文件前请确认不再需要",
                auto_approve=False
            ))
        
        return checks
    
    def _check_location_safety(self, file_info: FileInfo) -> List[SafetyCheck]:
        """
        检查文件位置安全性
        
        Args:
            file_info: 文件信息
            
        Returns:
            检查结果列表
        """
        checks = []
        file_dir = os.path.dirname(file_info.path)
        
        # 检查用户主目录下的重要位置
        home_dir = os.path.expanduser("~")
        if file_info.path.startswith(home_dir):
            # 检查是否在重要子目录
            important_subdirs = {
                '.ssh', '.gnupg', '.config', 'Documents', 'Desktop'
            }
            
            rel_path = os.path.relpath(file_info.path, home_dir)
            first_component = rel_path.split(os.sep)[0]
            
            if first_component in important_subdirs:
                checks.append(SafetyCheck(
                    level=SafetyLevel.WARNING,
                    reason=f"文件位于重要目录 {first_component}",
                    suggestion="此目录通常包含重要文件",
                    auto_approve=False
                ))
        
        # 检查临时目录
        temp_dirs = {'/tmp', '/var/tmp', os.path.expanduser('~/tmp')}
        if any(file_dir.startswith(temp_dir) for temp_dir in temp_dirs):
            checks.append(SafetyCheck(
                level=SafetyLevel.SAFE,
                reason="文件位于临时目录",
                suggestion="临时目录中的文件通常可以安全删除",
                auto_approve=True
            ))
        
        return checks
    
    def _check_user_rules(self, file_info: FileInfo) -> List[SafetyCheck]:
        """
        检查用户自定义规则
        
        Args:
            file_info: 文件信息
            
        Returns:
            检查结果列表
        """
        checks = []
        user_rules = self.config.get_user_rules()
        
        for rule in user_rules:
            pattern = rule.get('pattern', '')
            action = rule.get('action', 'warn')
            message = rule.get('message', '')
            
            # 简单的模式匹配
            if self._match_pattern(file_info.name, pattern):
                level_map = {
                    'safe': SafetyLevel.SAFE,
                    'warn': SafetyLevel.CAUTION,
                    'warning': SafetyLevel.WARNING,
                    'danger': SafetyLevel.DANGER,
                    'forbidden': SafetyLevel.FORBIDDEN
                }
                
                level = level_map.get(action, SafetyLevel.CAUTION)
                checks.append(SafetyCheck(
                    level=level,
                    reason=f"匹配用户规则: {pattern}",
                    suggestion=message or "用户自定义规则",
                    auto_approve=(action == 'safe')
                ))
        
        return checks
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        简单的模式匹配
        
        Args:
            filename: 文件名
            pattern: 匹配模式
            
        Returns:
            是否匹配
        """
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def _is_executable(self, file_info: FileInfo) -> bool:
        """
        检查文件是否可执行
        
        Args:
            file_info: 文件信息
            
        Returns:
            是否可执行
        """
        try:
            return os.access(file_info.path, os.X_OK)
        except:
            return False
    
    def _calculate_risk_score(self, checks: List[SafetyCheck]) -> int:
        """
        计算风险分数
        
        Args:
            checks: 检查结果列表
            
        Returns:
            风险分数 (0-100)
        """
        if not checks:
            return 10  # 基础风险分数
        
        # 根据安全等级计算分数
        level_scores = {
            SafetyLevel.SAFE: -10,
            SafetyLevel.CAUTION: 20,
            SafetyLevel.WARNING: 50,
            SafetyLevel.DANGER: 80,
            SafetyLevel.FORBIDDEN: 100
        }
        
        total_score = 10  # 基础分数
        for check in checks:
            total_score += level_scores.get(check.level, 0)
        
        # 限制在 0-100 范围内
        return max(0, min(100, total_score))
    
    def _determine_safety_level(self, risk_score: int, checks: List[SafetyCheck]) -> SafetyLevel:
        """
        确定总体安全等级
        
        Args:
            risk_score: 风险分数
            checks: 检查结果列表
            
        Returns:
            安全等级
        """
        # 如果有任何禁止级别的检查，返回禁止
        if any(check.level == SafetyLevel.FORBIDDEN for check in checks):
            return SafetyLevel.FORBIDDEN
        
        # 根据风险分数确定等级
        if risk_score >= 80:
            return SafetyLevel.DANGER
        elif risk_score >= 50:
            return SafetyLevel.WARNING
        elif risk_score >= 20:
            return SafetyLevel.CAUTION
        else:
            return SafetyLevel.SAFE
    
    def get_safety_summary(self, file_risks: List[FileRisk]) -> Dict[str, any]:
        """
        获取安全检查汇总
        
        Args:
            file_risks: 文件风险列表
            
        Returns:
            汇总信息
        """
        if not file_risks:
            return {
                "total_files": 0,
                "safe_files": 0,
                "caution_files": 0,
                "warning_files": 0,
                "danger_files": 0,
                "forbidden_files": 0,
                "can_delete_count": 0,
                "auto_approve_count": 0,
                "avg_risk_score": 0
            }
        
        # 统计各等级文件数量
        level_counts = {level: 0 for level in SafetyLevel}
        for risk in file_risks:
            level_counts[risk.safety_level] += 1
        
        # 统计可删除和自动批准的文件
        can_delete_count = sum(1 for risk in file_risks if risk.can_delete)
        auto_approve_count = sum(1 for risk in file_risks 
                               if any(check.auto_approve for check in risk.checks))
        
        # 计算平均风险分数
        avg_risk_score = sum(risk.risk_score for risk in file_risks) / len(file_risks)
        
        return {
            "total_files": len(file_risks),
            "safe_files": level_counts[SafetyLevel.SAFE],
            "caution_files": level_counts[SafetyLevel.CAUTION],
            "warning_files": level_counts[SafetyLevel.WARNING],
            "danger_files": level_counts[SafetyLevel.DANGER],
            "forbidden_files": level_counts[SafetyLevel.FORBIDDEN],
            "can_delete_count": can_delete_count,
            "auto_approve_count": auto_approve_count,
            "avg_risk_score": avg_risk_score
        }


def check_file_safety(file_info: FileInfo) -> FileRisk:
    """
    检查文件安全性的便捷函数
    
    Args:
        file_info: 文件信息
        
    Returns:
        文件风险评估
    """
    checker = SafetyChecker()
    return checker.check_file_safety(file_info)


if __name__ == '__main__':
    # 测试安全检查器
    from file_matcher import FileMatchEngine
    
    # 初始化组件
    engine = FileMatchEngine(".")
    checker = SafetyChecker()
    
    # 搜索一些测试文件
    result = engine.find_files("*", recursive=False)
    
    print("=== 安全检查测试 ===")
    if result.files:
        # 检查前几个文件
        for file_info in result.files[:5]:
            risk = checker.check_file_safety(file_info)
            
            print(f"\n文件: {file_info.name}")
            print(f"安全等级: {risk.safety_level.value}")
            print(f"风险分数: {risk.risk_score}/100")
            print(f"可删除: {'是' if risk.can_delete else '否'}")
            
            if risk.checks:
                print("检查结果:")
                for check in risk.checks:
                    print(f"  - {check.level.value}: {check.reason}")
                    if check.suggestion:
                        print(f"    建议: {check.suggestion}")
        
        # 生成汇总报告
        all_risks = checker.check_files_batch(result.files)
        summary = checker.get_safety_summary(all_risks)
        
        print(f"\n=== 安全汇总 ===")
        print(f"总文件数: {summary['total_files']}")
        print(f"安全文件: {summary['safe_files']}")
        print(f"谨慎文件: {summary['caution_files']}")
        print(f"警告文件: {summary['warning_files']}")
        print(f"危险文件: {summary['danger_files']}")
        print(f"禁止文件: {summary['forbidden_files']}")
        print(f"可删除: {summary['can_delete_count']}")
        print(f"平均风险: {summary['avg_risk_score']:.1f}")
    else:
        print("未找到测试文件")
