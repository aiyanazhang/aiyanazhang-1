#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令详情显示模块
负责显示Linux命令的详细信息，包括语法、参数、示例等
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re

class CommandDetailManager:
    """命令详情管理器"""
    
    def __init__(self, commands_file: str):
        self.commands_file = Path(commands_file)
        self.commands_data = self._load_commands()
        self.command_index = self._build_command_index()
    
    def _load_commands(self) -> Dict[str, Any]:
        """加载命令数据"""
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"命令数据文件未找到: {self.commands_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"命令数据文件格式错误: {e}")
    
    def _build_command_index(self) -> Dict[str, Dict[str, Any]]:
        """构建命令索引"""
        index = {}
        for cmd in self.commands_data['commands']:
            index[cmd['name']] = cmd
        return index
    
    def get_command_detail(self, command_name: str) -> Optional[Dict[str, Any]]:
        """获取指定命令的详细信息"""
        return self.command_index.get(command_name)
    
    def command_exists(self, command_name: str) -> bool:
        """检查命令是否存在"""
        return command_name in self.command_index
    
    def get_similar_commands(self, command_name: str, limit: int = 5) -> List[str]:
        """获取相似命令建议"""
        if command_name in self.command_index:
            return []
        
        suggestions = []
        command_lower = command_name.lower()
        
        # 查找前缀匹配
        for cmd_name in self.command_index:
            if cmd_name.lower().startswith(command_lower):
                suggestions.append(cmd_name)
        
        # 查找包含匹配
        if len(suggestions) < limit:
            for cmd_name in self.command_index:
                if (command_lower in cmd_name.lower() and 
                    cmd_name not in suggestions):
                    suggestions.append(cmd_name)
        
        # 查找编辑距离相近的命令
        if len(suggestions) < limit:
            from difflib import get_close_matches
            close_matches = get_close_matches(
                command_name, 
                self.command_index.keys(), 
                n=limit-len(suggestions), 
                cutoff=0.6
            )
            suggestions.extend(close_matches)
        
        return suggestions[:limit]

class CommandDetailFormatter:
    """命令详情格式化器"""
    
    def __init__(self, detail_manager: CommandDetailManager):
        self.detail_manager = detail_manager
    
    def format_command_detail(self, command_name: str, 
                             style: str = 'full') -> Dict[str, Any]:
        """格式化命令详情"""
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
        """完整格式化"""
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
        """简要格式化"""
        return {
            'name': command['name'],
            'description': command.get('description', ''),
            'syntax': command.get('syntax', ''),
            'categories': command.get('categories', [])
        }
    
    def _format_syntax_only(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """仅语法格式化"""
        return {
            'name': command['name'],
            'syntax': self._format_syntax(command),
            'options': self._format_options(command, brief=True)
        }
    
    def _format_syntax(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """格式化语法信息"""
        syntax = command.get('syntax', '')
        
        # 解析语法组件
        components = self._parse_syntax_components(syntax)
        
        return {
            'basic': syntax,
            'components': components,
            'explanation': self._explain_syntax(syntax)
        }
    
    def _parse_syntax_components(self, syntax: str) -> Dict[str, List[str]]:
        """解析语法组件"""
        components = {
            'command': [],
            'required_args': [],
            'optional_args': [],
            'flags': []
        }
        
        if not syntax:
            return components
        
        # 简单的语法解析（可以根据需要扩展）
        parts = syntax.split()
        
        if parts:
            components['command'] = [parts[0]]
        
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
        """解释语法含义"""
        if not syntax:
            return ""
        
        explanations = []
        
        if '[选项]' in syntax:
            explanations.append("[] 表示可选参数")
        if '...' in syntax:
            explanations.append("... 表示可以指定多个参数")
        if '|' in syntax:
            explanations.append("| 表示可选的参数之一")
        
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
    """命令比较工具"""
    
    def __init__(self, detail_manager: CommandDetailManager):
        self.detail_manager = detail_manager
    
    def compare_commands(self, command1: str, command2: str) -> Dict[str, Any]:
        """比较两个命令"""
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
    """测试函数"""
    import os
    
    # 获取数据文件的路径
    current_dir = Path(__file__).parent
    commands_file = current_dir.parent / 'data' / 'commands.json'
    
    try:
        # 创建详情管理器
        manager = CommandDetailManager(str(commands_file))
        formatter = CommandDetailFormatter(manager)
        comparison = CommandComparison(manager)
        
        print("=== 命令详情测试 ===")
        
        # 测试命令详情
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
        
        # 测试命令比较
        print(f"\n--- 命令比较: cp vs mv ---")
        comp = comparison.compare_commands('cp', 'mv')
        if 'error' not in comp:
            print(f"相似之处: {comp['similarities']}")
            print(f"建议: {comp['recommendation']}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    main()