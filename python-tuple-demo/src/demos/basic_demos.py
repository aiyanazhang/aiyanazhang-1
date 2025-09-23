#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础操作演示模块

提供Python元组的基础操作演示，包括：
- 元组创建
- 元组访问 
- 元组遍历
- 元组特性
- 元组方法
"""

import time
from typing import Any, Tuple, List
from utils.error_handler import ErrorHandler, InputValidator


class BasicTupleDemo:
    """基础元组操作演示类"""
    
    def __init__(self):
        """初始化演示类"""
        self.demo_data = {
            'numbers': (1, 2, 3, 4, 5),
            'mixed': (1, 'hello', 3.14, True, None),
            'nested': ((1, 2), (3, 4), (5, 6)),
            'single': (42,),
            'empty': (),
            'fruits': ('苹果', '香蕉', '橙子', '葡萄', '西瓜')
        }
    
    def demonstrate_tuple_creation(self) -> None:
        """演示元组创建的各种方式"""
        self._print_section_header("🔨 元组创建演示")
        
        print("Python中创建元组有多种方式：\n")
        
        # 1. 使用圆括号创建
        print("1️⃣  使用圆括号创建元组：")
        self._show_code_example(
            "numbers = (1, 2, 3, 4, 5)",
            self.demo_data['numbers']
        )
        
        self._show_code_example(
            "mixed = (1, 'hello', 3.14, True, None)",
            self.demo_data['mixed']
        )
        
        # 2. 不使用括号创建（逗号分隔）
        print("\n2️⃣  不使用括号创建元组（逗号分隔）：")
        no_paren = 1, 2, 3, 4, 5
        self._show_code_example(
            "no_paren = 1, 2, 3, 4, 5",
            no_paren
        )
        
        # 3. 单元素元组
        print("\n3️⃣  单元素元组（注意逗号的重要性）：")
        self._show_code_example(
            "single = (42,)  # 注意逗号",
            self.demo_data['single']
        )
        
        # 错误示例
        print("\n❌ 常见错误：")
        not_tuple = (42)  # 这不是元组，是整数
        self._show_code_example(
            "not_tuple = (42)  # 这不是元组！",
            not_tuple,
            f"类型: {type(not_tuple).__name__}"
        )
        
        # 4. 空元组
        print("\n4️⃣  空元组：")
        self._show_code_example(
            "empty = ()",
            self.demo_data['empty']
        )
        
        # 5. 使用tuple()构造函数
        print("\n5️⃣  使用tuple()构造函数：")
        from_list = tuple([1, 2, 3, 4, 5])
        self._show_code_example(
            "from_list = tuple([1, 2, 3, 4, 5])",
            from_list
        )
        
        from_string = tuple("hello")
        self._show_code_example(
            "from_string = tuple('hello')",
            from_string
        )
        
        # 6. 嵌套元组
        print("\n6️⃣  嵌套元组：")
        self._show_code_example(
            "nested = ((1, 2), (3, 4), (5, 6))",
            self.demo_data['nested']
        )
        
        print("\n💡 小贴士：")
        print("   • 元组是不可变的序列类型")
        print("   • 圆括号是可选的，逗号才是关键")
        print("   • 单元素元组必须包含逗号")
        print("   • 可以包含不同类型的元素")
    
    def demonstrate_tuple_access(self) -> None:
        """演示元组访问操作"""
        self._print_section_header("🔍 元组访问演示")
        
        fruits = self.demo_data['fruits']
        print(f"示例元组: {fruits}\n")
        
        # 1. 正向索引
        print("1️⃣  正向索引访问：")
        for i in range(len(fruits)):
            self._show_code_example(
                f"fruits[{i}]",
                fruits[i]
            )
        
        # 2. 反向索引
        print("\n2️⃣  反向索引访问：")
        for i in range(-1, -len(fruits)-1, -1):
            self._show_code_example(
                f"fruits[{i}]",
                fruits[i]
            )
        
        # 3. 切片操作
        print("\n3️⃣  切片操作：")
        slice_examples = [
            ("fruits[:3]", fruits[:3], "前3个元素"),
            ("fruits[1:]", fruits[1:], "从索引1开始的所有元素"),
            ("fruits[1:4]", fruits[1:4], "索引1到3的元素"),
            ("fruits[::2]", fruits[::2], "每隔一个元素"),
            ("fruits[::-1]", fruits[::-1], "反向所有元素"),
            ("fruits[-3:]", fruits[-3:], "最后3个元素")
        ]
        
        for code, result, description in slice_examples:
            self._show_code_example(code, result, description)
        
        # 4. 嵌套元组访问
        print("\n4️⃣  嵌套元组访问：")
        nested = self.demo_data['nested']
        print(f"嵌套元组: {nested}")
        
        self._show_code_example(
            "nested[0]",
            nested[0],
            "访问第一个子元组"
        )
        
        self._show_code_example(
            "nested[0][1]",
            nested[0][1], 
            "访问第一个子元组的第二个元素"
        )
        
        # 5. 错误处理演示
        print("\n5️⃣  索引错误处理演示：")
        try:
            result = fruits[10]  # 超出范围
        except IndexError as e:
            print(f"❌ fruits[10] -> IndexError: {e}")
        
        print("\n💡 小贴士：")
        print("   • 索引从0开始")
        print("   • 负数索引从-1开始（最后一个元素）")
        print("   • 切片操作返回新的元组")
        print("   • 访问不存在的索引会抛出IndexError")
    
    def demonstrate_tuple_iteration(self) -> None:
        """演示元组遍历操作"""
        self._print_section_header("🔄 元组遍历演示")
        
        fruits = self.demo_data['fruits']
        print(f"示例元组: {fruits}\n")
        
        # 1. 基本遍历
        print("1️⃣  基本遍历：")
        print("for fruit in fruits:")
        for fruit in fruits:
            print(f"    {fruit}")
        
        # 2. 带索引遍历
        print("\n2️⃣  带索引遍历（enumerate）：")
        print("for index, fruit in enumerate(fruits):")
        for index, fruit in enumerate(fruits):
            print(f"    [{index}] {fruit}")
        
        # 3. 带自定义起始索引
        print("\n3️⃣  带自定义起始索引：")
        print("for index, fruit in enumerate(fruits, 1):")
        for index, fruit in enumerate(fruits, 1):
            print(f"    第{index}个: {fruit}")
        
        # 4. 使用range和len遍历
        print("\n4️⃣  使用range和len遍历：")
        print("for i in range(len(fruits)):")
        for i in range(len(fruits)):
            print(f"    fruits[{i}] = {fruits[i]}")
        
        # 5. 嵌套元组遍历
        print("\n5️⃣  嵌套元组遍历：")
        nested = self.demo_data['nested']
        print(f"嵌套元组: {nested}")
        print("for sub_tuple in nested:")
        print("    for item in sub_tuple:")
        for sub_tuple in nested:
            for item in sub_tuple:
                print(f"        {item}")
        
        # 6. 使用解包遍历
        print("\n6️⃣  使用解包遍历嵌套元组：")
        coordinates = ((1, 2), (3, 4), (5, 6))
        print(f"坐标元组: {coordinates}")
        print("for x, y in coordinates:")
        for x, y in coordinates:
            print(f"    坐标点: ({x}, {y})")
        
        # 7. 反向遍历
        print("\n7️⃣  反向遍历：")
        print("for fruit in reversed(fruits):")
        for fruit in reversed(fruits):
            print(f"    {fruit}")
        
        # 8. 遍历多个元组
        print("\n8️⃣  同时遍历多个元组（zip）：")
        numbers = (1, 2, 3, 4, 5)
        letters = ('A', 'B', 'C', 'D', 'E')
        print(f"数字: {numbers}")
        print(f"字母: {letters}")
        print("for num, letter in zip(numbers, letters):")
        for num, letter in zip(numbers, letters):
            print(f"    {num} -> {letter}")
        
        print("\n💡 小贴士：")
        print("   • for循环是遍历元组最常用的方法")
        print("   • enumerate()可以同时获取索引和值")
        print("   • zip()可以同时遍历多个序列")
        print("   • reversed()可以反向遍历")
    
    def demonstrate_tuple_properties(self) -> None:
        """演示元组特性"""
        self._print_section_header("🔒 元组特性演示")
        
        # 1. 不可变性
        print("1️⃣  不可变性演示：")
        fruits = self.demo_data['fruits']
        print(f"原始元组: {fruits}")
        
        print("\n尝试修改元组元素：")
        try:
            # fruits[0] = '苹果'  # 这会引发错误
            print("fruits[0] = '芒果'")
            exec("fruits[0] = '芒果'")
        except TypeError as e:
            print(f"❌ TypeError: {e}")
        
        print("\n尝试删除元组元素：")
        try:
            print("del fruits[0]")
            exec("del fruits[0]")
        except TypeError as e:
            print(f"❌ TypeError: {e}")
        
        # 2. 元组可以包含可变对象
        print("\n2️⃣  元组包含可变对象：")
        tuple_with_list = ([1, 2, 3], [4, 5, 6])
        print(f"包含列表的元组: {tuple_with_list}")
        
        print("修改列表内容（元组本身不变）：")
        tuple_with_list[0].append(4)
        print(f"修改后: {tuple_with_list}")
        print("注意：元组本身没有改变，但其包含的可变对象可以修改")
        
        # 3. 元组的身份和相等性
        print("\n3️⃣  元组的身份和相等性：")
        tuple1 = (1, 2, 3)
        tuple2 = (1, 2, 3)
        tuple3 = tuple1
        
        self._show_comparison("tuple1 == tuple2", tuple1, tuple2, tuple1 == tuple2)
        self._show_comparison("tuple1 is tuple2", tuple1, tuple2, tuple1 is tuple2)
        self._show_comparison("tuple1 is tuple3", tuple1, tuple3, tuple1 is tuple3)
        
        # 4. 元组的哈希性
        print("\n4️⃣  元组的哈希性：")
        hashable_tuple = (1, 2, 3, 'hello')
        print(f"可哈希元组: {hashable_tuple}")
        print(f"哈希值: {hash(hashable_tuple)}")
        
        # 包含可变对象的元组不能哈希
        try:
            unhashable_tuple = ([1, 2], [3, 4])
            print(f"\n包含列表的元组: {unhashable_tuple}")
            print(f"尝试计算哈希值: hash({unhashable_tuple})")
            hash(unhashable_tuple)
        except TypeError as e:
            print(f"❌ TypeError: {e}")
        
        # 5. 元组作为字典键
        print("\n5️⃣  元组作为字典键：")
        coordinate_dict = {
            (0, 0): '原点',
            (1, 0): 'X轴上的点',
            (0, 1): 'Y轴上的点',
            (1, 1): '对角线上的点'
        }
        
        print("坐标字典:")
        for coord, description in coordinate_dict.items():
            print(f"    {coord}: {description}")
        
        # 6. 元组的内存效率
        print("\n6️⃣  元组的内存效率：")
        import sys
        
        list_obj = [1, 2, 3, 4, 5]
        tuple_obj = (1, 2, 3, 4, 5)
        
        print(f"列表大小: {sys.getsizeof(list_obj)} 字节")
        print(f"元组大小: {sys.getsizeof(tuple_obj)} 字节")
        print(f"元组比列表节省内存: {sys.getsizeof(list_obj) - sys.getsizeof(tuple_obj)} 字节")
        
        print("\n💡 小贴士：")
        print("   • 元组是不可变的，但可以包含可变对象")
        print("   • 元组可以作为字典的键（如果所有元素都是可哈希的）")
        print("   • 元组比列表更节省内存")
        print("   • 元组的不可变性使其线程安全")
    
    def demonstrate_tuple_methods(self) -> None:
        """演示元组方法"""
        self._print_section_header("🛠️  元组方法演示")
        
        # 示例数据
        numbers = (1, 2, 3, 2, 4, 2, 5)
        fruits = self.demo_data['fruits']
        
        print(f"数字元组: {numbers}")
        print(f"水果元组: {fruits}\n")
        
        # 1. count() 方法
        print("1️⃣  count() 方法 - 统计元素出现次数：")
        self._show_code_example(
            "numbers.count(2)",
            numbers.count(2),
            "数字2出现的次数"
        )
        
        self._show_code_example(
            "numbers.count(6)",
            numbers.count(6),
            "数字6出现的次数（不存在）"
        )
        
        self._show_code_example(
            "fruits.count('苹果')",
            fruits.count('苹果'),
            "苹果出现的次数"
        )
        
        # 2. index() 方法
        print("\n2️⃣  index() 方法 - 查找元素索引：")
        self._show_code_example(
            "numbers.index(3)",
            numbers.index(3),
            "数字3的第一个索引位置"
        )
        
        self._show_code_example(
            "fruits.index('香蕉')",
            fruits.index('香蕉'),
            "香蕉的索引位置"
        )
        
        # 查找多次出现的元素
        self._show_code_example(
            "numbers.index(2)",
            numbers.index(2),
            "数字2的第一个索引位置"
        )
        
        # 指定查找范围
        print("\n   指定查找范围：")
        self._show_code_example(
            "numbers.index(2, 2)",
            numbers.index(2, 2),
            "从索引2开始查找数字2"
        )
        
        self._show_code_example(
            "numbers.index(2, 2, 5)",
            numbers.index(2, 2, 5),
            "在索引2-4范围内查找数字2"
        )
        
        # 处理不存在的元素
        print("\n   处理不存在的元素：")
        try:
            result = numbers.index(10)
        except ValueError as e:
            print(f"❌ numbers.index(10) -> ValueError: {e}")
        
        # 3. 内置函数与元组
        print("\n3️⃣  常用内置函数：")
        
        # len()
        self._show_code_example(
            "len(numbers)",
            len(numbers),
            "元组长度"
        )
        
        # max() 和 min()
        self._show_code_example(
            "max(numbers)",
            max(numbers),
            "最大值"
        )
        
        self._show_code_example(
            "min(numbers)",
            min(numbers),
            "最小值"
        )
        
        # sum()
        self._show_code_example(
            "sum(numbers)",
            sum(numbers),
            "元素总和"
        )
        
        # sorted()
        self._show_code_example(
            "sorted(numbers)",
            sorted(numbers),
            "排序后的列表（注意返回列表）"
        )
        
        # 4. 成员测试
        print("\n4️⃣  成员测试（in 和 not in）：")
        self._show_code_example(
            "2 in numbers",
            2 in numbers,
            "检查2是否在元组中"
        )
        
        self._show_code_example(
            "10 not in numbers",
            10 not in numbers,
            "检查10是否不在元组中"
        )
        
        self._show_code_example(
            "'苹果' in fruits",
            '苹果' in fruits,
            "检查苹果是否在水果元组中"
        )
        
        # 5. 元组比较
        print("\n5️⃣  元组比较：")
        tuple1 = (1, 2, 3)
        tuple2 = (1, 2, 4)
        tuple3 = (1, 2, 3, 4)
        
        comparisons = [
            ("tuple1 < tuple2", tuple1 < tuple2),
            ("tuple1 > tuple2", tuple1 > tuple2),
            ("tuple1 == (1, 2, 3)", tuple1 == (1, 2, 3)),
            ("tuple1 < tuple3", tuple1 < tuple3)
        ]
        
        for code, result in comparisons:
            print(f"    {code} -> {result}")
        
        print("\n💡 小贴士：")
        print("   • count()和index()是元组仅有的两个方法")
        print("   • 可以使用内置函数对元组进行操作")
        print("   • 元组支持成员测试和比较操作")
        print("   • 元组比较按字典序进行")
    
    def _print_section_header(self, title: str) -> None:
        """打印章节标题"""
        print(f"\n{title}")
        print("=" * (len(title) - 2))  # 减去emoji字符长度
        print()
    
    def _show_code_example(self, code: str, result: Any, description: str = "") -> None:
        """显示代码示例和结果"""
        print(f"    {code}")
        print(f"    -> {result}")
        if description:
            print(f"    📝 {description}")
        print()
    
    def _show_comparison(self, operation: str, obj1: Any, obj2: Any, result: bool) -> None:
        """显示比较操作"""
        print(f"    {operation}")
        print(f"    {obj1} vs {obj2}")
        print(f"    -> {result}")
        print()