#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索引擎模块

本模块实现了智能的Linux文件命令搜索功能，支持多种搜索策略和相关性排序。
主要功能包括：
- 支持精确匹配、前缀匹配、词汇匹配和模糊匹配
- 智能的相关性评分和排序系统
- 命令自动完成和建议功能
- 高级搜索过滤和排序选项
- 支持中英文混合搜索
- 全文索引和多字段检索

作者: AI Assistant
版本: 1.0
创建时间: 2024
最后修改: 2025-09-25
"""

import re
import json
from typing import Dict, List, Optional, Set, Any, Tuple
from pathlib import Path
from difflib import SequenceMatcher
import math

class SearchEngine:
    """
    命令搜索引擎
    
    实现对Linux文件操作命令的智能搜索功能。支持多种搜索策略：
    1. 精确匹配 - 命令名的完全匹配
    2. 前缀匹配 - 命令名的前缀匹配
    3. 词汇匹配 - 在描述、分类等字段中搜索关键词
    4. 模糊匹配 - 基于字符串相似度的模糊匹配
    
    通过构建全文索引提高搜索效率，并实现智能的相关性评分系统。
    
    Attributes:
        commands_file (Path): 命令数据文件路径
        commands_data (Dict): 加载的命令数据
        command_index (Dict): 按命令名索引的字典
        word_index (Dict): 按词汇索引的字典，支持全文检索
    """
    
    def __init__(self, commands_file: str):
        """
        初始化搜索引擎
        
        加载命令数据并构建搜索索引。索引包括命令名、描述、分类、
        相关命令和选项说明等字段，支持中英文混合索引。
        
        Args:
            commands_file (str): 命令数据JSON文件的路径
            
        Raises:
            FileNotFoundError: 当命令数据文件不存在时
            ValueError: 当JSON文件格式错误时
        """
        self.commands_file = Path(commands_file)
        self.commands_data = self._load_commands()
        self._build_search_index()
    
    def _load_commands(self) -> Dict[str, Any]:
        """
        从JSON文件加载命令数据
        
        读取并解析命令数据文件，该文件包含所有Linux文件操作命令的
        详细信息，包括命令名、描述、语法、分类、示例等。
        
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
    
    def _build_search_index(self) -> None:
        """
        构建全文搜索索引
        
        为所有命令数据构建多维度的搜索索引，包括：
        1. 命令索引 - 按命令名直接索引
        2. 词汇索引 - 按关键词索引，支持多字段检索
        
        索引涵盖以下字段：
        - name: 命令名称
        - description: 命令描述
        - category: 功能分类
        - related: 相关命令
        - option: 选项说明
        
        支持中英文混合索引，自动提取有意义的词汇。
        """
        self.command_index = {}
        self.word_index = {}
        
        for cmd in self.commands_data['commands']:
            cmd_name = cmd['name']
            self.command_index[cmd_name] = cmd
            
            # 索引命令名 - 最高优先级的匹配字段
            self._add_to_word_index(cmd_name, cmd_name, 'name')
            
            # 索引描述 - 从描述中提取关键词
            description = cmd.get('description', '')
            words = self._extract_words(description)
            for word in words:
                self._add_to_word_index(word, cmd_name, 'description')
            
            # 索引分类 - 将分类名称中的词汇添加到索引
            categories = cmd.get('categories', [])
            for category in categories:
                category_words = self._extract_words(category)
                for word in category_words:
                    self._add_to_word_index(word, cmd_name, 'category')
            
            # 索引相关命令 - 建立命令间的关联
            related = cmd.get('related_commands', [])
            for rel_cmd in related:
                self._add_to_word_index(rel_cmd, cmd_name, 'related')
            
            # 索引选项和示例 - 从选项说明中提取关键词
            options = cmd.get('common_options', [])
            for option in options:
                opt_words = self._extract_words(option.get('description', ''))
                for word in opt_words:
                    self._add_to_word_index(word, cmd_name, 'option')
    
    def _add_to_word_index(self, word: str, command: str, field_type: str) -> None:
        """
        将词汇添加到索引中
        
        为指定的词汇和命令建立索引映射，记录词汇出现的字段类型。
        支持同一词汇在多个字段中出现，用于相关性评分计算。
        
        Args:
            word (str): 要索引的词汇
            command (str): 命令名称
            field_type (str): 字段类型（name/description/category/related/option）
        """
        word_lower = word.lower()
        if word_lower not in self.word_index:
            self.word_index[word_lower] = {}
        if command not in self.word_index[word_lower]:
            self.word_index[word_lower][command] = []
        self.word_index[word_lower][command].append(field_type)
    
    def _extract_words(self, text: str) -> List[str]:
        """
        从文本中提取有意义的词汇
        
        使用正则表达式从文本中提取中英文词汇，过滤掉太短的词汇。
        支持Unicode中文字符和英文字母数字的混合处理。
        
        Args:
            text (str): 要分析的文本
            
        Returns:
            List[str]: 提取出的词汇列表，已转为小写并过滤短词
        """
        if not text:
            return []
        # 使用正则表达式分割词汇，保留中英文字符和数字
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        # 过滤掉太短的词汇（小于2个字符）以减少噪声
        return [word for word in words if len(word) > 1]
    
    def search(self, query: str, 
              max_results: int = 20,
              include_fuzzy: bool = True) -> List[Dict[str, Any]]:
        """
        执行智能搜索
        
        综合使用多种搜索策略来查找相关命令，按相关性排序结果。
        搜索策略按优先级顺序执行：精确匹配 > 前缀匹配 > 词汇匹配 > 模糊匹配。
        
        Args:
            query (str): 搜索查询字符串
            max_results (int): 最大返回结果数，默认20
            include_fuzzy (bool): 是否包含模糊匹配，默认True
            
        Returns:
            List[Dict[str, Any]]: 排序后的搜索结果列表，每个结果包含：
                - command: 命令信息
                - match_type: 匹配类型
                - relevance_score: 相关性评分
                - match_field: 匹配字段
                - match_text: 匹配的文本
        """
        if not query.strip():
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        # 1. 精确匹配 - 最高优先级，命令名完全匹配
        exact_matches = self._exact_match_search(query_lower)
        results.extend(exact_matches)
        
        # 2. 前缀匹配 - 对于部分输入的命令名查找
        prefix_matches = self._prefix_match_search(query_lower)
        results.extend(prefix_matches)
        
        # 3. 词汇匹配 - 在所有字段中搜索关键词
        word_matches = self._word_match_search(query_lower)
        results.extend(word_matches)
        
        # 4. 模糊匹配 - 处理拼写错误和类似命令（如果启用）
        if include_fuzzy:
            fuzzy_matches = self._fuzzy_match_search(query_lower)
            results.extend(fuzzy_matches)
        
        # 去重并按相关性排序
        unique_results = self._deduplicate_and_rank(results, query_lower)
        
        return unique_results[:max_results]
    
    def _exact_match_search(self, query: str) -> List[Dict[str, Any]]:
        """
        精确匹配搜索
        
        查找命令名与查询字符串完全匹配的命令。这种匹配具有最高的
        相关性分数，通常用于用户明确知道命令名称的情况。
        
        Args:
            query (str): 已转为小写的查询字符串
            
        Returns:
            List[Dict[str, Any]]: 精确匹配的结果列表
        """
        results = []
        
        # 命令名精确匹配 - 最高优先级的匹配类型
        if query in self.command_index:
            results.append({
                'command': self.command_index[query],
                'match_type': 'exact_name',
                'relevance_score': 100,  # 精确匹配给予最高分数
                'match_field': 'name',
                'match_text': query
            })
        
        return results
    
    def _prefix_match_search(self, query: str) -> List[Dict[str, Any]]:
        """
        前缀匹配搜索
        
        查找以查询字符串为前缀的所有命令。这种匹配对于用户记得
        命令名开头但不记得完整名称的情况非常有用。
        
        Args:
            query (str): 已转为小写的查询字符串
            
        Returns:
            List[Dict[str, Any]]: 前缀匹配的结果列表
        """
        results = []
        
        # 遍历所有命令名，查承前缀匹配
        for cmd_name in self.command_index:
            if cmd_name.lower().startswith(query):
                results.append({
                    'command': self.command_index[cmd_name],
                    'match_type': 'prefix_name',
                    'relevance_score': 90,  # 前缀匹配给予较高分数
                    'match_field': 'name',
                    'match_text': cmd_name
                })
        
        return results
    
    def _word_match_search(self, query: str) -> List[Dict[str, Any]]:
        """
        词汇匹配搜索
        
        在所有索引字段中搜索包含查询词汇的命令。这是最灵活的搜索方式，
        能够根据描述、分类、相关命令等信息查找相关命令。支持多词查询。
        
        Args:
            query (str): 已转为小写的查询字符串
            
        Returns:
            List[Dict[str, Any]]: 词汇匹配的结果列表
        """
        results = []
        query_words = self._extract_words(query)
        
        if not query_words:
            return results
        
        # 为每个查询词汇在索引中搜索
        for word in query_words:
            if word in self.word_index:
                for cmd_name, field_types in self.word_index[word].items():
                    command = self.command_index[cmd_name]
                    
                    # 根据匹配字段类型计算相关性分数
                    for field_type in field_types:
                        score = self._calculate_field_score(field_type, word, command)
                        results.append({
                            'command': command,
                            'match_type': f'word_{field_type}',
                            'relevance_score': score,
                            'match_field': field_type,
                            'match_text': word
                        })
        
        return results
    
    def _fuzzy_match_search(self, query: str) -> List[Dict[str, Any]]:
        """
        模糊匹配搜索
        
        使用字符串相似度算法查找与查询相似的命令名。这种方法可以
        处理用户输入错误或记忆不清的情况，提供容错能力。
        
        Args:
            query (str): 已转为小写的查询字符串
            
        Returns:
            List[Dict[str, Any]]: 模糊匹配的结果列表
        """
        results = []
        threshold = 0.6  # 相似度阈值，只返回超过此阈值的结果
        
        # 遍历所有命令名，计算与查询的相似度
        for cmd_name in self.command_index:
            # 使用SequenceMatcher计算字符串相似度
            similarity = SequenceMatcher(None, query, cmd_name.lower()).ratio()
            if similarity >= threshold:
                score = int(similarity * 70)  # 模糊匹配的分数相对较低
                results.append({
                    'command': self.command_index[cmd_name],
                    'match_type': 'fuzzy_name',
                    'relevance_score': score,
                    'match_field': 'name',
                    'match_text': cmd_name,
                    'similarity': similarity  # 保存相似度信息供调试使用
                })
        
        return results
    
    def _calculate_field_score(self, field_type: str, word: str, 
                              command: Dict[str, Any]) -> int:
        """
        根据字段类型和匹配情况计算相关性分数
        
        不同字段的匹配具有不同的重要性，命令名匹配最重要，描述其次，
        分类、相关命令和选项说明依次递减。同时考虑匹配的精确度。
        
        Args:
            field_type (str): 字段类型（name/description/category/related/option）
            word (str): 匹配的词汇
            command (Dict[str, Any]): 命令信息
            
        Returns:
            int: 计算后的相关性分数
        """
        # 定义不同字段类型的基础分数
        base_scores = {
            'name': 80,        # 命令名匹配最重要
            'description': 60, # 描述匹配次之
            'category': 50,    # 分类匹配中等重要
            'related': 40,     # 相关命令匹配
            'option': 30       # 选项说明匹配最低
        }
        
        base_score = base_scores.get(field_type, 20)
        
        # 根据词汇在命令名中的匹配情况进行额外加分
        if field_type == 'name':
            cmd_name = command['name'].lower()
            if word == cmd_name:
                return base_score + 20  # 完全匹配加分
            elif cmd_name.startswith(word):
                return base_score + 10  # 前缀匹配加分
        
        return base_score
    
    def _deduplicate_and_rank(self, results: List[Dict[str, Any]], 
                             query: str) -> List[Dict[str, Any]]:
        """
        去除重复结果并按相关性排序
        
        由于多种搜索策略可能返回相同的命令，需要去除重复并保留最高分数。
        最终按相关性分数和使用频率进行排序。
        
        Args:
            results (List[Dict[str, Any]]): 原始搜索结果列表
            query (str): 查询字符串（用于额外的相关性评估）
            
        Returns:
            List[Dict[str, Any]]: 去重并排序后的结果列表
        """
        # 按命令名去重，保留最高分的结果
        command_scores = {}
        command_matches = {}
        
        for result in results:
            cmd_name = result['command']['name']
            score = result['relevance_score']
            
            # 如果该命令之前没有出现过，或者当前分数更高，则更新
            if cmd_name not in command_scores or score > command_scores[cmd_name]:
                command_scores[cmd_name] = score
                command_matches[cmd_name] = result
        
        # 按相关性分数和使用频率进行排序
        sorted_results = sorted(
            command_matches.values(),
            key=lambda x: (x['relevance_score'], self._get_usage_boost(x['command'])),
            reverse=True
        )
        
        return sorted_results
    
    def _get_usage_boost(self, command: Dict[str, Any]) -> int:
        """
        根据命令的使用频率给予分数提升
        
        对于常用命令给予额外的分数提升，使其在搜索结果中排名更靠前。
        这有助于提高用户体验，让最常用的命令更容易被找到。
        
        Args:
            command (Dict[str, Any]): 命令信息字典
            
        Returns:
            int: 使用频率加分（0-10分）
        """
        # 定义高频使用命令列表（可以根据实际使用统计调整）
        high_freq_commands = ['ls', 'cd', 'cp', 'mv', 'rm', 'cat', 'grep', 'find', 'chmod', 'chown']
        if command['name'] in high_freq_commands:
            return 10  # 高频命令给予额外加分
        return 0
    
    def suggest_commands(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        命令建议功能（自动完成）
        
        根据部分输入提供命令名称建议，用于实现自动完成功能。
        首先查找前缀匹配，如果结果不够再查找包含匹配。
        
        Args:
            partial_query (str): 部分命令名输入
            limit (int): 最大返回建议数量，默认5
            
        Returns:
            List[str]: 排序后的命令名建议列表
        """
        if not partial_query:
            return []
        
        partial_lower = partial_query.lower()
        suggestions = []
        
        # 首先查找前缀匹配，这些通常是用户最想要的结果
        for cmd_name in self.command_index:
            if cmd_name.lower().startswith(partial_lower):
                suggestions.append(cmd_name)
        
        # 如果前缀匹配结果不够，查找包含匹配
        if len(suggestions) < limit:
            for cmd_name in self.command_index:
                if (partial_lower in cmd_name.lower() and 
                    cmd_name not in suggestions):
                    suggestions.append(cmd_name)
        
        # 按字母顺序排序并限制数量
        return sorted(suggestions)[:limit]
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        获取搜索引擎统计信息
        
        返回关于搜索引擎当前状态的统计信息，包括索引的命令数量、
        词汇数量、支持的字段类型和搜索策略等。用于系统监控和调试。
        
        Returns:
            Dict[str, Any]: 包含统计信息的字典
        """
        return {
            'total_commands': len(self.command_index),
            'total_words': len(self.word_index),
            'indexed_fields': ['name', 'description', 'category', 'related', 'option'],
            'search_strategies': ['exact', 'prefix', 'word', 'fuzzy']
        }

class AdvancedSearchEngine(SearchEngine):
    """
    高级搜索引擎，支持更复杂的查询
    
    在基础搜索引擎的基础上扩展了高级功能，包括：
    - 多维度搜索过滤（按分类、难度等）
    - 多种排序方式（相关性、名称、分类）
    - 结合分类数据的智能筛选
    
    该类继承了SearchEngine的所有基础功能，并添加了更复杂的查询处理能力。
    
    Attributes:
        categories_file (Path): 分类数据文件路径
        categories_data (Dict): 加载的分类数据
    """
    
    def __init__(self, commands_file: str, categories_file: str):
        """
        初始化高级搜索引擎
        
        在基础搜索引擎的基础上加载分类数据，以支持更高级的过滤和排序功能。
        
        Args:
            commands_file (str): 命令数据JSON文件路径
            categories_file (str): 分类数据JSON文件路径
        """
        super().__init__(commands_file)
        self.categories_file = Path(categories_file)
        self.categories_data = self._load_categories()
    
    def _load_categories(self) -> Dict[str, Any]:
        """
        加载分类数据
        
        读取分类配置文件，包含命令的分类信息、难度等级划分等。
        如果文件不存在或格式错误，返回空字典以保证程序的稳定性。
        
        Returns:
            Dict[str, Any]: 分类数据字典，如果加载失败则返回空字典
        """
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 分类文件不存在时返回空字典，不影响基础搜索功能
            return {}
        except json.JSONDecodeError:
            # JSON格式错误时也返回空字典
            return {}
    
    def advanced_search(self, query: str, 
                       filters: Optional[Dict[str, str]] = None,
                       sort_by: str = 'relevance') -> List[Dict[str, Any]]:
        """
        高级搜索，支持过滤和排序
        
        在基础搜索的基础上添加高级过滤和排序功能。用户可以指定多种
        过滤条件来缩小搜索范围，并选择不同的排序方式。
        
        Args:
            query (str): 搜索查询字符串
            filters (Optional[Dict[str, str]]): 过滤条件，支持的键包括：
                - 'category': 按分类过滤
                - 'difficulty': 按难度过滤
            sort_by (str): 排序方式，可选'relevance'、'name'、'category'
            
        Returns:
            List[Dict[str, Any]]: 过滤和排序后的搜索结果
        """
        # 执行基础搜索获取初始结果
        results = self.search(query)
        
        # 应用高级过滤器缩小结果范围
        if filters:
            results = self._apply_search_filters(results, filters)
        
        # 应用指定的排序方式
        if sort_by != 'relevance':
            results = self._sort_search_results(results, sort_by)
        
        return results
    
    def _apply_search_filters(self, results: List[Dict[str, Any]], 
                             filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        应用高级搜索过滤器
        
        根据用户指定的过滤条件筛选搜索结果。支持按分类和难度等级进行
        过滤，多个过滤条件可以同时使用。
        
        Args:
            results (List[Dict[str, Any]]): 原始搜索结果
            filters (Dict[str, str]): 过滤条件字典
            
        Returns:
            List[Dict[str, Any]]: 过滤后的结果列表
        """
        filtered_results = results
        
        # 按分类过滤 - 只保留属于指定分类的命令
        if 'category' in filters:
            category = filters['category']
            filtered_results = [
                r for r in filtered_results
                if category in r['command'].get('categories', [])
            ]
        
        # 按难度过滤 - 只保留指定难度等级的命令
        if 'difficulty' in filters:
            difficulty = filters['difficulty']
            difficulty_commands = set()
            if difficulty in self.categories_data.get('difficulty_levels', {}):
                difficulty_commands = set(
                    self.categories_data['difficulty_levels'][difficulty]
                )
            
            filtered_results = [
                r for r in filtered_results
                if r['command']['name'] in difficulty_commands
            ]
        
        return filtered_results
    
    def _sort_search_results(self, results: List[Dict[str, Any]], 
                            sort_by: str) -> List[Dict[str, Any]]:
        """
        排序搜索结果
        
        根据指定的排序方式对搜索结果进行重新排序。除了默认的相关性排序外，
        还支持按命令名和分类排序。
        
        Args:
            results (List[Dict[str, Any]]): 待排序的搜索结果
            sort_by (str): 排序方式（'name'或'category'）
            
        Returns:
            List[Dict[str, Any]]: 排序后的结果列表
        """
        if sort_by == 'name':
            # 按命令名字母顺序排序
            return sorted(results, key=lambda x: x['command']['name'])
        elif sort_by == 'category':
            # 按主分类名称排序（取第一个分类）
            return sorted(results, 
                         key=lambda x: x['command'].get('categories', [''])[0])
        else:
            # 不支持的排序方式，返回原始结果
            return results

def main():
    """
    搜索引擎模块测试函数
    
    提供对搜索引擎功能的全面测试，包括：
    1. 不同类型的搜索测试（精确、前缀、词汇、模糊匹配）
    2. 中英文混合搜索测试
    3. 命令建议功能测试
    4. 搜索统计信息显示
    
    这个测试函数帮助开发者验证搜索引擎的各项功能是否正常工作。
    """
    import os
    
    # 获取数据文件的路径 - 相对于当前模块文件的位置
    current_dir = Path(__file__).parent
    commands_file = current_dir.parent / 'data' / 'commands.json'
    categories_file = current_dir.parent / 'data' / 'categories.json'
    
    try:
        # 创建高级搜索引擎实例
        engine = AdvancedSearchEngine(str(commands_file), str(categories_file))
        
        print("=== 搜索引擎测试 ===")
        
        # 测试不同类型的搜索
        test_queries = [
            'ls',           # 精确匹配 - 应该找到ls命令
            'cop',          # 前缀匹配 - 应该找到cp命令
            'file',         # 词汇匹配 - 在描述中搜索
            '文件',         # 中文搜索 - 测试中文支持
            'remove',       # 描述匹配 - 应该找到rm等命令
            'lss'           # 模糊匹配 - 应该找到ls命令
        ]
        
        for query in test_queries:
            print(f"\n搜索: '{query}'")
            results = engine.search(query, max_results=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    cmd = result['command']
                    print(f"  {i}. {cmd['name']}: {cmd['description']}")
                    print(f"     匹配类型: {result['match_type']}, "
                          f"相关度: {result['relevance_score']}")
            else:
                print("  未找到匹配结果")
        
        # 测试命令建议功能
        print(f"\n命令建议 ('gr'):")
        suggestions = engine.suggest_commands('gr')
        print(f"  建议: {suggestions}")
        
        # 测试搜索统计信息
        print(f"\n搜索统计:")
        stats = engine.get_search_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    # 仅在直接运行此文件时执行测试函数
    main()