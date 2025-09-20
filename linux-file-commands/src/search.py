#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索引擎模块
实现命令搜索功能，支持多种搜索策略和相关性排序
"""

import re
import json
from typing import Dict, List, Optional, Set, Any, Tuple
from pathlib import Path
from difflib import SequenceMatcher
import math

class SearchEngine:
    """命令搜索引擎"""
    
    def __init__(self, commands_file: str):
        self.commands_file = Path(commands_file)
        self.commands_data = self._load_commands()
        self._build_search_index()
    
    def _load_commands(self) -> Dict[str, Any]:
        """加载命令数据"""
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"命令数据文件未找到: {self.commands_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"命令数据文件格式错误: {e}")
    
    def _build_search_index(self) -> None:
        """构建搜索索引"""
        self.command_index = {}
        self.word_index = {}
        
        for cmd in self.commands_data['commands']:
            cmd_name = cmd['name']
            self.command_index[cmd_name] = cmd
            
            # 索引命令名
            self._add_to_word_index(cmd_name, cmd_name, 'name')
            
            # 索引描述
            description = cmd.get('description', '')
            words = self._extract_words(description)
            for word in words:
                self._add_to_word_index(word, cmd_name, 'description')
            
            # 索引分类
            categories = cmd.get('categories', [])
            for category in categories:
                category_words = self._extract_words(category)
                for word in category_words:
                    self._add_to_word_index(word, cmd_name, 'category')
            
            # 索引相关命令
            related = cmd.get('related_commands', [])
            for rel_cmd in related:
                self._add_to_word_index(rel_cmd, cmd_name, 'related')
            
            # 索引选项和示例
            options = cmd.get('common_options', [])
            for option in options:
                opt_words = self._extract_words(option.get('description', ''))
                for word in opt_words:
                    self._add_to_word_index(word, cmd_name, 'option')
    
    def _add_to_word_index(self, word: str, command: str, field_type: str) -> None:
        """添加到词汇索引"""
        word_lower = word.lower()
        if word_lower not in self.word_index:
            self.word_index[word_lower] = {}
        if command not in self.word_index[word_lower]:
            self.word_index[word_lower][command] = []
        self.word_index[word_lower][command].append(field_type)
    
    def _extract_words(self, text: str) -> List[str]:
        """从文本中提取词汇"""
        if not text:
            return []
        # 使用正则表达式分割词汇，保留中英文字符
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        return [word for word in words if len(word) > 1]
    
    def search(self, query: str, 
              max_results: int = 20,
              include_fuzzy: bool = True) -> List[Dict[str, Any]]:
        """执行搜索"""
        if not query.strip():
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        # 1. 精确匹配
        exact_matches = self._exact_match_search(query_lower)
        results.extend(exact_matches)
        
        # 2. 前缀匹配
        prefix_matches = self._prefix_match_search(query_lower)
        results.extend(prefix_matches)
        
        # 3. 词汇匹配
        word_matches = self._word_match_search(query_lower)
        results.extend(word_matches)
        
        # 4. 模糊匹配（如果启用）
        if include_fuzzy:
            fuzzy_matches = self._fuzzy_match_search(query_lower)
            results.extend(fuzzy_matches)
        
        # 去重并按相关性排序
        unique_results = self._deduplicate_and_rank(results, query_lower)
        
        return unique_results[:max_results]
    
    def _exact_match_search(self, query: str) -> List[Dict[str, Any]]:
        """精确匹配搜索"""
        results = []
        
        # 命令名精确匹配
        if query in self.command_index:
            results.append({
                'command': self.command_index[query],
                'match_type': 'exact_name',
                'relevance_score': 100,
                'match_field': 'name',
                'match_text': query
            })
        
        return results
    
    def _prefix_match_search(self, query: str) -> List[Dict[str, Any]]:
        """前缀匹配搜索"""
        results = []
        
        for cmd_name in self.command_index:
            if cmd_name.lower().startswith(query):
                results.append({
                    'command': self.command_index[cmd_name],
                    'match_type': 'prefix_name',
                    'relevance_score': 90,
                    'match_field': 'name',
                    'match_text': cmd_name
                })
        
        return results
    
    def _word_match_search(self, query: str) -> List[Dict[str, Any]]:
        """词汇匹配搜索"""
        results = []
        query_words = self._extract_words(query)
        
        if not query_words:
            return results
        
        # 为每个查询词汇搜索
        for word in query_words:
            if word in self.word_index:
                for cmd_name, field_types in self.word_index[word].items():
                    command = self.command_index[cmd_name]
                    
                    # 根据匹配字段类型计算分数
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
        """模糊匹配搜索"""
        results = []
        threshold = 0.6  # 相似度阈值
        
        for cmd_name in self.command_index:
            # 命令名模糊匹配
            similarity = SequenceMatcher(None, query, cmd_name.lower()).ratio()
            if similarity >= threshold:
                score = int(similarity * 70)  # 模糊匹配的分数较低
                results.append({
                    'command': self.command_index[cmd_name],
                    'match_type': 'fuzzy_name',
                    'relevance_score': score,
                    'match_field': 'name',
                    'match_text': cmd_name,
                    'similarity': similarity
                })
        
        return results
    
    def _calculate_field_score(self, field_type: str, word: str, 
                              command: Dict[str, Any]) -> int:
        """根据字段类型计算匹配分数"""
        base_scores = {
            'name': 80,
            'description': 60,
            'category': 50,
            'related': 40,
            'option': 30
        }
        
        base_score = base_scores.get(field_type, 20)
        
        # 根据词汇长度和匹配度调整分数
        if field_type == 'name':
            cmd_name = command['name'].lower()
            if word == cmd_name:
                return base_score + 20
            elif cmd_name.startswith(word):
                return base_score + 10
        
        return base_score
    
    def _deduplicate_and_rank(self, results: List[Dict[str, Any]], 
                             query: str) -> List[Dict[str, Any]]:
        """去重并按相关性排序"""
        # 按命令名去重，保留最高分的结果
        command_scores = {}
        command_matches = {}
        
        for result in results:
            cmd_name = result['command']['name']
            score = result['relevance_score']
            
            if cmd_name not in command_scores or score > command_scores[cmd_name]:
                command_scores[cmd_name] = score
                command_matches[cmd_name] = result
        
        # 排序
        sorted_results = sorted(
            command_matches.values(),
            key=lambda x: (x['relevance_score'], self._get_usage_boost(x['command'])),
            reverse=True
        )
        
        return sorted_results
    
    def _get_usage_boost(self, command: Dict[str, Any]) -> int:
        """根据使用频率给予分数提升"""
        # 这里可以根据实际使用统计调整
        high_freq_commands = ['ls', 'cd', 'cp', 'mv', 'rm', 'cat', 'grep']
        if command['name'] in high_freq_commands:
            return 10
        return 0
    
    def suggest_commands(self, partial_query: str, limit: int = 5) -> List[str]:
        """命令建议（自动完成）"""
        if not partial_query:
            return []
        
        partial_lower = partial_query.lower()
        suggestions = []
        
        # 首先查找前缀匹配
        for cmd_name in self.command_index:
            if cmd_name.lower().startswith(partial_lower):
                suggestions.append(cmd_name)
        
        # 如果前缀匹配不够，查找包含匹配
        if len(suggestions) < limit:
            for cmd_name in self.command_index:
                if (partial_lower in cmd_name.lower() and 
                    cmd_name not in suggestions):
                    suggestions.append(cmd_name)
        
        return sorted(suggestions)[:limit]
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        return {
            'total_commands': len(self.command_index),
            'total_words': len(self.word_index),
            'indexed_fields': ['name', 'description', 'category', 'related', 'option'],
            'search_strategies': ['exact', 'prefix', 'word', 'fuzzy']
        }

class AdvancedSearchEngine(SearchEngine):
    """高级搜索引擎，支持更复杂的查询"""
    
    def __init__(self, commands_file: str, categories_file: str):
        super().__init__(commands_file)
        self.categories_file = Path(categories_file)
        self.categories_data = self._load_categories()
    
    def _load_categories(self) -> Dict[str, Any]:
        """加载分类数据"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def advanced_search(self, query: str, 
                       filters: Optional[Dict[str, str]] = None,
                       sort_by: str = 'relevance') -> List[Dict[str, Any]]:
        """高级搜索，支持过滤和排序"""
        # 执行基础搜索
        results = self.search(query)
        
        # 应用过滤器
        if filters:
            results = self._apply_search_filters(results, filters)
        
        # 应用排序
        if sort_by != 'relevance':
            results = self._sort_search_results(results, sort_by)
        
        return results
    
    def _apply_search_filters(self, results: List[Dict[str, Any]], 
                             filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """应用搜索过滤器"""
        filtered_results = results
        
        # 按分类过滤
        if 'category' in filters:
            category = filters['category']
            filtered_results = [
                r for r in filtered_results
                if category in r['command'].get('categories', [])
            ]
        
        # 按难度过滤
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
        """排序搜索结果"""
        if sort_by == 'name':
            return sorted(results, key=lambda x: x['command']['name'])
        elif sort_by == 'category':
            return sorted(results, 
                         key=lambda x: x['command'].get('categories', [''])[0])
        else:
            return results

def main():
    """测试函数"""
    import os
    
    # 获取数据文件的路径
    current_dir = Path(__file__).parent
    commands_file = current_dir.parent / 'data' / 'commands.json'
    categories_file = current_dir.parent / 'data' / 'categories.json'
    
    try:
        # 创建搜索引擎
        engine = AdvancedSearchEngine(str(commands_file), str(categories_file))
        
        print("=== 搜索引擎测试 ===")
        
        # 测试不同类型的搜索
        test_queries = [
            'ls',           # 精确匹配
            'cop',          # 前缀匹配（应该找到cp）
            'file',         # 词汇匹配
            '文件',         # 中文搜索
            'remove',       # 描述匹配
            'lss'           # 模糊匹配
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
        
        # 测试命令建议
        print(f"\n命令建议 ('gr'):")
        suggestions = engine.suggest_commands('gr')
        print(f"  建议: {suggestions}")
        
        # 测试统计信息
        print(f"\n搜索统计:")
        stats = engine.get_search_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    main()