#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化输出模块
负责将数据格式化为不同的输出格式（表格、列表、JSON等）
支持颜色高亮和分页显示
"""

import json
import sys
import math
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class ColorCode:
    """颜色代码定义"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 高亮前景色
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'

class OutputFormat(Enum):
    """输出格式枚举"""
    TABLE = 'table'
    LIST = 'list'
    JSON = 'json'
    TREE = 'tree'
    COMPACT = 'compact'

class ColorTheme:
    """颜色主题"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        
        if enabled:
            self.header = ColorCode.BOLD + ColorCode.BRIGHT_CYAN
            self.command = ColorCode.BRIGHT_GREEN
            self.description = ColorCode.WHITE
            self.category = ColorCode.YELLOW
            self.option = ColorCode.BRIGHT_BLUE
            self.example = ColorCode.CYAN
            self.warning = ColorCode.BRIGHT_RED
            self.success = ColorCode.BRIGHT_GREEN
            self.info = ColorCode.BRIGHT_BLUE
            self.dim = ColorCode.DIM
            self.reset = ColorCode.RESET
        else:
            # 禁用颜色时所有颜色都为空字符串
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
    """表格格式化器"""
    
    def __init__(self, theme: ColorTheme):
        self.theme = theme
    
    def format_table(self, data: List[Dict[str, Any]], 
                    headers: List[str],
                    max_width: int = 80) -> List[str]:
        """格式化为表格"""
        if not data:
            return [f"{self.theme.info}没有数据显示{self.theme.reset}"]
        
        # 计算列宽
        col_widths = self._calculate_column_widths(data, headers, max_width)
        
        lines = []
        
        # 表头
        header_line = self._format_header_line(headers, col_widths)
        lines.append(header_line)
        
        # 分隔线
        separator = self._create_separator(col_widths)
        lines.append(separator)
        
        # 数据行
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
    """列表格式化器"""
    
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
    """统一输出格式化器"""
    
    def __init__(self, theme: Optional[ColorTheme] = None):
        self.theme = theme or ColorTheme()
        self.table_formatter = TableFormatter(self.theme)
        self.list_formatter = ListFormatter(self.theme)
        self.tree_formatter = TreeFormatter(self.theme)
        self.paginator = Paginator()
    
    def format_output(self, data: Any, 
                     format_type: OutputFormat = OutputFormat.TABLE,
                     **kwargs) -> List[str]:
        """统一格式化输出"""
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
    """测试函数"""
    # 测试数据
    test_data = [
        {'name': 'ls', 'description': '列出目录内容', 'category': '基础文件操作'},
        {'name': 'cp', 'description': '复制文件或目录', 'category': '基础文件操作'},
        {'name': 'grep', 'description': '搜索文本模式', 'category': '文件查看与编辑'}
    ]
    
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
    
    # 创建格式化器
    formatter = OutputFormatter()
    
    print("=== 格式化输出测试 ===")
    
    # 测试表格格式
    print("\n1. 表格格式:")
    table_lines = formatter.format_output(test_data, OutputFormat.TABLE)
    formatter.print_output(table_lines)
    
    # 测试列表格式
    print("\n2. 列表格式:")
    list_lines = formatter.format_output(test_data, OutputFormat.LIST)
    formatter.print_output(list_lines)
    
    # 测试树形格式
    print("\n3. 树形格式:")
    tree_lines = formatter.format_output(tree_data, OutputFormat.TREE)
    formatter.print_output(tree_lines)
    
    # 测试分页
    print("\n4. 分页测试:")
    paginated = formatter.format_with_pagination(
        test_data, OutputFormat.LIST, page_size=2, page_num=1
    )
    formatter.print_output(paginated['lines'])
    print(f"\n{paginated['page_info']}")
    
    # 测试状态消息
    print("\n5. 状态消息:")
    success_msg = formatter.create_status_message("操作成功！", 'success')
    warning_msg = formatter.create_status_message("注意：这是警告", 'warning')
    print(success_msg)
    print(warning_msg)

if __name__ == '__main__':
    main()