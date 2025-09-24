# 文本搜索工具

一个功能强大的Shell脚本，用于在文件系统中搜索文本内容。

## 特性

- 🔍 **灵活搜索**: 支持文本和正则表达式搜索
- 📁 **文件过滤**: 按文件类型和目录进行精确过滤
- 🎨 **多种输出**: 简单、详细、JSON三种输出格式
- ⚡ **高性能**: 并行搜索，智能缓存机制
- 🌈 **彩色输出**: 高亮显示搜索结果
- 🛡️ **错误处理**: 完善的错误提示和处理

## 快速开始

```bash
# 安装
chmod +x text-search.sh

# 基本用法
./text-search.sh -p "function"

# 正则表达式搜索
./text-search.sh -p "^class\s+\w+" -r

# 指定文件类型
./text-search.sh -p "TODO" -t "py,js,java"

# 查看帮助
./text-search.sh --help
```

## 主要参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p, --pattern` | 搜索模式（必需） | `-p "function"` |
| `-d, --directory` | 搜索目录 | `-d /path/to/project` |
| `-r, --regex` | 正则表达式模式 | `-r` |
| `-t, --type` | 文件类型过滤 | `-t "py,js,java"` |
| `-o, --output` | 输出格式 | `-o detail` |
| `-n, --line-number` | 显示行号 | `-n` |
| `-v, --verbose` | 详细模式 | `-v` |

## 项目结构

```
text-search-tool/
├── text-search.sh         # 主脚本
├── tests/run_tests.sh     # 测试脚本
├── docs/USER_GUIDE.md    # 详细文档
└── examples/              # 使用示例
```

## 测试

```bash
# 运行所有测试
./tests/run_tests.sh
```

## 文档

- [**用户指南**](docs/USER_GUIDE.md) - 详细的使用说明
- [**使用示例**](examples/usage_examples.sh) - 实际使用场景

此项目采用 MIT 许可证。