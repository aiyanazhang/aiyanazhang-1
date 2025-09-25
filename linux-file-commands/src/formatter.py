#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化输出模块

本模块负责将数据格式化为多种用户友好的输出格式，支持颜色高亮和分页显示。
主要功能包括：
- 多种输出格式（表格、列表、JSON、树形、紧凑格式）
- 智能的表格布局和列宽调整
- 丰富的颜色主题和终端显示支持
- 灵活的分页显示系统
- 自定义样式和主题支持
- 跨平台的终端颜色兼容性

作者: AI Assistant
版本: 1.0
创建时间: 2024
最后修改: 2025-09-25
"""

import json
import sys
import math
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class ColorCode:
    """
    终端颜色代码定义
    
    定义了终端中使用的ANSI颜色转义序列，支持基本颜色和高亮颜色。
    这些颜色代码可以在大多数支持ANSI的终端中正常工作。
    
    包含以下类型的颜色定义：
    - 控制字符（重置、加粗、变暗）
    - 基本前景色（8种基础颜色）
    - 高亮前景色（更鲜艳的颜色变体）
    """
    RESET = '\033[0m'      # 重置所有格式
    BOLD = '\033[1m'       # 加粗字体
    DIM = '\033[2m'        # 变暗显示
    
    # 基本前景色（标准颜色）
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 高亮前景色（更鲜艳的颜色版本）
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'

class OutputFormat(Enum):
    """
    输出格式枚举
    
    定义系统支持的所有输出格式类型。每种格式都适合不同的使用场景：
    - TABLE: 结构化数据的表格展示，适合数据对比
    - LIST: 线性列表展示，适合阅读详细信息
    - JSON: 机器可读格式，适合程序间交互
    - TREE: 层次结构展示，适合显示嵌套数据
    - COMPACT: 紧凑概览格式，适合快速浏览
    """
    TABLE = 'table'
    LIST = 'list'
    JSON = 'json'
    TREE = 'tree'
    COMPACT = 'compact'

class ColorTheme:
    """
    颜色主题管理器
    
    管理终端输出的颜色配置，提供统一的颜色主题体验。支持动态开关颜色，
    以适应不同的终端环境和用户偏好。为不同类型的内容分配合适的颜色。
    
    支持的元素类型：
    - header: 标题和头部信息
    - command: 命令名称
    - description: 描述文本
    - category: 分类标签
    - option: 命令选项
    - example: 使用示例
    - warning/success/info: 状态消息
    - dim: 辅助信息
    
    Attributes:
        enabled (bool): 是否启用颜色显示
    """
    
    def __init__(self, enabled: bool = True):
        """
        初始化颜色主题
        
        根据是否启用颜色来设置相应的颜色代码。当禁用颜色时，
        所有颜色属性都会设置为空字符串，以支持纯文本输出。
        
        Args:
            enabled (bool): 是否启用颜色显示，默认True
        """
        self.enabled = enabled
        
        if enabled:
            # 启用颜色时的配色方案
            self.header = ColorCode.BOLD + ColorCode.BRIGHT_CYAN      # 标题使用加粗的青色
            self.command = ColorCode.BRIGHT_GREEN                     # 命令名使用鲜绿色
            self.description = ColorCode.WHITE                        # 描述使用白色
            self.category = ColorCode.YELLOW                          # 分类使用黄色
            self.option = ColorCode.BRIGHT_BLUE                      # 选项使用鲜蓝色
            self.example = ColorCode.CYAN                             # 示例使用青色
            self.warning = ColorCode.BRIGHT_RED                      # 警告使用鲜红色
            self.success = ColorCode.BRIGHT_GREEN                    # 成功使用鲜绿色
            self.info = ColorCode.BRIGHT_BLUE                        # 信息使用鲜蓝色
            self.dim = ColorCode.DIM                                  # 辅助信息使用暗淡显示
            self.reset = ColorCode.RESET                             # 重置颜色
        else:
            # 禁用颜色时所有颜色都为空字符串，适合纯文本输出
            self.header = ''
            self.command = ''
            self.description = ''
            self.category = ''
            self.option = ''
            self.example = ''
            self.warning = ''
            self.success = ''
            self.info = ''
            self.dim = ''
            self.reset = ''

class TableFormatter:
    """
    表格格式化器
    
    负责将结构化数据格式化为美观的表格格式。提供智能的列宽计算和调整，
    支持颜色高亮和内容截断。能够自动适应不同的终端宽度。
    
    主要功能：
    - 自动计算和调整列宽
    - 支持颜色代码的正确处理
    - 内容过长时的智能截断
    - 美观的表格边框和对齐
    
    Attributes:
        theme (ColorTheme): 使用的颜色主题
    """
    
    def __init__(self, theme: ColorTheme):
        self.theme = theme
    
    def format_table(self, data: List[Dict[str, Any]], 
                    headers: List[str],
                    max_width: int = 80) -> List[str]:
        """
        格式化为表格
        
        将结构化数据转换为表格形式的文本输出。自动计算列宽并调整以适应
        指定的最大宽度。支持颜色高亮和内容截断。
        
        Args:
            data (List[Dict[str, Any]]): 要显示的数据列表
            headers (List[str]): 表头列名列表
            max_width (int): 表格最大宽度，默认80字符
            
        Returns:
            List[str]: 格式化后的表格行列表
        """
        if not data:
            return [f"{self.theme.info}没有数据显示{self.theme.reset}"]
        
        # 计算每列的最优宽度
        col_widths = self._calculate_column_widths(data, headers, max_width)
        
        lines = []
        
        # 生成表头行
        header_line = self._format_header_line(headers, col_widths)
        lines.append(header_line)
        
        # 生成分隔线
        separator = self._create_separator(col_widths)
        lines.append(separator)
        
        # 生成数据行
        for row in data:
            data_line = self._format_data_line(row, headers, col_widths)
            lines.append(data_line)
        
        return lines
    
    def _calculate_column_widths(self, data: List[Dict[str, Any]], 
                                headers: List[str], 
                                max_width: int) -> Dict[str, int]:
        """计算列宽"""
        col_widths = {}
        
        # 初始化为表头宽度
        for header in headers:
            col_widths[header] = len(header)
        
        # 计算数据的最大宽度
        for row in data:
            for header in headers:
                value = str(row.get(header, ''))
                # 移除颜色代码计算实际长度
                clean_value = self._remove_color_codes(value)
                col_widths[header] = max(col_widths[header], len(clean_value))
        
        # 调整宽度以适应最大宽度限制
        total_width = sum(col_widths.values()) + len(headers) * 3  # 3 = ' | '
        if total_width > max_width:
            self._adjust_column_widths(col_widths, max_width, len(headers))
        
        return col_widths
    
    def _remove_color_codes(self, text: str) -> str:
        """移除颜色代码"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _adjust_column_widths(self, col_widths: Dict[str, int], 
                             max_width: int, num_cols: int) -> None:
        """调整列宽以适应最大宽度"""
        available_width = max_width - num_cols * 3  # 减去分隔符宽度
        total_current = sum(col_widths.values())
        
        if total_current <= available_width:
            return
        
        # 等比例缩放
        scale_factor = available_width / total_current
        for col in col_widths:
            col_widths[col] = max(int(col_widths[col] * scale_factor), 8)
    
    def _format_header_line(self, headers: List[str], 
                           col_widths: Dict[str, int]) -> str:
        """格式化表头行"""
        formatted_headers = []
        for header in headers:
            formatted_header = f"{self.theme.header}{header:<{col_widths[header]}}{self.theme.reset}"
            formatted_headers.append(formatted_header)
        
        return " | ".join(formatted_headers)
    
    def _create_separator(self, col_widths: Dict[str, int]) -> str:
        """创建分隔线"""
        separators = []
        for width in col_widths.values():
            separators.append("-" * width)
        
        return "-+-".join(separators)
    
    def _format_data_line(self, row: Dict[str, Any], 
                         headers: List[str], 
                         col_widths: Dict[str, int]) -> str:
        """格式化数据行"""
        formatted_cells = []
        for header in headers:
            value = str(row.get(header, ''))
            
            # 截断过长的内容
            clean_value = self._remove_color_codes(value)
            if len(clean_value) > col_widths[header]:
                truncated = clean_value[:col_widths[header]-3] + "..."
                # 如果原值有颜色，保持颜色
                if len(value) > len(clean_value):  # 有颜色代码
                    color_prefix = value[:value.find(clean_value)]
                    value = color_prefix + truncated + self.theme.reset
                else:
                    value = truncated
            
            # 对齐
            padding = col_widths[header] - len(self._remove_color_codes(value))
            formatted_cell = value + " " * padding
            formatted_cells.append(formatted_cell)
        
        return " | ".join(formatted_cells)

