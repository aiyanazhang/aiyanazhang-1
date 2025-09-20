# 项目内容和修改时间列表工具 (list-project.sh)

一个强大的shell脚本工具，用于递归列出项目中的所有文件和目录，并显示其详细的修改时间信息。

## 功能特性

### 🔍 核心功能
- **递归遍历**: 深度优先遍历所有子目录
- **时间信息**: 显示文件的修改时间、访问时间、状态变更时间
- **多种格式**: 支持简洁、详细、表格、JSON、CSV等输出格式
- **灵活排序**: 按名称、大小、时间、扩展名等多种方式排序
- **智能过滤**: 支持包含/排除模式，可过滤特定文件类型

### 🛠️ 高级特性
- **符号链接处理**: 可选择是否跟随符号链接，避免循环引用
- **隐藏文件支持**: 可选择是否包含隐藏文件和目录
- **深度控制**: 可限制递归的最大深度
- **配置文件**: 支持配置文件和环境变量
- **错误处理**: 优雅处理权限错误和文件系统异常

## 安装和使用

### 快速开始

1. **下载脚本**:
   ```bash
   # 下载到当前目录
   curl -O https://raw.githubusercontent.com/your-repo/list-project.sh
   
   # 或者直接使用现有的脚本
   chmod +x list-project.sh
   ```

2. **基本使用**:
   ```bash
   # 列出当前目录
   ./list-project.sh
   
   # 列出指定目录
   ./list-project.sh /path/to/project
   
   # 显示帮助
   ./list-project.sh --help
   ```

### 命令行选项

| 选项 | 短选项 | 描述 | 默认值 |
|------|--------|------|--------|
| `--help` | `-h` | 显示帮助信息 | - |
| `--all` | `-a` | 包含隐藏文件和目录 | false |
| `--format FORMAT` | `-f` | 输出格式 | simple |
| `--sort SORT` | `-s` | 排序方式 | name |
| `--reverse` | `-r` | 反向排序 | false |
| `--depth DEPTH` | `-d` | 最大递归深度 | 无限制 |
| `--exclude PATTERN` | `-e` | 排除模式 | 预定义模式 |
| `--include PATTERN` | `-i` | 包含模式 | 所有文件 |
| `--time-format FMT` | `-t` | 时间格式 | %Y-%m-%d %H:%M:%S |
| `--follow-symlinks` | `-L` | 跟随符号链接 | false |
| `--verbose` | `-v` | 详细输出模式 | false |

## 输出格式详解

### 1. 简洁模式 (simple)
```
./README.md                     2025-09-20 08:34:55
./src/main.py                   2025-09-20 08:30:12
./docs/guide.md                 2025-09-20 08:25:30
```

### 2. 详细模式 (detailed)
```
文件路径                             大小   权限       修改时间         访问时间         状态时间        
======================================== ======== ============ ==================== ==================== ====================
README.md                                9KB      644          2025-09-20 08:34:55  2025-09-20 08:34:55  2025-09-20 08:34:55 
src/main.py                              2KB      644          2025-09-20 08:30:12  2025-09-20 08:30:15  2025-09-20 08:30:12 
```

### 3. JSON格式 (json)
```json
{
  "scan_info": {
    "timestamp": "2025-09-20T08:38:16Z",
    "total_files": 15,
    "total_directories": 5,
    "scan_duration": "0.15s"
  },
  "files": [
    {
      "path": "README.md",
      "type": "file",
      "size": 9216,
      "permissions": "644",
      "mtime": "2025-09-20T08:34:55+00:00",
      "atime": "2025-09-20T08:34:55+00:00",
      "ctime": "2025-09-20T08:34:55+00:00"
    }
  ]
}
```

### 4. CSV格式 (csv)
```csv
type,path,size,permissions,mtime,atime,ctime
file,"README.md",9216,"644","2025-09-20 08:34:55","2025-09-20 08:34:55","2025-09-20 08:34:55"
directory,"src/",,"755","2025-09-20 08:30:00","2025-09-20 08:30:00","2025-09-20 08:30:00"
```

## 排序选项

| 排序方式 | 描述 | 示例 |
|----------|------|------|
| `name` | 按文件名字母顺序 | `./list-project.sh -s name` |
| `size` | 按文件大小 | `./list-project.sh -s size -r` |
| `mtime` | 按修改时间 | `./list-project.sh -s mtime` |
| `atime` | 按访问时间 | `./list-project.sh -s atime` |
| `extension` | 按文件扩展名 | `./list-project.sh -s extension` |
| `depth` | 按目录深度 | `./list-project.sh -s depth` |

