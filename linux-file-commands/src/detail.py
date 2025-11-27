#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令详情显示模块

本模块负责显示Linux文件操作命令的详细信息，提供全面的命令参考功能。
主要功能包括：
- 命令详细信息展示（语法、参数、示例、安全提示等）
- 多种显示模式（完整、简要、语法专用）
- 智能的命令相似性建议和错误处理
- 命令间的对比分析功能
- 详细的语法解析和解释
- 使用示例的智能分析和分类

作者: AI Assistant
版本: 1.0
创建时间: 2024
最后修改: 2025-09-25
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re

class CommandDetailManager:
    """
    命令详情管理器
    
    负责加载和管理Linux命令的详细信息，提供命令查询、验证和相似性建议功能。
    该类是整个详情显示系统的数据层，为上层的格式化和显示组件提供数据支持。
    
    Attributes:
        commands_file (Path): 命令数据文件路径
        commands_data (Dict): 加载的命令数据
        command_index (Dict): 按命令名索引的字典，用于快速查找
    """
    
    def __init__(self, commands_file: str):
        """
        初始化命令详情管理器
        
        加载命令数据并构建索引，为后续的命令查询和详情展示做准备。
        
        Args:
            commands_file (str): 命令数据JSON文件的路径
            
        Raises:
            FileNotFoundError: 当命令数据文件不存在时
            ValueError: 当JSON文件格式错误时
        """
        self.commands_file = Path(commands_file)
        self.commands_data = self._load_commands()
        self.command_index = self._build_command_index()
    
    def _load_commands(self) -> Dict[str, Any]:
        """
        从JSON文件加载命令数据
        
        读取并解析包含所有Linux文件操作命令详细信息的JSON文件。
        文件应包含命令的完整信息，包括语法、参数、示例、安全提示等。
        
        Returns:
            Dict[str, Any]: 包含所有命令详细信息的字典
            
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
    
    def _build_command_index(self) -> Dict[str, Dict[str, Any]]:
        """
        构建命令索引
        
        为所有命令创建一个按名称索引的字典，以实现O(1)的命令查找效率。
        这个索引是整个详情系统的核心数据结构。
        
        Returns:
            Dict[str, Dict[str, Any]]: 命令名到命令详细信息的映射
        """
        index = {}
        # 为每个命令建立名称到详细信息的映射
        for cmd in self.commands_data['commands']:
            index[cmd['name']] = cmd
        return index
    
    def get_command_detail(self, command_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定命令的详细信息
        
        根据命令名称获取完整的命令信息，包括语法、参数、示例、
        分类、相关命令等所有可用信息。
        
        Args:
            command_name (str): 要查询的命令名称
            
        Returns:
            Optional[Dict[str, Any]]: 命令详细信息字典，如果命令不存在则返回None
        """
        return self.command_index.get(command_name)
    
    def command_exists(self, command_name: str) -> bool:
        """
        检查命令是否存在
        
        快速检查指定的命令名是否在系统的命令数据库中。
        这个方法通常用于输入验证和错误处理。
        
        Args:
            command_name (str): 要检查的命令名称
            
        Returns:
            bool: 命令存在返回True，不存在返回False
        """
        return command_name in self.command_index
    
    def get_similar_commands(self, command_name: str, limit: int = 5) -> List[str]:
        """
        获取相似命令建议
        
        当用户输入不存在的命令名时，提供可能的替代建议。使用多种策略：
        1. 前缀匹配 - 查找以相同字符开头的命令
        2. 包含匹配 - 查找包含输入字符的命令
        3. 编辑距离 - 使用模糊匹配查找相似命令
        
        Args:
            command_name (str): 用户输入的命令名
            limit (int): 最大返回建议数量，默认5
            
        Returns:
            List[str]: 相似命令名称列表，按相似度排序
        """
        if command_name in self.command_index:
            return []  # 命令存在时不需要建议
        
        suggestions = []
        command_lower = command_name.lower()
        
        # 查找前缀匹配 - 最可能的建议
        for cmd_name in self.command_index:
            if cmd_name.lower().startswith(command_lower):
                suggestions.append(cmd_name)
        
        # 查找包含匹配 - 扩大搜索范围
        if len(suggestions) < limit:
            for cmd_name in self.command_index:
                if (command_lower in cmd_name.lower() and 
                    cmd_name not in suggestions):
                    suggestions.append(cmd_name)
        
        # 查找编辑距离相近的命令 - 处理拼写错误
        if len(suggestions) < limit:
            from difflib import get_close_matches
            close_matches = get_close_matches(
                command_name, 
                self.command_index.keys(), 
                n=limit-len(suggestions), 
                cutoff=0.6  # 相似度阈值
            )
            suggestions.extend(close_matches)
        
        return suggestions[:limit]

