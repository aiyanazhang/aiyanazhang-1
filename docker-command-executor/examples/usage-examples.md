# Docker 命令执行工具使用示例

本文档提供了 Docker 命令执行工具的详细使用示例，涵盖从基础操作到高级功能的各种场景。

## 基础命令示例

### 文件系统操作

```bash
# 列出根目录内容
python docker-executor.py ls /

# 详细列出当前目录
python docker-executor.py ls -la

# 查看目录结构
python docker-executor.py ls -la /usr/bin

# 获取当前工作目录
python docker-executor.py pwd
```

### 文件内容查看

```bash
# 查看系统版本信息
python docker-executor.py cat /etc/os-release

# 查看文件前10行
python docker-executor.py head /etc/passwd

# 查看文件后10行
python docker-executor.py tail /var/log/messages

# 查看文件前5行
python docker-executor.py head -n 5 /etc/hosts
```

### 系统信息查询

```bash
# 查看系统内核信息
python docker-executor.py uname -a

# 查看当前用户
python docker-executor.py whoami

# 查看当前时间
python docker-executor.py date

# 查看系统架构
python docker-executor.py uname -m
```

## 文本处理示例

### 搜索和过滤

```bash
# 在文件中搜索特定文本
python docker-executor.py grep "root" /etc/passwd

# 大小写不敏感搜索
python docker-executor.py grep -i "error" /var/log/messages

# 显示行号
python docker-executor.py grep -n "bash" /etc/passwd

# 搜索多个文件
python docker-executor.py grep "localhost" /etc/hosts /etc/hostname
```

### 文本统计和处理

```bash
# 统计文件行数
python docker-executor.py wc -l /etc/passwd

# 统计字符数
python docker-executor.py wc -c /etc/hostname

# 统计单词数
python docker-executor.py wc -w /etc/hostname

# 排序文件内容
python docker-executor.py sort /etc/passwd

# 去重排序
python docker-executor.py sort /etc/passwd | uniq
```

## 文件查找示例

### 基础查找

```bash
# 查找文件
python docker-executor.py find /etc -name "*.conf"

# 查找目录
python docker-executor.py find /var -type d -name "log*"

# 按大小查找
python docker-executor.py find /tmp -size +1M

# 按时间查找
python docker-executor.py find /var/log -mtime -1
```

### 文件信息

```bash
# 查看文件详细信息
python docker-executor.py stat /etc/passwd

# 获取文件路径信息
python docker-executor.py basename /usr/bin/python3
python docker-executor.py dirname /usr/bin/python3

# 获取绝对路径
python docker-executor.py realpath /etc/passwd
```

## 目录挂载示例

### 挂载本地目录

```bash
# 挂载目录并列出内容
python docker-executor.py --mount /home/user/documents ls -la

# 挂载目录并查看文件
python docker-executor.py --mount /tmp cat important.txt

# 挂载目录并搜索文件
python docker-executor.py --mount /var/log find . -name "*.log"
```

### 工作目录操作

```bash
# 设置工作目录
python docker-executor.py --workdir /tmp pwd

# 在指定工作目录执行命令
python docker-executor.py --workdir /usr/bin ls -la
```

## 批量执行示例

### 创建批量命令文件

创建 `system_check.txt`:
```
uname -a
whoami
date
pwd
ls -la /
cat /etc/os-release
grep "root" /etc/passwd
```

执行批量命令:
```bash
python docker-executor.py --batch system_check.txt
```

### 日志分析批量命令

创建 `log_analysis.txt`:
```
find /var/log -name "*.log" -type f
wc -l /var/log/messages
tail -20 /var/log/messages
grep -i "error" /var/log/messages
```

执行:
```bash
python docker-executor.py --batch log_analysis.txt --mount /var/log
```

## 验证和安全示例

### 命令验证

```bash
# 验证安全命令
python docker-executor.py --validate "ls -la"

# 验证危险命令
python docker-executor.py --validate "rm -rf /"

# 验证复杂命令
python docker-executor.py --validate "find /tmp -name '*.txt' -exec cat {} \;"
```

### 安全测试

```bash
# 测试命令注入
python docker-executor.py --validate "ls; rm -rf /"

# 测试路径遍历
python docker-executor.py --validate "cat ../../../../etc/passwd"

# 测试特殊字符
python docker-executor.py --validate "ls `whoami`"
```

## 监控和诊断示例

### 系统状态查看

```bash
# 查看完整状态
python docker-executor.py --status

# JSON格式输出
python docker-executor.py --status --output json
```

### 命令历史

