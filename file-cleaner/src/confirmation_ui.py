#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
确认机制模块
提供用户交互和确认界面，支持多种确认方式
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from safety_checker import FileRisk, SafetyLevel
from file_matcher import FileInfo


class ConfirmationType(Enum):
    """确认类型枚举"""
    BATCH_CONFIRM = "batch"          # 批量确认
    INDIVIDUAL_CONFIRM = "individual" # 逐个确认
    AUTO_SAFE = "auto_safe"          # 自动确认安全文件
    PREVIEW_ONLY = "preview"         # 仅预览，不删除


@dataclass
class ConfirmationResult:
    """确认结果"""
    confirmed_files: List[FileInfo]   # 已确认删除的文件
    skipped_files: List[FileInfo]     # 跳过的文件
    cancelled: bool                   # 是否取消操作
    confirmation_type: ConfirmationType # 确认类型


class ColorCode:
    """颜色代码类"""
    RED = '\033[91m'      # 红色 - 危险
    YELLOW = '\033[93m'   # 黄色 - 警告
    GREEN = '\033[92m'    # 绿色 - 安全
    BLUE = '\033[94m'     # 蓝色 - 信息
    CYAN = '\033[96m'     # 青色 - 谨慎
    GRAY = '\033[90m'     # 灰色 - 禁止
    BOLD = '\033[1m'      # 粗体
    UNDERLINE = '\033[4m' # 下划线
    RESET = '\033[0m'     # 重置


