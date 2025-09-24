# 文本搜索工具 - 详细文档

## 概述

`text-search.sh` 是一个功能强大的Shell脚本，用于在文件系统中搜索文本内容。它支持普通文本搜索和正则表达式搜索，提供多种输出格式，并具有高度可配置的选项。

## 特性

### 核心功能
- 🔍 **灵活搜索**: 支持文本和正则表达式两种搜索模式
- 📁 **文件过滤**: 按文件类型和目录进行精确过滤
- 🎨 **多种输出格式**: 简单、详细、JSON三种输出格式
- ⚡ **高性能**: 支持并行搜索，智能缓存机制
- 🎯 **精确控制**: 可控制搜索深度、文件大小等参数

### 用户体验
- 🌈 **彩色输出**: 高亮显示搜索结果
- 📊 **进度显示**: 实时显示搜索进度
- 📈 **详细统计**: 完整的搜索统计信息
- 🛡️ **错误处理**: 完善的错误提示和处理

## 安装

### 快速安装

```bash
# 克隆项目
git clone <repository-url>
cd text-search-tool

# 赋予执行权限
chmod +x text-search.sh

# 测试安装
./text-search.sh --version
```

### 系统安装

```bash
# 复制到系统路径
sudo cp text-search.sh /usr/local/bin/text-search
sudo chmod +x /usr/local/bin/text-search

# 现在可以全局使用
text-search --help
```

## 使用指南

### 基本语法

```bash
./text-search.sh [选项] -p <搜索模式>
```

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p, --pattern <模式>` | 搜索模式（文本或正则表达式） | `-p "function main"` |

### 可选参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `-d, --directory <路径>` | 搜索目录 | 当前目录 | `-d /home/user/project` |
| `-r, --regex` | 启用正则表达式模式 | false | `-r` |
| `-t, --type <类型>` | 文件类型过滤 | 所有文件 | `-t "py,js,java"` |
| `-e, --exclude <目录>` | 排除目录 | 默认排除列表 | `-e ".git,node_modules"` |
| `-o, --output <格式>` | 输出格式 | simple | `-o detail` |
| `-n, --line-number` | 显示行号 | false | `-n` |
| `-c, --count` | 只显示匹配计数 | false | `-c` |
| `-l, --files-only` | 只显示文件名 | false | `-l` |
| `-v, --verbose` | 详细输出模式 | false | `-v` |
| `--no-color` | 禁用彩色输出 | false | `--no-color` |
| `--max-depth <深度>` | 最大搜索深度 | 10 | `--max-depth 5` |
| `--max-size <大小>` | 最大文件大小 | 10M | `--max-size 5M` |
| `-j, --jobs <数量>` | 并行作业数 | CPU核心数 | `-j 4` |

## 使用示例

### 1. 基本文本搜索

```bash
# 搜索包含"function main"的文件
./text-search.sh -p "function main"

# 在特定目录中搜索
./text-search.sh -p "TODO" -d /path/to/project

# 显示行号
./text-search.sh -p "error" -n
```

### 2. 正则表达式搜索

```bash
# 搜索以"class"开头的行
./text-search.sh -p "^class\s+\w+" -r

# 搜索函数定义
./text-search.sh -p "function\s+\w+\s*\(" -r

# 搜索注释中的TODO
./text-search.sh -p "//\s*TODO.*" -r
```

### 3. 文件类型过滤

```bash
# 只搜索Python文件
./text-search.sh -p "import" -t "py"

# 搜索多种文件类型
./text-search.sh -p "main" -t "py,js,java,cpp"

# 搜索配置文件
./text-search.sh -p "database" -t "json,yaml,yml,conf"
```

### 4. 目录排除

```bash
# 排除版本控制目录
./text-search.sh -p "config" -e ".git,.svn"

# 排除构建和依赖目录
./text-search.sh -p "api" -e "node_modules,target,build,dist"

# 排除测试目录
./text-search.sh -p "function" -e "test,tests,__pycache__"
```

### 5. 输出格式

```bash
# 简单格式（默认）
./text-search.sh -p "error" -o simple

# 详细格式（包含文件信息）
./text-search.sh -p "TODO" -o detail

# JSON格式（机器可读）
./text-search.sh -p "function" -o json
```

### 6. 统计和计数

```bash
# 只显示匹配计数
./text-search.sh -p "function" -c

# 只显示包含匹配的文件名
./text-search.sh -p "TODO" -l

# 详细统计信息
./text-search.sh -p "error" -v
```

### 7. 性能优化

```bash
# 使用并行搜索
./text-search.sh -p "main" -j 4

# 限制搜索深度
./text-search.sh -p "config" --max-depth 3

