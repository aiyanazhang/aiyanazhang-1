#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式练习模块

提供各种元组练习题，包括：
- 基础语法练习
- 数据操作练习  
- 应用场景练习
- 综合挑战题
"""

import random
import time
from collections import namedtuple
from typing import List, Tuple, Any, Dict
from utils.error_handler import ErrorHandler, InputValidator


class ExerciseManager:
    """练习管理器"""
    
    def __init__(self):
        """初始化练习管理器"""
        self.stats = {
            'total_exercises': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'start_time': None
        }
    
    def basic_syntax_exercises(self) -> None:
        """基础语法练习"""
        self._print_section_header("✏️  基础语法练习")
        
        exercises = [
            {
                'question': '创建一个包含数字1,2,3的元组，正确的语法是？',
                'options': ['A. [1,2,3]', 'B. (1,2,3)', 'C. {1,2,3}', 'D. <1,2,3>'],
                'answer': 'B',
                'explanation': '元组使用圆括号()创建'
            },
            {
                'question': '创建单元素元组的正确方式是？',
                'options': ['A. (42)', 'B. (42,)', 'C. [42]', 'D. tuple(42)'],
                'answer': 'B', 
                'explanation': '单元素元组必须包含逗号，如(42,)'
            },
            {
                'question': '元组的特性是？',
                'options': ['A. 可变的', 'B. 不可变的', 'C. 可排序的', 'D. 可哈希的'],
                'answer': 'B',
                'explanation': '元组是不可变(immutable)的序列类型'
            },
            {
                'question': '访问元组t=(1,2,3)的第二个元素用？',
                'options': ['A. t[2]', 'B. t[1]', 'C. t(1)', 'D. t.get(1)'],
                'answer': 'B',
                'explanation': '索引从0开始，第二个元素索引为1'
            }
        ]
        
        self._run_quiz(exercises, "基础语法")
    
    def data_operations_exercises(self) -> None:
        """数据操作练习"""
        self._print_section_header("🔧 数据操作练习")
        
        print("1️⃣  元组解包练习：")
        point = (3, 4, 5)
        print(f"给定元组: {point}")
        
        user_answer = input("请用解包语法将元组赋值给变量x,y,z: ").strip()
        correct_answers = ['x, y, z = point', 'x,y,z=point', '(x, y, z) = point']
        
        if any(user_answer == ans for ans in correct_answers):
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print("❌ 错误。正确答案: x, y, z = point")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
        
        print("2️⃣  元组切片练习：")
        numbers = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        print(f"给定元组: {numbers}")
        
        questions = [
            ("获取前3个元素", "numbers[:3]", numbers[:3]),
            ("获取最后3个元素", "numbers[-3:]", numbers[-3:]),
            ("获取索引2到5的元素", "numbers[2:6]", numbers[2:6])
        ]
        
        for desc, expected_code, expected_result in questions:
            user_code = input(f"{desc}的代码: ").strip()
            
            try:
                # 简单验证（在实际应用中需要更安全的方式）
                if user_code == expected_code:
                    print(f"✅ 正确！结果: {expected_result}")
                    self.stats['correct_answers'] += 1
                else:
                    print(f"❌ 错误。正确答案: {expected_code}, 结果: {expected_result}")
                    self.stats['wrong_answers'] += 1
            except:
                print(f"❌ 语法错误。正确答案: {expected_code}")
                self.stats['wrong_answers'] += 1
            
            self.stats['total_exercises'] += 1
            print()
        
        print("3️⃣  元组方法练习：")
        test_tuple = (1, 2, 3, 2, 4, 2, 5)
        print(f"给定元组: {test_tuple}")
        
        # count方法练习
        target = 2
        user_count = InputValidator.get_valid_integer(f"数字{target}出现了几次? ", 0, 10)
        correct_count = test_tuple.count(target)
        
        if user_count == correct_count:
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print(f"❌ 错误。正确答案: {correct_count}")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
    
    def application_exercises(self) -> None:
        """应用场景练习"""
        self._print_section_header("💼 应用场景练习")
        
        print("1️⃣  坐标计算练习：")
        point1 = (1, 2)
        point2 = (4, 6)
        print(f"点A: {point1}, 点B: {point2}")
        
        # 计算距离
        import math
        correct_distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        
        print("请计算两点间的距离（保留2位小数）")
        user_distance = float(input("距离: "))
        
        if abs(user_distance - correct_distance) < 0.01:
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print(f"❌ 错误。正确答案: {correct_distance:.2f}")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
        
        print("2️⃣  数据统计练习：")
        grades = (85, 92, 78, 96, 88, 91, 83, 87)
        print(f"学生成绩: {grades}")
        
        # 计算平均分
        correct_avg = sum(grades) / len(grades)
        user_avg = float(input("平均分（保留1位小数）: "))
        
        if abs(user_avg - correct_avg) < 0.1:
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print(f"❌ 错误。正确答案: {correct_avg:.1f}")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
        
        print("3️⃣  命名元组练习：")
        print("请创建一个表示学生的命名元组，包含字段: name, age, grade")
        
        user_code = input("代码: ").strip()
        expected_patterns = [
            "namedtuple('Student', ['name', 'age', 'grade'])",
            "namedtuple('Student', 'name age grade')",
            "namedtuple(\"Student\", [\"name\", \"age\", \"grade\"])"
        ]
        
        if any(pattern in user_code for pattern in expected_patterns):
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print("❌ 错误。参考答案: Student = namedtuple('Student', ['name', 'age', 'grade'])")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
    
    def comprehensive_challenge(self) -> None:
        """综合挑战题"""
        self._print_section_header("🏆 综合挑战题")
        
        print("挑战题：处理学生数据")
        print("给定学生信息元组列表，完成以下任务：")
        
        students = (
            ('张三', 18, 85),
            ('李四', 19, 92),
            ('王五', 20, 78),
            ('赵六', 18, 96),
            ('钱七', 19, 88)
        )
        
        print(f"学生数据: {students}")
        print("每个元组包含: (姓名, 年龄, 成绩)")
        print()
        
        # 任务1：找出最高分学生
        print("任务1：找出成绩最高的学生姓名")
        max_score_student = max(students, key=lambda x: x[2])
        user_answer1 = input("最高分学生姓名: ").strip()
        
        if user_answer1 == max_score_student[0]:
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print(f"❌ 错误。正确答案: {max_score_student[0]}")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
        
        # 任务2：计算18岁学生的平均成绩
        print("任务2：计算18岁学生的平均成绩")
        age_18_students = [s for s in students if s[1] == 18]
        avg_score_18 = sum(s[2] for s in age_18_students) / len(age_18_students)
        
        user_answer2 = float(input("18岁学生平均成绩: "))
        
        if abs(user_answer2 - avg_score_18) < 0.1:
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print(f"❌ 错误。正确答案: {avg_score_18:.1f}")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
        
        # 任务3：按成绩排序
        print("任务3：按成绩从高到低排序，写出前3名学生姓名")
        sorted_students = sorted(students, key=lambda x: x[2], reverse=True)
        top_3_names = [s[0] for s in sorted_students[:3]]
        
        user_names = input("前3名姓名（用逗号分隔）: ").strip().split(',')
        user_names = [name.strip() for name in user_names]
        
        if user_names == top_3_names:
            print("✅ 正确！")
            self.stats['correct_answers'] += 1
        else:
            print(f"❌ 错误。正确答案: {', '.join(top_3_names)}")
            self.stats['wrong_answers'] += 1
        
        self.stats['total_exercises'] += 1
        print()
    
    def show_exercise_stats(self) -> None:
        """显示练习统计"""
        self._print_section_header("📊 练习统计")
        
        if self.stats['total_exercises'] == 0:
            print("还没有完成任何练习。")
            return
        
        total = self.stats['total_exercises']
        correct = self.stats['correct_answers']
        wrong = self.stats['wrong_answers']
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print(f"📈 练习统计报告")
        print(f"=" * 30)
        print(f"总题数: {total}")
        print(f"正确: {correct}")
        print(f"错误: {wrong}")
        print(f"正确率: {accuracy:.1f}%")
        print()
        
        # 评级
        if accuracy >= 90:
            grade = "优秀 🌟"
        elif accuracy >= 80:
            grade = "良好 👍"
        elif accuracy >= 70:
            grade = "及格 ✔️"
        else:
            grade = "需要加强 💪"
        
        print(f"评级: {grade}")
        print()
        
        # 建议
        if accuracy < 70:
            print("💡 学习建议：")
            print("   • 重新复习基础概念")
            print("   • 多做练习题")
            print("   • 查看演示示例")
        elif accuracy < 90:
            print("💡 提升建议：")
            print("   • 尝试更多高级操作")
            print("   • 练习实际应用场景")
        else:
            print("🎉 恭喜！您已经很好地掌握了元组的使用！")
        print()
    
    def _run_quiz(self, exercises: List[Dict], category: str) -> None:
        """运行选择题测验"""
        print(f"开始{category}测验，共{len(exercises)}题")
        print("-" * 40)
        
        for i, exercise in enumerate(exercises, 1):
            print(f"\n第{i}题: {exercise['question']}")
            for option in exercise['options']:
                print(f"  {option}")
            
            user_answer = InputValidator.get_valid_choice(
                "请选择答案 (A/B/C/D): ",
                ['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd']
            ).upper()
            
            if user_answer == exercise['answer']:
                print("✅ 正确！")
                self.stats['correct_answers'] += 1
            else:
                print(f"❌ 错误。正确答案: {exercise['answer']}")
                print(f"💡 解释: {exercise['explanation']}")
                self.stats['wrong_answers'] += 1
            
            self.stats['total_exercises'] += 1
        
        print(f"\n{category}测验完成！")
    
    def _print_section_header(self, title: str) -> None:
        """打印章节标题"""
        print(f"\n{title}")
        print("=" * (len(title) - 2))
        print()