class ConfirmationUI:
    """确认界面"""
    
    def __init__(self, use_colors: bool = True):
        """
        初始化确认界面
        
        Args:
            use_colors: 是否使用颜色输出
        """
        self.use_colors = use_colors and self._supports_color()
        
        # 安全等级颜色映射
        self.level_colors = {
            SafetyLevel.SAFE: ColorCode.GREEN,
            SafetyLevel.CAUTION: ColorCode.CYAN,
            SafetyLevel.WARNING: ColorCode.YELLOW,
            SafetyLevel.DANGER: ColorCode.RED,
            SafetyLevel.FORBIDDEN: ColorCode.GRAY
        }
        
        # 安全等级图标
        self.level_icons = {
            SafetyLevel.SAFE: "✅",
            SafetyLevel.CAUTION: "⚠️",
            SafetyLevel.WARNING: "🔶",  
            SafetyLevel.DANGER: "🔴",
            SafetyLevel.FORBIDDEN: "🚫"
        }
    
    def _supports_color(self) -> bool:
        """检查终端是否支持颜色"""
        return (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and 
                os.environ.get('TERM') != 'dumb')
    
    def _colorize(self, text: str, color: str) -> str:
        """
        给文本添加颜色
        
        Args:
            text: 文本内容
            color: 颜色代码
            
        Returns:
            带颜色的文本
        """
        if self.use_colors:
            return f"{color}{text}{ColorCode.RESET}"
        return text
    
    def _format_file_size(self, size: int) -> str:
        """
        格式化文件大小
        
        Args:
            size: 文件大小（字节）
            
        Returns:
            格式化的大小字符串
        """
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f}MB"
        else:
            return f"{size/(1024*1024*1024):.1f}GB"
    
    def _format_time_ago(self, timestamp: float) -> str:
        """
        格式化时间差
        
        Args:
            timestamp: 时间戳
            
        Returns:
            格式化的时间差字符串
        """
        import time
        
        now = time.time()
        diff = now - timestamp
        
        if diff < 3600:  # 1小时内
            return f"{int(diff/60)}分钟前"
        elif diff < 86400:  # 24小时内
            return f"{int(diff/3600)}小时前"
        elif diff < 2592000:  # 30天内
            return f"{int(diff/86400)}天前"
        else:
            return f"{int(diff/2592000)}个月前"
    
    def show_file_list(self, file_risks: List[FileRisk], 
                      show_details: bool = True) -> None:
        """
        显示文件列表
        
        Args:
            file_risks: 文件风险列表
            show_details: 是否显示详细信息
        """
        if not file_risks:
            print("没有找到匹配的文件。")
            return
        
        print(f"\n{self._colorize('找到的文件列表:', ColorCode.BOLD)}")
        print("=" * 80)
        
        # 按安全等级分组显示
        level_groups = {}
        for risk in file_risks:
            level = risk.safety_level
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(risk)
        
        # 按风险等级排序显示
        level_order = [SafetyLevel.FORBIDDEN, SafetyLevel.DANGER, 
                      SafetyLevel.WARNING, SafetyLevel.CAUTION, SafetyLevel.SAFE]
        
        for level in level_order:
            if level not in level_groups:
                continue
                
            risks = level_groups[level]
            level_color = self.level_colors[level]
            level_name = level.value.upper()
            
            print(f"\n{self._colorize(f'{self.level_icons[level]} {level_name} ({len(risks)}个文件)', level_color)}")
            print("-" * 60)
            
            for i, risk in enumerate(risks, 1):
                file_info = risk.file_info
                
                # 基本信息
                file_display = f"{i:2d}. {file_info.name}"
                if file_info.is_hidden:
                    file_display += " (隐藏)"
                
                print(f"  {self._colorize(file_display, level_color)}")
                
                if show_details:
                    # 文件详细信息
                    size_str = self._format_file_size(file_info.size)
                    time_str = self._format_time_ago(file_info.modified_time)
                    
                    print(f"    路径: {file_info.relative_path}")
                    print(f"    大小: {size_str} | 修改: {time_str} | 风险分数: {risk.risk_score}/100")
                    
                    # 显示检查结果
                    if risk.checks:
                        main_reasons = [check.reason for check in risk.checks[:2]]  # 显示前2个原因
                        reasons_text = " | ".join(main_reasons)
                        print(f"    原因: {reasons_text}")
    
    def show_summary(self, file_risks: List[FileRisk]) -> None:
        """
        显示汇总信息
        
        Args:
            file_risks: 文件风险列表
        """
        if not file_risks:
            return
        
        # 统计信息
        total_files = len(file_risks)
        total_size = sum(risk.file_info.size for risk in file_risks)
        can_delete = sum(1 for risk in file_risks if risk.can_delete)
        forbidden = sum(1 for risk in file_risks if risk.safety_level == SafetyLevel.FORBIDDEN)
        
        print(f"\n{self._colorize('操作汇总:', ColorCode.BOLD)}")
        print("=" * 50)
        
        print(f"📁 总文件数: {self._colorize(str(total_files), ColorCode.BLUE)}")
        print(f"💾 总大小: {self._colorize(self._format_file_size(total_size), ColorCode.BLUE)}")
        print(f"✅ 可删除: {self._colorize(str(can_delete), ColorCode.GREEN)}")
        print(f"🚫 被保护: {self._colorize(str(forbidden), ColorCode.RED)}")
        
        if forbidden > 0:
            print(f"\n{self._colorize('注意: 某些文件被保护，无法删除', ColorCode.RED)}")
    
    def get_confirmation(self, file_risks: List[FileRisk]) -> ConfirmationResult:
        """
        获取用户确认
        
        Args:
            file_risks: 文件风险列表
            
        Returns:
            确认结果
        """
        # 过滤出可删除的文件
        deletable_risks = [risk for risk in file_risks if risk.can_delete]
        
        if not deletable_risks:
            print(f"\n{self._colorize('没有可删除的文件。', ColorCode.YELLOW)}")
            return ConfirmationResult([], [], True, ConfirmationType.PREVIEW_ONLY)
        
        # 显示确认选项
        print(f"\n{self._colorize('请选择操作:', ColorCode.BOLD)}")
        print("1. 批量确认删除所有可删除文件")
        print("2. 逐个确认每个文件")
        print("3. 只删除标记为'安全'的文件")
        print("4. 预览模式（不删除任何文件）")
        print("5. 取消操作")
        
        while True:
            try:
                choice = input(f"\n请输入选择 (1-5): ").strip()
                
                if choice == '1':
                    return self._batch_confirm(deletable_risks)
                elif choice == '2':
                    return self._individual_confirm(deletable_risks)
                elif choice == '3':
                    return self._auto_safe_confirm(deletable_risks)
                elif choice == '4':
                    return ConfirmationResult([], [risk.file_info for risk in deletable_risks], 
                                           False, ConfirmationType.PREVIEW_ONLY)
                elif choice == '5':
                    return ConfirmationResult([], [], True, ConfirmationType.BATCH_CONFIRM)
                else:
                    print(f"{self._colorize('无效选择，请输入 1-5', ColorCode.RED)}")
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\n{self._colorize('操作已取消', ColorCode.YELLOW)}")
                return ConfirmationResult([], [], True, ConfirmationType.BATCH_CONFIRM)
    
    def _batch_confirm(self, deletable_risks: List[FileRisk]) -> ConfirmationResult:
        """
        批量确认
        
        Args:
            deletable_risks: 可删除的文件风险列表
            
        Returns:
            确认结果
        """
        print(f"\n{self._colorize('批量删除确认', ColorCode.BOLD)}")
        print(f"将删除 {len(deletable_risks)} 个文件")
        
        # 显示风险统计
        danger_count = sum(1 for risk in deletable_risks 
                          if risk.safety_level == SafetyLevel.DANGER)
        warning_count = sum(1 for risk in deletable_risks 
                           if risk.safety_level == SafetyLevel.WARNING)
        
        if danger_count > 0:
            print(f"{self._colorize(f'警告: 包含 {danger_count} 个高风险文件!', ColorCode.RED)}")
        if warning_count > 0:
            print(f"{self._colorize(f'注意: 包含 {warning_count} 个警告级文件', ColorCode.YELLOW)}")
        
        # 最终确认
        confirm = input(f"\n{self._colorize('确认删除所有文件? (yes/no): ', ColorCode.BOLD)}").strip().lower()
        
        if confirm in ['yes', 'y', '是']:
            confirmed_files = [risk.file_info for risk in deletable_risks]
            return ConfirmationResult(confirmed_files, [], False, ConfirmationType.BATCH_CONFIRM)
        else:
            return ConfirmationResult([], [], True, ConfirmationType.BATCH_CONFIRM)
    
    def _individual_confirm(self, deletable_risks: List[FileRisk]) -> ConfirmationResult:
        """
        逐个确认
        
        Args:
            deletable_risks: 可删除的文件风险列表
            
        Returns:
            确认结果
        """
        confirmed_files = []
        skipped_files = []
        
        print(f"\n{self._colorize('逐个确认模式', ColorCode.BOLD)}")
        print("对每个文件输入: y(删除) / n(跳过) / q(退出)")
        
        for i, risk in enumerate(deletable_risks, 1):
            file_info = risk.file_info
            level_color = self.level_colors[risk.safety_level]
            
            print(f"\n[{i}/{len(deletable_risks)}] {self._colorize(file_info.name, level_color)}")
            print(f"  路径: {file_info.relative_path}")
            print(f"  大小: {self._format_file_size(file_info.size)}")
            print(f"  风险: {risk.safety_level.value} ({risk.risk_score}/100)")
            
            # 显示主要风险原因
            if risk.checks:
                main_reason = risk.checks[0].reason
                print(f"  原因: {main_reason}")
            
            while True:
                try:
                    choice = input("删除此文件? (y/n/q): ").strip().lower()
                    
                    if choice in ['y', 'yes', '是']:
                        confirmed_files.append(file_info)
                        break
                    elif choice in ['n', 'no', '否']:
                        skipped_files.append(file_info)
                        break
                    elif choice in ['q', 'quit', '退出']:
                        return ConfirmationResult(confirmed_files, skipped_files + 
                                               [r.file_info for r in deletable_risks[i:]], 
                                               True, ConfirmationType.INDIVIDUAL_CONFIRM)
                    else:
                        print(f"{self._colorize('请输入 y, n 或 q', ColorCode.RED)}")
                        
                except (KeyboardInterrupt, EOFError):
                    print(f"\n{self._colorize('操作已取消', ColorCode.YELLOW)}")
                    return ConfirmationResult(confirmed_files, skipped_files +
                                           [r.file_info for r in deletable_risks[i:]], 
                                           True, ConfirmationType.INDIVIDUAL_CONFIRM)
        
        return ConfirmationResult(confirmed_files, skipped_files, False, 
                                ConfirmationType.INDIVIDUAL_CONFIRM)
    
    def _auto_safe_confirm(self, deletable_risks: List[FileRisk]) -> ConfirmationResult:
        """
        自动确认安全文件
        
        Args:
            deletable_risks: 可删除的文件风险列表
            
        Returns:
            确认结果
        """
        safe_risks = [risk for risk in deletable_risks 
                     if risk.safety_level == SafetyLevel.SAFE]
        other_risks = [risk for risk in deletable_risks 
                      if risk.safety_level != SafetyLevel.SAFE]
        
        if not safe_risks:
            print(f"{self._colorize('没有找到标记为安全的文件', ColorCode.YELLOW)}")
            return ConfirmationResult([], [risk.file_info for risk in deletable_risks], 
                                   False, ConfirmationType.AUTO_SAFE)
        
        print(f"\n{self._colorize('自动安全模式', ColorCode.BOLD)}")
        print(f"将删除 {len(safe_risks)} 个安全文件")
        print(f"跳过 {len(other_risks)} 个非安全文件")
        
        # 显示安全文件列表
        if len(safe_risks) <= 10:
            print(f"\n{self._colorize('将删除的安全文件:', ColorCode.GREEN)}")
            for risk in safe_risks:
                print(f"  - {risk.file_info.name} ({self._format_file_size(risk.file_info.size)})")
        else:
            print(f"\n{self._colorize('安全文件过多，只显示前5个:', ColorCode.GREEN)}")
            for risk in safe_risks[:5]:
                print(f"  - {risk.file_info.name} ({self._format_file_size(risk.file_info.size)})")
            print(f"  ... 还有 {len(safe_risks) - 5} 个文件")
        
        confirm = input(f"\n{self._colorize('确认删除这些安全文件? (yes/no): ', ColorCode.BOLD)}").strip().lower()
        
        if confirm in ['yes', 'y', '是']:
            confirmed_files = [risk.file_info for risk in safe_risks]
            skipped_files = [risk.file_info for risk in other_risks]
            return ConfirmationResult(confirmed_files, skipped_files, False, 
                                   ConfirmationType.AUTO_SAFE)
        else:
            return ConfirmationResult([], [risk.file_info for risk in deletable_risks], 
                                   True, ConfirmationType.AUTO_SAFE)


