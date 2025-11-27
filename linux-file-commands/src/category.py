#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令分类显示模块

本模块负责按照分类组织和显示Linux文件操作命令，提供灵活的命令分类管理功能。
主要功能包括：
- 命令按功能分类管理和显示
- 支持多维度的命令过滤和排序
- 提供分类统计和数据分析
- 支持分层的分类树结构
- 按难度等级和使用频率组织命令

作者: AI Assistant
版本: 1.0
创建时间: 2024
最后修改: 2025-09-25
"""

import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

class CategoryManager:
    """
    命令分类管理器
    
    负责加载、组织和管理Linux命令的分类信息。提供命令的多维度索引，
    支持按分类、难度、使用频率等维度快速检索命令。该类是整个分类
    系统的核心，管理着命令数据和分类数据之间的映射关系。
    
    Attributes:
        commands_file (Path): 命令数据文件路径
        categories_file (Path): 分类数据文件路径
        commands_data (Dict): 加载的命令数据
        categories_data (Dict): 加载的分类数据
        command_by_name (Dict): 按命令名索引的字典
        commands_by_category (Dict): 按分类索引的命令字典
        commands_by_difficulty (Dict): 按难度索引的命令字典
        commands_by_frequency (Dict): 按使用频率索引的命令字典
    """
    
    def __init__(self, commands_file: str, categories_file: str):
        """
        初始化分类管理器
        
        Args:
            commands_file (str): 命令数据JSON文件的路径
            categories_file (str): 分类数据JSON文件的路径
            
        Raises:
            FileNotFoundError: 当数据文件不存在时
            ValueError: 当JSON文件格式错误时
        """
        self.commands_file = Path(commands_file)
        self.categories_file = Path(categories_file)
        self.commands_data = self._load_commands()
        self.categories_data = self._load_categories()
        self._build_command_index()
    
    def _load_commands(self) -> Dict[str, Any]:
        """
        从JSON文件加载命令数据
        
        读取命令数据文件，解析JSON格式的命令信息。文件应包含
        所有Linux文件操作命令的详细信息，包括语法、描述、示例等。
        
        Returns:
            Dict[str, Any]: 包含所有命令信息的字典
            
        Raises:
            FileNotFoundError: 当命令数据文件不存在时
            json.JSONDecodeError: 当JSON格式错误时
        """
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"命令数据文件未找到: {self.commands_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"命令数据文件格式错误: {e}")
    
    def _load_categories(self) -> Dict[str, Any]:
        """
        从JSON文件加载分类数据
        
        读取分类配置文件，包含命令的分类定义、难度等级划分、
        使用频率统计等信息。这些数据用于构建多维度的命令索引。
        
        Returns:
            Dict[str, Any]: 包含分类配置信息的字典
            
        Raises:
            FileNotFoundError: 当分类数据文件不存在时
            json.JSONDecodeError: 当JSON格式错误时
        """
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"分类数据文件未找到: {self.categories_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"分类数据文件格式错误: {e}")
    
    def _build_command_index(self) -> None:
        """
        构建多维度命令索引
        
        基于加载的命令和分类数据，构建多个索引字典以支持快速检索：
        - 按命令名称索引：用于快速查找单个命令
        - 按功能分类索引：用于显示分类下的所有命令
        - 按难度等级索引：用于按学习难度筛选命令
        - 按使用频率索引：用于按常用程度筛选命令
        
        这些索引提高了命令检索的效率和灵活性。
        """
        self.command_by_name = {}
        self.commands_by_category = {}
        self.commands_by_difficulty = {}
        self.commands_by_frequency = {}
        
        # 按命令名索引 - 建立命令名到命令对象的直接映射
        for cmd in self.commands_data['commands']:
            self.command_by_name[cmd['name']] = cmd
        
        # 按分类索引 - 将命令按功能分类组织
        for cmd in self.commands_data['commands']:
            for category in cmd.get('categories', []):
                if category not in self.commands_by_category:
                    self.commands_by_category[category] = []
                self.commands_by_category[category].append(cmd)
        
        # 按难度索引 - 按学习难度分组命令
        difficulty_levels = self.categories_data.get('difficulty_levels', {})
        for level, commands in difficulty_levels.items():
            self.commands_by_difficulty[level] = []
            for cmd_name in commands:
                if cmd_name in self.command_by_name:
                    self.commands_by_difficulty[level].append(
                        self.command_by_name[cmd_name]
                    )
        
        # 按使用频率索引 - 按常用程度分组命令
        usage_frequency = self.categories_data.get('usage_frequency', {})
        for freq, commands in usage_frequency.items():
            self.commands_by_frequency[freq] = []
            for cmd_name in commands:
                if cmd_name in self.command_by_name:
                    self.commands_by_frequency[freq].append(
                        self.command_by_name[cmd_name]
                    )
    
    def get_all_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有分类信息
        
        返回系统中定义的所有命令分类，包括分类名称、描述、
        子分类等信息。用于构建分类导航和显示分类概览。
        
        Returns:
            Dict[str, Dict[str, Any]]: 包含所有分类信息的字典
        """
        return self.categories_data.get('categories', {})
    
    def get_category_commands(self, category: str) -> List[Dict[str, Any]]:
        """
        获取指定分类的命令列表
        
        根据分类名称返回该分类下的所有命令。支持主分类和子分类的查询。
        
        Args:
            category (str): 分类名称
            
        Returns:
            List[Dict[str, Any]]: 该分类下的命令列表，如果分类不存在则返回空列表
        """
        return self.commands_by_category.get(category, [])
    
    def get_commands_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        按难度获取命令列表
        
        根据难度等级返回对应的命令列表。难度等级通常包括初级、
        中级、高级等，帮助用户按学习进度查找合适的命令。
        
        Args:
            difficulty (str): 难度等级（如初级、中级、高级）
            
        Returns:
            List[Dict[str, Any]]: 该难度等级的命令列表
        """
        return self.commands_by_difficulty.get(difficulty, [])
    
    def get_commands_by_frequency(self, frequency: str) -> List[Dict[str, Any]]:
        """
        按使用频率获取命令列表
        
        根据使用频率返回对应的命令列表。频率类别通常包括高频、
        中频、低频，帮助用户优先学习常用命令。
        
        Args:
            frequency (str): 使用频率（如高频、中频、低频）
            
        Returns:
            List[Dict[str, Any]]: 该频率类别的命令列表
        """
        return self.commands_by_frequency.get(frequency, [])
    
    def get_subcategories(self, category: str) -> Dict[str, List[str]]:
        """
        获取分类的子分类
        
        返回指定主分类下的所有子分类及其包含的命令列表。
        用于构建分层的分类结构和导航。
        
        Args:
            category (str): 主分类名称
            
        Returns:
            Dict[str, List[str]]: 子分类到命令列表的映射，如果分类不存在则返回空字典
        """
        categories = self.get_all_categories()
        if category in categories:
            return categories[category].get('subcategories', {})
        return {}
    
    def list_all_commands(self, 
                         filters: Optional[Dict[str, str]] = None,
                         sort_by: str = 'name') -> List[Dict[str, Any]]:
        """
        列出所有命令，支持过滤和排序
        
        提供灵活的命令查询功能，支持多维度过滤条件和多种排序方式。
        用户可以按难度、使用频率等条件筛选命令，并按名称、分类或使用频率排序。
        
        Args:
            filters (Optional[Dict[str, str]]): 过滤条件字典，支持的键包括：
                - 'difficulty': 难度等级过滤
                - 'frequency': 使用频率过滤
            sort_by (str): 排序方式，可选值为 'name'、'category'、'usage'
            
        Returns:
            List[Dict[str, Any]]: 筛选和排序后的命令列表
        """
        # 复制命令列表以避免修改原始数据
        commands = self.commands_data['commands'].copy()
        
        # 应用过滤条件筛选符合条件的命令
        if filters:
            commands = self._apply_filters(commands, filters)
        
        # 按指定方式排序命令列表
        commands = self._sort_commands(commands, sort_by)
        
        return commands
    
    def _apply_filters(self, commands: List[Dict[str, Any]], 
                      filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        应用过滤条件筛选命令
        
        根据用户指定的过滤条件，从命令列表中筛选出符合条件的命令。
        支持按难度等级和使用频率进行筛选，多个条件可以同时使用。
        
        Args:
            commands (List[Dict[str, Any]]): 原始命令列表
            filters (Dict[str, str]): 过滤条件字典
            
        Returns:
            List[Dict[str, Any]]: 筛选后的命令列表
        """
        filtered_commands = commands
        
        # 按难度过滤 - 筛选指定难度等级的命令
        if 'difficulty' in filters:
            difficulty_commands = set(
                cmd['name'] for cmd in self.get_commands_by_difficulty(filters['difficulty'])
            )
            filtered_commands = [
                cmd for cmd in filtered_commands 
                if cmd['name'] in difficulty_commands
            ]
        
        # 按使用频率过滤 - 筛选指定频率类别的命令
        if 'frequency' in filters:
            frequency_commands = set(
                cmd['name'] for cmd in self.get_commands_by_frequency(filters['frequency'])
            )
            filtered_commands = [
                cmd for cmd in filtered_commands 
                if cmd['name'] in frequency_commands
            ]
        
        return filtered_commands
    
    def _sort_commands(self, commands: List[Dict[str, Any]], 
                      sort_by: str) -> List[Dict[str, Any]]:
        """
        排序命令列表
        
        根据指定的排序方式对命令列表进行排序。支持按名称、分类和
        使用频率排序，其中使用频率排序会将高频命令排在前面。
        
        Args:
            commands (List[Dict[str, Any]]): 待排序的命令列表
            sort_by (str): 排序方式（'name'、'category'、'usage'）
            
        Returns:
            List[Dict[str, Any]]: 排序后的命令列表
        """
        if sort_by == 'name':
            # 按命令名称字母顺序排序
            return sorted(commands, key=lambda x: x['name'])
        elif sort_by == 'category':
            # 按主分类名称排序（取第一个分类）
            return sorted(commands, key=lambda x: x.get('categories', [''])[0])
        elif sort_by == 'usage':
            # 按使用频率排序（高频在前）
            usage_order = {'高频': 1, '中频': 2, '低频': 3}
            
            def get_usage_priority(cmd):
                """获取命令的使用频率优先级"""
                cmd_name = cmd['name']
                for freq, freq_commands in self.commands_by_frequency.items():
                    if any(c['name'] == cmd_name for c in freq_commands):
                        return usage_order.get(freq, 4)
                return 4  # 未分类的命令排在最后
            
            return sorted(commands, key=get_usage_priority)
        else:
            # 不支持的排序方式，返回原始列表
            return commands

