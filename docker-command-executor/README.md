# Docker 命令执行工具

一个通过 Docker 容器执行系统命令的安全工具，允许用户在隔离的环境中安全地运行各种命令。

## 特性

- **环境隔离**: 在独立的容器环境中执行命令，避免对宿主系统的影响
- **安全性**: 通过容器沙箱机制和白名单机制确保命令执行的安全性
- **可重复性**: 确保命令在一致的环境中执行
- **易用性**: 提供简单直观的命令行接口
- **监控功能**: 提供执行监控、性能分析和历史记录

## 安装

### 系统要求

- Python 3.7+
- Docker Engine
- Linux/macOS (推荐)

### 安装步骤

1. 克隆仓库:
```bash
git clone <repository-url>
cd docker-command-executor
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 确保Docker服务运行:
```bash
sudo systemctl start docker
# 或
sudo service docker start
```

4. 测试安装:
```bash
python docker-executor.py --status
```

## 快速开始

### 基础用法

```bash
# 执行简单命令
python docker-executor.py ls -la

# 查看系统信息
python docker-executor.py uname -a

# 查看文件内容
python docker-executor.py cat /etc/os-release
```

### 高级用法

```bash
# 挂载本地目录
python docker-executor.py --mount /home/user/data ls -la

# 设置超时时间
python docker-executor.py --timeout 60 find / -name "*.log"

# 仅验证命令安全性
python docker-executor.py --validate "rm -rf /"

# 批量执行命令
python docker-executor.py --batch commands.txt

# 交互模式
python docker-executor.py --interactive
```

## 配置

### 配置文件

创建配置文件 `config/custom.json`:

```json
{
  "docker": {
    "base_image": "alpine:latest",
    "timeout": 30,
    "memory_limit": "256m",
    "cpu_limit": 0.5,
    "network_mode": "none"
  },
  "security": {
    "allowed_commands": ["ls", "cat", "grep", "find"],
    "allow_network": false
  },
  "logging": {
    "level": "INFO",
    "file_path": "logs/executor.log"
  }
}
```

使用配置文件:
```bash
python docker-executor.py --config config/custom.json ls -la
```

### 环境变量

支持通过环境变量配置:

```bash
export DOCKER_BASE_IMAGE=ubuntu:20.04
export DOCKER_TIMEOUT=60
export LOG_LEVEL=DEBUG

python docker-executor.py ls -la
```

## 安全机制

### 命令白名单

默认只允许以下安全命令:
- 文件操作: `ls`, `cat`, `head`, `tail`, `find`, `stat`
- 系统信息: `whoami`, `uname`, `date`, `pwd`
- 文本处理: `grep`, `awk`, `sed`, `wc`, `sort`, `uniq`

### 危险命令阻止

自动阻止以下危险命令:
- 文件删除: `rm`, `rmdir`
- 权限操作: `sudo`, `su`, `chmod`, `chown`
- 系统控制: `reboot`, `shutdown`, `kill`

### 容器安全

- 非特权用户运行
- 只读文件系统
- 网络隔离
- 资源限制（CPU、内存）
- 安全选项配置

## 使用示例

### 1. 基础文件操作

```bash
# 列出目录内容
python docker-executor.py ls -la

# 查看文件内容
python docker-executor.py cat /etc/passwd

# 查找文件
python docker-executor.py find /tmp -name "*.txt"
```

### 2. 系统信息查询

```bash
# 查看系统版本
python docker-executor.py uname -a

# 查看当前用户
python docker-executor.py whoami

# 查看当前时间
python docker-executor.py date
```

### 3. 文本处理

```bash
# 搜索文本
python docker-executor.py grep "error" /var/log/messages

# 统计行数
python docker-executor.py wc -l /etc/passwd

# 排序内容
python docker-executor.py sort /etc/passwd
```

### 4. 挂载目录操作

```bash
# 挂载本地目录并操作
python docker-executor.py --mount /home/user/data ls -la
python docker-executor.py --mount /tmp cat important.txt
```

### 5. 批量执行

创建命令文件 `commands.txt`:
```
ls -la
uname -a
date
whoami
```

执行批量命令:
```bash
python docker-executor.py --batch commands.txt
```

### 6. 交互模式

```bash
python docker-executor.py --interactive
```

在交互模式中:
```
docker-exec> ls -la
docker-exec> cat /etc/os-release
docker-exec> status
docker-exec> history 5
docker-exec> exit
```

## 监控和诊断

### 查看系统状态

```bash
python docker-executor.py --status
```

输出示例:
```
health:
  initialized: true
  docker_healthy: true
  active_executions: 0
  total_executions: 15
  success_rate: 93.33
  average_execution_time: 1.24
```

### 查看命令历史

```bash
python docker-executor.py --history 10
```

### 性能分析

```bash
# 详细输出模式
python docker-executor.py --verbose ls -la

# JSON格式输出
python docker-executor.py --output json --status
```

## 故障排除

### 常见问题

1. **Docker连接失败**
   ```
   错误: Docker管理器初始化失败
   ```
   解决方案: 确保Docker服务运行，当前用户有Docker权限

2. **命令被拒绝**
   ```
   错误: 命令 'rm' 被明确禁止
   ```
   解决方案: 使用安全的替代命令或修改配置

3. **镜像拉取失败**
   ```
   错误: 无法获取基础镜像
   ```
   解决方案: 检查网络连接，或使用本地镜像

### 调试模式

```bash
# 启用详细日志
python docker-executor.py --verbose ls -la

# 仅验证不执行
python docker-executor.py --validate "dangerous-command"
```

## 开发

### 项目结构

```
docker-command-executor/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 主应用入口
│   ├── command_parser.py       # 命令解析器
│   ├── parameter_validator.py  # 参数验证器
│   ├── docker_manager.py       # Docker管理器
│   ├── execution_engine.py     # 执行引擎
│   └── config_manager.py       # 配置管理
├── tests/                      # 测试文件
├── config/                     # 配置文件
├── docs/                       # 文档
├── examples/                   # 示例
├── requirements.txt            # 依赖
└── docker-executor.py          # 启动脚本
```

### 运行测试

```bash
python -m pytest tests/
```

### 贡献

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目使用 MIT 许可证。详见 LICENSE 文件。

## 支持

如有问题或建议，请提交 Issue 或联系维护者。
