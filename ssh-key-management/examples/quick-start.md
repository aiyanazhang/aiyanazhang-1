# SSH密钥管理快速开始指南

## 概述

本指南提供SSH密钥管理的快速入门方法，通过简单的步骤帮助您快速建立安全的SSH环境。适合新手用户和需要快速配置的场景。

## 5分钟快速配置

### 步骤1: 生成SSH密钥

```bash
# 为GitHub/GitLab等代码托管平台生成密钥
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -C "your-email@example.com"

# 为服务器管理生成密钥
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_servers -C "server-admin@example.com"
```

### 步骤2: 配置SSH客户端

创建或编辑 `~/.ssh/config` 文件：

```bash
# GitHub配置
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes

# 个人服务器配置
Host myserver
    HostName your-server.com
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519_servers
    
# 开发服务器配置
Host dev
    HostName dev.company.com
    User developer
    IdentityFile ~/.ssh/id_ed25519_servers
    LocalForward 3000 localhost:3000
```

### 步骤3: 部署公钥到服务器

```bash
# 部署到服务器（推荐方法）
ssh-copy-id -i ~/.ssh/id_ed25519_servers.pub admin@your-server.com

# 或者手动复制
cat ~/.ssh/id_ed25519_github.pub
# 然后在GitHub设置中添加SSH密钥
```

### 步骤4: 测试连接

```bash
# 测试GitHub连接
ssh -T git@github.com

# 测试服务器连接
ssh myserver

# 测试开发环境
ssh dev
```

## 常用场景配置

### 场景1: 个人开发者

```bash
#!/bin/bash
# 个人开发者SSH配置脚本

echo "=== 个人开发者SSH环境配置 ==="

# 1. 生成不同用途的密钥
echo "生成SSH密钥..."
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -C "github@$(whoami).local"
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_personal -C "personal@$(whoami).local"

# 2. 设置正确权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/*.pub

# 3. 创建SSH配置
cat > ~/.ssh/config << 'EOF'
# 全局默认配置
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/master-%r@%h:%p
    ControlPersist 10m

# GitHub配置
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes

# GitLab配置
Host gitlab.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes

# 个人VPS
Host vps
    HostName your-vps-ip
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519_personal
EOF

chmod 600 ~/.ssh/config

echo "✅ SSH环境配置完成！"
echo ""
echo "下一步："
echo "1. 将 ~/.ssh/id_ed25519_github.pub 添加到GitHub"
echo "2. 部署 ~/.ssh/id_ed25519_personal.pub 到你的服务器"
echo "3. 测试连接: ssh -T git@github.com"
```

### 场景2: 企业环境配置

```bash
#!/bin/bash
# 企业环境SSH配置脚本

COMPANY_DOMAIN="${1:-company.com}"
USER_EMAIL="${2:-$(whoami)@$COMPANY_DOMAIN}"

echo "=== 企业环境SSH配置 ==="
echo "公司域名: $COMPANY_DOMAIN"
echo "用户邮箱: $USER_EMAIL"

# 1. 生成企业级密钥
echo "生成企业级SSH密钥..."
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_work -C "$USER_EMAIL"
ssh-keygen -t ecdsa -b 384 -f ~/.ssh/id_ecdsa_prod -C "prod-$USER_EMAIL"

# 2. 创建企业SSH配置
cat > ~/.ssh/config << EOF
# 企业环境全局配置
Host *
    ServerAliveInterval 30
    ServerAliveCountMax 3
    StrictHostKeyChecking yes
    IdentitiesOnly yes

# 开发环境
Host dev-*
    User developer
    IdentityFile ~/.ssh/id_ed25519_work
    ProxyJump bastion.dev.$COMPANY_DOMAIN

# 生产环境
Host prod-*
    User deploy
    IdentityFile ~/.ssh/id_ecdsa_prod
    ProxyJump bastion.prod.$COMPANY_DOMAIN

# 跳板机配置
Host bastion.*
    User $(whoami)
    IdentityFile ~/.ssh/id_ed25519_work
    ControlMaster yes
    ControlPersist 8h
EOF

chmod 600 ~/.ssh/config

echo "✅ 企业SSH环境配置完成！"
echo ""
echo "请联系系统管理员："
echo "1. 将公钥添加到企业身份管理系统"
echo "2. 获取跳板机和目标服务器的访问权限"
```

