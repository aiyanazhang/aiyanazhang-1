"""
元类应用示例

展示Python元类的高级用法，包括单例模式、注册器模式、属性验证等。
"""

import threading
import weakref
from typing import Any, Dict, Type, Optional, Callable, Union
from functools import wraps

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel


class SingletonMeta(type):
    """单例模式元类"""
    
    _instances: Dict[Type, Any] = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        """创建实例时调用"""
        if cls not in cls._instances:
            with cls._lock:
                # 双重检查锁定
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        
        return cls._instances[cls]
    
    def clear_instance(cls):
        """清除单例实例（用于测试）"""
        if cls in cls._instances:
            del cls._instances[cls]


class RegistryMeta(type):
    """注册器模式元类"""
    
    registry: Dict[str, Type] = {}
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        """创建类时调用"""
        # 从kwargs中获取注册名称
        registry_name = kwargs.pop('registry_name', None)
        
        # 创建类
        cls = super().__new__(mcs, name, bases, namespace)
        
        # 注册类
        if registry_name:
            mcs.registry[registry_name] = cls
            cls._registry_name = registry_name
        
        return cls
    
    @classmethod
    def get_class(mcs, name: str) -> Optional[Type]:
        """根据名称获取类"""
        return mcs.registry.get(name)
    
    @classmethod
    def list_classes(mcs) -> Dict[str, Type]:
        """列出所有注册的类"""
        return mcs.registry.copy()


class AttributeValidationMeta(type):
    """属性验证元类"""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        """创建类时调用"""
        # 收集需要验证的属性
        validated_attrs = {}
        
        for attr_name, attr_value in namespace.items():
            if hasattr(attr_value, '_validation_rules'):
                validated_attrs[attr_name] = attr_value._validation_rules
        
        # 如果有验证属性，修改__init__方法
        if validated_attrs:
            original_init = namespace.get('__init__')
            
            def validated_init(self, *args, **kwargs):
                # 调用原始__init__
                if original_init:
                    original_init(self, *args, **kwargs)
                
                # 验证属性
                for attr_name, rules in validated_attrs.items():
                    if hasattr(self, attr_name):
                        value = getattr(self, attr_name)
                        mcs._validate_attribute(attr_name, value, rules)
            
            namespace['__init__'] = validated_init
        
        return super().__new__(mcs, name, bases, namespace)
    
    @staticmethod
    def _validate_attribute(attr_name: str, value: Any, rules: Dict[str, Any]):
        """验证属性值"""
        for rule_name, rule_value in rules.items():
            if rule_name == 'type' and not isinstance(value, rule_value):
                raise TypeError(f"Attribute {attr_name} must be of type {rule_value.__name__}")
            elif rule_name == 'range' and not (rule_value[0] <= value <= rule_value[1]):
                raise ValueError(f"Attribute {attr_name} must be in range {rule_value}")
            elif rule_name == 'min_length' and len(value) < rule_value:
                raise ValueError(f"Attribute {attr_name} must have minimum length {rule_value}")


class AutoPropertyMeta(type):
    """自动属性生成元类"""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        """创建类时调用"""
        # 查找带有特殊标记的属性
        auto_properties = {}
        
        for attr_name, attr_value in list(namespace.items()):
            if isinstance(attr_value, AutoProperty):
                auto_properties[attr_name] = attr_value
                # 移除原始属性
                del namespace[attr_name]
        
        # 创建类
        cls = super().__new__(mcs, name, bases, namespace)
        
        # 为每个auto property生成实际的property
        for attr_name, auto_prop in auto_properties.items():
            private_name = f'_{attr_name}'
            
            def make_getter(pname):
                def getter(self):
                    return getattr(self, pname, None)
                return getter
            
            def make_setter(pname, validator):
                def setter(self, value):
                    if validator:
                        validator(value)
                    setattr(self, pname, value)
                return setter
            
            # 创建property
            prop = property(
                make_getter(private_name),
                make_setter(private_name, auto_prop.validator) if auto_prop.writable else None,
                doc=auto_prop.doc
            )
            
            setattr(cls, attr_name, prop)
        
        return cls


class AutoProperty:
    """自动属性描述符"""
    
    def __init__(self, doc: str = None, writable: bool = True, validator: Callable = None):
        self.doc = doc
        self.writable = writable
        self.validator = validator


def validated_attribute(**rules):
    """属性验证装饰器"""
    def decorator(attr):
        attr._validation_rules = rules
        return attr
    return decorator


# ============================================================================
# 示例类
# ============================================================================

