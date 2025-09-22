#!/bin/bash

# 安全检查器模块
# 功能：路径验证、权限检查、安全边界控制

# 导入系统检测器
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"

# 定义安全路径白名单（硬编码安全控制）
declare -a SAFE_PATH_PATTERNS=(
    "*/\.Trash"
    "*/\.Trash/*"
    "*/.local/share/Trash/files"
    "*/.local/share/Trash/files/*"
    "*/\.trash"
    "*/\.trash/*"
    "*/.Trash-*"
    "*/.Trash-*/*"
    "*.Trashes/*"
    "*.Trashes/*/*"
    "*\$Recycle.Bin*"
    "*RECYCLER*"
)

# 危险路径黑名单
declare -a DANGEROUS_PATHS=(
    "/"
    "/bin"
    "/sbin"
    "/usr"
    "/etc"
    "/var"
    "/sys"
    "/proc"
    "/boot"
    "/lib"
    "/lib64"
    "/opt"
    "/root"
    "$HOME"
    "$HOME/Desktop"
    "$HOME/Documents"
    "$HOME/Downloads"
    "$HOME/Pictures"
    "$HOME/Music"
    "$HOME/Videos"
)

# 检查路径是否在安全白名单中
is_path_in_whitelist() {
    local target_path="$1"
    local normalized_path
    
    # 规范化路径（解析符号链接和相对路径）
    if ! normalized_path=$(realpath "$target_path" 2>/dev/null); then
        normalized_path="$target_path"
    fi
    
    # 检查是否匹配白名单模式
    for pattern in "${SAFE_PATH_PATTERNS[@]}"; do
        if [[ "$normalized_path" == $pattern ]]; then
            return 0  # 在白名单中
        fi
    done
    
    return 1  # 不在白名单中
}

# 检查路径是否在危险黑名单中
is_path_dangerous() {
    local target_path="$1"
    local normalized_path
    
    # 规范化路径
    if ! normalized_path=$(realpath "$target_path" 2>/dev/null); then
        normalized_path="$target_path"
    fi
    
    # 检查是否为危险路径
    for dangerous_path in "${DANGEROUS_PATHS[@]}"; do
        # 检查是否为危险路径或其子路径
        if [[ "$normalized_path" == "$dangerous_path"* ]]; then
            return 0  # 是危险路径
        fi
    done
    
    return 1  # 不是危险路径
}

# 检查符号链接安全性
check_symlink_safety() {
    local target_path="$1"
    local link_count=0
    local current_path="$target_path"
    local max_links=10  # 防止无限循环
    
    while [[ -L "$current_path" ]] && [[ $link_count -lt $max_links ]]; do
        local link_target
        link_target=$(readlink "$current_path")
        
        if [[ -z "$link_target" ]]; then
            echo "ERROR: 无法读取符号链接: $current_path" >&2
            return 1
        fi
        
        # 如果是相对路径，转换为绝对路径
        if [[ "${link_target:0:1}" != "/" ]]; then
            link_target="$(dirname "$current_path")/$link_target"
        fi
        
        # 检查链接目标是否安全
        if is_path_dangerous "$link_target"; then
            echo "ERROR: 符号链接指向危险路径: $current_path -> $link_target" >&2
            return 1
        fi
        
        current_path="$link_target"
        ((link_count++))
    done
    
    if [[ $link_count -ge $max_links ]]; then
        echo "ERROR: 检测到符号链接循环: $target_path" >&2
        return 1
    fi
    
    # 检查最终路径是否安全
    if is_path_dangerous "$current_path"; then
        echo "ERROR: 符号链接最终指向危险路径: $target_path -> $current_path" >&2
        return 1
    fi
    
    return 0
}

# 验证路径深度（防止过深的路径操作）
check_path_depth() {
    local target_path="$1"
    local max_depth="${2:-20}"  # 默认最大深度20
    
    local depth
    depth=$(echo "$target_path" | tr -cd '/' | wc -c)
    
    if [[ $depth -gt $max_depth ]]; then
        echo "ERROR: 路径深度超过限制($max_depth): $target_path" >&2
        return 1
    fi
    
    return 0
}

# 检查文件/目录权限
check_permissions() {
    local target_path="$1"
    local required_perm="${2:-rw}"  # 默认需要读写权限
    
    if [[ ! -e "$target_path" ]]; then
        echo "ERROR: 路径不存在: $target_path" >&2
        return 1
    fi
    
    # 检查读权限
    if [[ "$required_perm" == *"r"* ]] && [[ ! -r "$target_path" ]]; then
        echo "ERROR: 缺少读取权限: $target_path" >&2
        return 2
    fi
    
    # 检查写权限
    if [[ "$required_perm" == *"w"* ]] && [[ ! -w "$target_path" ]]; then
        echo "ERROR: 缺少写入权限: $target_path" >&2
        return 3
    fi
    
    # 检查执行权限
    if [[ "$required_perm" == *"x"* ]] && [[ ! -x "$target_path" ]]; then
        echo "ERROR: 缺少执行权限: $target_path" >&2
        return 4
    fi
    
    return 0
}

