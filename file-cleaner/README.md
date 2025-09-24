# 本地目录文件清理脚本系统

一个交互式的本地目录文件清理工具，提供安全、可追溯的文件删除功能。

## 功能特性

- **🛡️ 安全删除**: 多重安全检查，防止误删重要文件
- **🧠 智能识别**: 自动识别系统文件、配置文件、项目文件
- **💬 交互确认**: 提供多种确认方式，包括批量、逐个、自动安全模式
- **⚖️ 风险评估**: 对每个文件进行风险评估和等级标识
- **🎨 彩色界面**: 支持彩色终端输出，直观显示文件风险等级
- **📦 自动备份**: 删除前自动创建备份，支持一键恢复
- **📝 操作日志**: 详细记录所有操作历史，支持审计
- **🔄 回滚功能**: 支持操作回滚和文件恢复
- **⚙️ 配置管理**: 灵活的配置文件系统，支持用户自定义规则

## 系统要求

- Python 3.6+
- Linux/Unix/macOS 系统
- 终端支持（推荐支持彩色输出）

## 快速开始

### 1. 下载和安装

```bash
# 下载项目
git clone <repository-url>
cd file-cleaner

# 给启动脚本添加执行权限
chmod +x clean-files.py
```

### 2. 基本使用

```bash
# 交互模式（推荐）
./clean-files.py

# 命令行模式示例
./clean-files.py -p "*.tmp"           # 删除临时文件
./clean-files.py -p "*.log" -r        # 递归删除日志文件
./clean-files.py -p "backup_*" --dry-run  # 预览模式
```

## 详细使用指南

### 交互模式

启动交互模式，输入文件模式进行搜索：

```bash
./clean-files.py

╔══════════════════════════════════════════════════════════════╗
║                    文件清理工具                                ║
║                   交互式模式                                   ║
╚══════════════════════════════════════════════════════════════╝

clean> *.tmp          # 搜索临时文件
clean> backup_*       # 搜索备份文件
clean> help           # 显示帮助
clean> backups        # 查看备份列表
clean> restore        # 恢复文件
clean> quit           # 退出
```

### 命令行模式

```bash
# 基本语法
./clean-files.py -p <模式> [选项]

# 常用选项
-p, --pattern PATTERN    要搜索的文件模式
-r, --recursive          递归搜索子目录
-d, --directory DIR      指定搜索目录
--dry-run               预览模式，不实际删除
-v, --verbose           详细输出
--list-backups          列出所有备份
--restore BACKUP_ID     恢复指定备份
```

### 支持的文件模式

| 模式类型 | 示例 | 说明 |
|----------|------|------|
| 精确匹配 | `test.txt` | 匹配确切的文件名 |
| 扩展名匹配 | `*.tmp` | 匹配特定扩展名的文件 |
| 前缀匹配 | `temp*` | 匹配指定前缀的文件 |
| 正则表达式 | `^backup.*\.old$` | 使用正则表达式匹配 |

## 安全等级说明

系统会对每个文件进行安全评估，并用颜色和图标标识：

- 🟢 **安全** - 临时文件、缓存文件等，可以放心删除
- 🔵 **谨慎** - 隐藏文件、最近修改的文件，建议确认
- 🟡 **警告** - 配置文件、大文件等，删除前请检查
- 🔴 **危险** - 项目重要文件、可执行文件，删除需谨慎
- ⚫ **禁止** - 系统文件、关键配置，禁止删除

## 配置系统

### 主配置文件 (~/.clean-script.conf)

```ini
# 基础设置
DEFAULT_BACKUP_DIR="$HOME/.clean-script-backups"
MAX_BACKUP_AGE_DAYS=30
LOG_LEVEL="INFO"
LOG_FILE="$HOME/.clean-script.log"

# 安全设置  
ENABLE_BACKUP=true
REQUIRE_CONFIRMATION=true
PROTECTED_DIRS="/bin:/usr:/etc:/home"
DANGEROUS_PATTERNS="*:/*:.*"

# 界面设置
USE_COLORS=true
SHOW_PROGRESS=true
PAGE_SIZE=20

# 文件大小警告阈值 (单位: MB)
LARGE_FILE_THRESHOLD=100

# 最近修改文件警告阈值 (单位: 小时)
RECENT_MODIFIED_THRESHOLD=24
```

### 保护规则文件 (~/.clean-script-protected.json)

```json
{
  "system_dirs": ["/bin", "/usr", "/etc", "/var"],
  "config_files": [".bashrc", ".profile", ".gitconfig"],
  "important_extensions": [".sql", ".json", ".yaml", ".md"],
  "project_files": ["package.json", "Makefile", "requirements.txt"],
  "user_rules": [
    {
      "pattern": "*.bak",
      "action": "warn",
      "message": "备份文件删除需要额外确认"
    },
    {
      "pattern": "*.tmp",
      "action": "safe",
      "message": "临时文件通常可以安全删除"
    }
  ]
}
```

## 使用示例

### 示例1: 清理临时文件