class ListFormatter:
    """
    列表格式化器
    
    负责将数据格式化为易于阅读的列表形式。支持简单列表和详细列表两种模式，
    适合显示不同类型的信息。相比表格格式，列表格式更适合阅读详细内容。
    
    主要功能：
    - 简单列表：显示标题和描述
    - 详细列表：显示完整的字段信息
    - 灵活的索引显示控制
    - 美观的分隔和缩进
    
    Attributes:
        theme (ColorTheme): 使用的颜色主题
    """
    
    def __init__(self, theme: ColorTheme):
        self.theme = theme
    
    def format_list(self, data: List[Dict[str, Any]], 
                   title_field: str = 'name',
                   description_field: str = 'description',
                   show_index: bool = True) -> List[str]:
        """格式化为列表"""
        if not data:
            return [f"{self.theme.info}没有数据显示{self.theme.reset}"]
        
        lines = []
        
        for i, item in enumerate(data, 1):
            # 索引和标题
            if show_index:
                index_str = f"{self.theme.dim}{i:2d}.{self.theme.reset} "
            else:
                index_str = f"{self.theme.dim}•{self.theme.reset} "
            
            title = item.get(title_field, '')
            description = item.get(description_field, '')
            
            title_line = f"{index_str}{self.theme.command}{title}{self.theme.reset}"
            
            if description:
                desc_line = f"    {self.theme.description}{description}{self.theme.reset}"
                lines.extend([title_line, desc_line])
            else:
                lines.append(title_line)
            
            # 添加空行分隔（除了最后一项）
            if i < len(data):
                lines.append("")
        
        return lines
    
    def format_detailed_list(self, data: List[Dict[str, Any]]) -> List[str]:
        """格式化为详细列表"""
        if not data:
            return [f"{self.theme.info}没有数据显示{self.theme.reset}"]
        
        lines = []
        
        for i, item in enumerate(data, 1):
            # 标题行
            name = item.get('name', f'项目 {i}')
            lines.append(f"{self.theme.header}━━━ {name} ━━━{self.theme.reset}")
            
            # 详细信息
            for key, value in item.items():
                if key == 'name':
                    continue
                
                if isinstance(value, list):
                    if value:  # 非空列表
                        lines.append(f"{self.theme.info}{key}:{self.theme.reset}")
                        for v in value:
                            lines.append(f"  • {v}")
                elif isinstance(value, dict):
                    if value:  # 非空字典
                        lines.append(f"{self.theme.info}{key}:{self.theme.reset}")
                        for k, v in value.items():
                            lines.append(f"  {k}: {v}")
                else:
                    if value:  # 非空值
                        lines.append(f"{self.theme.info}{key}:{self.theme.reset} {value}")
            
            # 分隔线（除了最后一项）
            if i < len(data):
                lines.append("")
        
        return lines