# 限制文件大小
./text-search.sh -p "data" --max-size 1M
```

## 输出格式详解

### 简单格式 (simple)

```
文件路径:行号: 匹配内容
./src/main.py:15: def main():
./src/utils.py:8: # Main utility functions
```

### 详细格式 (detail)

```
文件: ./src/main.py
大小: 2.5KB
修改时间: 2024-01-15 10:30:45
---
行号 15: def main():
行号 42: if __name__ == "__main__":
匹配数: 2

文件: ./src/utils.py
大小: 1.8KB
修改时间: 2024-01-15 09:20:30
---
行号 8: # Main utility functions
匹配数: 1
```

### JSON格式 (json)

```json
{
  "search_summary": {
    "pattern": "main",
    "directory": "./src",
    "regex_mode": false,
    "total_files": 5,
    "total_matches": 8,
    "search_time": "0.12s"
  },
  "results": [
    {
      "file": "./src/main.py",
      "matches": [
        {
          "line": 15,
          "content": "def main():"
        },
        {
          "line": 42,
          "content": "if __name__ == \"__main__\":"
        }
      ]
    }
  ]
}
```

## 配置文件

可以创建配置文件 `~/.text-searchrc` 来设置默认值：

```bash
# 文本搜索工具配置文件

# 默认排除目录
DEFAULT_EXCLUDES=".git,.svn,node_modules,target,.idea,.vscode"

# 最大搜索深度
MAX_DEPTH=15

# 彩色输出开关
COLORED_OUTPUT=true

# 最大文件大小限制
MAX_FILE_SIZE="20M"

# 并行作业数
PARALLEL_JOBS=4

# 详细模式开关
VERBOSE=false

# 默认输出格式
OUTPUT_FORMAT="simple"
```

## 高级用法

### 1. 组合使用管道

```bash
# 将结果传递给其他工具
./text-search.sh -p "error" -o json | jq '.results[].file' | sort | uniq

# 统计每个文件的匹配数
./text-search.sh -p "TODO" -c | awk '{print $1, $2}' | sort -nr
```

### 2. 脚本集成

```bash
#!/bin/bash
# 项目代码质量检查脚本

echo "检查TODO项目..."
./text-search.sh -p "TODO" -c

echo "检查FIXME项目..."
./text-search.sh -p "FIXME" -c

echo "检查debug代码..."
./text-search.sh -p "console\.log\|print\(" -r -c
```

### 3. 性能监控

```bash
# 使用time命令测量性能
time ./text-search.sh -p "function" -d /large/project -j 8

# 使用详细模式查看统计
./text-search.sh -p "main" -v | grep "搜索耗时"
```

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 确保脚本有执行权限
   chmod +x text-search.sh
   
   # 确保搜索目录可读
   ls -la /path/to/search/directory
   ```

2. **搜索结果为空**
   ```bash
   # 检查搜索模式是否正确
   ./text-search.sh -p "pattern" -v
   
   # 检查文件类型过滤
   ./text-search.sh -p "pattern" -t "txt" -v
   ```

3. **正则表达式错误**
   ```bash
   # 测试正则表达式
   echo "test string" | grep -E "your_regex"
   
   # 使用详细模式查看构建的命令
   ./text-search.sh -p "regex" -r -v
   ```

4. **性能问题**
   ```bash
   # 减少搜索深度
   ./text-search.sh -p "pattern" --max-depth 3
   
   # 排除大目录
   ./text-search.sh -p "pattern" -e "node_modules,target,build"
   
   # 限制文件大小
   ./text-search.sh -p "pattern" --max-size 1M
   ```

### 调试模式

启用详细模式来获取调试信息：

```bash
./text-search.sh -p "pattern" -v
```

这将显示：
- 解析的参数
- 构建的find和grep命令
- 搜索进度
- 详细的统计信息

## 最佳实践

### 1. 性能优化

- 对于大型项目，使用文件类型过滤 (`-t`)
- 排除不必要的目录 (`-e`)
- 在多核系统上启用并行搜索 (`-j`)
- 设置合理的搜索深度 (`--max-depth`)

### 2. 搜索技巧

- 使用简单的文本搜索，除非确实需要正则表达式
- 对于复杂的正则表达式，先在小范围内测试
- 使用行号选项 (`-n`) 便于定位代码

### 3. 结果处理

- 对于自动化脚本，使用JSON格式输出
- 使用计数模式 (`-c`) 快速获得统计信息
- 使用文件模式 (`-l`) 找到相关文件

## 版本历史

- **v1.0.0** - 初始版本
  - 基本文本和正则表达式搜索
  - 多种输出格式
  - 文件类型过滤
  - 并行搜索支持
  - 错误处理和日志记录

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 支持

如果遇到问题或有功能建议，请：

1. 查看本文档的故障排除部分
2. 在项目仓库创建 Issue
3. 联系维护者

---

*最后更新: 2024年9月24日*