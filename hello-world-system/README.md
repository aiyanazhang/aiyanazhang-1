# Hello World Python脚本系统

一个简单而可扩展的Python Hello World脚本系统，支持多语言、多格式输出。

## 功能特性

- 基础问候功能
- 个性化问候（支持用户名）
- 多语言支持（中文、英文）
- 多种输出格式（文本、JSON、XML）
- 配置文件支持
- 完整的错误处理
- 单元测试覆盖

## 快速开始

```bash
# 基础使用
python main.py

# 个性化问候
python main.py --name "张三"

# 指定语言
python main.py --name "Zhang San" --language en

# 指定输出格式
python main.py --name "张三" --format json
```

## 项目结构

```
hello-world-system/
├── src/           # 源代码目录
├── tests/         # 测试文件目录
├── config/        # 配置文件目录
├── docs/          # 文档目录
├── examples/      # 使用示例目录
└── README.md      # 项目说明
```

## 依赖要求

- Python 3.7+
- 标准库：sys, os, argparse, json, xml, unittest

## 许可证

MIT License