class TreeFormatter:
    """树形格式化器"""
    
    def __init__(self, theme: ColorTheme):
        self.theme = theme
    
    def format_tree(self, data: Dict[str, Any], 
                   max_depth: int = 3) -> List[str]:
        """格式化为树形结构"""
        lines = []
        self._format_tree_recursive(data, lines, "", True, 0, max_depth)
        return lines
    
    def _format_tree_recursive(self, data: Union[Dict, List, str], 
                              lines: List[str], 
                              prefix: str, 
                              is_last: bool, 
                              depth: int, 
                              max_depth: int) -> None:
        """递归格式化树形结构"""
        if depth > max_depth:
            return
        
        if isinstance(data, dict):
            for i, (key, value) in enumerate(data.items()):
                is_last_item = i == len(data) - 1
                
                # 树形连接符
                connector = "└── " if is_last_item else "├── "
                
                # 键名
                key_line = f"{prefix}{connector}{self.theme.category}{key}{self.theme.reset}"
                
                # 如果值是简单类型，直接显示
                if isinstance(value, (str, int, float, bool)):
                    key_line += f": {self.theme.description}{value}{self.theme.reset}"
                    lines.append(key_line)
                elif isinstance(value, list) and all(isinstance(x, str) for x in value):
                    # 字符串列表直接显示
                    key_line += f": {self.theme.description}[{', '.join(value)}]{self.theme.reset}"
                    lines.append(key_line)
                else:
                    lines.append(key_line)
                    
                    # 递归处理复杂值
                    if isinstance(value, (dict, list)):
                        next_prefix = prefix + ("    " if is_last_item else "│   ")
                        self._format_tree_recursive(
                            value, lines, next_prefix, True, depth + 1, max_depth
                        )
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                is_last_item = i == len(data) - 1
                connector = "└── " if is_last_item else "├── "
                
                if isinstance(item, str):
                    lines.append(f"{prefix}{connector}{self.theme.description}{item}{self.theme.reset}")
                else:
                    lines.append(f"{prefix}{connector}{self.theme.info}[{i}]{self.theme.reset}")
                    next_prefix = prefix + ("    " if is_last_item else "│   ")
                    self._format_tree_recursive(
                        item, lines, next_prefix, True, depth + 1, max_depth
                    )