def get_user_confirmation(file_risks: List[FileRisk], use_colors: bool = True) -> ConfirmationResult:
    """
    获取用户确认的便捷函数
    
    Args:
        file_risks: 文件风险列表
        use_colors: 是否使用颜色
        
    Returns:
        确认结果
    """
    ui = ConfirmationUI(use_colors)
    ui.show_file_list(file_risks)
    ui.show_summary(file_risks)
    return ui.get_confirmation(file_risks)


if __name__ == '__main__':
    # 测试确认界面
    from safety_checker import SafetyChecker
    from file_matcher import FileMatchEngine, FileInfo
    
    # 创建测试数据
    engine = FileMatchEngine(".")
    checker = SafetyChecker()
    
    # 搜索文件并进行安全检查
    result = engine.find_files("*.py", recursive=False)  
    if result.files:
        file_risks = checker.check_files_batch(result.files[:3])  # 测试前3个文件
        
        print("=== 确认界面测试 ===")
        ui = ConfirmationUI(True)
        ui.show_file_list(file_risks)
        ui.show_summary(file_risks)
        
        # 注意: 在实际测试中取消注释下面这行
        # confirmation = ui.get_confirmation(file_risks)
        # print(f"确认结果: {len(confirmation.confirmed_files)} 个文件将被删除")
    else:
        print("未找到测试文件")