# 验证路径是否为有效的回收站路径
validate_trash_path() {
    local target_path="$1"
    local os_type="${2:-$(detect_os)}"
    
    # 基本存在性检查
    if [[ ! -d "$target_path" ]]; then
        echo "ERROR: 回收站目录不存在: $target_path" >&2
        return 1
    fi
    
    # 符号链接安全检查
    if ! check_symlink_safety "$target_path"; then
        return 2
    fi
    
    # 路径深度检查
    if ! check_path_depth "$target_path"; then
        return 3
    fi
    
    # 危险路径检查
    if is_path_dangerous "$target_path"; then
        echo "ERROR: 路径在危险区域内: $target_path" >&2
        return 4
    fi
    
    # 白名单检查
    if ! is_path_in_whitelist "$target_path"; then
        echo "ERROR: 路径不在安全白名单中: $target_path" >&2
        return 5
    fi
    
    # 权限检查
    if ! check_permissions "$target_path" "rw"; then
        return 6
    fi
    
    # 系统特定验证
    case "$os_type" in
        "macos")
            if [[ ! "$target_path" =~ (\.Trash|\.Trashes) ]]; then
                echo "ERROR: 非标准macOS回收站路径: $target_path" >&2
                return 7
            fi
            ;;
            
        "linux")
            if [[ ! "$target_path" =~ (Trash|\.trash) ]]; then
                echo "ERROR: 非标准Linux回收站路径: $target_path" >&2
                return 7
            fi
            ;;
            
        "windows")
            if [[ ! "$target_path" =~ (Recycle\.Bin|RECYCLER) ]]; then
                echo "ERROR: 非标准Windows回收站路径: $target_path" >&2
                return 7
            fi
            ;;
    esac
    
    return 0
}

# 安全地获取绝对路径
get_safe_absolute_path() {
    local input_path="$1"
    local absolute_path
    
    # 尝试获取绝对路径
    if absolute_path=$(realpath "$input_path" 2>/dev/null); then
        echo "$absolute_path"
        return 0
    elif absolute_path=$(readlink -f "$input_path" 2>/dev/null); then
        echo "$absolute_path"
        return 0
    else
        # 手动构建绝对路径
        if [[ "${input_path:0:1}" == "/" ]]; then
            echo "$input_path"
        else
            echo "$PWD/$input_path"
        fi
        return 0
    fi
}

# 检查用户权限级别
check_user_privileges() {
    local required_level="${1:-user}"  # user, admin, root
    
    case "$required_level" in
        "user")
            return 0  # 普通用户权限，总是满足
            ;;
            
        "admin")
            # 检查是否在管理员组中
            if groups | grep -qE "(sudo|wheel|admin)"; then
                return 0
            else
                echo "ERROR: 需要管理员权限" >&2
                return 1
            fi
            ;;
            
        "root")
            if [[ $EUID -eq 0 ]]; then
                return 0
            else
                echo "ERROR: 需要root权限" >&2
                return 1
            fi
            ;;
            
        *)
            echo "ERROR: 未知的权限级别: $required_level" >&2
            return 1
            ;;
    esac
}

# 创建安全沙箱环境
create_security_sandbox() {
    local sandbox_dir="${1:-/tmp/trash-cleaner-$$}"
    
    # 创建临时工作目录
    if ! mkdir -p "$sandbox_dir"; then
        echo "ERROR: 无法创建沙箱目录: $sandbox_dir" >&2
        return 1
    fi
    
    # 设置严格权限
    chmod 700 "$sandbox_dir"
    
    # 导出沙箱路径
    export TRASH_CLEANER_SANDBOX="$sandbox_dir"
    
    echo "创建安全沙箱: $sandbox_dir"
    return 0
}

# 清理安全沙箱
cleanup_security_sandbox() {
    local sandbox_dir="${TRASH_CLEANER_SANDBOX:-}"
    
    if [[ -n "$sandbox_dir" ]] && [[ -d "$sandbox_dir" ]]; then
        rm -rf "$sandbox_dir" 2>/dev/null
        unset TRASH_CLEANER_SANDBOX
        echo "清理安全沙箱: $sandbox_dir"
    fi
}

# 综合安全验证函数
perform_comprehensive_security_check() {
    local target_path="$1"
    local operation="${2:-read}"  # read, write, delete
    local privilege_level="${3:-user}"
    
    echo "执行安全检查: $target_path"
    
    # 1. 用户权限检查
    if ! check_user_privileges "$privilege_level"; then
        return 1
    fi
    
    # 2. 获取安全的绝对路径
    local safe_path
    safe_path=$(get_safe_absolute_path "$target_path")
    
    # 3. 验证为有效回收站路径
    if ! validate_trash_path "$safe_path"; then
        return 2
    fi
    
    # 4. 操作特定检查
    case "$operation" in
        "read")
            if ! check_permissions "$safe_path" "r"; then
                return 3
            fi
            ;;
            
        "write")
            if ! check_permissions "$safe_path" "rw"; then
                return 3
            fi
            ;;
            
        "delete")
            if ! check_permissions "$safe_path" "rw"; then
                return 3
            fi
            
            # 删除操作需要额外检查父目录权限
            local parent_dir
            parent_dir=$(dirname "$safe_path")
            if ! check_permissions "$parent_dir" "rw"; then
                echo "ERROR: 父目录权限不足: $parent_dir" >&2
                return 4
            fi
            ;;
    esac
    
    echo "✓ 安全检查通过: $safe_path"
    return 0
}

# 主函数：安全检查
main_security_check() {
    local target_path="$1"
    local operation="${2:-read}"
    local privilege_level="${3:-user}"
    
    if [[ -z "$target_path" ]]; then
        echo "用法: $0 <路径> [操作类型] [权限级别]" >&2
        echo "操作类型: read, write, delete" >&2
        echo "权限级别: user, admin, root" >&2
        return 1
    fi
    
    perform_comprehensive_security_check "$target_path" "$operation" "$privilege_level"
}

# 设置陷阱清理函数
trap cleanup_security_sandbox EXIT

# 如果直接运行此脚本，执行主安全检查函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_security_check "$@"
fi