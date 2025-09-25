#!/bin/bash
# SSH密钥管理自动化脚本
# 版本: 1.0
# 作者: SSH密钥管理文档团队

set -euo pipefail

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_DIR="$HOME/.ssh"
BACKUP_DIR="$HOME/.ssh-backups"
LOG_FILE="/tmp/ssh-key-manager.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️  $*${NC}"
    log "INFO: $*"
}

success() {
    echo -e "${GREEN}✅ $*${NC}"
    log "SUCCESS: $*"
}

warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
    log "WARNING: $*"
}

error() {
    echo -e "${RED}❌ $*${NC}"
    log "ERROR: $*"
}

# 显示帮助信息
show_help() {
    cat << 'EOF'
SSH密钥管理自动化工具

用法: ./ssh-key-manager.sh [命令] [选项]

命令:
  generate     生成新的SSH密钥
  deploy       部署SSH密钥到服务器
  backup       备份SSH配置
  restore      恢复SSH配置
  check        检查SSH配置
  clean        清理无用的密钥
  rotate       轮换SSH密钥
  test         测试SSH连接
  setup        一键设置SSH环境

选项:
  -h, --help   显示此帮助信息
  -v, --verbose 启用详细输出
  -f, --force  强制执行（跳过确认）

示例:
  ./ssh-key-manager.sh generate --type ed25519 --name work
  ./ssh-key-manager.sh deploy --server web1.example.com --user deploy
  ./ssh-key-manager.sh backup
  ./ssh-key-manager.sh test --config-file servers.txt
  ./ssh-key-manager.sh setup --preset personal

更多信息请参考文档: docs/
EOF
}

# 检查必要的命令
check_dependencies() {
    local missing_deps=()
    
    for cmd in ssh ssh-keygen ssh-copy-id; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "缺少必要的命令: ${missing_deps[*]}"
        error "请安装 OpenSSH 客户端"
        exit 1
    fi
}

# 初始化SSH目录
init_ssh_dir() {
    if [[ ! -d "$SSH_DIR" ]]; then
        info "创建SSH目录: $SSH_DIR"
        mkdir -p "$SSH_DIR"
        chmod 700 "$SSH_DIR"
    fi
    
    # 检查权限
    local dir_perms=$(stat -c "%a" "$SSH_DIR")
    if [[ "$dir_perms" != "700" ]]; then
        warning "修复SSH目录权限: $dir_perms -> 700"
        chmod 700 "$SSH_DIR"
    fi
}

# 生成SSH密钥
generate_key() {
    local key_type="ed25519"
    local key_name=""
    local comment=""
    local passphrase=""
    local force=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)
                key_type="$2"
                shift 2
                ;;
            --name)
                key_name="$2"
                shift 2
                ;;
            --comment)
                comment="$2"
                shift 2
                ;;
            --passphrase)
                passphrase="$2"
                shift 2
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done
    
    # 验证密钥类型
    if [[ ! "$key_type" =~ ^(rsa|ecdsa|ed25519)$ ]]; then
        error "不支持的密钥类型: $key_type"
        return 1
    fi
    
    # 设置默认名称
    if [[ -z "$key_name" ]]; then
        key_name="id_${key_type}_$(date +%Y%m%d)"
    fi
    
    local key_file="$SSH_DIR/$key_name"
    
    # 检查密钥是否已存在
    if [[ -f "$key_file" ]] && [[ "$force" != true ]]; then
        error "密钥文件已存在: $key_file"
        error "使用 --force 强制覆盖"
        return 1
    fi
    
    # 设置默认注释
    if [[ -z "$comment" ]]; then
        comment="$key_name@$(hostname)-$(date +%Y%m%d)"
    fi
    
    info "生成SSH密钥:"
    info "  类型: $key_type"
    info "  文件: $key_file"
    info "  注释: $comment"
    
    # 生成密钥
    case "$key_type" in
        "ed25519")
            ssh-keygen -t ed25519 -f "$key_file" -N "$passphrase" -C "$comment"
            ;;
        "ecdsa")
            ssh-keygen -t ecdsa -b 384 -f "$key_file" -N "$passphrase" -C "$comment"
            ;;
        "rsa")
            ssh-keygen -t rsa -b 4096 -f "$key_file" -N "$passphrase" -C "$comment"
            ;;
    esac
    
    # 设置正确权限
    chmod 600 "$key_file"
    chmod 644 "$key_file.pub"
    
    success "SSH密钥生成完成: $key_file"
    
    # 显示密钥信息
    info "密钥指纹:"
    ssh-keygen -l -f "$key_file.pub"
}

