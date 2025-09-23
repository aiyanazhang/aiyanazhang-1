"""
动态类创建示例

展示Python动态类创建的高级技术，包括类工厂、混入模式、API生成等。
"""

from typing import Any, Dict, List, Type, Callable, Optional
import inspect

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel


class ClassFactory:
    """类工厂"""
    
    @staticmethod
    def create_data_class(class_name: str, fields: Dict[str, Type], base_classes: tuple = ()) -> Type:
        """创建数据类"""
        
        def __init__(self, **kwargs):
            for field_name, field_type in fields.items():
                value = kwargs.get(field_name)
                if value is not None and not isinstance(value, field_type):
                    raise TypeError(f"{field_name} must be of type {field_type.__name__}")
                setattr(self, field_name, value)
        
        def __repr__(self):
            field_strs = [f"{name}={getattr(self, name)!r}" for name in fields.keys()]
            return f"{class_name}({', '.join(field_strs)})"
        
        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return all(getattr(self, name) == getattr(other, name) for name in fields.keys())
        
        # 动态创建类
        namespace = {
            '__init__': __init__,
            '__repr__': __repr__,
            '__eq__': __eq__,
            '_fields': fields
        }
        
        return type(class_name, base_classes, namespace)
    
    @staticmethod
    def create_enum_class(class_name: str, values: List[str]) -> Type:
        """创建枚举类"""
        
        def __init__(self, value):
            if value not in values:
                raise ValueError(f"Invalid value: {value}. Must be one of {values}")
            self.value = value
        
        def __repr__(self):
            return f"{class_name}.{self.value}"
        
        def __eq__(self, other):
            if isinstance(other, str):
                return self.value == other
            return isinstance(other, self.__class__) and self.value == other.value
        
        # 创建类方法
        namespace = {
            '__init__': __init__,
            '__repr__': __repr__,
            '__eq__': __eq__,
            '_values': values
        }
        
        # 添加类常量
        for value in values:
            namespace[value] = lambda v=value: type.__call__(cls, v)
        
        cls = type(class_name, (), namespace)
        
        # 设置类常量
        for value in values:
            setattr(cls, value, cls(value))
        
        return cls


