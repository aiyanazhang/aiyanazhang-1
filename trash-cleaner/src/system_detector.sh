#!/bin/bash

# 系统检测器模块
# 功能：识别操作系统类型和回收站路径

# 检测操作系统类型
detect_os() {
    local os_type=""
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
        os_type="linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        os_type="windows"
    else
        os_type="unknown"
    fi
    
    echo "$os_type"
}

# 获取回收站路径列表
get_trash_paths() {
    local os_type="$1"
    local paths=()
    
    case "$os_type" in
        "macos")
            # macOS 用户回收站
            if [[ -d "$HOME/.Trash" ]]; then
                paths+=("$HOME/.Trash")
            fi
            
            # 外置设备回收站
            for volume in /Volumes/*/; do
                if [[ -d "${volume}.Trashes/$UID" ]]; then
                    paths+=("${volume}.Trashes/$UID")
                fi
            done
            ;;
            
        "linux")
            # XDG 标准回收站
            if [[ -d "$HOME/.local/share/Trash/files" ]]; then
                paths+=("$HOME/.local/share/Trash/files")
            fi
            
            # 传统回收站路径
            if [[ -d "$HOME/.trash" ]]; then
                paths+=("$HOME/.trash")
            fi
            
            # 检查其他可能的回收站位置
            for mount_point in $(df --output=target | tail -n +2); do
                if [[ -d "$mount_point/.Trash-$UID" ]]; then
                    paths+=("$mount_point/.Trash-$UID")
                fi
            done
            ;;
            
        "windows")
            # Windows 回收站
            if [[ -d "/c/\$Recycle.Bin" ]]; then
                paths+=("/c/\$Recycle.Bin")
            fi
            
            if [[ -d "/c/RECYCLER" ]]; then
                paths+=("/c/RECYCLER")
            fi
            ;;
    esac
    
    printf '%s\n' "${paths[@]}"
}

# 检查回收站是否存在且可访问
verify_trash_access() {
    local trash_path="$1"
    
    if [[ ! -d "$trash_path" ]]; then
        return 1  # 目录不存在
    fi
    
    if [[ ! -r "$trash_path" ]]; then
        return 2  # 没有读取权限
    fi
    
    if [[ ! -w "$trash_path" ]]; then
        return 3  # 没有写入权限
    fi
    
    return 0  # 访问正常
}

# 获取系统信息摘要
get_system_info() {
    local os_type
    local kernel_version
    local shell_version
    
    os_type=$(detect_os)
    kernel_version=$(uname -r 2>/dev/null || echo "unknown")
    shell_version=$($SHELL --version 2>/dev/null | head -n1 || echo "unknown")
    
    cat <<EOF
{
    "os_type": "$os_type",
    "kernel_version": "$kernel_version",
    "shell_version": "$shell_version",
    "user_id": "$UID",
    "home_dir": "$HOME",
    "current_dir": "$PWD"
}
EOF
}

# 检查必要的系统命令
check_required_commands() {
    local required_cmds=("find" "rm" "du" "wc" "stat" "date")
    local missing_cmds=()
    
    for cmd in "${required_cmds[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_cmds+=("$cmd")
        fi
    done
    
    if [[ ${#missing_cmds[@]} -gt 0 ]]; then
        printf "ERROR: 缺少必要的系统命令: %s\n" "${missing_cmds[*]}" >&2
        return 1
    fi
    
    return 0
}

# 获取磁盘空间信息
get_disk_space() {
    local path="$1"
    
    if [[ ! -d "$path" ]]; then
        echo "路径不存在: $path" >&2
        return 1
    fi
    
    # 使用 df 获取磁盘空间信息
    local disk_info
    disk_info=$(df -h "$path" 2>/dev/null | tail -n1)
    
    if [[ -n "$disk_info" ]]; then
        local filesystem=$(echo "$disk_info" | awk '{print $1}')
        local size=$(echo "$disk_info" | awk '{print $2}')
        local used=$(echo "$disk_info" | awk '{print $3}')
        local available=$(echo "$disk_info" | awk '{print $4}')
        local use_percent=$(echo "$disk_info" | awk '{print $5}')
        
        cat <<EOF
{
    "filesystem": "$filesystem",
    "total_size": "$size",
    "used_space": "$used",
    "available_space": "$available",
    "usage_percent": "$use_percent"
}
EOF
    else
        echo "无法获取磁盘空间信息" >&2
        return 1
    fi
}

# 主函数：系统检测
main_detect_system() {
    local os_type
    local trash_paths
    local accessible_paths=()
    
    # 检查必要命令
    if ! check_required_commands; then
        return 1
    fi
    
    # 检测操作系统
    os_type=$(detect_os)
    if [[ "$os_type" == "unknown" ]]; then
        echo "ERROR: 不支持的操作系统类型" >&2
        return 1
    fi
    
    echo "检测到操作系统: $os_type"
    
    # 获取回收站路径
    mapfile -t trash_paths < <(get_trash_paths "$os_type")
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        echo "WARNING: 未找到回收站目录" >&2
        return 1
    fi
    
    echo "找到 ${#trash_paths[@]} 个回收站路径:"
    
    # 验证每个回收站路径的访问权限
    for path in "${trash_paths[@]}"; do
        if verify_trash_access "$path"; then
            accessible_paths+=("$path")
            echo "  ✓ $path (可访问)"
        else
            local error_code=$?
            case $error_code in
                1) echo "  ✗ $path (目录不存在)" ;;
                2) echo "  ✗ $path (无读取权限)" ;;
                3) echo "  ✗ $path (无写入权限)" ;;
            esac
        fi
    done
    
    if [[ ${#accessible_paths[@]} -eq 0 ]]; then
        echo "ERROR: 没有可访问的回收站目录" >&2
        return 1
    fi
    
    # 输出可访问的回收站路径
    printf '%s\n' "${accessible_paths[@]}"
    return 0
}

# 如果直接运行此脚本，执行主检测函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_detect_system "$@"
fi