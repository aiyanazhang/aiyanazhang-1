#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际应用演示模块

展示Python元组在实际应用场景中的使用
"""

import math
from collections import namedtuple
from typing import Tuple, List, Dict, Any
from utils.error_handler import ErrorHandler, InputValidator


class ApplicationDemo:
    """实际应用演示类"""
    
    def __init__(self):
        """初始化演示类"""
        self.db_records = (
            (1, '张三', 'zhangsan@email.com', '计算机科学', 85.5),
            (2, '李四', 'lisi@email.com', '数学', 92.0),
            (3, '王五', 'wangwu@email.com', '物理', 78.5),
            (4, '赵六', 'zhaoliu@email.com', '化学', 96.5)
        )
    
    def demonstrate_database_records(self) -> None:
        """演示数据库记录模拟"""
        self._print_section_header("🗄️  数据库记录模拟")
        
        print("1️⃣  学生记录表：")
        print("结构: (id, name, email, major, grade)")
        for record in self.db_records:
            student_id, name, email, major, grade = record
            print(f"  ID:{student_id} | {name} | {major} | {grade}分")
        print()
        
        print("2️⃣  数据查询和过滤：")
        high_grade = tuple(r for r in self.db_records if r[4] >= 90.0)
        print(f"高分学生: {[r[1] for r in high_grade]}")
        
        grades = tuple(r[4] for r in self.db_records)
        print(f"平均分: {sum(grades)/len(grades):.1f}")
        print()
        
        print("3️⃣  使用命名元组优化：")
        Student = namedtuple('Student', 'id name email major grade')
        students = tuple(Student(*r) for r in self.db_records)
        
        for s in students[:2]:
            print(f"  {s.name} ({s.major}) - {s.grade}分")
        print()
        
        print("💡 元组适合不可变的数据库记录，命名元组提供更好的可读性")
    
    def demonstrate_coordinate_system(self) -> None:
        """演示坐标系统应用"""
        self._print_section_header("📍 坐标系统应用")
        
        print("1️⃣  二维坐标系统：")
        points = ((0, 0), (3, 4), (-2, 3), (1, -1))
        
        print("坐标点和到原点距离:")
        for x, y in points:
            distance = math.sqrt(x*x + y*y)
            print(f"  ({x:2d}, {y:2d}) -> 距离: {distance:.2f}")
        print()
        
        print("2️⃣  坐标变换：")
        original = ((1, 2), (3, 4))
        print(f"原始坐标: {original}")
        
        # 平移
        translated = tuple((x+2, y+1) for x, y in original)
        print(f"平移(2,1): {translated}")
        
        # 缩放
        scaled = tuple((x*2, y*2) for x, y in original)
        print(f"缩放2倍: {scaled}")
        print()
        
        print("3️⃣  几何图形：")
        triangle = ((0, 0), (3, 0), (1.5, 2.6))
        print(f"三角形顶点: {triangle}")
        
        # 周长计算
        def distance(p1, p2):
            return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        
        perimeter = (distance(triangle[0], triangle[1]) + 
                    distance(triangle[1], triangle[2]) + 
                    distance(triangle[2], triangle[0]))
        print(f"周长: {perimeter:.2f}")
        print()
        
        print("4️⃣  命名坐标点：")
        Point = namedtuple('Point', 'x y')
        p1, p2 = Point(3, 4), Point(6, 8)
        dist = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2)
        print(f"{p1} 到 {p2} 距离: {dist:.2f}")
        print()
        
        print("💡 元组非常适合表示不可变的坐标点，支持数学运算")
    
    def demonstrate_configuration_management(self) -> None:
        """演示配置参数管理"""
        self._print_section_header("⚙️  配置管理")
        
        print("1️⃣  应用配置：")
        config = (
            ('host', 'localhost'),
            ('port', 8080),
            ('debug', True),
            ('timeout', 30),
            ('max_connections', 100)
        )
        
        for key, value in config:
            print(f"  {key}: {value}")
        print()
        
        print("2️⃣  多环境配置：")
        dev_config = (('env', 'dev'), ('debug', True), ('port', 8080))
        prod_config = (('env', 'prod'), ('debug', False), ('port', 80))
        
        configs = {'dev': dev_config, 'prod': prod_config}
        for env, cfg in configs.items():
            print(f"  {env.upper()}: {dict(cfg)}")
        print()
        
        print("3️⃣  命名配置：")
        Config = namedtuple('Config', 'host port debug timeout')
        app_config = Config('localhost', 8080, True, 30)
        print(f"服务器: {app_config.host}:{app_config.port}")
        print(f"调试模式: {'开启' if app_config.debug else '关闭'}")
        print()
        
        print("💡 元组保证配置不可变性，防止意外修改")
    
    def demonstrate_multiple_return_values(self) -> None:
        """演示函数多值返回"""
        self._print_section_header("↩️  函数多值返回")
        
        print("1️⃣  统计函数：")
        def calc_stats(numbers):
            return sum(numbers), len(numbers), max(numbers), min(numbers)
        
        data = [85, 92, 78, 96, 88]
        total, count, max_val, min_val = calc_stats(data)
        print(f"数据: {data}")
        print(f"统计: 总和={total}, 数量={count}, 最大={max_val}, 最小={min_val}")
        print()
        
        print("2️⃣  解方程函数：")
        def solve_quadratic(a, b, c):
            discriminant = b*b - 4*a*c
            if discriminant < 0:
                return None, None, "无实数解"
            elif discriminant == 0:
                root = -b / (2*a)
                return root, root, "一个重根"
            else:
                sqrt_d = math.sqrt(discriminant)
                r1 = (-b + sqrt_d) / (2*a)
                r2 = (-b - sqrt_d) / (2*a)
                return r1, r2, "两个不同根"
        
        x1, x2, status = solve_quadratic(1, -5, 6)
        print(f"方程 x² - 5x + 6 = 0: x₁={x1}, x₂={x2} ({status})")
        print()
        
        print("3️⃣  命名返回值：")
        Stats = namedtuple('Stats', 'count sum avg max min')
        
        def advanced_stats(numbers):
            c = len(numbers)
            s = sum(numbers)
            return Stats(c, s, s/c, max(numbers), min(numbers))
        
        stats = advanced_stats(data)
        print(f"结果: {stats}")
        print(f"平均值: {stats.avg:.1f}")
        print()
        
        print("💡 元组是Python多值返回的标准方式，命名元组增强可读性")
    
    def demonstrate_data_structures(self) -> None:
        """演示数据结构设计"""
        self._print_section_header("🏗️  数据结构设计")
        
        print("1️⃣  图的边表示：")
        edges = (('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'))
        print("图的边:")
        for src, dst in edges:
            print(f"  {src} -> {dst}")
        print()
        
        print("2️⃣  状态转换：")
        transitions = (
            ('IDLE', 'start', 'RUNNING'),
            ('RUNNING', 'pause', 'PAUSED'),
            ('PAUSED', 'resume', 'RUNNING'),
            ('RUNNING', 'stop', 'IDLE')
        )
        
        print("状态机转换:")
        for current, event, next_state in transitions:
            print(f"  {current} --{event}--> {next_state}")
        print()
        
        print("3️⃣  事件记录：")
        Event = namedtuple('Event', 'time level message')
        events = (
            Event('10:00:01', 'INFO', '系统启动'),
            Event('10:00:15', 'WARN', '内存使用率高'),
            Event('10:01:30', 'ERROR', '连接失败')
        )
        
        print("系统事件:")
        for event in events:
            print(f"  [{event.time}] {event.level}: {event.message}")
        print()
        
        print("4️⃣  缓存结构：")
        cache_items = (
            ('user:123', {'name': '张三'}, 1001),
            ('user:456', {'name': '李四'}, 1002),
            ('config:app', {'debug': True}, 1003)
        )
        
        print("缓存项 (key, value, timestamp):")
        for key, value, ts in cache_items:
            print(f"  {key}: {value} @{ts}")
        print()
        
        print("💡 元组适合表示各种不可变的数据结构，保证数据完整性")
    
    def _print_section_header(self, title: str) -> None:
        """打印章节标题"""
        print(f"\n{title}")
        print("=" * (len(title) - 2))
        print()