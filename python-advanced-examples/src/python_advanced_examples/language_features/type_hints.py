"""
类型提示进阶

展示现代Python类型提示系统的高级用法，包括泛型、协议、类型变量等。
"""

from typing import (
    TypeVar, Generic, Protocol, Union, Optional, Literal, 
    Type, Any, Callable, Iterable, Iterator, Dict, List, Tuple
)
from typing_extensions import TypedDict, Final
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

# 类型变量定义
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
NumericType = TypeVar('NumericType', int, float, complex)


# ============================================================================
# 泛型容器示例
# ============================================================================

class GenericContainer(Generic[T]):
    """泛型容器示例"""
    
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        """添加项目"""
        self._items.append(item)
    
    def get(self, index: int) -> T:
        """获取项目"""
        return self._items[index]
    
    def filter(self, predicate: Callable[[T], bool]) -> 'GenericContainer[T]':
        """过滤项目"""
        result = GenericContainer[T]()
        for item in self._items:
            if predicate(item):
                result.add(item)
        return result
    
    def map(self, func: Callable[[T], K]) -> 'GenericContainer[K]':
        """映射项目"""
        result: GenericContainer[K] = GenericContainer()
        for item in self._items:
            result.add(func(item))
        return result
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __iter__(self) -> Iterator[T]:
        return iter(self._items)


class BoundedContainer(Generic[T]):
    """有界泛型容器"""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self._items: List[T] = []
    
    def add(self, item: T) -> bool:
        """添加项目，返回是否成功"""
        if len(self._items) < self.max_size:
            self._items.append(item)
            return True
        return False
    
    def is_full(self) -> bool:
        """检查是否已满"""
        return len(self._items) >= self.max_size


# ============================================================================
# 协议示例
# ============================================================================

class Drawable(Protocol):
    """可绘制协议"""
    
    def draw(self) -> str:
        """绘制方法"""
        ...
    
    @property
    def area(self) -> float:
        """面积属性"""
        ...


class Comparable(Protocol):
    """可比较协议"""
    
    def __lt__(self, other: 'Comparable') -> bool:
        """小于比较"""
        ...


class Serializable(Protocol):
    """可序列化协议"""
    
    def serialize(self) -> Dict[str, Any]:
        """序列化为字典"""
        ...
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Serializable':
        """从字典反序列化"""
        ...


# 实现协议的具体类
@dataclass
class Rectangle:
    """矩形类（实现Drawable协议）"""
    width: float
    height: float
    
    def draw(self) -> str:
        return f"Rectangle({self.width}x{self.height})"
    
    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass 
class Circle:
    """圆形类（实现Drawable协议）"""
    radius: float
    
    def draw(self) -> str:
        return f"Circle(r={self.radius})"
    
    @property
    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2


# ============================================================================
# 字面量类型示例
# ============================================================================

StatusType = Literal["success", "error", "pending"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]


class ApiResponse(TypedDict):
    """API响应类型"""
    status: StatusType
    data: Optional[Dict[str, Any]]
    message: str
    timestamp: float


class ConfigDict(TypedDict, total=False):
    """配置字典类型（部分字段可选）"""
    host: str
    port: int
    debug: bool  # 可选字段
    timeout: float  # 可选字段


# ============================================================================
# 高级类型组合
# ============================================================================

def process_drawable_items(items: List[Drawable]) -> Dict[str, float]:
    """处理可绘制项目列表"""
    result = {}
    for item in items:
        result[item.draw()] = item.area
    return result


def sort_comparable_items(items: List[T]) -> List[T]:
    """排序可比较项目（类型变量约束）"""
    return sorted(items)


def create_response(
    status: StatusType,
    data: Optional[Dict[str, Any]] = None,
    message: str = ""
) -> ApiResponse:
    """创建API响应"""
    import time
    return {
        "status": status,
        "data": data,
        "message": message,
        "timestamp": time.time()
    }


# ============================================================================
# 函数重载示例
# ============================================================================

from typing import overload

class Calculator:
    """计算器类（函数重载示例）"""
    
    @overload
    def add(self, x: int, y: int) -> int: ...
    
    @overload
    def add(self, x: float, y: float) -> float: ...
    
    @overload
    def add(self, x: str, y: str) -> str: ...
    
    def add(self, x: Union[int, float, str], y: Union[int, float, str]) -> Union[int, float, str]:
        """加法运算（支持多种类型）"""
        return x + y  # type: ignore


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="generic_container_example",
    category=ExampleCategory.TYPE_HINTS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="泛型容器类型提示示例",
    tags=["generics", "container", "type-safety"]
)
@demo(title="泛型容器示例")
def generic_container_example():
    """展示泛型容器的用法"""
    
    # 创建整数容器
    int_container: GenericContainer[int] = GenericContainer()
    int_container.add(1)
    int_container.add(2)
    int_container.add(3)
    
    print("整数容器:", list(int_container))
    
    # 过滤偶数
    even_container = int_container.filter(lambda x: x % 2 == 0)
    print("偶数容器:", list(even_container))
    
    # 映射为字符串
    str_container = int_container.map(lambda x: f"number_{x}")
    print("字符串容器:", list(str_container))
    
    # 创建字符串容器
    string_container: GenericContainer[str] = GenericContainer()
    string_container.add("hello")
    string_container.add("world")
    string_container.add("python")
    
    print("字符串容器:", list(string_container))
    
    # 映射为长度
    length_container = string_container.map(len)
    print("长度容器:", list(length_container))


