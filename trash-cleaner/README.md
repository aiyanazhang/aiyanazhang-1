# 回收站清理工具 (trash-cleaner)

一个安全、高效、跨平台的回收站清理工具，支持Linux、macOS和Windows系统。

## 特性

- 🛡️ **多层安全验证** - 严格的路径验证和权限检查，防止误删系统文件
- 🌐 **跨平台支持** - 自动识别不同操作系统的回收站位置
- 🔍 **灵活筛选** - 支持按时间、大小、文件类型和名称模式过滤
- 📊 **详细统计** - 提供清理前后的详细统计信息
- 🎯 **预览模式** - 支持预览要删除的内容，无风险查看
- 📝 **完整日志** - 详细的操作日志和审计跟踪
- 🎨 **友好界面** - 彩色输出、进度条和交互式确认
- ⚙️ **高度可配置** - 支持配置文件和命令行参数

## 快速开始

### 基本用法

```bash
# 交互式清理（默认模式）
./trash-cleaner.sh

# 预览模式 - 查看将要删除什么
./trash-cleaner.sh --dry-run

# 自动清理 - 跳过确认
./trash-cleaner.sh --yes

# 详细输出
./trash-cleaner.sh --verbose
```

### 常用示例

```bash
# 清理30天前的文件
./trash-cleaner.sh --older-than 30d

# 清理大于100MB的文件
./trash-cleaner.sh --size-limit 100M

# 清理临时文件
./trash-cleaner.sh --pattern "*.tmp"

# 组合条件：清理30天前的大于10MB的日志文件
./trash-cleaner.sh --older-than 30d --size-limit 10M --pattern "*.log"
```

## 安装

### 系统要求

- Linux、macOS 或 Windows (通过WSL/MSYS2)
- Bash 4.0+
- 基本的Unix工具：`find`, `rm`, `du`, `stat`, `date`

### 安装步骤

1. 克隆项目：
```bash
git clone https://github.com/your-repo/trash-cleaner.git
cd trash-cleaner
```

2. 设置执行权限：
```bash
chmod +x trash-cleaner.sh
chmod +x tests/test_all.sh
```

3. 运行测试（可选）：
```bash
./tests/test_all.sh
```

4. 创建配置文件（可选）：
```bash
cp config/trash-cleaner.conf.example ~/.trash-cleaner.conf
```

## 命令行选项

| 选项 | 描述 | 示例 |
|------|------|------|
| `-h, --help` | 显示帮助信息 | `--help` |
| `-V, --version` | 显示版本信息 | `--version` |
| `-v, --verbose` | 启用详细输出 | `--verbose` |
| `-y, --yes` | 自动确认，跳过交互 | `--yes` |
| `-n, --dry-run` | 预览模式，不删除文件 | `--dry-run` |
| `-t, --type` | 清理类型 | `--type files` |
| `-d, --older-than` | 时间过滤 | `--older-than 30d` |
| `-s, --size-limit` | 大小过滤 | `--size-limit 100M` |
| `-p, --pattern` | 文件名模式 | `--pattern "*.tmp"` |
| `--max-depth` | 遍历深度限制 | `--max-depth 5` |
| `-c, --config` | 配置文件路径 | `--config /path/to/config` |
| `-l, --log` | 日志文件路径 | `--log /var/log/cleanup.log` |
| `--no-color` | 禁用彩色输出 | `--no-color` |
| `--no-progress` | 禁用进度条 | `--no-progress` |

## 配置文件

配置文件使用简单的 `key=value` 格式，支持注释。默认位置：`~/.trash-cleaner.conf`

### 主要配置选项

```ini
# 基本设置
default_mode=interactive
confirm_deletion=true
verbose=false
dry_run=false

# 清理规则
clean_type=all
pattern=*
max_file_age_days=0
min_file_size_mb=0

# 过滤器
older_than=30d
size_limit=100M

# 日志设置
enable_logging=true
log_file=~/.trash-cleaner.log
log_retention_days=30

# 界面设置
color_output=true
progress_bar=true
```

## 使用场景

### 日常维护

```bash
# 每周清理临时文件
./trash-cleaner.sh --older-than 7d --pattern "*.tmp" --yes

# 清理大文件释放空间
./trash-cleaner.sh --size-limit 500M --dry-run
```

### 系统管理

```bash
# 定期自动清理（cron任务）
0 2 * * 0 /path/to/trash-cleaner.sh --yes --older-than 30d --log /var/log/cleanup.log

# 紧急空间清理
./trash-cleaner.sh --size-limit 1G --older-than 1d --yes
```

### 开发环境

```bash
# 清理构建产物
./trash-cleaner.sh --pattern "*.o" --pattern "*.tmp" --pattern "*~"

# 清理日志文件
./trash-cleaner.sh --older-than 14d --pattern "*.log"
```

## 安全特性

### 多层安全验证

1. **路径白名单** - 仅允许操作预定义的回收站路径
2. **符号链接检查** - 防止通过软链接访问非回收站目录
3. **权限验证** - 确保有足够权限执行操作
4. **深度限制** - 限制目录遍历深度防止意外操作

### 安全使用建议

- 总是先使用 `--dry-run` 预览要删除的内容
- 启用详细日志记录便于审计
- 对重要数据定期备份
- 避免使用通配符匹配过于宽泛的模式

## 故障排除

### 常见问题

#### 权限问题
```bash
# 检查回收站权限
ls -la ~/.local/share/Trash/

# 如果需要，使用sudo（谨慎）
sudo ./trash-cleaner.sh --verbose
```

#### 配置问题
```bash
# 验证配置文件格式
head -10 ~/.trash-cleaner.conf

# 使用默认配置运行
./trash-cleaner.sh --config /dev/null
```

#### 调试模式
```bash
# 启用bash调试
bash -x ./trash-cleaner.sh --dry-run --verbose
```

### 日志分析

```bash
# 查看最近的操作日志
tail -50 ~/.trash-cleaner.log

# 搜索错误信息
grep ERROR ~/.trash-cleaner.log

# 统计清理记录
grep "操作完成" ~/.trash-cleaner.log | wc -l
```

## 开发

### 项目结构

```
trash-cleaner/
├── trash-cleaner.sh          # 主入口脚本
├── src/                      # 源代码模块
│   ├── system_detector.sh    # 系统检测
│   ├── security_checker.sh   # 安全检查
│   ├── config_manager.sh     # 配置管理
│   ├── trash_scanner.sh      # 回收站扫描
│   ├── cleanup_executor.sh   # 清理执行
│   ├── logger.sh             # 日志系统
│   └── ui.sh                 # 用户界面
├── config/                   # 配置文件
├── tests/                    # 测试套件
├── docs/                     # 文档
└── examples/                 # 使用示例
```

### 运行测试

```bash
# 运行完整测试套件
./tests/test_all.sh

# 运行特定测试
bash -x ./tests/test_all.sh
```

### 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 提交Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 支持

- 🐛 [报告Bug](https://github.com/your-repo/trash-cleaner/issues)
- 💡 [功能请求](https://github.com/your-repo/trash-cleaner/issues)
- 📖 [文档](https://github.com/your-repo/trash-cleaner/wiki)
- 💬 [讨论](https://github.com/your-repo/trash-cleaner/discussions)

## 版本历史

### v1.0.0 (2024-12-20)
- 初始版本发布
- 支持Linux、macOS、Windows
- 完整的安全验证机制
- 丰富的过滤和配置选项
- 详细的日志和审计功能