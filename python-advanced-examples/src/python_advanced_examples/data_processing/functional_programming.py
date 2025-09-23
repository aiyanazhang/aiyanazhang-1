"""
函数式编程模式示例

展示函数式编程的核心概念：
- 高阶函数
- 柯里化
- 函数组合
- 不可变数据结构
- Monad模式
- 惰性求值
"""

from typing import Any, Callable, TypeVar, Generic, Optional, Union, Iterator, List, Tuple
from functools import wraps, reduce, partial
from abc import ABC, abstractmethod
import itertools
from collections.abc import Iterable

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

class FunctionalUtils:
    """函数式编程工具类"""
    
    @staticmethod
    def compose(*functions: Callable) -> Callable:
        """函数组合：将多个函数组合成一个函数"""
        if not functions:
            return lambda x: x
        
        def composed(arg):
            result = arg
            for func in reversed(functions):
                result = func(result)
            return result
        
        return composed
    
    @staticmethod
    def pipe(*functions: Callable) -> Callable:
        """管道操作：从左到右应用函数"""
        if not functions:
            return lambda x: x
        
        def piped(arg):
            result = arg
            for func in functions:
                result = func(result)
            return result
        
        return piped
    
    @staticmethod
    def curry(func: Callable) -> Callable:
        """柯里化：将多参数函数转换为单参数函数序列"""
        def curried(*args, **kwargs):
            if len(args) + len(kwargs) >= func.__code__.co_argcount:
                return func(*args, **kwargs)
            return lambda *more_args, **more_kwargs: curried(
                *(args + more_args), **{**kwargs, **more_kwargs}
            )
        return curried
    
    @staticmethod
    def memoize(func: Callable) -> Callable:
        """记忆化：缓存函数结果"""
        cache = {}
        
        @wraps(func)
        def memoized(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        
        return memoized
    
    @staticmethod
    def partial_apply(func: Callable, *args, **kwargs) -> Callable:
        """部分应用：固定函数的部分参数"""
        return partial(func, *args, **kwargs)


class Monad(Generic[T], ABC):
    """Monad抽象基类"""
    
    def __init__(self, value: T):
        self._value = value
    
    @abstractmethod
    def bind(self, func: Callable[[T], 'Monad[U]']) -> 'Monad[U]':
        """绑定操作（flatMap）"""
        pass
    
    @classmethod
    @abstractmethod
    def unit(cls, value: T) -> 'Monad[T]':
        """单位操作（return）"""
        pass
    
    def map(self, func: Callable[[T], U]) -> 'Monad[U]':
        """映射操作"""
        return self.bind(lambda x: self.__class__.unit(func(x)))
    
    @property
    def value(self) -> T:
        return self._value


class Maybe(Monad[T]):
    """Maybe Monad - 处理可能为空的值"""
    
    def __init__(self, value: Optional[T]):
        super().__init__(value)
        self._is_nothing = value is None
    
    def bind(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self._is_nothing:
            return Maybe(None)
        return func(self._value)
    
    @classmethod
    def unit(cls, value: T) -> 'Maybe[T]':
        return cls(value)
    
    @classmethod
    def nothing(cls) -> 'Maybe[None]':
        return cls(None)
    
    def is_nothing(self) -> bool:
        return self._is_nothing
    
    def get_or_else(self, default: T) -> T:
        return default if self._is_nothing else self._value
    
    def __repr__(self) -> str:
        return f"Nothing" if self._is_nothing else f"Just({self._value})"


class Either(Generic[T, U]):
    """Either类型 - 表示两种可能的值之一"""
    
    def __init__(self, value: Union[T, U], is_left: bool = False):
        self._value = value
        self._is_left = is_left
    
    @classmethod
    def left(cls, value: T) -> 'Either[T, U]':
        """创建Left值（通常表示错误）"""
        return cls(value, is_left=True)
    
    @classmethod
    def right(cls, value: U) -> 'Either[T, U]':
        """创建Right值（通常表示成功）"""
        return cls(value, is_left=False)
    
    def is_left(self) -> bool:
        return self._is_left
    
    def is_right(self) -> bool:
        return not self._is_left
    
    def map(self, func: Callable[[U], V]) -> 'Either[T, V]':
        """对Right值应用函数"""
        if self._is_left:
            return Either.left(self._value)
        return Either.right(func(self._value))
    
    def flat_map(self, func: Callable[[U], 'Either[T, V]']) -> 'Either[T, V]':
        """绑定操作"""
        if self._is_left:
            return Either.left(self._value)
        return func(self._value)
    
    def get_or_else(self, default: U) -> U:
        return default if self._is_left else self._value
    
    @property
    def value(self) -> Union[T, U]:
        return self._value
    
    def __repr__(self) -> str:
        side = "Left" if self._is_left else "Right"
        return f"{side}({self._value})"


class FunctionComposition:
    """函数组合示例"""
    
    @staticmethod
    def create_pipeline(*operations: Callable) -> Callable:
        """创建数据处理管道"""
        return FunctionalUtils.pipe(*operations)
    
    @staticmethod
    def create_transformer(
        validator: Callable[[Any], bool],
        transformer: Callable[[Any], Any],
        error_handler: Callable[[Any], Any] = lambda x: x
    ) -> Callable:
        """创建带验证的转换器"""
        def transform(data):
            if validator(data):
                return transformer(data)
            return error_handler(data)
        return transform
    
    @classmethod
    def example_data_pipeline(cls):
        """数据处理管道示例"""
        # 定义各个处理步骤
        validate_number = lambda x: isinstance(x, (int, float))
        square = lambda x: x ** 2
        add_ten = lambda x: x + 10
        to_string = lambda x: f"Result: {x}"
        
        # 创建管道
        pipeline = cls.create_pipeline(
            lambda x: x if validate_number(x) else 0,
            square,
            add_ten,
            to_string
        )
        
        return pipeline


class CurryingExample:
    """柯里化示例"""
    
    @staticmethod
    @FunctionalUtils.curry
    def multiply_three_numbers(a: float, b: float, c: float) -> float:
        """三个数相乘"""
        return a * b * c
    
    @staticmethod
    @FunctionalUtils.curry
    def create_formatter(prefix: str, suffix: str, content: str) -> str:
        """创建格式化器"""
        return f"{prefix}{content}{suffix}"
    
    @classmethod
    def demonstrate_currying(cls):
        """演示柯里化用法"""
        # 部分应用
        double = cls.multiply_three_numbers(2)
        quadruple = double(2)
        
        # 创建专用格式化器
        html_formatter = cls.create_formatter("<p>", "</p>")
        bracket_formatter = cls.create_formatter("[", "]")
        
        return {
            'quadruple_5': quadruple(5),  # 2 * 2 * 5 = 20
            'html_hello': html_formatter("Hello"),
            'bracket_world': bracket_formatter("World")
        }


class LazyEvaluation:
    """惰性求值示例"""
    
    @staticmethod
    def lazy_range(start: int, end: int, step: int = 1) -> Iterator[int]:
        """惰性范围生成器"""
        current = start
        while current < end:
            yield current
            current += step
    
    @staticmethod
    def lazy_fibonacci() -> Iterator[int]:
        """惰性斐波那契数列"""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    @staticmethod
    def lazy_map(func: Callable[[T], U], iterable: Iterable[T]) -> Iterator[U]:
        """惰性映射"""
        for item in iterable:
            yield func(item)
    
    @staticmethod
    def lazy_filter(predicate: Callable[[T], bool], iterable: Iterable[T]) -> Iterator[T]:
        """惰性过滤"""
        for item in iterable:
            if predicate(item):
                yield item
    
    @staticmethod
    def take(n: int, iterable: Iterable[T]) -> List[T]:
        """取前n个元素"""
        return list(itertools.islice(iterable, n))
    
    @classmethod
    def demonstrate_lazy_evaluation(cls):
        """演示惰性求值"""
        # 创建惰性序列
        numbers = cls.lazy_range(1, 1000)
        squares = cls.lazy_map(lambda x: x ** 2, numbers)
        even_squares = cls.lazy_filter(lambda x: x % 2 == 0, squares)
        
        # 只在需要时才计算
        first_10_even_squares = cls.take(10, even_squares)
        
        # 斐波那契数列
        fib = cls.lazy_fibonacci()
        first_20_fib = cls.take(20, fib)
        
        return {
            'first_10_even_squares': first_10_even_squares,
            'first_20_fibonacci': first_20_fib
        }


# 使用示例
def demonstrate_functional_programming():
    """演示函数式编程概念"""
    print("=== 函数式编程示例 ===\n")
    
    # 1. 函数组合
    print("1. 函数组合:")
    add_one = lambda x: x + 1
    multiply_by_two = lambda x: x * 2
    composed = FunctionalUtils.compose(multiply_by_two, add_one)
    print(f"composed(5) = {composed(5)}")  # (5 + 1) * 2 = 12
    
    # 2. 管道操作
    print("\n2. 管道操作:")
    piped = FunctionalUtils.pipe(add_one, multiply_by_two)
    print(f"piped(5) = {piped(5)}")  # (5 + 1) * 2 = 12
    
    # 3. Maybe Monad
    print("\n3. Maybe Monad:")
    maybe_value = Maybe.unit(10)
    maybe_none = Maybe.nothing()
    
    result1 = maybe_value.map(lambda x: x * 2).map(lambda x: x + 1)
    result2 = maybe_none.map(lambda x: x * 2).map(lambda x: x + 1)
    
    print(f"Maybe(10) -> {result1}")
    print(f"Maybe(None) -> {result2}")
    
    # 4. Either类型
    print("\n4. Either类型:")
    success = Either.right(42)
    error = Either.left("Error occurred")
    
    success_result = success.map(lambda x: x * 2)
    error_result = error.map(lambda x: x * 2)
    
    print(f"Right(42) -> {success_result}")
    print(f"Left('Error') -> {error_result}")
    
    # 5. 柯里化
    print("\n5. 柯里化:")
    curry_demo = CurryingExample.demonstrate_currying()
    for key, value in curry_demo.items():
        print(f"{key}: {value}")
    
    # 6. 惰性求值
    print("\n6. 惰性求值:")
    lazy_demo = LazyEvaluation.demonstrate_lazy_evaluation()
    print(f"前10个偶数平方: {lazy_demo['first_10_even_squares']}")
    print(f"前20个斐波那契数: {lazy_demo['first_20_fibonacci']}")


if __name__ == "__main__":
    demonstrate_functional_programming()