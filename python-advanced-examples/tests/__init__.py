"""测试包初始化"""

import pytest
import sys
from pathlib import Path

# 添加源代码路径到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 导入主要模块进行测试准备
try:
    import python_advanced_examples
    from python_advanced_examples.core import registry, runner, performance
    from python_advanced_examples.language_features import advanced_decorators
except ImportError as e:
    pytest.skip(f"跳过测试，导入失败: {e}", allow_module_level=True)