class Paginator:
    """分页器"""
    
    def __init__(self, page_size: int = 20):
        self.page_size = page_size
    
    def paginate(self, lines: List[str], 
                page_num: int = 1) -> Dict[str, Any]:
        """分页处理"""
        total_lines = len(lines)
        total_pages = math.ceil(total_lines / self.page_size) if total_lines > 0 else 1
        
        # 确保页码有效
        page_num = max(1, min(page_num, total_pages))
        
        # 计算起始和结束索引
        start_idx = (page_num - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_lines)
        
        page_lines = lines[start_idx:end_idx]
        
        return {
            'lines': page_lines,
            'current_page': page_num,
            'total_pages': total_pages,
            'total_items': total_lines,
            'has_prev': page_num > 1,
            'has_next': page_num < total_pages,
            'page_info': f"第 {page_num} 页，共 {total_pages} 页 (总计 {total_lines} 项)"
        }

class OutputFormatter:
    """
    统一输出格式化器
    
    作为整个格式化系统的主入口，统一管理所有格式化功能。整合了各种
    具体的格式化器，并提供统一的接口。支持多种输出格式和高级功能。
    
    主要特性：
    - 统一的格式化接口
    - 自动格式选择和适配
    - 内置分页支持
    - 状态消息管理
    - 多种输出渠道支持
    
    Attributes:
        theme (ColorTheme): 使用的颜色主题
        table_formatter (TableFormatter): 表格格式化器实例
        list_formatter (ListFormatter): 列表格式化器实例
        tree_formatter (TreeFormatter): 树形格式化器实例
        paginator (Paginator): 分页器实例
    """
    
    def __init__(self, theme: Optional[ColorTheme] = None):
        """
        初始化输出格式化器
        
        创建所有需要的子格式化器实例，并设置默认配置。
        
        Args:
            theme (Optional[ColorTheme]): 可选的颜色主题，如未指定则使用默认主题
        """
        self.theme = theme or ColorTheme()
        self.table_formatter = TableFormatter(self.theme)
        self.list_formatter = ListFormatter(self.theme)
        self.tree_formatter = TreeFormatter(self.theme)
        self.paginator = Paginator()
    
    def format_output(self, data: Any, 
                     format_type: OutputFormat = OutputFormat.TABLE,
                     **kwargs) -> List[str]:
        """
        统一格式化输出
        
        根据指定的格式类型将数据格式化为相应的输出形式。自动判断数据类型
        的适配性，并提供错误处理。
        
        Args:
            data (Any): 要格式化的数据
            format_type (OutputFormat): 输出格式类型，默认为表格格式
            **kwargs: 传递给具体格式化器的额外参数
            
        Returns:
            List[str]: 格式化后的输出行列表
        """
        if format_type == OutputFormat.JSON:
            return [json.dumps(data, ensure_ascii=False, indent=2)]
        
        elif format_type == OutputFormat.TABLE:
            headers = kwargs.get('headers', [])
            if isinstance(data, list) and data and isinstance(data[0], dict):
                if not headers:
                    headers = list(data[0].keys())
                return self.table_formatter.format_table(data, headers)
            return [f"{self.theme.warning}数据格式不适合表格显示{self.theme.reset}"]
        
        elif format_type == OutputFormat.LIST:
            if isinstance(data, list):
                return self.list_formatter.format_list(data, **kwargs)
            return [f"{self.theme.warning}数据格式不适合列表显示{self.theme.reset}"]
        
        elif format_type == OutputFormat.TREE:
            if isinstance(data, dict):
                return self.tree_formatter.format_tree(data, **kwargs)
            return [f"{self.theme.warning}数据格式不适合树形显示{self.theme.reset}"]
        
        elif format_type == OutputFormat.COMPACT:
            return self._format_compact(data)
        
        else:
            return [str(data)]
    
    def _format_compact(self, data: Any) -> List[str]:
        """紧凑格式"""
        if isinstance(data, list):
            items = []
            for item in data:
                if isinstance(item, dict):
                    name = item.get('name', str(item))
                    desc = item.get('description', '')
                    if desc:
                        items.append(f"{self.theme.command}{name}{self.theme.reset} - {desc[:50]}...")
                    else:
                        items.append(f"{self.theme.command}{name}{self.theme.reset}")
                else:
                    items.append(str(item))
            return items
        return [str(data)]
    
    def format_with_pagination(self, data: Any, 
                              format_type: OutputFormat = OutputFormat.TABLE,
                              page_size: int = 20,
                              page_num: int = 1,
                              **kwargs) -> Dict[str, Any]:
        """带分页的格式化输出"""
        lines = self.format_output(data, format_type, **kwargs)
        
        self.paginator.page_size = page_size
        result = self.paginator.paginate(lines, page_num)
        
        return result
    
    def print_output(self, lines: List[str], file=None) -> None:
        """打印输出"""
        output_file = file or sys.stdout
        for line in lines:
            print(line, file=output_file)
    
    def create_status_message(self, message: str, 
                             status: str = 'info') -> str:
        """创建状态消息"""
        status_colors = {
            'success': self.theme.success,
            'warning': self.theme.warning,
            'error': self.theme.warning,
            'info': self.theme.info
        }
        
        color = status_colors.get(status, self.theme.info)
        return f"{color}{message}{self.theme.reset}"