### 场景3: 多账户管理

```bash
#!/bin/bash
# 多账户SSH管理脚本

# 账户配置
declare -A ACCOUNTS=(
    ["personal"]="personal@example.com"
    ["work"]="work@company.com"
    ["client1"]="contractor@client1.com"
    ["client2"]="contractor@client2.com"
)

echo "=== 多账户SSH管理配置 ==="

# 为每个账户生成密钥
for account in "${!ACCOUNTS[@]}"; do
    email="${ACCOUNTS[$account]}"
    key_file="~/.ssh/id_ed25519_$account"
    
    echo "为账户 $account 生成密钥..."
    ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519_$account" -C "$email"
done

# 创建多账户配置
cat > ~/.ssh/config << 'EOF'
# 个人GitHub账户
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes

# 工作GitHub账户
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes

# 客户端1环境
Host client1-*
    User contractor
    IdentityFile ~/.ssh/id_ed25519_client1
    
# 客户端2环境
Host client2-*
    User contractor
    IdentityFile ~/.ssh/id_ed25519_client2
EOF

echo "✅ 多账户配置完成！"
echo ""
echo "使用方法："
echo "git clone git@github-personal:username/repo.git  # 个人账户"
echo "git clone git@github-work:company/repo.git       # 工作账户"
echo "ssh client1-server                               # 客户端1服务器"
```

## 实用脚本集合

### SSH密钥备份脚本

```bash
#!/bin/bash
# SSH密钥备份脚本

BACKUP_DIR="$HOME/ssh-backup-$(date +%Y%m%d)"
SSH_DIR="$HOME/.ssh"

create_backup() {
    echo "创建SSH密钥备份到: $BACKUP_DIR"
    
    mkdir -p "$BACKUP_DIR"
    
    # 备份所有SSH文件（排除known_hosts，因为它可能很大）
    for file in "$SSH_DIR"/*; do
        filename=$(basename "$file")
        
        # 跳过某些文件
        case "$filename" in
            "known_hosts"|"known_hosts.old")
                continue
                ;;
            *)
                if [[ -f "$file" ]]; then
                    cp "$file" "$BACKUP_DIR/"
                    echo "备份: $filename"
                fi
                ;;
        esac
    done
    
    # 创建备份清单
    ls -la "$SSH_DIR" > "$BACKUP_DIR/file_list.txt"
    
    # 创建密钥信息
    echo "SSH密钥信息:" > "$BACKUP_DIR/key_info.txt"
    for key in "$SSH_DIR"/*.pub; do
        [[ ! -f "$key" ]] && continue
        echo "=== $(basename "$key") ===" >> "$BACKUP_DIR/key_info.txt"
        ssh-keygen -l -f "$key" >> "$BACKUP_DIR/key_info.txt"
        echo "" >> "$BACKUP_DIR/key_info.txt"
    done
    
    # 压缩备份
    tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
    rm -rf "$BACKUP_DIR"
    
    echo "✅ 备份完成: $BACKUP_DIR.tar.gz"
}

restore_backup() {
    local backup_file="$1"
    
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ 备份文件不存在: $backup_file"
        return 1
    fi
    
    echo "从备份恢复SSH配置: $backup_file"
    
    # 备份当前配置
    if [[ -d "$SSH_DIR" ]]; then
        mv "$SSH_DIR" "$SSH_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 解压备份
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # 恢复文件
    mkdir -p "$SSH_DIR"
    cp "$temp_dir"/*/* "$SSH_DIR/"
    
    # 设置正确权限
    chmod 700 "$SSH_DIR"
    chmod 600 "$SSH_DIR"/id_* "$SSH_DIR"/config "$SSH_DIR"/authorized_keys 2>/dev/null
    chmod 644 "$SSH_DIR"/*.pub 2>/dev/null
    
    rm -rf "$temp_dir"
    
    echo "✅ 恢复完成"
}

case "$1" in
    "backup"|"create")
        create_backup
        ;;
    "restore")
        restore_backup "$2"
        ;;
    *)
        echo "SSH密钥备份工具"
        echo "用法: $0 {backup|restore} [备份文件]"
        echo ""
        echo "示例:"
        echo "  $0 backup                           # 创建备份"
        echo "  $0 restore ssh-backup-20241225.tar.gz  # 恢复备份"
        ;;
esac
```

