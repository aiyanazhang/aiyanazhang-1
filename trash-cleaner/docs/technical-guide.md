# 回收站清理工具技术文档

## 架构概述

本系统采用模块化设计，每个模块负责特定功能，通过主入口脚本进行协调。

### 核心模块

1. **system_detector.sh** - 系统检测器
2. **security_checker.sh** - 安全检查器  
3. **config_manager.sh** - 配置管理器
4. **trash_scanner.sh** - 回收站扫描器
5. **cleanup_executor.sh** - 清理执行器
6. **logger.sh** - 日志系统
7. **ui.sh** - 用户界面

## 安全机制

### 路径白名单验证

系统仅允许操作预定义的回收站路径：

```bash
# macOS
~/.Trash/
/Volumes/*/Trash/

# Linux  
~/.local/share/Trash/files/
~/.trash/
$mount_point/.Trash-$UID

# Windows
C:\$Recycle.Bin\
C:\RECYCLER\
```

### 多层安全检查

1. **路径规范化** - 解析符号链接，获取真实路径
2. **黑名单检查** - 拒绝操作系统关键目录
3. **白名单验证** - 仅允许回收站路径模式
4. **权限验证** - 检查读写权限
5. **深度限制** - 防止过深路径遍历

## 配置系统

### 配置优先级

1. 命令行参数（最高优先级）
2. 配置文件设置
3. 默认值（最低优先级）

### 配置处理流程

```bash
init_config() -> load_config_file() -> parse_command_line() -> apply_cli_overrides() -> validate_config()
```

## 扫描算法

### 目录树遍历

使用 `find` 命令进行高效遍历：

```bash
find "$dir_path" -mindepth 1 -maxdepth $max_depth -print0
```

### 过滤器链

1. **时间过滤器** - 基于文件修改时间
2. **大小过滤器** - 基于文件大小  
3. **模式过滤器** - 基于文件名模式匹配

## 日志格式

```
[timestamp] level source:line category pid - message | metadata
```

示例：
```
[2024-12-20 10:30:00] INFO system_detector.sh:45 SYSTEM 1234 - 回收站路径检测完成 | paths=3, accessible=2
```

## 错误处理

### 错误码定义

- 1: 安全检查失败
- 2: 文件不存在  
- 3: 删除操作失败
- 4: 权限不足

### 异常恢复策略

- **权限错误** - 提示使用sudo或检查权限
- **文件被占用** - 记录失败继续处理其他文件
- **网络中断** - 重试机制，超时后报告失败

## 性能优化

### 批量处理

- 避免单文件循环删除
- 使用批量删除操作
- 异步进度反馈

### 内存管理

- 流式处理大目录
- 及时释放资源
- 分块处理数据

## 测试策略

### 测试分类

1. **单元测试** - 各模块功能测试
2. **集成测试** - 模块间协作测试
3. **安全测试** - 安全机制验证
4. **性能测试** - 大量文件处理测试

### 测试覆盖

- 功能测试：正常清理、预览模式、错误处理
- 安全测试：路径验证、权限检查、恶意输入
- 兼容测试：不同操作系统、不同Shell版本

## 扩展性设计

### 添加新的操作系统支持

1. 在 `detect_os()` 中添加检测逻辑
2. 在 `get_trash_paths()` 中添加路径规则
3. 更新安全白名单模式
4. 添加对应测试用例

### 添加新的过滤器

1. 在 `trash_scanner.sh` 中实现过滤函数
2. 在配置管理中添加参数解析
3. 更新帮助信息和文档
4. 添加测试用例

## 部署建议

### 生产环境

- 使用专用配置文件
- 启用详细日志记录
- 设置日志轮转
- 定期运行测试

### 自动化部署

```bash
# 定期清理任务
0 2 * * 0 /opt/trash-cleaner/trash-cleaner.sh --config /etc/trash-cleaner.conf --yes --older-than 30d

# 日志监控
tail -f /var/log/trash-cleaner.log | grep ERROR
```

## 已知限制

1. **网络存储** - 对网络文件系统的支持有限
2. **大文件** - 超大文件(>10GB)删除可能较慢
3. **并发** - 不支持多实例并发运行同一回收站
4. **符号链接** - 复杂符号链接结构可能导致误判

## 故障排除指南

### 常见问题诊断

1. **权限问题**
   ```bash
   ls -la ~/.local/share/Trash/
   id
   ```

2. **配置问题**  
   ```bash
   ./trash-cleaner.sh --config /dev/null --dry-run
   ```

3. **路径问题**
   ```bash  
   bash -x ./trash-cleaner.sh --dry-run 2>&1 | grep "安全检查"
   ```

### 调试技巧

- 使用 `--dry-run --verbose` 查看详细操作
- 启用bash调试：`bash -x script.sh`
- 检查日志文件中的ERROR和WARN消息
- 使用strace跟踪系统调用（高级）