def main():
    """
    格式化模块测试函数
    
    提供对所有格式化功能的全面测试，包括：
    1. 不同输出格式的测试（表格、列表、树形）
    2. 分页功能测试
    3. 颜色主题和状态消息测试
    4. 各种数据类型的兼容性测试
    
    这个测试函数帮助开发者验证格式化系统的所有功能是否正常工作。
    """
    # 构造测试数据 - 模拟真实的命令数据结构
    test_data = [
        {'name': 'ls', 'description': '列出目录内容', 'category': '基础文件操作'},
        {'name': 'cp', 'description': '复制文件或目录', 'category': '基础文件操作'},
        {'name': 'grep', 'description': '搜索文本模式', 'category': '文件查看与编辑'}
    ]
    
    # 构造层次结构数据 - 用于测试树形显示
    tree_data = {
        '基础文件操作': {
            '文件创建': ['touch', 'mkdir'],
            '文件删除': ['rm', 'rmdir'],
            '描述': '基本的文件和目录操作'
        },
        '文件查看': {
            '内容查看': ['cat', 'less', 'head', 'tail'],
            '描述': '查看文件内容的命令'
        }
    }
    
    # 创建格式化器实例
    formatter = OutputFormatter()
    
    print("=== 格式化输出测试 ===")
    
    # 测试表格格式 - 适合结构化数据对比
    print("\n1. 表格格式:")
    table_lines = formatter.format_output(test_data, OutputFormat.TABLE)
    formatter.print_output(table_lines)
    
    # 测试列表格式 - 适合详细信息显示
    print("\n2. 列表格式:")
    list_lines = formatter.format_output(test_data, OutputFormat.LIST)
    formatter.print_output(list_lines)
    
    # 测试树形格式 - 适合层次结构显示
    print("\n3. 树形格式:")
    tree_lines = formatter.format_output(tree_data, OutputFormat.TREE)
    formatter.print_output(tree_lines)
    
    # 测试分页功能 - 适合大量数据显示
    print("\n4. 分页测试:")
    paginated = formatter.format_with_pagination(
        test_data, OutputFormat.LIST, page_size=2, page_num=1
    )
    formatter.print_output(paginated['lines'])
    print(f"\n{paginated['page_info']}")
    
    # 测试状态消息 - 显示不同类型的反馈
    print("\n5. 状态消息:")
    success_msg = formatter.create_status_message("操作成功！", 'success')
    warning_msg = formatter.create_status_message("注意：这是警告", 'warning')
    print(success_msg)
    print(warning_msg)

if __name__ == '__main__':
    # 仅在直接运行此文件时执行测试函数
    main()