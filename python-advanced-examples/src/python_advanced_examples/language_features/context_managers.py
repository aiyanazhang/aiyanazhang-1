"""
上下文管理器进阶

展示高级上下文管理器的实现和应用，包括资源管理、异常处理、状态管理等。
"""

import contextlib
import logging
import threading
import time
from contextlib import contextmanager
from typing import Any, Optional, Generator, Dict, List
from dataclasses import dataclass

from ..core.decorators import example, demo
from ..core.registry import ExampleCategory, DifficultyLevel

logger = logging.getLogger(__name__)


class ResourceManager:
    """资源管理上下文管理器"""
    
    def __init__(self, resource_name: str, acquire_timeout: float = 30.0):
        self.resource_name = resource_name
        self.acquire_timeout = acquire_timeout
        self.resource = None
        self.acquired_at = None
    
    def __enter__(self):
        """获取资源"""
        logger.info(f"Acquiring resource: {self.resource_name}")
        start_time = time.time()
        
        # 模拟资源获取
        time.sleep(0.1)
        self.resource = f"Resource-{self.resource_name}-{int(time.time())}"
        self.acquired_at = time.time()
        
        logger.info(f"Resource acquired: {self.resource}")
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """释放资源"""
        if self.resource:
            usage_time = time.time() - self.acquired_at if self.acquired_at else 0
            logger.info(f"Releasing resource: {self.resource} (used for {usage_time:.2f}s)")
            
            # 模拟资源释放
            time.sleep(0.1)
            self.resource = None
            self.acquired_at = None
            
            if exc_type:
                logger.warning(f"Resource released due to exception: {exc_type.__name__}")
            else:
                logger.info("Resource released normally")
        
        # 返回False表示不抑制异常
        return False


@contextmanager
def temporary_directory(prefix: str = "tmp", cleanup: bool = True) -> Generator[str, None, None]:
    """临时目录上下文管理器"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    logger.info(f"Created temporary directory: {temp_dir}")
    
    try:
        yield temp_dir
    finally:
        if cleanup:
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup temporary directory {temp_dir}: {e}")


class StateManager:
    """状态管理上下文管理器"""
    
    def __init__(self, obj: Any, **state_changes):
        self.obj = obj
        self.state_changes = state_changes
        self.original_state = {}
    
    def __enter__(self):
        """保存原始状态并应用新状态"""
        for attr_name, new_value in self.state_changes.items():
            if hasattr(self.obj, attr_name):
                self.original_state[attr_name] = getattr(self.obj, attr_name)
                setattr(self.obj, attr_name, new_value)
        
        return self.obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """恢复原始状态"""
        for attr_name, original_value in self.original_state.items():
            setattr(self.obj, attr_name, original_value)
        
        return False


# ============================================================================
# 示例函数
# ============================================================================

@example(
    name="resource_manager_example",
    category=ExampleCategory.CONTEXT_MANAGERS,
    difficulty=DifficultyLevel.BEGINNER,
    description="资源管理器上下文管理器示例",
    tags=["resource-management", "context-manager", "cleanup"]
)
@demo(title="资源管理器示例")
def resource_manager_example():
    """展示资源管理器的用法"""
    
    print("正常使用资源：")
    with ResourceManager("database_connection") as resource:
        print(f"使用资源: {resource}")
        time.sleep(0.2)  # 模拟使用资源
    
    print("\n异常情况下的资源管理：")
    try:
        with ResourceManager("file_handle") as resource:
            print(f"使用资源: {resource}")
            raise ValueError("模拟异常")
    except ValueError as e:
        print(f"捕获异常: {e}")


@example(
    name="state_manager_example", 
    category=ExampleCategory.CONTEXT_MANAGERS,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="状态管理器上下文管理器示例",
    tags=["state-management", "context-manager", "temporary-changes"]
)
@demo(title="状态管理器示例")
def state_manager_example():
    """展示状态管理器的用法"""
    
    @dataclass
    class Configuration:
        debug: bool = False
        timeout: int = 30
        retries: int = 3
    
    config = Configuration()
    print(f"原始配置: debug={config.debug}, timeout={config.timeout}, retries={config.retries}")
    
    # 临时修改配置
    with StateManager(config, debug=True, timeout=60, retries=5):
        print(f"临时配置: debug={config.debug}, timeout={config.timeout}, retries={config.retries}")
        # 在这个块中，配置已被临时修改
    
    print(f"恢复配置: debug={config.debug}, timeout={config.timeout}, retries={config.retries}")


@example(
    name="temporary_directory_example",
    category=ExampleCategory.CONTEXT_MANAGERS,
    difficulty=DifficultyLevel.BEGINNER,
    description="临时目录上下文管理器示例",
    tags=["temporary", "directory", "cleanup", "context-manager"]
)
@demo(title="临时目录示例")
def temporary_directory_example():
    """展示临时目录管理器的用法"""
    import os
    
    print("创建临时目录：")
    with temporary_directory(prefix="example_") as temp_dir:
        print(f"临时目录路径: {temp_dir}")
        print(f"目录存在: {os.path.exists(temp_dir)}")
        
        # 在临时目录中创建文件
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("这是一个测试文件")
        
        print(f"创建的文件: {test_file}")
        print(f"文件存在: {os.path.exists(test_file)}")
    
    print(f"退出后目录存在: {os.path.exists(temp_dir)}")


# 导出的类和函数
__all__ = [
    "ResourceManager",
    "StateManager", 
    "temporary_directory",
    "resource_manager_example",
    "state_manager_example",
    "temporary_directory_example"
]