# 部署SSH密钥
deploy_key() {
    local server=""
    local user=""
    local port="22"
    local key_file=""
    local force=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --server)
                server="$2"
                shift 2
                ;;
            --user)
                user="$2"
                shift 2
                ;;
            --port)
                port="$2"
                shift 2
                ;;
            --key)
                key_file="$2"
                shift 2
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done
    
    # 验证必要参数
    if [[ -z "$server" || -z "$user" ]]; then
        error "必须指定服务器和用户名"
        return 1
    fi
    
    # 查找密钥文件
    if [[ -z "$key_file" ]]; then
        # 自动选择最新的密钥
        key_file=$(ls -t "$SSH_DIR"/id_*.pub 2>/dev/null | head -1)
        if [[ -z "$key_file" ]]; then
            error "未找到SSH公钥文件"
            return 1
        fi
        info "自动选择密钥: $key_file"
    fi
    
    if [[ ! -f "$key_file" ]]; then
        error "密钥文件不存在: $key_file"
        return 1
    fi
    
    info "部署SSH密钥:"
    info "  服务器: $user@$server:$port"
    info "  密钥: $key_file"
    
    # 部署密钥
    if ssh-copy-id -i "$key_file" -p "$port" "$user@$server"; then
        success "密钥部署成功"
        
        # 测试连接
        info "测试SSH连接..."
        if ssh -p "$port" -o BatchMode=yes -o ConnectTimeout=10 "$user@$server" 'echo "连接测试成功"'; then
            success "SSH连接测试通过"
        else
            warning "SSH连接测试失败"
        fi
    else
        error "密钥部署失败"
        return 1
    fi
}