```bash
# 查看最近10条命令
python docker-executor.py --history 10

# 查看最近5条命令
python docker-executor.py --history 5
```

### 性能监控

```bash
# 详细模式执行
python docker-executor.py --verbose find /usr -name "python*"

# 设置超时
python docker-executor.py --timeout 10 find / -name "*.conf"
```

## 交互模式示例

启动交互模式:
```bash
python docker-executor.py --interactive
```

交互会话示例:
```
docker-exec> ls -la
状态: ✓ 成功
退出码: 0
执行时间: 0.15s

--- 标准输出 ---
total 48
drwxr-xr-x    1 root     root          4096 Nov 15 10:30 .
drwxr-xr-x    1 root     root          4096 Nov 15 10:30 ..
...

docker-exec> uname -a
状态: ✓ 成功
退出码: 0
执行时间: 0.08s

--- 标准输出 ---
Linux abc123 5.4.0-89-generic #100-Ubuntu SMP Fri Sep 24 14:50:10 UTC 2021 x86_64 Linux

docker-exec> status
health:
  initialized: true
  docker_healthy: true
  active_executions: 0
  total_executions: 2
  success_rate: 100.0
  average_execution_time: 0.12

docker-exec> history 5
[最近5条命令历史]

docker-exec> exit
```

## 高级配置示例

### 自定义配置文件

创建 `config/production.json`:
```json
{
  "docker": {
    "base_image": "ubuntu:20.04",
    "timeout": 60,
    "memory_limit": "512m",
    "cpu_limit": 1.0
  },
  "security": {
    "allowed_commands": [
      "ls", "cat", "grep", "find", "head", "tail",
      "wc", "sort", "uniq", "awk", "sed"
    ],
    "max_file_size": 52428800
  },
  "logging": {
    "level": "DEBUG",
    "file_path": "/var/log/docker-executor.log"
  }
}
```

使用配置:
```bash
python docker-executor.py --config config/production.json ls -la
```

### 环境变量配置

```bash
# 设置环境变量
export DOCKER_BASE_IMAGE=alpine:3.14
export DOCKER_TIMEOUT=120
export LOG_LEVEL=DEBUG

# 使用环境变量
python docker-executor.py ls -la
```

## 错误处理示例

### 命令格式错误

```bash
# 空命令
python docker-executor.py ""
# 输出: 错误: 命令不能为空

# 不支持的操作符
python docker-executor.py "ls | grep test"
# 输出: 错误: 不支持管道操作
```

### 权限错误

```bash
# 被禁止的命令
python docker-executor.py rm file.txt
# 输出: 验证失败: 命令 'rm' 被明确禁止

# 危险路径访问
python docker-executor.py cat /etc/shadow
# 输出: 验证失败: 访问危险路径: /etc/shadow
```

### Docker错误

```bash
# Docker服务未运行时
python docker-executor.py ls
# 输出: 错误: Docker管理器初始化失败
```

## 实际应用场景

### 1. 日志分析

```bash
# 分析Apache访问日志
python docker-executor.py --mount /var/log/apache2 \
  grep "404" access.log | wc -l

# 查看最新错误
python docker-executor.py --mount /var/log \
  tail -50 error.log | grep -i "critical"
```

### 2. 系统巡检

创建 `health_check.txt`:
```
uname -a
date
whoami
df -h
free -m
ps aux | head -20
netstat -tuln
```

执行:
```bash
python docker-executor.py --batch health_check.txt --output json > health_report.json
```

### 3. 文件审计

```bash
# 查找大文件
python docker-executor.py --mount /var/log \
  find . -size +100M -type f

# 查找最近修改的文件
python docker-executor.py --mount /etc \
  find . -mtime -1 -type f
```

### 4. 配置检查

```bash
# 检查配置文件语法
python docker-executor.py --mount /etc/nginx \
  grep -n "server_name" nginx.conf

# 查看服务状态
python docker-executor.py --mount /etc/systemd/system \
  ls -la *.service
```

## 最佳实践

### 1. 安全使用

- 始终使用 `--validate` 验证不确定的命令
- 定期检查命令历史发现异常
- 使用最小权限原则配置允许命令列表

### 2. 性能优化

- 对于长时间运行的命令设置合适的超时
- 使用批量执行减少容器创建开销
- 监控系统资源使用情况

### 3. 故障排除

- 使用 `--verbose` 模式获取详细信息
- 检查 `--status` 了解系统健康状态
- 查看命令历史分析问题模式

这些示例涵盖了工具的主要功能和使用场景，可以根据实际需求进行调整和扩展。