class ConfigManager(metaclass=SingletonMeta):
    """配置管理器（单例模式）"""
    
    def __init__(self):
        self.settings = {}
        self.initialized = True
    
    def set_setting(self, key: str, value: Any):
        """设置配置项"""
        self.settings[key] = value
    
    def get_setting(self, key: str, default: Any = None):
        """获取配置项"""
        return self.settings.get(key, default)
    
    def __repr__(self):
        return f"ConfigManager(settings={len(self.settings)})"


class DatabaseAdapter(metaclass=RegistryMeta, registry_name="database"):
    """数据库适配器基类"""
    
    def connect(self):
        raise NotImplementedError
    
    def query(self, sql: str):
        raise NotImplementedError


class MySQLAdapter(DatabaseAdapter, metaclass=RegistryMeta, registry_name="mysql"):
    """MySQL适配器"""
    
    def connect(self):
        return "Connected to MySQL"
    
    def query(self, sql: str):
        return f"MySQL query: {sql}"


class PostgreSQLAdapter(DatabaseAdapter, metaclass=RegistryMeta, registry_name="postgresql"):
    """PostgreSQL适配器"""
    
    def connect(self):
        return "Connected to PostgreSQL"
    
    def query(self, sql: str):
        return f"PostgreSQL query: {sql}"


class User(metaclass=AttributeValidationMeta):
    """用户类（带属性验证）"""
    
    @validated_attribute(type=str, min_length=2)
    def username(self):
        pass
    
    @validated_attribute(type=int, range=(0, 150))
    def age(self):
        pass
    
    @validated_attribute(type=str, min_length=5)
    def email(self):
        pass
    
    def __init__(self, username: str, age: int, email: str):
        self.username = username
        self.age = age
        self.email = email
    
    def __repr__(self):
        return f"User(username='{self.username}', age={self.age}, email='{self.email}')"


class Product(metaclass=AutoPropertyMeta):
    """产品类（自动属性生成）"""
    
    # 自动生成getter/setter
    name = AutoProperty(doc="Product name", writable=True)
    price = AutoProperty(
        doc="Product price", 
        writable=True,
        validator=lambda x: x >= 0 or ValueError("Price must be non-negative")
    )
    
    # 只读属性
    id = AutoProperty(doc="Product ID", writable=False)
    
    def __init__(self, id: str, name: str, price: float):
        self._id = id
        self.name = name
        self.price = price
    
    def __repr__(self):
        return f"Product(id='{self.id}', name='{self.name}', price={self.price})"


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="singleton_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="单例模式元类示例",
    tags=["metaclass", "singleton", "design-pattern"]
)
@demo(title="单例模式元类示例")
def singleton_example():
    """展示单例模式元类的使用"""
    
    print("单例模式元类示例")
    
    # 创建多个ConfigManager实例
    print("\n创建多个ConfigManager实例:")
    
    config1 = ConfigManager()
    config2 = ConfigManager()
    config3 = ConfigManager()
    
    print(f"config1 id: {id(config1)}")
    print(f"config2 id: {id(config2)}")
    print(f"config3 id: {id(config3)}")
    
    print(f"config1 is config2: {config1 is config2}")
    print(f"config2 is config3: {config2 is config3}")
    
    # 测试状态共享
    print(f"\n测试状态共享:")
    
    config1.set_setting("database_url", "postgresql://localhost:5432/mydb")
    config1.set_setting("debug", True)
    
    print(f"config1 设置: {config1.settings}")
    print(f"config2 设置: {config2.settings}")
    print(f"config3 设置: {config3.settings}")
    
    # 通过config2修改设置
    config2.set_setting("debug", False)
    config2.set_setting("log_level", "INFO")
    
    print(f"\n通过config2修改后:")
    print(f"config1 设置: {config1.settings}")
    print(f"config3 设置: {config3.settings}")
    
    print(f"\n单例模式确保:")
    print("• 只有一个实例存在")
    print("• 全局状态共享")
    print("• 避免重复初始化")
    
    # 清理（用于测试）
    ConfigManager.clear_instance()


