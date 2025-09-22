# 回收站清理工具 - 增强版使用指南

## 新增功能概述

本次更新为回收站清理工具增加了强大的预检查和列表管理功能，提供了更安全、更智能的文件分析和风险评估能力。

### 🆕 主要新增功能

1. **智能文件分析** - 自动识别文件类型、大小、修改时间等属性
2. **风险评估系统** - 基于多维度因素评估文件删除风险
3. **多视图列表展示** - 支持概览、详细、分类等多种显示模式
4. **交互式选择** - 精确控制要删除的文件
5. **多格式导出** - 支持JSON、CSV、TXT格式报告
6. **分组和排序** - 按类型、大小、时间等维度组织文件
7. **风险过滤** - 仅显示特定风险等级的文件

## 🎯 使用场景

### 场景1：安全预览模式
在执行任何删除操作之前，先查看回收站内容和风险分析：

```bash
# 仅列出文件，不执行删除
./trash-cleaner.sh -L

# 显示详细信息和风险分析
./trash-cleaner.sh --detailed -r
```

### 场景2：交互式精确清理
需要手动选择要删除的文件时：

```bash
# 启动交互式选择模式
./trash-cleaner.sh -I

# 仅显示高风险文件进行交互选择
./trash-cleaner.sh -I -m 70
```

### 场景3：生成分析报告
需要生成详细的文件分析报告时：

```bash
# 导出JSON格式报告
./trash-cleaner.sh -L -x json --export-file report.json

# 导出CSV格式报告并按风险排序
./trash-cleaner.sh -L -x csv -S risk --export-file analysis.csv

# 导出可读性强的文本报告
./trash-cleaner.sh --detailed -x txt --export-file summary.txt
```

### 场景4：分类管理
按不同维度查看和管理文件：

```bash
# 按文件类型分组显示
./trash-cleaner.sh -L -g type

# 按风险等级分组，风险高的在前
./trash-cleaner.sh --detailed -g risk -S risk

# 按修改时间分组，最新的在前
./trash-cleaner.sh -L -g time -S mtime
```

## 📊 新增命令行参数

### 预检查相关参数

| 参数 | 长格式 | 说明 | 示例 |
|------|--------|------|------|
| `-L` | `--list-only` | 仅列出文件，不执行删除 | `-L` |
| | `--detailed` | 显示详细文件信息 | `--detailed` |
| `-r` | `--risk-analysis` | 启用风险分析 | `-r` |
| `-g` | `--group-by` | 分组方式 | `-g type` |
| `-S` | `--sort-by` | 排序方式 | `-S risk` |
| `-I` | `--interactive` | 交互式选择模式 | `-I` |
| `-m` | `--min-risk` | 最低风险等级(0-100) | `-m 50` |

### 导出相关参数

| 参数 | 长格式 | 说明 | 示例 |
|------|--------|------|------|
| `-x` | `--export` | 导出格式 | `-x json` |
| | `--export-file` | 导出文件路径 | `--export-file report.json` |
| `-T` | `--table-format` | 表格格式 | `-T fancy` |
| `-w` | `--width` | 显示宽度限制 | `-w 120` |
| `-C` | `--columns` | 显示列 | `-C name,size,risk` |
| `-H` | `--no-header` | 不显示表头 | `-H` |

### 高级参数

| 参数 | 长格式 | 说明 | 示例 |
|------|--------|------|------|
| | `--clear-screen` | 交互模式中清屏 | `--clear-screen` |

## 🎨 分组和排序选项

### 分组方式 (`-g, --group-by`)
- `type` - 按文件类型分组
- `size` - 按文件大小分组
- `time` - 按修改时间分组
- `risk` - 按风险等级分组
- `location` - 按文件位置分组

### 排序方式 (`-S, --sort-by`)
- `name` - 按文件名排序
- `size` - 按文件大小排序
- `time` - 按修改时间排序
- `mtime` - 按修改时间排序
- `atime` - 按访问时间排序
- `risk` - 按风险评分排序
- `importance` - 按重要性排序

## 🛡️ 风险评估系统

### 风险等级
- **CRITICAL** (90-100分) - 极高风险，强烈建议保留
- **HIGH** (75-89分) - 高风险，建议仔细检查
- **MEDIUM** (50-74分) - 中等风险，建议确认
- **LOW** (25-49分) - 低风险，相对安全
- **SAFE** (0-24分) - 安全，可以删除

