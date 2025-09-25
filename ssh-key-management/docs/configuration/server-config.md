# SSH服务器配置指南

## 概述

SSH服务器配置直接影响系统的安全性和可用性。正确的服务器配置可以有效防范攻击、提高性能并简化管理。本指南详细介绍sshd_config的配置选项和安全最佳实践。

## 配置文件基础

### 主要配置文件

| 文件路径 | 用途 | 权限 |
|----------|------|------|
| `/etc/ssh/sshd_config` | 主配置文件 | 644 |
| `/etc/ssh/ssh_host_*_key` | 服务器私钥 | 600 |
| `/etc/ssh/ssh_host_*_key.pub` | 服务器公钥 | 644 |
| `/etc/ssh/moduli` | DH参数 | 644 |

### 配置语法规则

```bash
# sshd_config 语法规则
# 注释以 # 开头
# 参数格式：关键字 值
# 大小写敏感
# 第一个匹配项生效

# 示例配置
Port 22
Protocol 2
PermitRootLogin no
PasswordAuthentication no
```

## 基础安全配置

### 必备安全设置

```bash
# /etc/ssh/sshd_config - 基础安全配置

# 协议版本（必须）
Protocol 2

# 禁用root直接登录
PermitRootLogin no

# 禁用空密码
PermitEmptyPasswords no

# 禁用密码认证（推荐使用密钥认证）
PasswordAuthentication no
ChallengeResponseAuthentication no

# 禁用主机认证
HostbasedAuthentication no

# 禁用X11转发（除非需要）
X11Forwarding no

# 限制认证尝试次数
MaxAuthTries 3

# 设置登录宽限时间
LoginGraceTime 30

# 限制并发连接
MaxStartups 10:30:60
MaxSessions 10
```

### 端口和网络配置

```bash
# 网络配置
Port 22                    # 标准端口
#Port 2222                 # 自定义端口（提高安全性）

# 监听地址
ListenAddress 0.0.0.0     # 监听所有IPv4地址
#ListenAddress ::          # 监听所有IPv6地址
#ListenAddress 192.168.1.10 # 监听特定IP

# 地址族
AddressFamily inet         # 仅IPv4
#AddressFamily inet6       # 仅IPv6  
#AddressFamily any         # IPv4和IPv6

# TCP保活设置
TCPKeepAlive yes
ClientAliveInterval 300
ClientAliveCountMax 2
```

## 认证配置

### 公钥认证配置

```bash
# 公钥认证设置
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 严格模式（检查文件权限）
StrictModes yes

# 禁用其他认证方式（可选）
PasswordAuthentication no
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no

# 限制认证时间
LoginGraceTime 30
MaxAuthTries 3
```

### 用户和组限制

```bash
# 用户访问控制
AllowUsers user1 user2 admin@192.168.1.*
DenyUsers guest test

# 组访问控制
AllowGroups ssh-users admin
DenyGroups guests

# 结合示例
Match User deploy
    AllowTcpForwarding no
    X11Forwarding no
    ForceCommand /usr/local/bin/deploy-script
```

## 高级安全配置

### 加密算法配置

```bash
# 密钥交换算法（按安全性排序）
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group16-sha512

# 主机密钥算法
HostKeyAlgorithms ssh-ed25519,ecdsa-sha2-nistp384,ecdsa-sha2-nistp256,rsa-sha2-512,rsa-sha2-256

# 对称加密算法
Ciphers aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr

# 消息认证码算法
MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha2-512

# 公钥签名算法
PubkeyAcceptedKeyTypes ssh-ed25519,ecdsa-sha2-nistp384,ecdsa-sha2-nistp256,rsa-sha2-512,rsa-sha2-256
```

### 主机密钥配置

```bash
# 主机密钥文件（按优先级）
HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_rsa_key

# 生成主机密钥命令
ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ""
ssh-keygen -t ecdsa -b 384 -f /etc/ssh/ssh_host_ecdsa_key -N ""
ssh-keygen -t rsa -b 4096 -f /etc/ssh/ssh_host_rsa_key -N ""
```

### 连接限制和防护

```bash
# 连接限制
MaxStartups 10:30:60      # 最大未认证连接
MaxSessions 10            # 最大会话数

# 失败延迟
LoginGraceTime 30         # 认证超时时间

# 网络保活
ClientAliveInterval 300   # 保活间隔（秒）
ClientAliveCountMax 2     # 最大保活次数

# 压缩设置
Compression delayed       # 认证后启用压缩
```