### SSH连接测试脚本

```bash
#!/bin/bash
# SSH连接批量测试脚本

# 配置文件格式: host:port:user:key_file
CONFIG_FILE="${1:-servers.txt}"

# 示例配置文件内容
create_example_config() {
    cat > servers.txt << 'EOF'
# 格式: host:port:user:key_file
web1.example.com:22:deploy:~/.ssh/id_ed25519_work
web2.example.com:22:deploy:~/.ssh/id_ed25519_work
db1.example.com:3306:dbadmin:~/.ssh/id_ed25519_db
monitoring.example.com:2222:monitor:~/.ssh/id_ed25519_monitor
EOF
    echo "创建示例配置文件: servers.txt"
}

# 测试单个连接
test_connection() {
    local host="$1"
    local port="$2"
    local user="$3"
    local key_file="$4"
    
    echo -n "测试 $user@$host:$port ... "
    
    # 展开波浪号
    key_file="${key_file/#\~/$HOME}"
    
    if [[ ! -f "$key_file" ]]; then
        echo "❌ 密钥文件不存在: $key_file"
        return 1
    fi
    
    # 测试连接
    if ssh -i "$key_file" -p "$port" -o BatchMode=yes -o ConnectTimeout=10 \
       "$user@$host" 'echo "OK"' >/dev/null 2>&1; then
        echo "✅ 成功"
        return 0
    else
        echo "❌ 失败"
        return 1
    fi
}

# 批量测试
batch_test() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "配置文件不存在: $CONFIG_FILE"
        echo "创建示例配置..."
        create_example_config
        return 1
    fi
    
    echo "=== SSH连接批量测试 ==="
    echo "配置文件: $CONFIG_FILE"
    echo ""
    
    local total=0
    local success=0
    local failed=0
    
    while IFS=':' read -r host port user key_file; do
        # 跳过注释和空行
        [[ -z "$host" || "$host" =~ ^# ]] && continue
        
        ((total++))
        
        if test_connection "$host" "$port" "$user" "$key_file"; then
            ((success++))
        else
            ((failed++))
        fi
        
    done < "$CONFIG_FILE"
    
    echo ""
    echo "=== 测试结果 ==="
    echo "总计: $total"
    echo "成功: $success"
    echo "失败: $failed"
    
    if [[ $failed -eq 0 ]]; then
        echo "🎉 所有连接测试通过！"
    else
        echo "⚠️  有 $failed 个连接失败，请检查配置"
    fi
}

# 主程序
if [[ $# -eq 0 ]]; then
    echo "SSH连接批量测试工具"
    echo "用法: $0 [配置文件]"
    echo ""
    echo "配置文件格式 (每行):"
    echo "host:port:user:key_file"
    echo ""
    echo "示例:"
    echo "  $0                # 使用默认配置文件 servers.txt"
    echo "  $0 prod.txt      # 使用指定配置文件"
    echo ""
    
    if [[ ! -f "servers.txt" ]]; then
        echo "创建示例配置文件..."
        create_example_config
    fi
else
    batch_test
fi
```

### SSH密钥信息查看脚本