class CommandDetailFormatter:
    """
    命令详情格式化器
    
    负责将命令的原始数据格式化为用户友好的显示形式。提供多种显示模式，
    满足不同场景的需求：从简单的命令查询到详细的学习指南。该类还包含
    智能的语法解析、示例解释和附加信息生成功能。
    
    Attributes:
        detail_manager (CommandDetailManager): 关联的详情管理器实例
    """
    
    def __init__(self, detail_manager: CommandDetailManager):
        self.detail_manager = detail_manager
    
    def format_command_detail(self, command_name: str, 
                             style: str = 'full') -> Dict[str, Any]:
        """
        格式化命令详情
        
        根据指定的样式格式化命令详情。支持多种显示模式以适应不同的使用场景。
        如果命令不存在，会提供错误信息和相似命令建议。
        
        Args:
            command_name (str): 要格式化的命令名
            style (str): 显示样式，可选值：
                - 'full': 完整详细信息（默认）
                - 'brief': 简要信息
                - 'syntax': 仅语法信息
        
        Returns:
            Dict[str, Any]: 格式化后的命令信息或错误信息
        """
        command = self.detail_manager.get_command_detail(command_name)
        
        if not command:
            return {
                'error': f"命令 '{command_name}' 未找到",
                'suggestions': self.detail_manager.get_similar_commands(command_name)
            }
        
        if style == 'brief':
            return self._format_brief(command)
        elif style == 'syntax':
            return self._format_syntax_only(command)
        else:  # full
            return self._format_full(command)
    
    def _format_full(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整格式化命令详情
        
        生成包含所有可用信息的完整命令详情，包括基本信息、语法、
        选项、示例、相关命令和安全提示等。这是最详细的显示模式。
        
        Args:
            command (Dict[str, Any]): 命令原始数据
            
        Returns:
            Dict[str, Any]: 完整的格式化命令详情
        """
        result = {
            'name': command['name'],
            'description': command.get('description', ''),
            'categories': command.get('categories', []),
            'syntax': self._format_syntax(command),
            'options': self._format_options(command),
            'examples': self._format_examples(command),
            'related_commands': command.get('related_commands', []),
            'safety_tips': command.get('safety_tips', ''),
            'additional_info': self._generate_additional_info(command)
        }
        
        return result
    
    def _format_brief(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        简要格式化命令详情
        
        生成包含基本信息的简化版命令详情，适用于快速查阅和概览。
        只包含最关键的信息：命令名、描述、基本语法和分类。
        
        Args:
            command (Dict[str, Any]): 命令原始数据
            
        Returns:
            Dict[str, Any]: 简要的格式化命令详情
        """
        return {
            'name': command['name'],
            'description': command.get('description', ''),
            'syntax': command.get('syntax', ''),
            'categories': command.get('categories', [])
        }
    
    def _format_syntax_only(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        仅语法格式化
        
        生成专注于命令语法的详情，包括详细的语法解析和主要选项。
        适用于需要快速了解命令用法的场景。
        
        Args:
            command (Dict[str, Any]): 命令原始数据
            
        Returns:
            Dict[str, Any]: 以语法为主的格式化命令详情
        """
        return {
            'name': command['name'],
            'syntax': self._format_syntax(command),
            'options': self._format_options(command, brief=True)
        }
    
    def _format_syntax(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化语法信息
        
        解析和格式化命令的语法信息，将原始语法字符串分解为结构化的组件，
        并提供详细的解释说明。帮助用户理解命令的参数结构。
        
        Args:
            command (Dict[str, Any]): 命令原始数据
            
        Returns:
            Dict[str, Any]: 包含基本语法、组件分析和解释的字典
        """
        syntax = command.get('syntax', '')
        
        # 解析语法组件
        components = self._parse_syntax_components(syntax)
        
        return {
            'basic': syntax,
            'components': components,
            'explanation': self._explain_syntax(syntax)
        }
    
    def _parse_syntax_components(self, syntax: str) -> Dict[str, List[str]]:
        """
        解析语法组件
        
        将命令语法字符串分解为不同的组件类型，包括命令名、必需参数、
        可选参数和标志。使用正则表达式和模式匹配来识别不同的语法元素。
        
        Args:
            syntax (str): 原始命令语法字符串
            
        Returns:
            Dict[str, List[str]]: 按类型分组的语法组件
        """
        components = {
            'command': [],
            'required_args': [],
            'optional_args': [],
            'flags': []
        }
        
        if not syntax:
            return components
        
        # 简单的语法解析（可以根据需要扩展为更复杂的解析器）
        parts = syntax.split()
        
        if parts:
            components['command'] = [parts[0]]  # 第一部分通常是命令名
        
        # 查找可选参数（用[]包围）
        optional_pattern = r'\[([^\]]+)\]'
        optional_matches = re.findall(optional_pattern, syntax)
        components['optional_args'] = optional_matches
        
        # 查找必需参数（不在[]中的参数）
        required_pattern = r'(?<!\[)\b(?!选项|文件|目录|命令)[A-Z_]+(?!\])'
        required_matches = re.findall(required_pattern, syntax)
        components['required_args'] = required_matches
        
        return components
    
    def _explain_syntax(self, syntax: str) -> str:
        """
        解释语法含义
        
        根据语法中的特殊字符和符号生成人类可读的解释说明。
        帮助用户理解命令语法中的约定和符号含义。
        
        Args:
            syntax (str): 命令语法字符串
            
        Returns:
            str: 语法解释文本
        """
        if not syntax:
            return ""
        
        explanations = []
        
        # 根据语法中的常见符号提供解释
        if '[选项]' in syntax:
            explanations.append("[] 表示可选参数")
        if '...' in syntax:
            explanations.append("... 表示可以指定多个参数")
        if '|' in syntax:
            explanations.append("| 表示可选的参数之一")
        if '<' in syntax and '>' in syntax:
            explanations.append("<> 表示必需参数")
        
        return "; ".join(explanations)
    
    def _format_options(self, command: Dict[str, Any], 
                       brief: bool = False) -> List[Dict[str, Any]]:
        """格式化选项信息"""
        options = command.get('common_options', [])
        
        if brief:
            return [
                {'option': opt.get('option', ''), 'description': opt.get('description', '')}
                for opt in options[:5]  # 只显示前5个选项
            ]
        
        formatted_options = []
        for opt in options:
            formatted_opt = {
                'option': opt.get('option', ''),
                'description': opt.get('description', ''),
                'usage_example': self._generate_option_example(
                    command['name'], opt.get('option', '')
                )
            }
            formatted_options.append(formatted_opt)
        
        return formatted_options
    
    def _generate_option_example(self, command_name: str, option: str) -> str:
        """生成选项使用示例"""
        if not option:
            return ""
        
        # 基于命令和选项生成简单示例
        examples = {
            ('ls', '-l'): 'ls -l /home/user',
            ('ls', '-a'): 'ls -a',
            ('cp', '-r'): 'cp -r source_dir dest_dir',
            ('cp', '-i'): 'cp -i file1.txt file2.txt',
            ('find', '-name'): "find /path -name '*.txt'",
            ('grep', '-r'): "grep -r 'pattern' /path",
            ('chmod', '-R'): 'chmod -R 755 /path'
        }
        
        return examples.get((command_name, option), f"{command_name} {option}")
    
    def _format_examples(self, command: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化示例"""
        examples = command.get('examples', [])
        
        formatted_examples = []
        for i, example in enumerate(examples, 1):
            formatted_example = {
                'number': i,
                'command': example,
                'explanation': self._explain_example(command['name'], example),
                'use_case': self._determine_use_case(example)
            }
            formatted_examples.append(formatted_example)
        
        return formatted_examples
    
    def _explain_example(self, command_name: str, example: str) -> str:
        """解释示例的作用"""
        # 基于命令和示例内容生成解释
        explanations = {
            'ls -la': '以长格式显示所有文件（包括隐藏文件）',
            'ls -lh': '以易读格式显示文件大小',
            'cp -r': '递归复制目录',
            'cp -i': '复制时如果目标文件存在会询问是否覆盖',
            'find . -name': '在当前目录下按文件名搜索',
            'grep -r': '递归搜索目录中的文本'
        }
        
        # 查找匹配的解释
        for pattern, explanation in explanations.items():
            if pattern in example:
                return explanation
        
        # 默认解释
        return f"执行 {command_name} 命令的示例用法"
    
    def _determine_use_case(self, example: str) -> str:
        """确定使用场景"""
        if '/home' in example or '~' in example:
            return '用户目录操作'
        elif '/var/log' in example:
            return '日志文件操作'
        elif '/etc' in example:
            return '系统配置操作'
        elif '/tmp' in example:
            return '临时文件操作'
        elif '*.txt' in example or '*.log' in example:
            return '文件类型过滤'
        else:
            return '常规使用'
    
    def _generate_additional_info(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """生成附加信息"""
        info = {}
        
        # 命令类型判断
        command_name = command['name']
        if command_name in ['rm', 'rmdir', 'unlink']:
            info['type'] = '危险命令'
            info['warning'] = '此命令会删除文件，使用时请谨慎'
        elif command_name in ['cat', 'less', 'head', 'tail', 'grep']:
            info['type'] = '安全查看命令'
        elif command_name in ['chmod', 'chown', 'chgrp']:
            info['type'] = '权限管理命令'
            info['note'] = '需要适当权限才能执行'
        
        # 使用频率
        high_freq = ['ls', 'cd', 'cp', 'mv', 'rm', 'cat', 'grep']
        if command_name in high_freq:
            info['frequency'] = '高频使用'
        
        # 学习建议
        categories = command.get('categories', [])
        if '基础文件操作' in categories:
            info['learning_tip'] = '这是基础命令，建议优先掌握'
        
        return info

class CommandComparison:
    """
    命令比较工具
    
    提供两个或多个命令之间的对比分析功能。能够找出命令之间的相似性和差异，
    帮助用户理解不同命令的特点和使用场景，并提供选择建议。
    这对于学习和区分相似功能的命令非常有用。
    
    Attributes:
        detail_manager (CommandDetailManager): 关联的详情管理器实例
    """
    
    def __init__(self, detail_manager: CommandDetailManager):
        self.detail_manager = detail_manager
    
    def compare_commands(self, command1: str, command2: str) -> Dict[str, Any]:
        """
        比较两个命令
        
        对两个命令进行全面的对比分析，包括功能相似性、差异点、使用场景对比
        和使用建议。如果任一命令不存在，将返回错误信息。
        
        Args:
            command1 (str): 第一个要比较的命令名
            command2 (str): 第二个要比较的命令名
            
        Returns:
            Dict[str, Any]: 包含比较结果的详细报告或错误信息
        """
        cmd1 = self.detail_manager.get_command_detail(command1)
        cmd2 = self.detail_manager.get_command_detail(command2)
        
        if not cmd1 or not cmd2:
            return {
                'error': f"命令不存在: {command1 if not cmd1 else command2}"
            }
        
        comparison = {
            'commands': [command1, command2],
            'similarities': self._find_similarities(cmd1, cmd2),
            'differences': self._find_differences(cmd1, cmd2),
            'use_cases': self._compare_use_cases(cmd1, cmd2),
            'recommendation': self._generate_recommendation(cmd1, cmd2)
        }
        
        return comparison
    
    def _find_similarities(self, cmd1: Dict[str, Any], 
                          cmd2: Dict[str, Any]) -> List[str]:
        """找出相似之处"""
        similarities = []
        
        # 分类相似性
        categories1 = set(cmd1.get('categories', []))
        categories2 = set(cmd2.get('categories', []))
        common_categories = categories1.intersection(categories2)
        if common_categories:
            similarities.append(f"都属于分类: {', '.join(common_categories)}")
        
        # 相关命令
        related1 = set(cmd1.get('related_commands', []))
        related2 = set(cmd2.get('related_commands', []))
        if cmd1['name'] in related2 or cmd2['name'] in related1:
            similarities.append("互为相关命令")
        
        return similarities
    
    def _find_differences(self, cmd1: Dict[str, Any], 
                         cmd2: Dict[str, Any]) -> Dict[str, List[str]]:
        """找出不同之处"""
        differences = {
            cmd1['name']: [],
            cmd2['name']: []
        }
        
        # 功能描述差异
        desc1 = cmd1.get('description', '')
        desc2 = cmd2.get('description', '')
        if desc1 != desc2:
            differences[cmd1['name']].append(f"功能: {desc1}")
            differences[cmd2['name']].append(f"功能: {desc2}")
        
        return differences
    
    def _compare_use_cases(self, cmd1: Dict[str, Any], 
                          cmd2: Dict[str, Any]) -> Dict[str, str]:
        """比较使用场景"""
        return {
            cmd1['name']: f"适用于: {cmd1.get('description', '')}",
            cmd2['name']: f"适用于: {cmd2.get('description', '')}"
        }
    
    def _generate_recommendation(self, cmd1: Dict[str, Any], 
                               cmd2: Dict[str, Any]) -> str:
        """生成使用建议"""
        # 简单的建议逻辑，可以根据需要扩展
        name1, name2 = cmd1['name'], cmd2['name']
        
        recommendations = {
            ('cp', 'mv'): "cp用于复制文件，mv用于移动或重命名文件",
            ('cat', 'less'): "cat适合查看小文件，less适合查看大文件",
            ('find', 'locate'): "find实时搜索，locate基于数据库快速搜索"
        }
        
        key = tuple(sorted([name1, name2]))
        return recommendations.get(key, "建议根据具体需求选择合适的命令")

def main():
    """
    命令详情模块测试函数
    
    提供对命令详情管理和显示功能的全面测试，包括：
    1. 命令详情查询和格式化测试
    2. 不同显示模式的测试
    3. 错误处理和相似命令建议测试
    4. 命令比较功能测试
    
    这个测试函数帮助开发者验证详情系统的各项功能是否正常工作。
    """
    import os
    
    # 获取数据文件的路径 - 相对于当前模块文件的位置
    current_dir = Path(__file__).parent
    commands_file = current_dir.parent / 'data' / 'commands.json'
    
    try:
        # 创建各个组件的实例
        manager = CommandDetailManager(str(commands_file))
        formatter = CommandDetailFormatter(manager)
        comparison = CommandComparison(manager)
        
        print("=== 命令详情测试 ===")
        
        # 测试命令详情显示
        test_commands = ['ls', 'grep', 'nonexistent']
        
        for cmd in test_commands:
            print(f"\n--- {cmd} 命令详情 ---")
            detail = formatter.format_command_detail(cmd, style='full')
            
            if 'error' in detail:
                print(f"错误: {detail['error']}")
                if 'suggestions' in detail:
                    print(f"建议: {detail['suggestions']}")
            else:
                print(f"名称: {detail['name']}")
                print(f"描述: {detail['description']}")
                print(f"分类: {', '.join(detail['categories'])}")
                print(f"语法: {detail['syntax']['basic']}")
                
                if detail['options']:
                    print("主要选项:")
                    for opt in detail['options'][:3]:  # 只显示前3个
                        print(f"  {opt['option']}: {opt['description']}")
                
                if detail['examples']:
                    print("使用示例:")
                    for ex in detail['examples'][:2]:  # 只显示前2个
                        print(f"  {ex['command']}")
                        print(f"    {ex['explanation']}")
        
        # 测试命令比较功能
        print(f"\n--- 命令比较: cp vs mv ---")
        comp = comparison.compare_commands('cp', 'mv')
        if 'error' not in comp:
            print(f"相似之处: {comp['similarities']}")
            print(f"建议: {comp['recommendation']}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    # 仅在直接运行此文件时执行测试函数
    main()