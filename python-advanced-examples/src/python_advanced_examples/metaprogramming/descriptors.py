"""
描述符协议示例

展示Python描述符协议的高级用法，包括属性验证、缓存属性、类型检查等。
"""

import time
import threading
import weakref
from typing import Any, Dict, Type, Optional, Callable, Union
from functools import wraps

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel


class ValidatedAttribute:
    """通用属性验证描述符"""
    
    def __init__(self, validator: Callable[[Any], bool], error_message: str = "Invalid value"):
        self.validator = validator
        self.error_message = error_message
        self.name = None
    
    def __set_name__(self, owner, name):
        """设置描述符名称（Python 3.6+）"""
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, instance, owner=None):
        """获取属性值"""
        if instance is None:
            return self
        
        return getattr(instance, self.private_name, None)
    
    def __set__(self, instance, value):
        """设置属性值"""
        if not self.validator(value):
            raise ValueError(f"{self.error_message}: {value}")
        
        setattr(instance, self.private_name, value)
    
    def __delete__(self, instance):
        """删除属性"""
        if hasattr(instance, self.private_name):
            delattr(instance, self.private_name)


class TypedAttribute:
    """类型检查描述符"""
    
    def __init__(self, expected_type: Type, allow_none: bool = False):
        self.expected_type = expected_type
        self.allow_none = allow_none
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        return getattr(instance, self.private_name, None)
    
    def __set__(self, instance, value):
        if value is None and self.allow_none:
            setattr(instance, self.private_name, value)
            return
        
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be of type {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        
        setattr(instance, self.private_name, value)
    
    def __delete__(self, instance):
        if hasattr(instance, self.private_name):
            delattr(instance, self.private_name)


class RangeValidatedAttribute:
    """范围验证描述符"""
    
    def __init__(self, min_value: Union[int, float], max_value: Union[int, float]):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        return getattr(instance, self.private_name, None)
    
    def __set__(self, instance, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        
        if not (self.min_value <= value <= self.max_value):
            raise ValueError(
                f"{self.name} must be between {self.min_value} and {self.max_value}, "
                f"got {value}"
            )
        
        setattr(instance, self.private_name, value)
    
    def __delete__(self, instance):
        if hasattr(instance, self.private_name):
            delattr(instance, self.private_name)


class CachedProperty:
    """缓存属性描述符"""
    
    def __init__(self, func: Callable, ttl: Optional[float] = None):
        self.func = func
        self.ttl = ttl  # 生存时间（秒）
        self.name = func.__name__
        self.doc = func.__doc__
        self._cache_name = f'_cached_{self.name}'
        self._time_name = f'_cached_time_{self.name}'
        self.lock = threading.Lock()
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        with self.lock:
            # 检查是否有缓存
            cached_value = getattr(instance, self._cache_name, None)
            cached_time = getattr(instance, self._time_name, 0)
            
            current_time = time.time()
            
            # 检查缓存是否有效
            if (cached_value is not None and 
                (self.ttl is None or current_time - cached_time < self.ttl)):
                return cached_value
            
            # 计算新值
            value = self.func(instance)
            
            # 缓存结果
            setattr(instance, self._cache_name, value)
            setattr(instance, self._time_name, current_time)
            
            return value
    
    def __set__(self, instance, value):
        """允许手动设置缓存值"""
        setattr(instance, self._cache_name, value)
        setattr(instance, self._time_name, time.time())
    
    def __delete__(self, instance):
        """清除缓存"""
        if hasattr(instance, self._cache_name):
            delattr(instance, self._cache_name)
        if hasattr(instance, self._time_name):
            delattr(instance, self._time_name)
    
    def clear_cache(self, instance):
        """手动清除缓存"""
        self.__delete__(instance)


class WeakKeyedDescriptor:
    """使用弱引用的描述符"""
    
    def __init__(self, default_value: Any = None):
        self.default_value = default_value
        self.data = weakref.WeakKeyDictionary()
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        return self.data.get(instance, self.default_value)
    
    def __set__(self, instance, value):
        self.data[instance] = value
    
    def __delete__(self, instance):
        if instance in self.data:
            del self.data[instance]


class LoggedAttribute:
    """记录访问日志的描述符"""
    
    def __init__(self, default_value: Any = None, log_access: bool = True, log_mutation: bool = True):
        self.default_value = default_value
        self.log_access = log_access
        self.log_mutation = log_mutation
        self.access_log = []
        self.mutation_log = []
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        value = getattr(instance, self.private_name, self.default_value)
        
        if self.log_access:
            self.access_log.append({
                'timestamp': time.time(),
                'instance_id': id(instance),
                'action': 'get',
                'value': value
            })
        
        return value
    
    def __set__(self, instance, value):
        old_value = getattr(instance, self.private_name, self.default_value)
        setattr(instance, self.private_name, value)
        
        if self.log_mutation:
            self.mutation_log.append({
                'timestamp': time.time(),
                'instance_id': id(instance),
                'action': 'set',
                'old_value': old_value,
                'new_value': value
            })
    
    def get_access_log(self):
        """获取访问日志"""
        return self.access_log.copy()
    
    def get_mutation_log(self):
        """获取变更日志"""
        return self.mutation_log.copy()
    
    def clear_logs(self):
        """清除日志"""
        self.access_log.clear()
        self.mutation_log.clear()


# ============================================================================
# 示例类
# ============================================================================

class Person:
    """使用各种描述符的Person类"""
    
    # 类型检查
    name = TypedAttribute(str)
    age = TypedAttribute(int)
    
    # 范围验证
    height = RangeValidatedAttribute(0.0, 3.0)  # 身高（米）
    weight = RangeValidatedAttribute(0.0, 500.0)  # 体重（公斤）
    
    # 自定义验证
    email = ValidatedAttribute(
        validator=lambda x: isinstance(x, str) and '@' in x and '.' in x,
        error_message="Invalid email format"
    )
    
    # 弱引用存储
    notes = WeakKeyedDescriptor(default_value="")
    
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
    
    def __repr__(self):
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"


class ComputationIntensive:
    """计算密集型类（使用缓存属性）"""
    
    def __init__(self, data: list):
        self.data = data
    
    @CachedProperty
    def expensive_computation(self):
        """昂贵的计算（会被缓存）"""
        print("执行昂贵计算...")
        time.sleep(0.1)  # 模拟计算时间
        return sum(x * x for x in self.data)
    
    @CachedProperty
    def statistical_summary(self):
        """统计摘要（会被缓存）"""
        print("计算统计摘要...")
        time.sleep(0.05)
        
        if not self.data:
            return {"mean": 0, "min": 0, "max": 0, "count": 0}
        
        return {
            "mean": sum(self.data) / len(self.data),
            "min": min(self.data),
            "max": max(self.data),
            "count": len(self.data)
        }


class MonitoredClass:
    """被监控的类（使用日志描述符）"""
    
    # 记录访问和变更的属性
    value = LoggedAttribute(default_value=0)
    name = LoggedAttribute(default_value="", log_access=False)  # 只记录变更
    
    def __init__(self, name: str = "", value: int = 0):
        self.name = name
        self.value = value


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="descriptor_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="描述符协议基础示例",
    tags=["descriptors", "validation", "properties"]
)
@demo(title="描述符协议基础示例")
def descriptor_example():
    """展示描述符协议的基本使用"""
    
    print("描述符协议基础示例")
    
    # 创建有效的Person实例
    print("\n创建有效的Person实例:")
    
    try:
        person1 = Person("Alice", 30, "alice@example.com")
        print(f"✅ 创建成功: {person1}")
        
        # 设置物理属性
        person1.height = 1.65
        person1.weight = 60.0
        person1.notes = "友好的同事"
        
        print(f"身高: {person1.height}m, 体重: {person1.weight}kg")
        print(f"备注: {person1.notes}")
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
    
    # 测试各种验证失败情况
    print(f"\n测试验证失败情况:")
    
    # 类型错误
    try:
        person2 = Person("Bob", "thirty", "bob@example.com")  # 年龄应该是int
    except TypeError as e:
        print(f"✅ 类型验证: {e}")
    
    # 邮箱格式错误
    try:
        person3 = Person("Charlie", 25, "invalid-email")
    except ValueError as e:
        print(f"✅ 邮箱验证: {e}")
    
    # 范围验证错误
    try:
        person1.height = 5.0  # 超出合理身高范围
    except ValueError as e:
        print(f"✅ 身高范围验证: {e}")
    
    try:
        person1.weight = -10  # 负体重
    except ValueError as e:
        print(f"✅ 体重范围验证: {e}")
    
    print(f"\n描述符的优势:")
    print("• 重用验证逻辑")
    print("• 声明式属性定义")
    print("• 自动类型和范围检查")
    print("• 清晰的错误消息")


@example(
    name="cached_property_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="缓存属性描述符示例",
    tags=["descriptors", "caching", "performance"]
)
@demo(title="缓存属性描述符示例")
def cached_property_example():
    """展示缓存属性描述符的使用"""
    
    print("缓存属性描述符示例")
    
    # 创建计算密集型对象
    data = list(range(1, 1001))  # 1到1000的数字
    obj = ComputationIntensive(data)
    
    print(f"数据大小: {len(obj.data)}")
    
    # 第一次访问（会执行计算）
    print(f"\n第一次访问expensive_computation:")
    start_time = time.time()
    result1 = obj.expensive_computation
    time1 = time.time() - start_time
    print(f"结果: {result1}")
    print(f"耗时: {time1:.3f}s")
    
    # 第二次访问（从缓存获取）
    print(f"\n第二次访问expensive_computation:")
    start_time = time.time()
    result2 = obj.expensive_computation
    time2 = time.time() - start_time
    print(f"结果: {result2}")
    print(f"耗时: {time2:.6f}s")
    print(f"加速比: {time1/time2:.0f}x" if time2 > 0 else "无限倍加速")
    
    # 统计摘要测试
    print(f"\n统计摘要测试:")
    
    start_time = time.time()
    summary1 = obj.statistical_summary
    time1 = time.time() - start_time
    print(f"第一次计算: {summary1}")
    print(f"耗时: {time1:.3f}s")
    
    start_time = time.time()
    summary2 = obj.statistical_summary
    time2 = time.time() - start_time
    print(f"第二次获取: {summary2}")
    print(f"耗时: {time2:.6f}s")
    
    # 手动清除缓存
    print(f"\n清除缓存后:")
    ComputationIntensive.expensive_computation.clear_cache(obj)
    
    start_time = time.time()
    result3 = obj.expensive_computation
    time3 = time.time() - start_time
    print(f"清除缓存后重新计算耗时: {time3:.3f}s")
    
    print(f"\n缓存属性的优势:")
    print("• 自动缓存昂贵计算")
    print("• 透明的缓存管理")
    print("• 显著提升性能")
    print("• 支持手动缓存控制")


@example(
    name="logged_descriptor_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.ADVANCED,
    description="日志记录描述符示例",
    tags=["descriptors", "logging", "monitoring"]
)
@demo(title="日志记录描述符示例")
def logged_descriptor_example():
    """展示日志记录描述符的使用"""
    
    print("日志记录描述符示例")
    
    # 创建被监控的对象
    obj1 = MonitoredClass("Object1", 100)
    obj2 = MonitoredClass("Object2", 200)
    
    print(f"创建对象: {obj1.name} (value={obj1.value})")
    print(f"创建对象: {obj2.name} (value={obj2.value})")
    
    # 进行一些操作
    print(f"\n执行操作:")
    
    # 读取操作
    val1 = obj1.value
    val2 = obj2.value
    print(f"读取 obj1.value: {val1}")
    print(f"读取 obj2.value: {val2}")
    
    # 写入操作
    obj1.value = 150
    obj2.value = 250
    print(f"设置 obj1.value = 150")
    print(f"设置 obj2.value = 250")
    
    # 再次读取
    val1_new = obj1.value
    val2_new = obj2.value
    print(f"再次读取 obj1.value: {val1_new}")
    print(f"再次读取 obj2.value: {val2_new}")
    
    # 修改名称（只记录变更，不记录访问）
    obj1.name = "Object1_Modified"
    obj2.name = "Object2_Modified"
    
    # 查看日志
    print(f"\n访问日志 (value属性):")
    access_log = MonitoredClass.value.get_access_log()
    for i, log_entry in enumerate(access_log[-6:], 1):  # 显示最后6次访问
        timestamp = time.strftime('%H:%M:%S', time.localtime(log_entry['timestamp']))
        print(f"  {i}. {timestamp} - 实例{log_entry['instance_id']} 读取值: {log_entry['value']}")
    
    print(f"\n变更日志 (value属性):")
    mutation_log = MonitoredClass.value.get_mutation_log()
    for i, log_entry in enumerate(mutation_log, 1):
        timestamp = time.strftime('%H:%M:%S', time.localtime(log_entry['timestamp']))
        print(f"  {i}. {timestamp} - 实例{log_entry['instance_id']} "
              f"从 {log_entry['old_value']} 改为 {log_entry['new_value']}")
    
    print(f"\n变更日志 (name属性):")
    name_mutation_log = MonitoredClass.name.get_mutation_log()
    for i, log_entry in enumerate(name_mutation_log, 1):
        timestamp = time.strftime('%H:%M:%S', time.localtime(log_entry['timestamp']))
        print(f"  {i}. {timestamp} - 实例{log_entry['instance_id']} "
              f"从 '{log_entry['old_value']}' 改为 '{log_entry['new_value']}'")
    
    print(f"\n日志描述符的优势:")
    print("• 自动记录属性访问")
    print("• 跟踪数据变更历史")
    print("• 调试和审计支持")
    print("• 可配置的日志级别")


# 导出的类和函数
__all__ = [
    "ValidatedAttribute",
    "TypedAttribute",
    "RangeValidatedAttribute",
    "CachedProperty",
    "WeakKeyedDescriptor",
    "LoggedAttribute",
    "Person",
    "ComputationIntensive",
    "MonitoredClass",
    "descriptor_example",
    "cached_property_example",
    "logged_descriptor_example"
]