class DynamicMixin:
    """动态混入生成器"""
    
    @staticmethod
    def create_serializable_mixin() -> Type:
        """创建序列化混入"""
        
        def to_dict(self) -> Dict[str, Any]:
            """转换为字典"""
            result = {}
            for attr_name in dir(self):
                if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                    result[attr_name] = getattr(self, attr_name)
            return result
        
        def from_dict(cls, data: Dict[str, Any]):
            """从字典创建实例"""
            instance = cls.__new__(cls)
            for key, value in data.items():
                setattr(instance, key, value)
            return instance
        
        def to_json(self) -> str:
            """转换为JSON字符串"""
            import json
            return json.dumps(self.to_dict())
        
        @classmethod
        def from_json(cls, json_str: str):
            """从JSON字符串创建实例"""
            import json
            data = json.loads(json_str)
            return cls.from_dict(data)
        
        return type('SerializableMixin', (), {
            'to_dict': to_dict,
            'from_dict': classmethod(from_dict),
            'to_json': to_json,
            'from_json': from_json
        })
    
    @staticmethod
    def create_observable_mixin() -> Type:
        """创建可观察混入"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._observers = []
        
        def add_observer(self, observer: Callable):
            """添加观察者"""
            if observer not in self._observers:
                self._observers.append(observer)
        
        def remove_observer(self, observer: Callable):
            """移除观察者"""
            if observer in self._observers:
                self._observers.remove(observer)
        
        def notify_observers(self, event: str, **kwargs):
            """通知观察者"""
            for observer in self._observers:
                observer(self, event, **kwargs)
        
        def __setattr__(self, name, value):
            """重写属性设置以触发通知"""
            if hasattr(self, '_observers') and not name.startswith('_'):
                old_value = getattr(self, name, None)
                super().__setattr__(name, value)
                self.notify_observers('attribute_changed', 
                                    attribute=name, 
                                    old_value=old_value, 
                                    new_value=value)
            else:
                super().__setattr__(name, value)
        
        return type('ObservableMixin', (), {
            '__init__': __init__,
            'add_observer': add_observer,
            'remove_observer': remove_observer,
            'notify_observers': notify_observers,
            '__setattr__': __setattr__
        })


class APIGenerator:
    """API类生成器"""
    
    @staticmethod
    def create_rest_client(base_url: str, endpoints: Dict[str, str]) -> Type:
        """创建REST客户端类"""
        
        def __init__(self, auth_token: Optional[str] = None):
            self.base_url = base_url.rstrip('/')
            self.auth_token = auth_token
        
        def _make_request(self, method: str, endpoint: str, **kwargs):
            """模拟HTTP请求"""
            url = f"{self.base_url}{endpoint}"
            headers = kwargs.get('headers', {})
            
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"
            
            # 模拟请求结果
            return {
                'method': method,
                'url': url,
                'headers': headers,
                'data': kwargs.get('data'),
                'status': 200,
                'response': f"Mock response for {method} {url}"
            }
        
        # 为每个端点创建方法
        namespace = {
            '__init__': __init__,
            '_make_request': _make_request,
            '_endpoints': endpoints
        }
        
        for method_name, endpoint in endpoints.items():
            def create_method(ep):
                def api_method(self, **kwargs):
                    http_method = 'GET'
                    if 'create' in method_name.lower() or 'post' in method_name.lower():
                        http_method = 'POST'
                    elif 'update' in method_name.lower() or 'put' in method_name.lower():
                        http_method = 'PUT'
                    elif 'delete' in method_name.lower():
                        http_method = 'DELETE'
                    
                    return self._make_request(http_method, ep, **kwargs)
                return api_method
            
            namespace[method_name] = create_method(endpoint)
        
        return type('RESTClient', (), namespace)
    
    @staticmethod
    def create_model_class(model_name: str, schema: Dict[str, Dict[str, Any]]) -> Type:
        """根据模式创建模型类"""
        
        def __init__(self, **kwargs):
            for field_name, field_config in schema.items():
                field_type = field_config.get('type', str)
                default_value = field_config.get('default')
                required = field_config.get('required', False)
                
                value = kwargs.get(field_name, default_value)
                
                if required and value is None:
                    raise ValueError(f"Field '{field_name}' is required")
                
                if value is not None:
                    # 类型转换
                    if field_type == int and isinstance(value, str) and value.isdigit():
                        value = int(value)
                    elif field_type == float and isinstance(value, (str, int)):
                        value = float(value)
                    elif field_type == bool and isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    
                    # 类型检查
                    if not isinstance(value, field_type):
                        raise TypeError(f"Field '{field_name}' must be of type {field_type.__name__}")
                
                setattr(self, field_name, value)
        
        def validate(self):
            """验证模型数据"""
            errors = []
            
            for field_name, field_config in schema.items():
                value = getattr(self, field_name, None)
                
                # 检查必填字段
                if field_config.get('required', False) and value is None:
                    errors.append(f"Field '{field_name}' is required")
                
                # 检查值范围
                if value is not None:
                    min_val = field_config.get('min')
                    max_val = field_config.get('max')
                    
                    if min_val is not None and value < min_val:
                        errors.append(f"Field '{field_name}' must be >= {min_val}")
                    
                    if max_val is not None and value > max_val:
                        errors.append(f"Field '{field_name}' must be <= {max_val}")
            
            return errors
        
        def __repr__(self):
            field_strs = []
            for field_name in schema.keys():
                value = getattr(self, field_name, None)
                field_strs.append(f"{field_name}={value!r}")
            return f"{model_name}({', '.join(field_strs)})"
        
        return type(model_name, (), {
            '__init__': __init__,
            'validate': validate,
            '__repr__': __repr__,
            '_schema': schema
        })


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="dynamic_class_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.ADVANCED,
    description="动态类创建示例",
    tags=["dynamic", "class-factory", "metaprogramming"]
)
@demo(title="动态类创建示例")
def dynamic_class_example():
    """展示动态类创建的用法"""
    
    print("动态类创建示例")
    
    # 1. 创建数据类
    print("\n1. 动态创建数据类:")
    
    Person = ClassFactory.create_data_class(
        'Person',
        {
            'name': str,
            'age': int,
            'email': str
        }
    )
    
    person1 = Person(name="Alice", age=30, email="alice@example.com")
    person2 = Person(name="Bob", age=25, email="bob@example.com")
    
    print(f"Person类: {Person}")
    print(f"实例1: {person1}")
    print(f"实例2: {person2}")
    print(f"相等性: {person1 == person2}")
    
    # 2. 创建枚举类
    print("\n2. 动态创建枚举类:")
    
    Status = ClassFactory.create_enum_class('Status', ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED'])
    
    status1 = Status.PENDING
    status2 = Status.RUNNING
    
    print(f"Status类: {Status}")
    print(f"状态1: {status1}")
    print(f"状态2: {status2}")
    print(f"比较: {status1 == 'PENDING'}")
    print(f"所有状态: {Status._values}")
    
    # 3. 创建产品类（结合数据类和枚举）
    print("\n3. 结合使用:")
    
    Product = ClassFactory.create_data_class(
        'Product',
        {
            'name': str,
            'price': float,
            'status': type(Status.PENDING)  # 使用枚举类型
        }
    )
    
    product = Product(name="Laptop", price=999.99, status=Status.PENDING)
    print(f"产品: {product}")
    
    # 验证类型
    try:
        invalid_product = Product(name="Mouse", price="invalid", status=Status.COMPLETED)
    except TypeError as e:
        print(f"✅ 类型验证: {e}")


@example(
    name="mixin_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.ADVANCED,
    description="动态混入模式示例",
    tags=["mixin", "composition", "observer-pattern"]
)
@demo(title="动态混入模式示例")
def mixin_example():
    """展示动态混入模式的用法"""
    
    print("动态混入模式示例")
    
    # 创建混入类
    SerializableMixin = DynamicMixin.create_serializable_mixin()
    ObservableMixin = DynamicMixin.create_observable_mixin()
    
    # 创建使用混入的类
    class User(SerializableMixin, ObservableMixin):
        def __init__(self, name: str, email: str):
            super().__init__()
            self.name = name
            self.email = email
    
    print("\n1. 序列化混入测试:")
    
    user = User("Alice", "alice@example.com")
    
    # 测试序列化
    user_dict = user.to_dict()
    print(f"转换为字典: {user_dict}")
    
    user_json = user.to_json()
    print(f"转换为JSON: {user_json}")
    
    # 测试反序列化
    user_from_dict = User.from_dict({'name': 'Bob', 'email': 'bob@example.com'})
    print(f"从字典创建: {user_from_dict.name}, {user_from_dict.email}")
    
    user_from_json = User.from_json('{"name": "Charlie", "email": "charlie@example.com"}')
    print(f"从JSON创建: {user_from_json.name}, {user_from_json.email}")
    
    # 2. 观察者混入测试
    print("\n2. 观察者混入测试:")
    
    def user_observer(obj, event, **kwargs):
        """用户观察者"""
        if event == 'attribute_changed':
            print(f"  观察到变化: {kwargs['attribute']} "
                  f"从 '{kwargs['old_value']}' 改为 '{kwargs['new_value']}'")
    
    # 添加观察者
    user.add_observer(user_observer)
    
    print("修改用户属性:")
    user.name = "Alice Smith"
    user.email = "alice.smith@example.com"
    
    # 移除观察者
    user.remove_observer(user_observer)
    print("移除观察者后修改:")
    user.name = "Alice Johnson"  # 不会触发观察者
    
    print("\n混入模式的优势:")
    print("• 代码重用和组合")
    print("• 功能模块化")
    print("• 动态行为添加")
    print("• 避免深层继承")


@example(
    name="api_generator_example",
    category=ExampleCategory.METAPROGRAMMING,
    difficulty=DifficultyLevel.EXPERT,
    description="API生成器示例",
    tags=["api", "code-generation", "rest", "models"]
)
@demo(title="API生成器示例")
def api_generator_example():
    """展示API生成器的用法"""
    
    print("API生成器示例")
    
    # 1. 创建REST客户端
    print("\n1. 动态创建REST客户端:")
    
    UserAPI = APIGenerator.create_rest_client(
        'https://api.example.com',
        {
            'get_users': '/users',
            'get_user': '/users/{id}',
            'create_user': '/users',
            'update_user': '/users/{id}',
            'delete_user': '/users/{id}'
        }
    )
    
    api_client = UserAPI(auth_token="abc123")
    
    # 使用生成的API方法
    print("使用生成的API方法:")
    
    result1 = api_client.get_users()
    print(f"获取用户列表: {result1['method']} {result1['url']}")
    
    result2 = api_client.create_user(data={'name': 'Alice', 'email': 'alice@example.com'})
    print(f"创建用户: {result2['method']} {result2['url']}")
    print(f"请求数据: {result2['data']}")
    
    result3 = api_client.update_user(data={'name': 'Alice Smith'})
    print(f"更新用户: {result3['method']} {result3['url']}")
    
    # 2. 创建模型类
    print("\n2. 动态创建模型类:")
    
    User = APIGenerator.create_model_class(
        'User',
        {
            'id': {'type': int, 'required': False},
            'name': {'type': str, 'required': True, 'min': 2},
            'email': {'type': str, 'required': True},
            'age': {'type': int, 'required': False, 'min': 0, 'max': 150},
            'active': {'type': bool, 'default': True}
        }
    )
    
    # 创建有效用户
    try:
        user1 = User(name="Alice", email="alice@example.com", age=30)
        print(f"✅ 用户创建成功: {user1}")
        
        # 验证用户数据
        errors = user1.validate()
        if errors:
            print(f"验证错误: {errors}")
        else:
            print("✅ 用户数据验证通过")
        
    except Exception as e:
        print(f"❌ 用户创建失败: {e}")
    
    # 测试验证失败
    print("\n测试验证:")
    
    try:
        invalid_user = User(email="bob@example.com", age=200)  # 缺少name，age超出范围
        errors = invalid_user.validate()
        print(f"验证错误: {errors}")
        
    except Exception as e:
        print(f"创建时就失败: {e}")
    
    # 3. 类型转换测试
    print("\n3. 自动类型转换:")
    
    user2 = User(name="Charlie", email="charlie@example.com", age="25", active="true")
    print(f"类型转换后: {user2}")
    print(f"age类型: {type(user2.age)}, active类型: {type(user2.active)}")
    
    print("\nAPI生成器的优势:")
    print("• 自动生成API客户端")
    print("• 基于模式的模型类")
    print("• 自动类型转换和验证")
    print("• 减少样板代码")


# 导出的类和函数
__all__ = [
    "ClassFactory",
    "DynamicMixin",
    "APIGenerator",
    "dynamic_class_example",
    "mixin_example",
    "api_generator_example"
]