class CategoryDisplayer:
    """
    分类显示器
    
    负责将命令分类数据格式化为用户友好的显示形式。提供多种显示模式，
    包括分类概览、分类树结构、特定分类的命令列表等。该类与
    CategoryManager紧密配合，将数据管理和展示逻辑分离。
    
    Attributes:
        category_manager (CategoryManager): 关联的分类管理器实例
    """
    
    def __init__(self, category_manager: CategoryManager):
        """
        初始化分类显示器
        
        Args:
            category_manager (CategoryManager): 已初始化的分类管理器实例
        """
        self.category_manager = category_manager
    
    def display_all_categories(self) -> List[Dict[str, Any]]:
        """
        显示所有分类的概览信息
        
        生成包含所有分类的概览列表，包括分类名称、描述、子分类数量和
        命令数量等统计信息。用于显示分类导航页面或概览界面。
        
        Returns:
            List[Dict[str, Any]]: 包含每个分类信息的列表，每个元素包含：
                - name: 分类名称
                - description: 分类描述
                - subcategories: 子分类名称列表
                - command_count: 该分类下的命令总数
        """
        categories = self.category_manager.get_all_categories()
        category_list = []
        
        for name, info in categories.items():
            subcategories = info.get('subcategories', {})
            # 统计该分类及其子分类的总命令数
            command_count = sum(
                len(self.category_manager.get_category_commands(name))
                for name in [name] + list(subcategories.keys())
            )
            
            category_list.append({
                'name': name,
                'description': info.get('description', ''),
                'subcategories': list(subcategories.keys()),
                'command_count': command_count
            })
        
        return category_list
    
    def display_category_tree(self) -> Dict[str, Any]:
        """
        显示分类树结构
        
        生成层次化的分类树结构，展示主分类、子分类及其包含的命令。
        这种层次结构便于用户理解命令的组织方式和导航到特定的命令组。
        
        Returns:
            Dict[str, Any]: 层次化的分类树，结构为：
                {
                    '主分类名': {
                        'description': '分类描述',
                        'subcategories': {
                            '子分类名': {
                                'commands': ['命令列表'],
                                'count': 命令数量
                            }
                        }
                    }
                }
        """
        categories = self.category_manager.get_all_categories()
        tree = {}
        
        for category_name, category_info in categories.items():
            subcategories = category_info.get('subcategories', {})
            tree[category_name] = {
                'description': category_info.get('description', ''),
                'subcategories': {}
            }
            
            # 处理每个子分类，统计可用命令数量
            for sub_name, sub_commands in subcategories.items():
                available_commands = [
                    cmd for cmd in sub_commands 
                    if cmd in self.category_manager.command_by_name
                ]
                tree[category_name]['subcategories'][sub_name] = {
                    'commands': available_commands,
                    'count': len(available_commands)
                }
        
        return tree
    
    def display_category_commands(self, category: str, 
                                include_details: bool = False) -> Dict[str, Any]:
        """
        显示指定分类的命令列表
        
        获取并格式化指定分类下的所有命令。支持主分类和子分类的查询，
        可选择是否包含命令的详细信息。用于分类页面的命令列表显示。
        
        Args:
            category (str): 分类名称（可以是主分类或子分类）
            include_details (bool): 是否包含命令的详细信息（语法、分类、相关命令等）
            
        Returns:
            Dict[str, Any]: 包含分类信息和命令列表的字典：
                - category: 分类名称
                - commands: 命令列表
                - count: 命令数量
        """
        commands = self.category_manager.get_category_commands(category)
        
        if not commands:
            # 检查是否是子分类 - 在主分类中搜索匹配的子分类
            all_categories = self.category_manager.get_all_categories()
            for main_cat, info in all_categories.items():
                subcategories = info.get('subcategories', {})
                if category in subcategories:
                    # 获取子分类中的命令
                    cmd_names = subcategories[category]
                    commands = [
                        self.category_manager.command_by_name[name]
                        for name in cmd_names
                        if name in self.category_manager.command_by_name
                    ]
                    break
        
        result = {
            'category': category,
            'commands': [],
            'count': len(commands)
        }
        
        # 构建命令信息列表
        for cmd in commands:
            cmd_info = {
                'name': cmd['name'],
                'description': cmd['description']
            }
            
            # 根据需要添加详细信息
            if include_details:
                cmd_info.update({
                    'syntax': cmd.get('syntax', ''),
                    'categories': cmd.get('categories', []),
                    'related_commands': cmd.get('related_commands', [])
                })
            
            result['commands'].append(cmd_info)
        
        return result
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """
        获取分类统计信息
        
        生成关于命令分类系统的统计数据，包括分类数量、命令数量、
        各分类的命令分布、难度分布和频率分布等信息。用于数据分析和系统概览。
        
        Returns:
            Dict[str, Any]: 包含以下统计信息的字典：
                - total_categories: 总分类数
                - total_commands: 总命令数
                - category_distribution: 各分类的命令数量分布
                - difficulty_distribution: 难度等级分布
                - frequency_distribution: 使用频率分布
        """
        stats = {
            'total_categories': len(self.category_manager.get_all_categories()),
            'total_commands': len(self.category_manager.commands_data['commands']),
            'category_distribution': {},
            'difficulty_distribution': {},
            'frequency_distribution': {}
        }
        
        # 分类分布 - 统计每个分类包含的命令数量
        for category in self.category_manager.commands_by_category:
            count = len(self.category_manager.get_category_commands(category))
            stats['category_distribution'][category] = count
        
        # 难度分布 - 统计不同难度等级的命令数量
        for difficulty in self.category_manager.commands_by_difficulty:
            count = len(self.category_manager.get_commands_by_difficulty(difficulty))
            stats['difficulty_distribution'][difficulty] = count
        
        # 频率分布 - 统计不同使用频率的命令数量
        for frequency in self.category_manager.commands_by_frequency:
            count = len(self.category_manager.get_commands_by_frequency(frequency))
            stats['frequency_distribution'][frequency] = count
        
        return stats