```bash
$ ./clean-files.py -p "*.tmp"

搜索模式: '*.tmp'
搜索目录: /home/user/project
------------------------------------------------------------
输入类型: wildcard
风险等级: 低
说明: 安全的扩展名模式: tmp

🔍 搜索匹配文件...
找到 3 个文件，总大小 1.2KB

🛡️ 执行安全检查...

找到的文件列表:
================================================================================

🟢 SAFE (3个文件)
------------------------------------------------------------
   1. temp1.tmp
    路径: ./temp1.tmp
    大小: 256B | 修改: 2小时前 | 风险分数: 5/100
    原因: 文件类型 (.tmp) 通常可以安全删除

请选择操作:
1. 批量确认删除所有可删除文件
2. 逐个确认每个文件
3. 只删除标记为'安全'的文件
4. 预览模式（不删除任何文件）
5. 取消操作

请输入选择 (1-5): 3

自动安全模式
将删除 3 个安全文件
跳过 0 个非安全文件

确认删除这些安全文件? (yes/no): yes

✅ 备份已创建: backup_20241220_143022

============================================================
🗑️ 删除操作完成
============================================================
📊 操作统计:
   ✅ 成功删除: 3 个文件
   ❌ 删除失败: 0 个文件
   ⏭️ 跳过文件: 0 个文件
   💾 释放空间: 1.2KB
   ⏱️ 耗时: 0.35 秒
   🛡️ 备份ID: backup_20241220_143022
```

### 示例2: 预览删除操作

```bash
$ ./clean-files.py -p "backup_*" --dry-run

📋 预览模式 - 不会实际删除文件

找到的文件列表:
================================================================================

🔵 CAUTION (2个文件)
------------------------------------------------------------
   1. backup_old.tar.gz (大文件)
   2. backup_2023.sql (重要文件类型)

操作汇总:
==================================================
📁 总文件数: 2
💾 总大小: 156MB
✅ 可删除: 2
🚫 被保护: 0
```

### 示例3: 恢复误删文件

```bash
$ ./clean-files.py --list-backups

📋 备份列表 (共 3 个备份):
================================================================================
 1. backup_20241220_143022
    📅 时间: 2024-12-20 14:30:22 (2.5小时前)
    📁 文件: 3 个
    💾 大小: 1.2KB
    📝 描述: 清理操作: *.tmp

$ ./clean-files.py --restore backup_20241220_143022

🔄 开始恢复备份: backup_20241220_143022

📋 备份详细信息: backup_20241220_143022
============================================================
📅 创建时间: 2024-12-20 14:30:22
📝 描述: 清理操作: *.tmp
📁 文件数量: 3
💾 总大小: 1.2KB

  ✅ 已恢复: temp1.tmp
  ✅ 已恢复: temp2.tmp
  ✅ 已恢复: temp3.tmp

🎉 恢复完成: 3/3 个文件
```

## 项目结构

```
file-cleaner/
├── src/                      # 源代码目录
│   ├── main.py              # 主程序入口
│   ├── config_manager.py    # 配置管理模块
│   ├── input_validator.py   # 输入验证模块
│   ├── file_matcher.py      # 文件匹配引擎
│   ├── safety_checker.py    # 安全检查模块
│   ├── confirmation_ui.py   # 确认界面模块
│   ├── backup_manager.py    # 备份管理模块
│   ├── file_deleter.py      # 删除执行器
│   ├── logger.py           # 日志记录器
│   └── rollback_manager.py  # 回滚管理器
├── config/                   # 配置文件目录
│   ├── default.conf         # 默认配置文件
│   └── protected-rules.json # 保护规则文件
├── tests/                    # 测试目录
│   └── test_suite.py        # 测试套件
├── clean-files.py           # 启动脚本
└── README.md                # 说明文档
```

## 开发和测试

### 运行测试

```bash
# 运行完整测试套件
python3 tests/test_suite.py

# 运行特定测试
python3 -m unittest tests.test_suite.TestConfigManager
```

### 开发模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 测试模式（不实际删除文件）
./clean-files.py -p "*.tmp" --dry-run -v
```

## 故障排除

### 常见问题

1. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x clean-files.py
   
   # 对于需要 sudo 权限的文件
   sudo ./clean-files.py -p "pattern"
   ```

2. **Python版本问题**
   ```bash
   # 检查Python版本
   python3 --version
   
   # 确保使用Python 3.6+
   python3 clean-files.py
   ```

3. **配置文件问题**
   ```bash
   # 重新生成默认配置
   rm ~/.clean-script.conf
   ./clean-files.py config
   ```

4. **备份空间不足**
   ```bash
   # 清理旧备份
   ./clean-files.py --list-backups
   
   # 手动清理备份目录
   rm -rf ~/.clean-script-backups/old_backup_*
   ```

### 日志和调试

```bash
# 查看日志文件
tail -f ~/.clean-script.log

# 启用详细输出
./clean-files.py -p "*.tmp" -v

# 查看操作历史
./clean-files.py
clean> history
```

## 安全注意事项

1. **备份重要数据**: 虽然工具会自动创建备份，但建议重要数据另外备份
2. **谨慎使用通配符**: 避免使用过于宽泛的模式如 `*`
3. **测试模式**: 首次使用时建议使用 `--dry-run` 预览
4. **权限管理**: 不要以root权限运行，除非确实需要
5. **定期清理**: 定期清理旧备份以节省磁盘空间

## 贡献指南

欢迎贡献代码和改进建议！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发规范

- 遵循 PEP 8 代码规范
- 添加适当的注释和文档字符串
- 为新功能编写测试用例
- 确保所有测试通过

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 版本历史

- **v1.0.0** (2024): 初始版本
  - 实现基本的文件搜索和删除功能
  - 支持多重安全检查
  - 提供交互式和命令行界面
  - 集成备份和恢复功能
  - 完整的日志记录系统

## 联系信息

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送 Pull Request
- 邮件联系: [your-email@example.com]

---

**感谢使用本地目录文件清理脚本系统！希望它能帮助您更加安全、高效地管理文件。**