### 风险评分因素
- **文件类型** (30%) - 文档、配置文件等重要性更高
- **文件大小** (20%) - 适中大小的文件通常更重要
- **修改时间** (25%) - 最近修改的文件重要性更高
- **文件位置** (15%) - 桌面、文档等重要目录权重更高
- **文件关联** (10%) - 有关联文件的权重更高

## 📁 文件类型分类

### 支持的文件类型
- **document** - 文档类：docx, pdf, txt, rtf等
- **spreadsheet** - 表格类：xlsx, csv, ods等
- **presentation** - 演示文稿：pptx, key, odp等
- **image** - 图片类：jpg, png, gif, svg等
- **audio** - 音频类：mp3, wav, flac等
- **video** - 视频类：mp4, avi, mkv等
- **archive** - 压缩包：zip, rar, 7z等
- **executable** - 可执行文件：exe, app, deb等
- **code** - 代码文件：py, js, cpp, java等
- **config** - 配置文件：conf, ini, plist等
- **temporary** - 临时文件：tmp, cache, log等

## 📋 导出格式说明

### JSON格式
包含完整的文件分析和风险评估数据，适合程序处理：
```json
{
  "file_list": [
    {
      "path": "/path/to/file.txt",
      "filename": "file.txt",
      "type": "document",
      "size": 1024,
      "risk_level": "MEDIUM",
      "risk_score": 65,
      "selected": false
    }
  ]
}
```

### CSV格式
表格形式，适合Excel等工具分析：
```csv
filename,path,type,size,mtime,risk_level,risk_score,selected
file.txt,/path/to/file.txt,document,1024,1703097600,MEDIUM,65,false
```

### TXT格式
人类友好的可读格式，包含统计信息和详细列表。

## 🔧 配置文件支持

可以在 `~/.trash-cleaner.conf` 中设置默认参数：

```ini
# 预检查相关配置
list_only=false
detailed_list=false
risk_analysis=true
group_by=type
sort_by=name
interactive_mode=true
min_risk_level=0

# 导出相关配置
export_format=
export_file=
table_format=auto
display_width=auto
display_columns=name,size,time,risk,type
no_header=false

# 界面相关配置
clear_screen=false
```

## 💡 最佳实践

### 1. 首次使用建议
```bash
# 先查看概览，了解回收站内容
./trash-cleaner.sh -L

# 查看详细信息和风险分析
./trash-cleaner.sh --detailed -r

# 生成完整报告备查
./trash-cleaner.sh -L -x json --export-file backup-analysis.json
```

### 2. 安全清理流程
```bash
# 1. 预览高风险文件
./trash-cleaner.sh -L -m 70

# 2. 交互式选择
./trash-cleaner.sh -I

# 3. 预览模式确认选择
./trash-cleaner.sh -n -I

# 4. 执行实际删除
./trash-cleaner.sh -I
```

### 3. 定期维护
```bash
# 生成月度清理报告
./trash-cleaner.sh --detailed -x txt --export-file "cleanup-$(date +%Y%m).txt"

# 清理30天前的低风险文件
./trash-cleaner.sh -d 30d -m 0 --max-risk 40 -y

# 交互式清理大文件
./trash-cleaner.sh -I -s 100M
```

## ⚠️ 注意事项

1. **首次使用** - 建议先使用 `-L` 参数预览文件列表
2. **高风险文件** - 对于CRITICAL和HIGH风险等级的文件，建议手动确认
3. **备份重要文件** - 删除前确保重要文件已有备份
4. **大文件处理** - 处理大量文件时可能需要较长时间
5. **权限要求** - 确保对回收站目录有适当的读写权限

## 🐛 故障排除

### 常见问题

**Q: 提示"未找到回收站目录"**
A: 检查操作系统类型和回收站路径权限

**Q: 风险分析结果不准确**
A: 可以通过配置文件调整风险权重因子

**Q: 导出文件失败**
A: 检查目标目录的写入权限

**Q: 交互模式无响应**
A: 检查终端环境，确保支持交互式操作

### 调试模式
使用 `-v` 参数启用详细输出模式：
```bash
./trash-cleaner.sh -L -v
```

## 📈 性能优化

### 处理大量文件
- 使用 `-m` 参数过滤低风险文件
- 分批处理，避免一次性处理过多文件
- 使用 `--no-color` 禁用彩色输出提高性能

### 内存使用优化
- 大文件分析时会自动使用流式处理
- 缓存机制减少重复分析开销
- 分页显示避免内存溢出

---

*更多信息请参考项目主页或使用 `--help` 查看完整参数列表。*