## 日志和监控配置

### 日志配置

```bash
# 日志设置
SyslogFacility AUTH
LogLevel INFO            # 或 VERBOSE 用于调试

# 详细日志级别说明：
# QUIET    - 静默模式
# FATAL    - 仅致命错误
# ERROR    - 错误信息
# INFO     - 一般信息（推荐）
# VERBOSE  - 详细信息（调试用）
# DEBUG    - 调试信息（最详细）
```

### 横幅和消息

```bash
# 登录横幅
Banner /etc/ssh/banner.txt

# 欢迎消息
PrintMotd yes
PrintLastLog yes

# 示例banner.txt内容
cat > /etc/ssh/banner.txt << 'EOF'
***************************************************************************
                    WARNING: AUTHORIZED ACCESS ONLY
                    
This system is for authorized users only. All activities are monitored
and recorded. Unauthorized access is strictly prohibited and will be
prosecuted to the full extent of the law.
***************************************************************************
EOF
```

## 环境特定配置

### 生产环境配置

```bash
# /etc/ssh/sshd_config - 生产环境
Protocol 2
Port 2222                                    # 非标准端口
PermitRootLogin no
PasswordAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
StrictModes yes

# 强化的算法配置
KexAlgorithms curve25519-sha256,ecdh-sha2-nistp384
HostKeyAlgorithms ssh-ed25519,ecdsa-sha2-nistp384
Ciphers aes256-gcm@openssh.com,aes256-ctr
MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com

# 连接限制
MaxAuthTries 2
LoginGraceTime 20
MaxStartups 5:50:10
MaxSessions 4

# 用户限制
AllowGroups ssh-users admin
DenyUsers guest anonymous

# 日志和监控
LogLevel VERBOSE
SyslogFacility AUTH

# 网络保活
ClientAliveInterval 300
ClientAliveCountMax 1
```

### 开发环境配置

```bash
# /etc/ssh/sshd_config - 开发环境
Protocol 2
Port 22
PermitRootLogin no
PasswordAuthentication yes                   # 开发便利性
PubkeyAuthentication yes

# 相对宽松的限制
MaxAuthTries 6
LoginGraceTime 60
MaxStartups 10:30:100

# 允许端口转发（开发需要）
AllowTcpForwarding yes
GatewayPorts clientspecified
X11Forwarding yes

# 标准日志级别
LogLevel INFO
```

## 高级功能配置

### 条件配置（Match块）

```bash
# 管理员用户特殊配置
Match Group admin
    AllowTcpForwarding yes
    GatewayPorts yes
    PermitTunnel yes

# 特定用户限制
Match User backup
    ForceCommand /usr/local/bin/backup-only
    AllowTcpForwarding no
    X11Forwarding no

# 内网用户宽松配置
Match Address 192.168.1.0/24
    PasswordAuthentication yes
    MaxAuthTries 6

# 外网用户严格配置
Match Address !192.168.1.0/24
    PasswordAuthentication no
    MaxAuthTries 2
    DenyUsers guest
```

### SFTP专用配置

```bash
# SFTP子系统
Subsystem sftp /usr/lib/openssh/sftp-server

# SFTP专用用户组
Match Group sftp-only
    ChrootDirectory /sftp/%u
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication no
```

### 端口转发配置

```bash
# 端口转发控制
AllowTcpForwarding yes               # 允许TCP转发
GatewayPorts no                      # 仅本地绑定
PermitTunnel no                      # 禁用隧道

# 限制特定用户的转发
Match User developer
    AllowTcpForwarding local         # 仅允许本地转发
    PermitOpen localhost:3000 localhost:5432
```

## 配置验证和测试

### 配置语法检查

