"""
Web演示界面模块

提供基于FastAPI的Web界面，用于演示Python高级用法示例：
- RESTful API接口
- 交互式示例展示
- 实时代码执行
- 性能监控展示
"""

from .api import *
from .static import *
from .templates import *

__all__ = [
    # API相关
    'create_app',
    'ExampleAPI',
    'PerformanceAPI',
    'MonitoringAPI',
    
    # 静态资源
    'get_static_files',
    'StaticFileHandler',
    
    # 模板
    'TemplateManager',
    'render_template',
]