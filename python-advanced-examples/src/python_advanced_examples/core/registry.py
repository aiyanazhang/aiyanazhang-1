"""
示例注册中心

提供示例的注册、发现和管理功能。支持分类、标签、难度等级等多维度的示例组织。
"""

import inspect
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from pathlib import Path
import importlib.util
from functools import wraps

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """示例难度等级"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExampleCategory(Enum):
    """示例分类"""
    DECORATORS = "decorators"
    CONTEXT_MANAGERS = "context_managers"
    GENERATORS = "generators"
    ASYNC_PROGRAMMING = "async_programming"
    CONCURRENCY = "concurrency"
    PERFORMANCE = "performance"
    METAPROGRAMMING = "metaprogramming"
    DATA_PROCESSING = "data_processing"
    DESIGN_PATTERNS = "design_patterns"
    TYPE_HINTS = "type_hints"


@dataclass
class Example:
    """示例数据类"""
    name: str
    func: Callable
    category: ExampleCategory
    difficulty: DifficultyLevel
    description: str
    tags: Set[str] = field(default_factory=set)
    source_file: Optional[Path] = None
    dependencies: List[str] = field(default_factory=list)
    expected_output: Optional[str] = None
    setup_code: Optional[str] = None
    cleanup_code: Optional[str] = None
    execution_time_limit: float = 30.0  # 秒
    memory_limit: int = 512  # MB
    author: Optional[str] = None
    created_at: Optional[str] = None
    version: str = "1.0"
    
    def __post_init__(self):
        """后处理初始化"""
        if self.source_file is None and hasattr(self.func, '__code__'):
            try:
                self.source_file = Path(self.func.__code__.co_filename)
            except (AttributeError, OSError):
                pass
    
    def get_signature(self) -> str:
        """获取函数签名"""
        try:
            return str(inspect.signature(self.func))
        except (ValueError, TypeError):
            return "()"
    
    def get_docstring(self) -> str:
        """获取函数文档字符串"""
        return self.func.__doc__ or self.description
    
    def get_source_code(self) -> Optional[str]:
        """获取源代码"""
        try:
            return inspect.getsource(self.func)
        except (OSError, TypeError):
            return None
    
    def matches_filter(self, **filters) -> bool:
        """检查是否匹配过滤条件"""
        for key, value in filters.items():
            if key == "category" and self.category != value:
                return False
            elif key == "difficulty" and self.difficulty != value:
                return False
            elif key == "tags" and not (set(value) & self.tags):
                return False
            elif key == "name_pattern" and value.lower() not in self.name.lower():
                return False
        return True


class ExampleRegistry:
    """示例注册中心"""
    
    def __init__(self):
        self._examples: Dict[str, Example] = {}
        self._categories: Dict[ExampleCategory, List[Example]] = {
            category: [] for category in ExampleCategory
        }
        self._tags: Dict[str, List[Example]] = {}
        self._difficulty_levels: Dict[DifficultyLevel, List[Example]] = {
            level: [] for level in DifficultyLevel
        }
    
    def register(
        self,
        name: str,
        category: Union[ExampleCategory, str],
        difficulty: Union[DifficultyLevel, str],
        description: str,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Callable:
        """注册示例的装饰器
        
        Args:
            name: 示例名称
            category: 示例分类
            difficulty: 难度等级
            description: 描述信息
            tags: 标签列表
            **kwargs: 其他Example参数
        """
        def decorator(func: Callable) -> Callable:
            # 类型转换
            if isinstance(category, str):
                cat = ExampleCategory(category)
            else:
                cat = category
                
            if isinstance(difficulty, str):
                diff = DifficultyLevel(difficulty)
            else:
                diff = difficulty
            
            # 创建示例对象
            example = Example(
                name=name,
                func=func,
                category=cat,
                difficulty=diff,
                description=description,
                tags=set(tags or []),
                **kwargs
            )
            
            # 注册示例
            self._register_example(example)
            
            # 添加元数据到函数
            func._example_metadata = example
            
            return func
        
        return decorator
    
    def _register_example(self, example: Example) -> None:
        """内部注册方法"""
        # 检查名称冲突
        if example.name in self._examples:
            logger.warning(f"Example '{example.name}' already exists, overwriting")
        
        # 注册到主字典
        self._examples[example.name] = example
        
        # 注册到分类索引
        self._categories[example.category].append(example)
        
        # 注册到难度索引
        self._difficulty_levels[example.difficulty].append(example)
        
        # 注册到标签索引
        for tag in example.tags:
            if tag not in self._tags:
                self._tags[tag] = []
            self._tags[tag].append(example)
        
        logger.info(f"Registered example: {example.name}")
    
    def get_example(self, name: str) -> Optional[Example]:
        """获取指定名称的示例"""
        return self._examples.get(name)
    
    def list_examples(
        self,
        category: Optional[Union[ExampleCategory, str]] = None,
        difficulty: Optional[Union[DifficultyLevel, str]] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None
    ) -> List[Example]:
        """列出符合条件的示例
        
        Args:
            category: 分类筛选
            difficulty: 难度筛选
            tags: 标签筛选（包含任一标签即可）
            name_pattern: 名称模式匹配
        """
        examples = list(self._examples.values())
        
        # 构建过滤条件
        filters = {}
        if category is not None:
            if isinstance(category, str):
                filters["category"] = ExampleCategory(category)
            else:
                filters["category"] = category
                
        if difficulty is not None:
            if isinstance(difficulty, str):
                filters["difficulty"] = DifficultyLevel(difficulty)
            else:
                filters["difficulty"] = difficulty
                
        if tags:
            filters["tags"] = tags
            
        if name_pattern:
            filters["name_pattern"] = name_pattern
        
        # 应用过滤
        if filters:
            examples = [ex for ex in examples if ex.matches_filter(**filters)]
        
        return sorted(examples, key=lambda x: (x.category.value, x.difficulty.value, x.name))
    
    def get_categories(self) -> List[ExampleCategory]:
        """获取所有分类"""
        return [cat for cat in ExampleCategory if self._categories[cat]]
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        return sorted(self._tags.keys())
    
    def get_by_category(self, category: Union[ExampleCategory, str]) -> List[Example]:
        """按分类获取示例"""
        if isinstance(category, str):
            category = ExampleCategory(category)
        return self._categories[category].copy()
    
    def get_by_difficulty(self, difficulty: Union[DifficultyLevel, str]) -> List[Example]:
        """按难度获取示例"""
        if isinstance(difficulty, str):
            difficulty = DifficultyLevel(difficulty)
        return self._difficulty_levels[difficulty].copy()
    
    def get_by_tag(self, tag: str) -> List[Example]:
        """按标签获取示例"""
        return self._tags.get(tag, []).copy()
    
    def search(self, query: str) -> List[Example]:
        """搜索示例
        
        在名称、描述、标签中搜索关键词
        """
        query = query.lower()
        results = []
        
        for example in self._examples.values():
            # 搜索名称
            if query in example.name.lower():
                results.append(example)
                continue
            
            # 搜索描述
            if query in example.description.lower():
                results.append(example)
                continue
            
            # 搜索标签
            if any(query in tag.lower() for tag in example.tags):
                results.append(example)
                continue
            
            # 搜索文档字符串
            docstring = example.get_docstring().lower()
            if query in docstring:
                results.append(example)
                continue
        
        return sorted(results, key=lambda x: x.name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取注册统计信息"""
        stats = {
            "total_examples": len(self._examples),
            "categories": {
                cat.value: len(examples) 
                for cat, examples in self._categories.items() 
                if examples
            },
            "difficulty_levels": {
                diff.value: len(examples)
                for diff, examples in self._difficulty_levels.items()
                if examples
            },
            "total_tags": len(self._tags),
            "most_used_tags": sorted(
                [(tag, len(examples)) for tag, examples in self._tags.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        return stats
    
    def load_from_module(self, module_path: str) -> int:
        """从模块加载示例
        
        Args:
            module_path: 模块路径
            
        Returns:
            加载的示例数量
        """
        try:
            spec = importlib.util.spec_from_file_location("example_module", module_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {module_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 计算加载前的示例数量
            before_count = len(self._examples)
            
            # 扫描模块中的函数
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if hasattr(obj, '_example_metadata'):
                    # 如果函数已经有示例元数据，重新注册
                    self._register_example(obj._example_metadata)
            
            # 返回新加载的示例数量
            return len(self._examples) - before_count
            
        except Exception as e:
            logger.error(f"Failed to load examples from {module_path}: {e}")
            return 0
    
    def export_registry(self, include_source: bool = False) -> Dict[str, Any]:
        """导出注册表信息"""
        exported = {
            "examples": {},
            "statistics": self.get_statistics(),
            "export_timestamp": None,  # 可以添加时间戳
        }
        
        for name, example in self._examples.items():
            example_data = {
                "name": example.name,
                "category": example.category.value,
                "difficulty": example.difficulty.value,
                "description": example.description,
                "tags": list(example.tags),
                "signature": example.get_signature(),
                "docstring": example.get_docstring(),
                "dependencies": example.dependencies,
                "author": example.author,
                "version": example.version,
            }
            
            if include_source:
                example_data["source_code"] = example.get_source_code()
            
            exported["examples"][name] = example_data
        
        return exported
    
    def clear(self) -> None:
        """清空注册表"""
        self._examples.clear()
        for category_list in self._categories.values():
            category_list.clear()
        for difficulty_list in self._difficulty_levels.values():
            difficulty_list.clear()
        self._tags.clear()
        logger.info("Registry cleared")


# 创建全局注册表实例
registry = ExampleRegistry()


def example(
    name: str,
    category: Union[ExampleCategory, str],
    difficulty: Union[DifficultyLevel, str] = DifficultyLevel.INTERMEDIATE,
    description: str = "",
    tags: Optional[List[str]] = None,
    **kwargs
) -> Callable:
    """示例注册装饰器的便捷接口"""
    return registry.register(
        name=name,
        category=category,
        difficulty=difficulty,
        description=description,
        tags=tags,
        **kwargs
    )