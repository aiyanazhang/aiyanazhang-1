#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级操作演示模块

提供Python元组的高级操作演示，包括：
- 元组解包
- 嵌套元组
- 命名元组
- 元组推导 
- 元组排序
"""

from collections import namedtuple
from typing import Any, Tuple, List, Iterator
from utils.error_handler import ErrorHandler, InputValidator


class AdvancedTupleDemo:
    """高级元组操作演示类"""
    
    def __init__(self):
        """初始化演示类"""
        self.demo_data = {
            'coordinates': ((1, 2), (3, 4), (5, 6), (7, 8)),
            'student_records': (
                ('张三', 18, 85.5),
                ('李四', 19, 92.0),
                ('王五', 20, 78.5),
                ('赵六', 18, 96.5)
            )
        }
    
    def demonstrate_tuple_unpacking(self) -> None:
        """演示元组解包操作"""
        self._print_section_header("📦 元组解包演示")
        
        # 1. 基本解包
        print("1️⃣  基本解包：")
        point = (3, 4)
        print(f"原始元组: {point}")
        
        self._show_code_example("x, y = point", None, "将元组解包到变量x和y")
        x, y = point
        print(f"    x = {x}, y = {y}\n")
        
        # 2. 扩展解包
        print("2️⃣  扩展解包（Python 3.0+）：")
        numbers = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        print(f"数字序列: {numbers}")
        
        self._show_code_example("first, *middle, last = numbers", None, "解包为首、中、尾")
        first, *middle, last = numbers
        print(f"    first = {first}, middle = {middle[:3]}..., last = {last}\n")
        
        # 3. 交换变量
        print("3️⃣  变量交换：")
        a, b = 10, 20
        print(f"交换前: a = {a}, b = {b}")
        a, b = b, a
        print(f"交换后: a = {a}, b = {b}\n")
        
        # 4. 函数返回值解包
        print("4️⃣  函数返回值解包：")
        def get_name_and_score():
            return '王五', 88.5
        
        name, score = get_name_and_score()
        print(f"函数返回: name = {name}, score = {score}\n")
        
        print("💡 小贴士：解包时变量数量必须匹配，使用*捕获多个元素")
    
    def demonstrate_nested_tuples(self) -> None:
        """演示嵌套元组操作"""
        self._print_section_header("🪆 嵌套元组演示")
        
        # 1. 创建和访问
        print("1️⃣  嵌套元组创建和访问：")
        matrix = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        print(f"矩阵: {matrix}")
        
        self._show_code_example("matrix[1][2]", matrix[1][2], "第2行第3列元素")
        
        # 2. 遍历嵌套结构
        print("2️⃣  遍历嵌套结构：")
        points = ((0, 0), (1, 1), (2, 2))
        print("for x, y in points:")
        for x, y in points:
            print(f"    点坐标: ({x}, {y})")
        print()
        
        # 3. 扁平化
        print("3️⃣  扁平化操作：")
        nested = ((1, 2), (3, 4), (5, 6))
        flattened = tuple(item for subtuple in nested for item in subtuple)
        self._show_code_example("扁平化", flattened, "将嵌套元组展开")
        
        print("💡 小贴士：嵌套元组适合表示矩阵、坐标等多维数据")
    
    def demonstrate_named_tuples(self) -> None:
        """演示命名元组操作"""
        self._print_section_header("🏷️  命名元组演示")
        
        # 1. 创建命名元组类
        print("1️⃣  创建命名元组类：")
        Student = namedtuple('Student', ['name', 'age', 'grade', 'major'])
        Point = namedtuple('Point', 'x y')
        
        print("Student = namedtuple('Student', ['name', 'age', 'grade', 'major'])")
        print("Point = namedtuple('Point', 'x y')\n")
        
        # 2. 创建实例
        print("2️⃣  创建和使用实例：")
        student1 = Student('张三', 20, 85.5, '计算机科学')
        point1 = Point(3, 4)
        
        print(f"学生: {student1}")
        print(f"坐标: {point1}\n")
        
        # 3. 访问字段
        print("3️⃣  字段访问：")
        self._show_code_example("student1.name", student1.name, "按名称访问")
        self._show_code_example("student1[0]", student1[0], "按索引访问")
        
        # 4. 特殊方法
        print("4️⃣  特殊方法：")
        self._show_code_example("student1._asdict()", student1._asdict(), "转换为字典")
        
        student2 = student1._replace(grade=90.0)
        self._show_code_example("_replace()更新", student2, "创建新实例")
        
        # 5. 应用示例
        print("5️⃣  实际应用 - 配置对象：")
        Config = namedtuple('Config', 'host port debug timeout')
        config = Config('localhost', 8080, True, 30)
        print(f"服务器配置: {config}")
        print(f"访问地址: {config.host}:{config.port}\n")
        
        print("💡 小贴士：命名元组提供类似类的接口但保持不可变性")
    
    def demonstrate_tuple_comprehension(self) -> None:
        """演示元组推导（生成器表达式）"""
        self._print_section_header("🔄 元组推导演示")
        
        print("注意：Python中使用生成器表达式创建元组\n")
        
        # 1. 基本推导
        print("1️⃣  基本生成器表达式：")
        numbers = [1, 2, 3, 4, 5]
        
        squares = tuple(x**2 for x in numbers)
        self._show_code_example("tuple(x**2 for x in numbers)", squares, "平方数元组")
        
        evens = tuple(x for x in numbers if x % 2 == 0)
        self._show_code_example("偶数过滤", evens, "筛选偶数")
        
        # 2. 字符串处理
        print("2️⃣  字符串处理：")
        words = ['hello', 'world', 'python']
        
        upper_words = tuple(word.upper() for word in words)
        self._show_code_example("大写转换", upper_words, "转为大写")
        
        lengths = tuple(len(word) for word in words)
        self._show_code_example("长度统计", lengths, "单词长度")
        
        # 3. 复杂表达式
        print("3️⃣  复杂表达式：")
        points = [(1, 2), (3, 4), (5, 6)]
        
        distances = tuple((point, (point[0]**2 + point[1]**2)**0.5) for point in points)
        print("距离计算:")
        for point, dist in distances:
            print(f"    {point} -> 距离: {dist:.2f}")
        print()
        
        # 4. 条件表达式
        print("4️⃣  条件表达式：")
        nums = range(-3, 4)
        categories = tuple('pos' if x > 0 else 'neg' if x < 0 else 'zero' for x in nums)
        self._show_code_example("数字分类", categories, "正负零分类")
        
        print("💡 小贴士：生成器表达式比列表推导更节省内存")
    
    def demonstrate_tuple_sorting(self) -> None:
        """演示元组排序操作"""
        self._print_section_header("📊 元组排序演示")
        
        # 1. 基本排序
        print("1️⃣  基本排序：")
        numbers = (3, 1, 4, 1, 5, 9, 2, 6)
        print(f"原始: {numbers}")
        
        sorted_tuple = tuple(sorted(numbers))
        self._show_code_example("tuple(sorted(numbers))", sorted_tuple, "升序排列")
        
        reverse_sorted = tuple(sorted(numbers, reverse=True))
        self._show_code_example("逆序排序", reverse_sorted, "降序排列")
        
        # 2. 字符串排序
        print("2️⃣  字符串排序：")
        fruits = ('苹果', '香蕉', '橙子', '葡萄')
        sorted_fruits = tuple(sorted(fruits))
        self._show_code_example("字符串排序", sorted_fruits, "按字典序")
        
        by_length = tuple(sorted(fruits, key=len))
        self._show_code_example("按长度排序", by_length, "使用key参数")
        
        # 3. 复杂对象排序
        print("3️⃣  复杂对象排序：")
        students = (
            ('张三', 85),
            ('李四', 92),
            ('王五', 78),
            ('赵六', 96)
        )
        
        by_score = tuple(sorted(students, key=lambda x: x[1]))
        print(f"按成绩排序: {by_score}")
        
        by_name = tuple(sorted(students, key=lambda x: x[0]))
        print(f"按姓名排序: {by_name}\n")
        
        # 4. 多级排序
        print("4️⃣  多级排序：")
        data = (
            ('A', 85, 20),
            ('B', 85, 18),
            ('C', 92, 19),
            ('A', 78, 21)
        )
        
        # 先按第二列排序，再按第一列排序
        multi_sort = tuple(sorted(data, key=lambda x: (x[1], x[0])))
        print(f"多级排序: {multi_sort}\n")
        
        print("💡 小贴士：sorted()返回列表，需要tuple()转换；使用key参数自定义排序规则")
    
    def _print_section_header(self, title: str) -> None:
        """打印章节标题"""
        print(f"\n{title}")
        print("=" * (len(title) - 2))
        print()
    
    def _show_code_example(self, code: str, result: Any, description: str = "") -> None:
        """显示代码示例和结果"""
        print(f"    {code}")
        if result is not None:
            print(f"    -> {result}")
        if description:
            print(f"    📝 {description}")
        print()