@example(
    name="protocol_example",
    category=ExampleCategory.TYPE_HINTS,
    difficulty=DifficultyLevel.ADVANCED,
    description="协议类型提示示例",
    tags=["protocols", "duck-typing", "interfaces"]
)
@demo(title="协议示例")
def protocol_example():
    """展示协议的用法"""
    
    # 创建不同的可绘制对象
    shapes: List[Drawable] = [
        Rectangle(5, 3),
        Circle(2),
        Rectangle(4, 4)
    ]
    
    print("可绘制对象:")
    for shape in shapes:
        print(f"  {shape.draw()}: 面积 = {shape.area:.2f}")
    
    # 使用协议作为类型提示
    result = process_drawable_items(shapes)
    print(f"\n处理结果: {result}")
    
    # 演示结构化子类型（duck typing）
    class Triangle:
        def __init__(self, base: float, height: float):
            self.base = base
            self.height = height
        
        def draw(self) -> str:
            return f"Triangle({self.base}x{self.height})"
        
        @property
        def area(self) -> float:
            return 0.5 * self.base * self.height
    
    # Triangle自动符合Drawable协议
    triangle = Triangle(6, 4)
    shapes_with_triangle: List[Drawable] = shapes + [triangle]
    
    print(f"\n包含三角形: {triangle.draw()}: 面积 = {triangle.area:.2f}")


@example(
    name="literal_types_example",
    category=ExampleCategory.TYPE_HINTS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="字面量类型提示示例",
    tags=["literals", "typed-dict", "api-design"]
)
@demo(title="字面量类型示例")
def literal_types_example():
    """展示字面量类型的用法"""
    
    # 创建API响应
    success_response = create_response("success", {"user_id": 123}, "操作成功")
    error_response = create_response("error", None, "用户未找到")
    
    print("API响应示例:")
    print(f"成功响应: {success_response}")
    print(f"错误响应: {error_response}")
    
    # 配置字典示例
    config: ConfigDict = {
        "host": "localhost",
        "port": 8080,
        "debug": True
    }
    
    print(f"\n配置示例: {config}")
    
    # HTTP方法示例
    def handle_request(method: HttpMethod, url: str) -> str:
        return f"处理 {method} 请求到 {url}"
    
    methods: List[HttpMethod] = ["GET", "POST", "PUT", "DELETE"]
    for method in methods:
        result = handle_request(method, "/api/users")
        print(f"  {result}")


@example(
    name="function_overload_example",
    category=ExampleCategory.TYPE_HINTS,
    difficulty=DifficultyLevel.ADVANCED,
    description="函数重载类型提示示例",
    tags=["overload", "function-types", "polymorphism"]
)
@demo(title="函数重载示例")
def function_overload_example():
    """展示函数重载的用法"""
    
    calc = Calculator()
    
    # 整数加法
    int_result = calc.add(5, 3)
    print(f"整数加法: 5 + 3 = {int_result} (类型: {type(int_result).__name__})")
    
    # 浮点数加法
    float_result = calc.add(2.5, 3.7)
    print(f"浮点数加法: 2.5 + 3.7 = {float_result} (类型: {type(float_result).__name__})")
    
    # 字符串加法
    str_result = calc.add("Hello", " World")
    print(f"字符串加法: 'Hello' + ' World' = '{str_result}' (类型: {type(str_result).__name__})")


@example(
    name="advanced_type_constraints_example",
    category=ExampleCategory.TYPE_HINTS,
    difficulty=DifficultyLevel.EXPERT,
    description="高级类型约束示例",
    tags=["type-variables", "constraints", "bounds"]
)
@demo(title="高级类型约束示例")
def advanced_type_constraints_example():
    """展示高级类型约束的用法"""
    
    def numeric_add(x: NumericType, y: NumericType) -> NumericType:
        """数值类型加法（类型变量约束）"""
        return x + y  # type: ignore
    
    # 整数
    int_result = numeric_add(5, 3)
    print(f"整数: {int_result} (类型: {type(int_result).__name__})")
    
    # 浮点数
    float_result = numeric_add(2.5, 3.7)
    print(f"浮点数: {float_result} (类型: {type(float_result).__name__})")
    
    # 复数
    complex_result = numeric_add(1+2j, 3+4j)
    print(f"复数: {complex_result} (类型: {type(complex_result).__name__})")
    
    # 有界容器示例
    bounded_container: BoundedContainer[str] = BoundedContainer(3)
    
    items = ["apple", "banana", "cherry", "date"]
    print(f"\n有界容器 (最大容量: 3):")
    
    for item in items:
        success = bounded_container.add(item)
        status = "成功" if success else "失败（容器已满）"
        print(f"  添加 '{item}': {status}")


# 导出的类和函数
__all__ = [
    "GenericContainer",
    "BoundedContainer",
    "Drawable",
    "Comparable", 
    "Serializable",
    "Rectangle",
    "Circle",
    "StatusType",
    "LogLevel",
    "HttpMethod",
    "ApiResponse",
    "ConfigDict",
    "Calculator",
    "process_drawable_items",
    "sort_comparable_items",
    "create_response",
    "generic_container_example",
    "protocol_example",
    "literal_types_example",
    "function_overload_example",
    "advanced_type_constraints_example"
]