def main():
    """
    模块测试函数
    
    提供对CategoryManager和CategoryDisplayer类的功能测试。
    测试内容包括：
    1. 分类管理器的初始化和数据加载
    2. 分类概览显示
    3. 分类树结构展示
    4. 特定分类的命令列表
    5. 系统统计信息显示
    
    这个测试函数可以在开发调试时使用，验证模块的基本功能是否正常。
    """
    import os
    
    # 获取数据文件的路径 - 相对于当前模块文件的位置
    current_dir = Path(__file__).parent
    commands_file = current_dir.parent / 'data' / 'commands.json'
    categories_file = current_dir.parent / 'data' / 'categories.json'
    
    try:
        # 创建和初始化分类管理器和显示器
        manager = CategoryManager(str(commands_file), str(categories_file))
        displayer = CategoryDisplayer(manager)
        
        print("=== 分类管理器测试 ===")
        
        # 测试获取所有分类
        print("\n1. 所有分类:")
        categories = displayer.display_all_categories()
        for cat in categories:
            print(f"  {cat['name']}: {cat['description']} ({cat['command_count']}个命令)")
        
        # 测试分类树
        print("\n2. 分类树结构:")
        tree = displayer.display_category_tree()
        for main_cat, info in tree.items():
            print(f"  {main_cat}: {info['description']}")
            for sub_cat, sub_info in info['subcategories'].items():
                print(f"    └─ {sub_cat}: {sub_info['count']}个命令")
        
        # 测试特定分类的命令
        print("\n3. 基础文件操作分类的命令:")
        category_commands = displayer.display_category_commands('基础文件操作')
        print(f"  找到 {category_commands['count']} 个命令:")
        for cmd in category_commands['commands']:
            print(f"    {cmd['name']}: {cmd['description']}")
        
        # 测试统计信息
        print("\n4. 统计信息:")
        stats = displayer.get_category_statistics()
        print(f"  总分类数: {stats['total_categories']}")
        print(f"  总命令数: {stats['total_commands']}")
        print("  难度分布:", stats['difficulty_distribution'])
        print("  频率分布:", stats['frequency_distribution'])
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    # 仅在直接运行此文件时执行测试函数
    main()