@example(
    name="registry_metaclass_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="注册器模式元类示例",
    tags=["metaclass", "registry", "factory-pattern"]
)
@demo(title="注册器模式元类示例")
def registry_metaclass_example():
    """展示注册器模式元类的使用"""
    
    print("注册器模式元类示例")
    
    # 显示注册的类
    print(f"\n注册的适配器类:")
    registry = RegistryMeta.list_classes()
    
    for name, cls in registry.items():
        print(f"  {name}: {cls.__name__}")
    
    # 动态创建适配器实例
    print(f"\n动态创建适配器实例:")
    
    adapter_types = ["mysql", "postgresql", "database"]
    
    for adapter_type in adapter_types:
        adapter_class = RegistryMeta.get_class(adapter_type)
        
        if adapter_class:
            try:
                adapter = adapter_class()
                connect_result = adapter.connect()
                query_result = adapter.query("SELECT * FROM users")
                
                print(f"  {adapter_type}:")
                print(f"    连接: {connect_result}")
                print(f"    查询: {query_result}")
                
            except NotImplementedError:
                print(f"  {adapter_type}: 基类，无法实例化")
        else:
            print(f"  {adapter_type}: 未找到适配器")
    
    # 工厂函数示例
    def create_adapter(adapter_type: str):
        """适配器工厂函数"""
        adapter_class = RegistryMeta.get_class(adapter_type)
        if adapter_class and adapter_class != DatabaseAdapter:
            return adapter_class()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    print(f"\n使用工厂函数:")
    
    try:
        mysql_adapter = create_adapter("mysql")
        print(f"MySQL适配器: {mysql_adapter.connect()}")
        
        pg_adapter = create_adapter("postgresql")
        print(f"PostgreSQL适配器: {pg_adapter.connect()}")
        
        # 尝试创建未知类型
        unknown_adapter = create_adapter("oracle")
        
    except ValueError as e:
        print(f"错误: {e}")
    
    print(f"\n注册器模式优势:")
    print("• 自动类注册")
    print("• 动态类发现")
    print("• 工厂模式实现")
    print("• 插件系统基础")


@example(
    name="validation_metaclass_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.ADVANCED,
    description="属性验证元类示例",
    tags=["metaclass", "validation", "data-validation"]
)
@demo(title="属性验证元类示例")
def validation_metaclass_example():
    """展示属性验证元类的使用"""
    
    print("属性验证元类示例")
    
    # 创建有效用户
    print(f"\n创建有效用户:")
    
    try:
        user1 = User("alice", 25, "alice@example.com")
        print(f"✅ 用户创建成功: {user1}")
        
        user2 = User("bob123", 30, "bob@company.org")
        print(f"✅ 用户创建成功: {user2}")
        
    except Exception as e:
        print(f"❌ 用户创建失败: {e}")
    
    # 测试各种验证失败情况
    print(f"\n测试验证失败情况:")
    
    # 用户名太短
    try:
        invalid_user1 = User("a", 25, "a@example.com")
        print(f"❌ 应该失败但成功了: {invalid_user1}")
    except ValueError as e:
        print(f"✅ 用户名验证失败: {e}")
    
    # 年龄超出范围
    try:
        invalid_user2 = User("alice", 200, "alice@example.com")
        print(f"❌ 应该失败但成功了: {invalid_user2}")
    except ValueError as e:
        print(f"✅ 年龄验证失败: {e}")
    
    # 年龄类型错误
    try:
        invalid_user3 = User("alice", "25", "alice@example.com")
        print(f"❌ 应该失败但成功了: {invalid_user3}")
    except TypeError as e:
        print(f"✅ 年龄类型验证失败: {e}")
    
    # 邮箱太短
    try:
        invalid_user4 = User("alice", 25, "a@b")
        print(f"❌ 应该失败但成功了: {invalid_user4}")
    except ValueError as e:
        print(f"✅ 邮箱验证失败: {e}")
    
    print(f"\n自动属性生成示例:")
    
    # 创建产品
    try:
        product1 = Product("P001", "Laptop", 999.99)
        print(f"✅ 产品创建成功: {product1}")
        
        # 修改属性
        product1.name = "Gaming Laptop"
        product1.price = 1299.99
        
        print(f"✅ 属性修改成功: {product1}")
        
        # 尝试修改只读属性
        # product1.id = "P002"  # 这会失败，因为id是只读的
        
        # 测试价格验证
        product1.price = -100  # 这应该失败
        
    except Exception as e:
        print(f"✅ 价格验证失败: {e}")
    
    print(f"\n元类验证的优势:")
    print("• 声明式验证规则")
    print("• 自动验证注入")
    print("• 类级别的约束")
    print("• 减少重复代码")


# 导出的类和函数
__all__ = [
    "SingletonMeta",
    "RegistryMeta",
    "AttributeValidationMeta",
    "AutoPropertyMeta",
    "AutoProperty",
    "validated_attribute",
    "ConfigManager",
    "DatabaseAdapter",
    "MySQLAdapter",
    "PostgreSQLAdapter",
    "User",
    "Product",
    "singleton_example",
    "registry_metaclass_example",
    "validation_metaclass_example"
]