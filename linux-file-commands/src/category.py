#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令分类显示模块
负责按照分类组织和显示Linux文件操作命令
"""

import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

class CategoryManager:
    """分类管理器"""
    
    def __init__(self, commands_file: str, categories_file: str):
        self.commands_file = Path(commands_file)
        self.categories_file = Path(categories_file)
        self.commands_data = self._load_commands()
        self.categories_data = self._load_categories()
        self._build_command_index()
    
    def _load_commands(self) -> Dict[str, Any]:
        """加载命令数据"""
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"命令数据文件未找到: {self.commands_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"命令数据文件格式错误: {e}")
    
    def _load_categories(self) -> Dict[str, Any]:
        """加载分类数据"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"分类数据文件未找到: {self.categories_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"分类数据文件格式错误: {e}")
    
    def _build_command_index(self) -> None:
        """构建命令索引"""
        self.command_by_name = {}
        self.commands_by_category = {}
        self.commands_by_difficulty = {}
        self.commands_by_frequency = {}
        
        # 按命令名索引
        for cmd in self.commands_data['commands']:
            self.command_by_name[cmd['name']] = cmd
        
        # 按分类索引
        for cmd in self.commands_data['commands']:
            for category in cmd.get('categories', []):
                if category not in self.commands_by_category:
                    self.commands_by_category[category] = []
                self.commands_by_category[category].append(cmd)
        
        # 按难度索引
        difficulty_levels = self.categories_data.get('difficulty_levels', {})
        for level, commands in difficulty_levels.items():
            self.commands_by_difficulty[level] = []
            for cmd_name in commands:
                if cmd_name in self.command_by_name:
                    self.commands_by_difficulty[level].append(
                        self.command_by_name[cmd_name]
                    )
        
        # 按使用频率索引
        usage_frequency = self.categories_data.get('usage_frequency', {})
        for freq, commands in usage_frequency.items():
            self.commands_by_frequency[freq] = []
            for cmd_name in commands:
                if cmd_name in self.command_by_name:
                    self.commands_by_frequency[freq].append(
                        self.command_by_name[cmd_name]
                    )
    
    def get_all_categories(self) -> Dict[str, Dict[str, Any]]:
        """获取所有分类信息"""
        return self.categories_data.get('categories', {})
    
    def get_category_commands(self, category: str) -> List[Dict[str, Any]]:
        """获取指定分类的命令列表"""
        return self.commands_by_category.get(category, [])
    
    def get_commands_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """按难度获取命令列表"""
        return self.commands_by_difficulty.get(difficulty, [])
    
    def get_commands_by_frequency(self, frequency: str) -> List[Dict[str, Any]]:
        """按使用频率获取命令列表"""
        return self.commands_by_frequency.get(frequency, [])
    
    def get_subcategories(self, category: str) -> Dict[str, List[str]]:
        """获取分类的子分类"""
        categories = self.get_all_categories()
        if category in categories:
            return categories[category].get('subcategories', {})
        return {}
    
    def list_all_commands(self, 
                         filters: Optional[Dict[str, str]] = None,
                         sort_by: str = 'name') -> List[Dict[str, Any]]:
        """列出所有命令，支持过滤和排序"""
        commands = self.commands_data['commands'].copy()
        
        # 应用过滤器
        if filters:
            commands = self._apply_filters(commands, filters)
        
        # 排序
        commands = self._sort_commands(commands, sort_by)
        
        return commands
    
    def _apply_filters(self, commands: List[Dict[str, Any]], 
                      filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """应用过滤器"""
        filtered_commands = commands
        
        # 按难度过滤
        if 'difficulty' in filters:
            difficulty_commands = set(
                cmd['name'] for cmd in self.get_commands_by_difficulty(filters['difficulty'])
            )
            filtered_commands = [
                cmd for cmd in filtered_commands 
                if cmd['name'] in difficulty_commands
            ]
        
        # 按使用频率过滤
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
        """排序命令列表"""
        if sort_by == 'name':
            return sorted(commands, key=lambda x: x['name'])
        elif sort_by == 'category':
            return sorted(commands, key=lambda x: x.get('categories', [''])[0])
        elif sort_by == 'usage':
            # 按使用频率排序（高频在前）
            usage_order = {'高频': 1, '中频': 2, '低频': 3}
            
            def get_usage_priority(cmd):
                cmd_name = cmd['name']
                for freq, freq_commands in self.commands_by_frequency.items():
                    if any(c['name'] == cmd_name for c in freq_commands):
                        return usage_order.get(freq, 4)
                return 4
            
            return sorted(commands, key=get_usage_priority)
        else:
            return commands

class CategoryDisplayer:
    """分类显示器"""
    
    def __init__(self, category_manager: CategoryManager):
        self.category_manager = category_manager
    
    def display_all_categories(self) -> List[Dict[str, Any]]:
        """显示所有分类"""
        categories = self.category_manager.get_all_categories()
        category_list = []
        
        for name, info in categories.items():
            subcategories = info.get('subcategories', {})
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
        """显示分类树结构"""
        categories = self.category_manager.get_all_categories()
        tree = {}
        
        for category_name, category_info in categories.items():
            subcategories = category_info.get('subcategories', {})
            tree[category_name] = {
                'description': category_info.get('description', ''),
                'subcategories': {}
            }
            
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
        """显示指定分类的命令"""
        commands = self.category_manager.get_category_commands(category)
        
        if not commands:
            # 检查是否是子分类
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
        
        for cmd in commands:
            cmd_info = {
                'name': cmd['name'],
                'description': cmd['description']
            }
            
            if include_details:
                cmd_info.update({
                    'syntax': cmd.get('syntax', ''),
                    'categories': cmd.get('categories', []),
                    'related_commands': cmd.get('related_commands', [])
                })
            
            result['commands'].append(cmd_info)
        
        return result
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """获取分类统计信息"""
        stats = {
            'total_categories': len(self.category_manager.get_all_categories()),
            'total_commands': len(self.category_manager.commands_data['commands']),
            'category_distribution': {},
            'difficulty_distribution': {},
            'frequency_distribution': {}
        }
        
        # 分类分布
        for category in self.category_manager.commands_by_category:
            count = len(self.category_manager.get_category_commands(category))
            stats['category_distribution'][category] = count
        
        # 难度分布
        for difficulty in self.category_manager.commands_by_difficulty:
            count = len(self.category_manager.get_commands_by_difficulty(difficulty))
            stats['difficulty_distribution'][difficulty] = count
        
        # 频率分布
        for frequency in self.category_manager.commands_by_frequency:
            count = len(self.category_manager.get_commands_by_frequency(frequency))
            stats['frequency_distribution'][frequency] = count
        
        return stats

def main():
    """测试函数"""
    import os
    
    # 获取数据文件的路径
    current_dir = Path(__file__).parent
    commands_file = current_dir.parent / 'data' / 'commands.json'
    categories_file = current_dir.parent / 'data' / 'categories.json'
    
    try:
        # 创建分类管理器
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
    main()