```bash
#!/bin/bash
# SSH密钥信息查看工具

show_key_info() {
    local key_file="$1"
    
    if [[ ! -f "$key_file" ]]; then
        echo "❌ 密钥文件不存在: $key_file"
        return 1
    fi
    
    echo "=== 密钥信息: $(basename "$key_file") ==="
    
    # 基本信息
    local key_info=$(ssh-keygen -l -f "$key_file" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        echo "指纹: $key_info"
    else
        echo "❌ 无法读取密钥信息"
        return 1
    fi
    
    # 详细信息
    local key_type=$(echo "$key_info" | awk '{print $4}' | tr -d '()')
    local key_length=$(echo "$key_info" | awk '{print $1}')
    local fingerprint=$(echo "$key_info" | awk '{print $2}')
    
    echo "类型: $key_type"
    echo "长度: $key_length 位"
    echo "SHA256: $fingerprint"
    
    # 文件信息
    local file_perms=$(stat -c "%a" "$key_file")
    local file_size=$(stat -c "%s" "$key_file")
    local file_mtime=$(stat -c "%y" "$key_file")
    
    echo "权限: $file_perms"
    echo "大小: $file_size 字节"
    echo "修改时间: $file_mtime"
    
    # 安全检查
    echo ""
    echo "安全检查:"
    
    # 权限检查
    if [[ "$key_file" == *.pub ]]; then
        if [[ "$file_perms" == "644" || "$file_perms" == "600" ]]; then
            echo "✅ 公钥权限正确"
        else
            echo "⚠️  公钥权限异常 ($file_perms)"
        fi
    else
        if [[ "$file_perms" == "600" ]]; then
            echo "✅ 私钥权限正确"
        else
            echo "❌ 私钥权限不安全 ($file_perms)，应该是600"
        fi
    fi
    
    # 密钥强度检查
    case "$key_type" in
        "RSA")
            if [[ $key_length -ge 2048 ]]; then
                echo "✅ RSA密钥长度安全"
            else
                echo "❌ RSA密钥长度不足 ($key_length < 2048)"
            fi
            ;;
        "DSA")
            echo "⚠️  DSA算法已过时，建议升级"
            ;;
        "ECDSA"|"ED25519")
            echo "✅ 现代密钥算法"
            ;;
    esac
    
    echo ""
}

# 显示所有SSH密钥信息
show_all_keys() {
    echo "=== SSH密钥库概览 ==="
    echo ""
    
    local ssh_dir="$HOME/.ssh"
    local key_count=0
    
    # 私钥
    echo "私钥文件:"
    for key_file in "$ssh_dir"/id_*; do
        [[ ! -f "$key_file" ]] && continue
        [[ "$key_file" == *.pub ]] && continue
        
        ((key_count++))
        show_key_info "$key_file"
    done
    
    # 公钥
    echo "公钥文件:"
    for pub_file in "$ssh_dir"/*.pub; do
        [[ ! -f "$pub_file" ]] && continue
        
        show_key_info "$pub_file"
    done
    
    if [[ $key_count -eq 0 ]]; then
        echo "未找到SSH密钥文件"
        echo ""
        echo "生成密钥:"
        echo "  ssh-keygen -t ed25519 -C 'your-email@example.com'"
    fi
}

# 主程序
if [[ $# -eq 0 ]]; then
    show_all_keys
else
    for key_file in "$@"; do
        show_key_info "$key_file"
    done
fi
```

## 快速参考

### 常用命令速查

```bash
# 密钥生成
ssh-keygen -t ed25519 -C "email@example.com"                    # 生成Ed25519密钥
ssh-keygen -t rsa -b 4096 -C "email@example.com"               # 生成RSA密钥
ssh-keygen -t ecdsa -b 384 -C "email@example.com"              # 生成ECDSA密钥

# 密钥部署
ssh-copy-id user@server                                         # 部署默认密钥
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server              # 部署指定密钥

# 连接测试
ssh -T git@github.com                                           # 测试GitHub连接
ssh -vvv user@server                                           # 详细调试连接
ssh -o BatchMode=yes user@server 'echo test'                   # 非交互式测试

# 密钥信息
ssh-keygen -l -f ~/.ssh/id_ed25519.pub                         # 查看密钥指纹
ssh-keygen -y -f ~/.ssh/id_ed25519                             # 从私钥生成公钥
ssh-add -l                                                      # 查看SSH agent中的密钥

# 权限修复
chmod 700 ~/.ssh                                               # 修复SSH目录权限
chmod 600 ~/.ssh/id_* ~/.ssh/config                           # 修复私钥权限
chmod 644 ~/.ssh/*.pub                                         # 修复公钥权限
```

### 配置模板

```bash
# ~/.ssh/config 基础模板
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/master-%r@%h:%p
    ControlPersist 10m

Host shortname
    HostName real-server.com
    User username
    Port 22
    IdentityFile ~/.ssh/id_ed25519_specific
```

## 下一步

完成快速配置后，建议深入学习：

1. **[SSH配置详解](../configuration/client-config.md)** - 详细的配置选项
2. **[安全最佳实践](../security/security-policies.md)** - 提高安全性
3. **[高级功能](../advanced/proxy-forwarding.md)** - 探索SSH高级特性

---

🚀 **快速开始提醒**: 
- 优先使用Ed25519密钥类型
- 为不同用途生成不同的密钥
- 定期备份SSH配置和密钥
- 保持密钥的安全和更新