# 备份SSH配置
backup_ssh() {
    local backup_name="ssh-backup-$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    info "创建SSH配置备份: $backup_path"
    
    mkdir -p "$backup_path"
    
    # 备份SSH文件
    if [[ -d "$SSH_DIR" ]]; then
        cp -r "$SSH_DIR"/* "$backup_path/" 2>/dev/null || true
        
        # 创建备份清单
        {
            echo "SSH配置备份清单"
            echo "创建时间: $(date)"
            echo "=============================="
            echo ""
            echo "文件列表:"
            ls -la "$SSH_DIR"
            echo ""
            echo "密钥信息:"
            for pub_key in "$SSH_DIR"/*.pub; do
                [[ ! -f "$pub_key" ]] && continue
                echo "--- $(basename "$pub_key") ---"
                ssh-keygen -l -f "$pub_key"
                echo ""
            done
        } > "$backup_path/backup_info.txt"
        
        # 压缩备份
        tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "$backup_name"
        rm -rf "$backup_path"
        
        success "备份完成: $backup_path.tar.gz"
    else
        error "SSH目录不存在: $SSH_DIR"
        return 1
    fi
}

# 检查SSH配置
check_ssh() {
    info "检查SSH配置..."
    
    local issues=0
    
    # 检查SSH目录
    if [[ -d "$SSH_DIR" ]]; then
        local dir_perms=$(stat -c "%a" "$SSH_DIR")
        if [[ "$dir_perms" == "700" ]]; then
            success "SSH目录权限正确"
        else
            warning "SSH目录权限错误: $dir_perms (应该是700)"
            ((issues++))
        fi
    else
        error "SSH目录不存在: $SSH_DIR"
        ((issues++))
    fi
    
    # 检查密钥文件
    local key_count=0
    for key_file in "$SSH_DIR"/id_*; do
        [[ ! -f "$key_file" ]] && continue
        [[ "$key_file" == *.pub ]] && continue
        
        ((key_count++))
        local key_perms=$(stat -c "%a" "$key_file")
        
        if [[ "$key_perms" == "600" ]]; then
            success "私钥权限正确: $(basename "$key_file")"
        else
            warning "私钥权限错误: $(basename "$key_file") $key_perms (应该是600)"
            ((issues++))
        fi
        
        # 检查对应的公钥
        if [[ -f "$key_file.pub" ]]; then
            local pub_perms=$(stat -c "%a" "$key_file.pub")
            if [[ "$pub_perms" == "644" ]]; then
                success "公钥权限正确: $(basename "$key_file.pub")"
            else
                warning "公钥权限错误: $(basename "$key_file.pub") $pub_perms (应该是644)"
                ((issues++))
            fi
        else
            warning "缺少公钥文件: $key_file.pub"
            ((issues++))
        fi
    done
    
    # 检查配置文件
    if [[ -f "$SSH_DIR/config" ]]; then
        local config_perms=$(stat -c "%a" "$SSH_DIR/config")
        if [[ "$config_perms" == "600" ]]; then
            success "SSH配置文件权限正确"
        else
            warning "SSH配置文件权限错误: $config_perms (应该是600)"
            ((issues++))
        fi
    fi
    
    info "检查完成: 发现 $issues 个问题"
    
    if [[ $issues -eq 0 ]]; then
        success "SSH配置检查通过！"
    else
        warning "发现配置问题，建议修复"
    fi
    
    return $issues
}

# 修复SSH权限
fix_permissions() {
    info "修复SSH文件权限..."
    
    # 修复SSH目录权限
    chmod 700 "$SSH_DIR" 2>/dev/null || true
    
    # 修复私钥权限
    chmod 600 "$SSH_DIR"/id_* 2>/dev/null || true
    chmod 600 "$SSH_DIR"/config 2>/dev/null || true
    chmod 600 "$SSH_DIR"/authorized_keys 2>/dev/null || true
    
    # 修复公钥权限
    chmod 644 "$SSH_DIR"/*.pub 2>/dev/null || true
    
    success "权限修复完成"
}

# 一键设置SSH环境
setup_ssh() {
    local preset="personal"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --preset)
                preset="$2"
                shift 2
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done
    
    info "设置SSH环境 (预设: $preset)"
    
    # 初始化SSH目录
    init_ssh_dir
    
    case "$preset" in
        "personal")
            # 个人开发者设置
            info "配置个人开发者环境..."
            
            # 生成GitHub密钥
            if [[ ! -f "$SSH_DIR/id_ed25519_github" ]]; then
                ssh-keygen -t ed25519 -f "$SSH_DIR/id_ed25519_github" -N "" -C "github@$(whoami).local"
                success "GitHub密钥生成完成"
            fi
            
            # 生成个人服务器密钥
            if [[ ! -f "$SSH_DIR/id_ed25519_personal" ]]; then
                ssh-keygen -t ed25519 -f "$SSH_DIR/id_ed25519_personal" -N "" -C "personal@$(whoami).local"
                success "个人服务器密钥生成完成"
            fi
            
            # 创建SSH配置
            cat > "$SSH_DIR/config" << 'EOF'
# 个人SSH配置
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
EOF
            ;;
            
        "work")
            # 工作环境设置
            info "配置工作环境..."
            
            # 生成工作密钥
            if [[ ! -f "$SSH_DIR/id_ed25519_work" ]]; then
                ssh-keygen -t ed25519 -f "$SSH_DIR/id_ed25519_work" -N "" -C "work@$(whoami).local"
                success "工作密钥生成完成"
            fi
            
            # 创建工作配置
            cat > "$SSH_DIR/config" << 'EOF'
# 工作SSH配置
Host *
    ServerAliveInterval 30
    ServerAliveCountMax 3
    StrictHostKeyChecking yes
    IdentitiesOnly yes

# 开发环境
Host dev-*
    User developer
    IdentityFile ~/.ssh/id_ed25519_work

# 生产环境 (通过跳板机)
Host prod-*
    User deploy
    IdentityFile ~/.ssh/id_ed25519_work
    ProxyJump bastion.company.com
EOF
            ;;
            
        *)
            error "未知预设: $preset"
            return 1
            ;;
    esac
    
    # 修复权限
    fix_permissions
    
    success "SSH环境设置完成!"
    
    info "下一步:"
    info "1. 将公钥添加到相应的服务"
    info "2. 测试SSH连接"
    info "3. 根据需要调整配置文件"
}

# 主函数
main() {
    # 检查依赖
    check_dependencies
    
    # 解析命令
    case "${1:-help}" in
        "generate")
            shift
            generate_key "$@"
            ;;
        "deploy")
            shift
            deploy_key "$@"
            ;;
        "backup")
            backup_ssh
            ;;
        "check")
            check_ssh
            ;;
        "fix")
            fix_permissions
            ;;
        "setup")
            shift
            setup_ssh "$@"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"