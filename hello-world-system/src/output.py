# -*- coding: utf-8 -*-
"""
输出处理模块
负责多格式输出支持和显示管理
"""

import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
from typing import Dict, Any, Optional
from datetime import datetime


class OutputManager:
    """输出管理器"""
    
    def __init__(self):
        """初始化输出管理器"""
        self.formatters = {
            'text': self._format_text,
            'json': self._format_json,
            'xml': self._format_xml
        }
        
        # ANSI 颜色代码
        self.colors = {
            'reset': '\033[0m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'bold': '\033[1m'
        }
    
    def format_output(self, message: Dict, format_type: str = 'text', 
                     enable_colors: bool = True) -> str:
        """
        格式化输出内容
        
        Args:
            message: 问候消息数据
            format_type: 输出格式类型
            enable_colors: 是否启用颜色
            
        Returns:
            格式化后的输出字符串
        """
        if format_type not in self.formatters:
            raise ValueError(f"不支持的输出格式: {format_type}")
        
        formatter = self.formatters[format_type]
        formatted_content = formatter(message)
        
        # 如果是文本格式且启用了颜色，添加颜色
        if format_type == 'text' and enable_colors and self._supports_color():
            formatted_content = self._add_colors(formatted_content, message)
        
        return formatted_content
    
    def _format_text(self, message: Dict) -> str:
        """
        格式化为文本输出
        
        Args:
            message: 消息数据
            
        Returns:
            格式化的文本
        """
        output_lines = []
        
        # 主要消息
        output_lines.append(message['message'])
        
        # 如果是详细模式，添加额外信息
        if message.get('verbose'):
            output_lines.append("")  # 空行
            output_lines.append("=== 详细信息 ===")
            output_lines.append(f"用户名: {message['name']}")
            output_lines.append(f"语言: {message['language']}")
            output_lines.append(f"时间戳: {message['timestamp']}")
            output_lines.append(f"模板: {message['template_used']}")
        
        return '\n'.join(output_lines)
    
    def _format_json(self, message: Dict) -> str:
        """
        格式化为JSON输出
        
        Args:
            message: 消息数据
            
        Returns:
            格式化的JSON字符串
        """
        # 构建JSON输出结构
        json_output = {
            "greeting": {
                "message": message['message'],
                "metadata": {
                    "name": message['name'],
                    "language": message['language'],
                    "timestamp": message['timestamp'],
                    "verbose": message['verbose'],
                    "template_used": message['template_used']
                },
                "system_info": {
                    "version": "1.0.0",
                    "format": "json",
                    "generated_at": datetime.now().isoformat()
                }
            }
        }
        
        return json.dumps(json_output, ensure_ascii=False, indent=2)
    
    def _format_xml(self, message: Dict) -> str:
        """
        格式化为XML输出
        
        Args:
            message: 消息数据
            
        Returns:
            格式化的XML字符串
        """
        # 创建根元素
        root = ET.Element("greeting")
        root.set("version", "1.0.0")
        root.set("format", "xml")
        root.set("generated_at", datetime.now().isoformat())
        
        # 添加消息元素
        message_elem = ET.SubElement(root, "message")
        message_elem.text = message['message']
        
        # 添加元数据
        metadata_elem = ET.SubElement(root, "metadata")
        
        name_elem = ET.SubElement(metadata_elem, "name")
        name_elem.text = message['name']
        
        language_elem = ET.SubElement(metadata_elem, "language")
        language_elem.text = message['language']
        
        timestamp_elem = ET.SubElement(metadata_elem, "timestamp")
        timestamp_elem.text = message['timestamp']
        
        verbose_elem = ET.SubElement(metadata_elem, "verbose")
        verbose_elem.text = str(message['verbose']).lower()
        
        template_elem = ET.SubElement(metadata_elem, "template_used")
        template_elem.text = message['template_used']
        
        # 转换为字符串并美化
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ").strip()
    
    def _add_colors(self, content: str, message: Dict) -> str:
        """
        为文本内容添加颜色
        
        Args:
            content: 原始文本内容
            message: 消息数据
            
        Returns:
            带颜色的文本内容
        """
        lines = content.split('\n')
        colored_lines = []
        
        for i, line in enumerate(lines):
            if i == 0:  # 主要问候消息
                if message['language'] == 'zh':
                    colored_line = f"{self.colors['green']}{self.colors['bold']}{line}{self.colors['reset']}"
                else:
                    colored_line = f"{self.colors['blue']}{self.colors['bold']}{line}{self.colors['reset']}"
            elif line.startswith("==="):  # 标题行
                colored_line = f"{self.colors['yellow']}{line}{self.colors['reset']}"
            elif ":" in line and not line.startswith("Current time"):  # 信息行
                parts = line.split(":", 1)
                if len(parts) == 2:
                    colored_line = f"{self.colors['cyan']}{parts[0]}:{self.colors['reset']}{parts[1]}"
                else:
                    colored_line = line
            else:
                colored_line = line
            
            colored_lines.append(colored_line)
        
        return '\n'.join(colored_lines)
    
    def _supports_color(self) -> bool:
        """
        检查终端是否支持颜色输出
        
        Returns:
            是否支持颜色
        """
        # 检查是否是终端
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # 检查环境变量
        import os
        term = os.environ.get('TERM', '')
        if term in ['dumb', '']:
            return False
        
        # 检查是否是Windows且未启用ANSI支持
        if sys.platform.startswith('win'):
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                # 在Windows上检查是否支持ANSI
                try:
                    import subprocess
                    result = subprocess.run(['where', 'cmd'], capture_output=True)
                    return result.returncode == 0
                except:
                    return False
        
        return True
    
    def display(self, content: str, output_file=None) -> None:
        """
        显示输出内容
        
        Args:
            content: 要显示的内容
            output_file: 输出文件对象，默认为stdout
        """
        if output_file is None:
            output_file = sys.stdout
        
        try:
            print(content, file=output_file)
            output_file.flush()
        except UnicodeEncodeError:
            # 如果遇到编码问题，回退到ASCII
            print(content.encode('ascii', 'replace').decode('ascii'), file=output_file)
            output_file.flush()
        except Exception as e:
            # 最后的回退方案
            print(f"输出错误: {e}", file=sys.stderr)
    
    def save_to_file(self, content: str, filename: str) -> bool:
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名
            
        Returns:
            是否保存成功
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存文件失败: {e}", file=sys.stderr)
            return False


class OutputValidator:
    """输出验证器"""
    
    @staticmethod
    def validate_json(json_string: str) -> bool:
        """
        验证JSON格式是否正确
        
        Args:
            json_string: JSON字符串
            
        Returns:
            是否为有效JSON
        """
        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError:
            return False
    
    @staticmethod
    def validate_xml(xml_string: str) -> bool:
        """
        验证XML格式是否正确
        
        Args:
            xml_string: XML字符串
            
        Returns:
            是否为有效XML
        """
        try:
            ET.fromstring(xml_string)
            return True
        except ET.ParseError:
            return False