## 过滤功能

### 排除模式
```bash
# 排除Python缓存文件
./list-project.sh -e "__pycache__"

# 排除多种文件类型
./list-project.sh -e "*.pyc" -e "*.log"

# 排除Git相关文件
./list-project.sh -e ".git"
```

### 包含模式
```bash
# 只包含Python文件
./list-project.sh -i "*.py"

# 只包含文档文件
./list-project.sh -i "*.md" -i "*.txt"
```

## 配置文件

创建配置文件以设置默认选项。配置文件优先级：

1. 当前目录：`./.list-project.conf`
2. 用户主目录：`~/.list-project.conf`  
3. 系统级：`/etc/list-project.conf`

### 配置文件示例
```bash
# 默认输出格式
OUTPUT_FORMAT="detailed"

# 默认排序方式
SORT_BY="mtime"

# 默认排除模式
EXCLUDE_PATTERNS=".git node_modules __pycache__ *.pyc"

# 默认显示隐藏文件
SHOW_HIDDEN=true

# 默认时间格式
TIME_FORMAT="%Y-%m-%d %H:%M:%S"
```

## 环境变量

支持通过环境变量覆盖配置：

```bash
export LIST_PROJECT_FORMAT="json"
export LIST_PROJECT_EXCLUDE=".git *.log"
export LIST_PROJECT_TIME_FORMAT="%Y/%m/%d %H:%M"
```

## 实用示例

### 1. 项目分析
```bash
# 查看项目文件概览
./list-project.sh -f detailed /path/to/project

# 查找最大的文件
./list-project.sh -s size -r -f detailed | head -10

# 查找最近修改的文件
./list-project.sh -s mtime -r | head -10
```

### 2. 数据导出
```bash
# 导出为JSON进行程序处理
./list-project.sh -f json > project_files.json

# 导出为CSV进行数据分析
./list-project.sh -f csv > project_files.csv
```

### 3. 过滤特定文件
```bash
# 只查看源代码文件
./list-project.sh -i "*.py" -i "*.js" -i "*.go"

# 排除构建产物和缓存
./list-project.sh -e "build" -e "dist" -e "node_modules"
```

### 4. 深度限制
```bash
# 只查看前两层目录
./list-project.sh -d 2

# 查看项目根目录文件
./list-project.sh -d 0
```

## 性能优化

### 大型项目优化
- 使用深度限制 (`-d`) 减少扫描范围
- 使用排除模式 (`-e`) 跳过不需要的目录
- 对于程序处理，优先使用JSON格式

### 内存使用
- 脚本使用流式处理，内存使用量与项目大小无关
- 对于超大项目，建议分批处理或使用包含模式

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 脚本会自动跳过无权限访问的文件，并在详细模式下显示警告
   ./list-project.sh -v
   ```

2. **符号链接循环**
   ```bash
   # 脚本自动检测循环引用，避免无限递归
   ./list-project.sh -L  # 跟随符号链接
   ```

3. **输出乱码**
   ```bash
   # 确保终端支持UTF-8编码
   export LANG=en_US.UTF-8
   ```

### 调试模式
```bash
# 启用详细输出查看处理过程
./list-project.sh -v

# 使用bash调试模式
bash -x ./list-project.sh
```

## 兼容性

### 操作系统支持
- ✅ Linux (完全支持)
- ✅ macOS (完全支持)  
- ✅ Windows WSL/Git Bash (基本支持)
- ✅ FreeBSD/OpenBSD (基本支持)

### Shell兼容性
- ✅ Bash 4.0+ (完全支持)
- ✅ Zsh (完全支持)
- ⚠️ Dash (基本功能支持)
- ⚠️ 其他POSIX Shell (基本功能支持)

## 测试

运行测试套件验证所有功能：

```bash
# 运行完整测试
./test-list-project.sh

# 查看测试覆盖的功能
./test-list-project.sh --help
```

## 贡献

欢迎提交问题报告和功能请求！

### 开发
1. Fork项目
2. 创建功能分支
3. 运行测试确保功能正常
4. 提交Pull Request

## 许可证

MIT License - 详见LICENSE文件

## 更新日志

### v1.0.0 (2025-09-20)
- 初始版本发布
- 支持多种输出格式
- 实现完整的排序和过滤功能
- 添加配置文件支持
- 完善错误处理机制