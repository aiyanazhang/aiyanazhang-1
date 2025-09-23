"""元编程模块初始化"""

from .metaclasses import *
from .descriptors import *
from .dynamic_classes import *

__all__ = [
    # 元类
    "SingletonMeta",
    "RegistryMeta",
    "AttributeValidationMeta",
    "AutoPropertyMeta",
    "singleton_example",
    "registry_metaclass_example",
    "validation_metaclass_example",
    
    # 描述符
    "ValidatedAttribute",
    "CachedProperty",
    "TypedAttribute",
    "RangeValidatedAttribute",
    "descriptor_example",
    "cached_property_example",
    "typed_attribute_example",
    
    # 动态类
    "ClassFactory",
    "DynamicMixin",
    "APIGenerator",
    "dynamic_class_example",
    "mixin_example",
    "api_generator_example",
]