```bash
#!/bin/bash
# SSH服务器配置验证脚本

# 检查配置语法
check_sshd_config() {
    echo "检查sshd配置语法..."
    
    if sshd -t -f /etc/ssh/sshd_config; then
        echo "✅ 配置语法正确"
        return 0
    else
        echo "❌ 配置语法错误"
        return 1
    fi
}

# 显示有效配置
show_effective_config() {
    echo "当前有效配置:"
    sshd -T | head -30
}

# 检查监听端口
check_listening_ports() {
    echo "SSH监听端口:"
    ss -tlnp | grep sshd
}

# 检查主机密钥
check_host_keys() {
    echo "检查主机密钥:"
    
    for key_file in /etc/ssh/ssh_host_*_key; do
        if [[ -f "$key_file" ]]; then
            echo "检查: $key_file"
            
            # 检查权限
            local perms=$(stat -c "%a" "$key_file")
            if [[ "$perms" == "600" ]]; then
                echo "  ✅ 权限正确 (600)"
            else
                echo "  ❌ 权限错误 ($perms)"
            fi
            
            # 检查密钥有效性
            if ssh-keygen -l -f "$key_file" >/dev/null 2>&1; then
                echo "  ✅ 密钥有效"
            else
                echo "  ❌ 密钥损坏"
            fi
        fi
    done
}

# 测试连接
test_ssh_connection() {
    local test_user="${1:-$(whoami)}"
    local test_host="${2:-localhost}"
    
    echo "测试SSH连接: $test_user@$test_host"
    
    if ssh -o BatchMode=yes -o ConnectTimeout=5 \
       "$test_user@$test_host" 'echo "连接测试成功"' 2>/dev/null; then
        echo "✅ 连接成功"
    else
        echo "❌ 连接失败"
    fi
}

# 主程序
main() {
    echo "SSH服务器配置验证"
    echo "=================="
    
    check_sshd_config
    echo ""
    
    check_host_keys
    echo ""
    
    check_listening_ports
    echo ""
    
    show_effective_config
}

main "$@"
```

### 安全审计脚本

```bash
#!/bin/bash
# SSH服务器安全审计脚本

audit_ssh_security() {
    echo "SSH安全配置审计"
    echo "==============="
    
    # 检查关键安全设置
    echo "1. 检查协议版本:"
    if sshd -T | grep -q "protocol 2"; then
        echo "✅ 使用SSH协议版本2"
    else
        echo "❌ 协议版本配置有问题"
    fi
    
    # 检查root登录
    echo "2. 检查root登录设置:"
    local root_login=$(sshd -T | grep permitrootlogin | awk '{print $2}')
    if [[ "$root_login" == "no" ]]; then
        echo "✅ 已禁用root登录"
    else
        echo "⚠️  root登录设置: $root_login"
    fi
    
    # 检查密码认证
    echo "3. 检查密码认证:"
    local pwd_auth=$(sshd -T | grep passwordauthentication | awk '{print $2}')
    if [[ "$pwd_auth" == "no" ]]; then
        echo "✅ 已禁用密码认证"
    else
        echo "⚠️  密码认证设置: $pwd_auth"
    fi
    
    # 检查弱算法
    echo "4. 检查加密算法:"
    if sshd -T | grep -E "(ciphers|macs|kexalgorithms)" | grep -q "sha1\|md5\|rc4"; then
        echo "❌ 发现弱加密算法"
        sshd -T | grep -E "(ciphers|macs|kexalgorithms)" | grep "sha1\|md5\|rc4"
    else
        echo "✅ 未发现明显的弱算法"
    fi
    
    # 检查连接限制
    echo "5. 检查连接限制:"
    local max_auth=$(sshd -T | grep maxauthtries | awk '{print $2}')
    if [[ "$max_auth" -le 3 ]]; then
        echo "✅ 认证尝试限制合理: $max_auth"
    else
        echo "⚠️  认证尝试次数较高: $max_auth"
    fi
}

audit_ssh_security
```

## 性能优化

### 连接性能优化

```bash
# 性能优化配置
UseDNS no                    # 禁用DNS反向解析
TCPKeepAlive yes            # 启用TCP保活
ClientAliveInterval 60       # 客户端保活间隔
Compression delayed          # 延迟压缩

# 并发连接优化
MaxStartups 50:30:100       # 增加并发连接限制
MaxSessions 20              # 增加会话限制

# 认证优化
GSSAPIAuthentication no     # 禁用GSSAPI（如不需要）
UsePAM no                   # 禁用PAM（如不需要）
```

### 日志轮转配置

```bash
# /etc/logrotate.d/sshd
/var/log/auth.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    postrotate
        /bin/kill -HUP `cat /var/run/rsyslogd.pid 2> /dev/null` 2> /dev/null || true
    endscript
}
```

## 下一步

完成服务器配置后，建议继续：

1. **[连接管理](./connection-management.md)** - 管理SSH连接
2. **[安全策略](../security/security-policies.md)** - 实施安全策略  
3. **[监控审计](../security/audit-logging.md)** - 设置监控和审计

---

🛡️ **安全提醒**: 
- 修改配置前务必备份原文件
- 测试配置更改不要影响现有连接
- 使用`systemctl reload sshd`重载配置
- 定期审计和更新安全设置