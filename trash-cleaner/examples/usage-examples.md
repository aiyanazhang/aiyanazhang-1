# 回收站清理工具使用示例

这个文档包含了各种使用场景的具体示例。

## 基本使用

### 1. 交互式清理（默认模式）
```bash
# 最简单的用法，会提示用户确认
./trash-cleaner.sh

# 显示详细信息
./trash-cleaner.sh --verbose
```

### 2. 预览模式
```bash
# 查看将要删除什么，但不实际删除
./trash-cleaner.sh --dry-run

# 预览模式 + 详细输出
./trash-cleaner.sh --dry-run --verbose
```

### 3. 自动清理
```bash
# 跳过确认提示，自动执行清理
./trash-cleaner.sh --yes

# 自动清理 + 详细日志
./trash-cleaner.sh --yes --verbose
```

## 按类型清理

### 1. 仅清理文件
```bash
./trash-cleaner.sh --type files
```

### 2. 仅清理目录
```bash
./trash-cleaner.sh --type dirs
```

### 3. 清理所有内容（默认）
```bash
./trash-cleaner.sh --type all
```

## 按时间过滤

### 1. 清理30天前的文件
```bash
./trash-cleaner.sh --older-than 30d
```

### 2. 清理1周前的文件
```bash
./trash-cleaner.sh --older-than 1w
```

### 3. 清理6个月前的文件
```bash
./trash-cleaner.sh --older-than 6M
```

### 4. 清理1年前的文件
```bash
./trash-cleaner.sh --older-than 1y
```

## 按大小过滤

### 1. 清理大于100MB的文件
```bash
./trash-cleaner.sh --size-limit 100M
```

### 2. 清理大于1GB的文件
```bash
./trash-cleaner.sh --size-limit 1G
```

### 3. 清理大于500KB的文件
```bash
./trash-cleaner.sh --size-limit 500K
```

## 按文件名模式过滤

### 1. 清理所有.tmp文件
```bash
./trash-cleaner.sh --pattern "*.tmp"
```

### 2. 清理所有以"backup"开头的文件
```bash
./trash-cleaner.sh --pattern "backup*"
```

### 3. 清理所有包含"test"的文件
```bash
./trash-cleaner.sh --pattern "*test*"
```

### 4. 清理特定扩展名的文件
```bash
./trash-cleaner.sh --pattern "*.log"
./trash-cleaner.sh --pattern "*.cache"
./trash-cleaner.sh --pattern "*.old"
```

## 组合条件

### 1. 清理30天前的临时文件
```bash
./trash-cleaner.sh --older-than 30d --pattern "*.tmp" --type files
```

### 2. 清理大于100MB且超过7天的文件
```bash
./trash-cleaner.sh --size-limit 100M --older-than 7d --type files
```

### 3. 预览大文件清理
```bash
./trash-cleaner.sh --dry-run --size-limit 500M --verbose
```

### 4. 自动清理旧的日志文件
```bash
./trash-cleaner.sh --yes --older-than 30d --pattern "*.log" --type files
```

## 配置文件使用

### 1. 使用自定义配置文件
```bash
./trash-cleaner.sh --config /path/to/my-config.conf
```

### 2. 创建个人配置文件
```bash
# 复制示例配置
cp config/trash-cleaner.conf.example ~/.trash-cleaner.conf

# 编辑配置文件
nano ~/.trash-cleaner.conf

# 使用配置文件运行
./trash-cleaner.sh
```

## 日志和审计

### 1. 指定日志文件
```bash
./trash-cleaner.sh --log /var/log/trash-cleaner.log
```

### 2. 查看日志
```bash
# 查看完整日志
cat ~/.trash-cleaner.log

# 查看最近的日志条目
tail -50 ~/.trash-cleaner.log

# 实时监控日志
tail -f ~/.trash-cleaner.log
```

### 3. 禁用彩色输出（适合日志记录）
```bash
./trash-cleaner.sh --no-color --verbose > cleanup.log 2>&1
```

## 高级用法

### 1. 限制目录遍历深度
```bash
./trash-cleaner.sh --max-depth 3
```

### 2. 静默运行（无进度条）
```bash
./trash-cleaner.sh --no-progress --no-color
```

### 3. 定期清理（cron任务）
```bash
# 每天凌晨2点自动清理30天前的文件
# 添加到 crontab -e：
0 2 * * * /path/to/trash-cleaner.sh --yes --older-than 30d --no-color >> /var/log/auto-cleanup.log 2>&1
```

### 4. 批处理脚本
```bash
#!/bin/bash
# cleanup-script.sh - 批量清理脚本

echo "开始定期清理..."

# 清理临时文件（30天）
./trash-cleaner.sh --yes --older-than 30d --pattern "*.tmp" --type files

# 清理日志文件（60天）
./trash-cleaner.sh --yes --older-than 60d --pattern "*.log" --type files

# 清理大文件（大于1GB，14天）
./trash-cleaner.sh --yes --size-limit 1G --older-than 14d --type files

echo "清理完成！"
```

## 安全使用建议

### 1. 总是先使用预览模式
```bash
# 先预览要删除的内容
./trash-cleaner.sh --dry-run --verbose

# 确认无误后再执行实际清理
./trash-cleaner.sh --yes
```

### 2. 针对特定内容进行清理
```bash
# 不要一次清理所有内容，而是分批处理
./trash-cleaner.sh --older-than 90d --dry-run  # 先查看90天前的内容
./trash-cleaner.sh --older-than 90d            # 确认后清理
```

### 3. 保持日志记录
```bash
# 总是启用详细日志，便于审计
./trash-cleaner.sh --verbose --log /var/log/cleanup.log
```

## 故障排除

### 1. 权限问题
```bash
# 如果遇到权限问题，使用sudo（谨慎）
sudo ./trash-cleaner.sh --verbose

# 或者检查当前用户权限
ls -la ~/.local/share/Trash/
```

### 2. 配置问题
```bash
# 验证配置文件语法
head -20 ~/.trash-cleaner.conf

# 使用默认配置运行
./trash-cleaner.sh --config /dev/null
```

### 3. 调试模式
```bash
# 启用bash调试
bash -x ./trash-cleaner.sh --dry-run --verbose
```

## 性能优化

### 1. 处理大量文件
```bash
# 限制遍历深度以提高性能
./trash-cleaner.sh --max-depth 2

# 分批处理
./trash-cleaner.sh --pattern "*.tmp" --older-than 30d
./trash-cleaner.sh --pattern "*.log" --older-than 60d
```

### 2. 网络存储
```bash
# 对于网络存储，使用更保守的设置
./trash-cleaner.sh --older-than 90d --no-progress
```

## 不同操作系统的特殊用法

### Linux
```bash
# 清理XDG标准回收站
./trash-cleaner.sh --verbose

# 检查多个挂载点的回收站
./trash-cleaner.sh --dry-run --verbose
```

### macOS
```bash
# 清理用户回收站
./trash-cleaner.sh --verbose

# 清理外置设备回收站
./trash-cleaner.sh --dry-run --verbose
```

### Windows (通过WSL/MSYS2)
```bash
# 在Windows子系统中运行
./trash-cleaner.sh --verbose --dry-run
```