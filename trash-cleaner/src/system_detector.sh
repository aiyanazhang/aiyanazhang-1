#!/bin/bash
#!/bin/bash
#
# 系统检测器模块
#
# 功能描述:
#   负责检测当前运行环境的操作系统类型，识别并定位各个平台的
#   回收站目录位置，验证访问权限，并提供系统信息查询功能。
#
# 主要功能:
#   - 跨平台操作系统检测 (Linux, macOS, Windows)
#   - 回收站路径发现和验证
#   - 系统资源和权限检查
#   - 磁盘空间统计和分析
#   - 系统依赖命令检查
#
# 支持的操作系统:
#   - Linux: 支持XDG标准和传统回收站
#   - macOS: 支持用户和外置设备回收站
#   - Windows: 支持WSL/Cygwin环境下的回收站
#
# 作者: AI Assistant
# 版本: 1.0.0
# 创建时间: 2024
#

# ==================== 操作系统检测 ====================

# 检测当前运行的操作系统类型
# 通过分析OSTYPE环境变量来识别不同的操作系统
detect_os() {
    local os_type=""
    
    # 检查不同的操作系统标识符
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"        # macOS / Mac OS X
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
        os_type="linux"        # Linux 各种发行版
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        os_type="windows"      # Windows (WSL/Cygwin)
    else
        os_type="unknown"      # 不支持的系统
    fi
    
    echo "$os_type"
}

# ==================== 回收站路径检测 ====================

# 根据操作系统类型获取所有可能的回收站路径
# 支持多个挂载点和外置设备的回收站检测
get_trash_paths() {
    local os_type="$1"
    local paths=()
    
    case "$os_type" in
        "macos")
            # macOS 用户主回收站
            if [[ -d "$HOME/.Trash" ]]; then
                paths+=("$HOME/.Trash")
            fi
            
            # 外置设备回收站（每个用户有独立的回收站）
            for volume in /Volumes/*/; do
                if [[ -d "${volume}.Trashes/$UID" ]]; then
                    paths+=("${volume}.Trashes/$UID")
                fi
            done
            ;;
            
        "linux")
            # XDG 标准回收站（现代Linux系统的标准位置）
            if [[ -d "$HOME/.local/share/Trash/files" ]]; then
                paths+=("$HOME/.local/share/Trash/files")
            fi
            
            # 传统回收站路径（老版本的Linux系统）
            if [[ -d "$HOME/.trash" ]]; then
                paths+=("$HOME/.trash")
            fi
            
            # 检查其他挂载点的回收站（为每个用户分别创建）
            for mount_point in $(df --output=target | tail -n +2); do
                if [[ -d "$mount_point/.Trash-$UID" ]]; then
                    paths+=("$mount_point/.Trash-$UID")
                fi
            done
            ;;
            
        "windows")
            # Windows 回收站（在WSL/Cygwin环境下访问）
            if [[ -d "/c/\$Recycle.Bin" ]]; then
                paths+=("/c/\$Recycle.Bin")
            fi
            
            # 老版本Windows系统的回收站
            if [[ -d "/c/RECYCLER" ]]; then
                paths+=("/c/RECYCLER")
            fi
            ;;
    esac
    
    # 输出所有找到的路径（每行一个）
    printf '%s\n' "${paths[@]}"
}

# ==================== 访问权限验证 ====================

# 检查回收站目录是否存在且可访问
# 验证读取和写入权限，确保能够正常执行清理操作
verify_trash_access() {
    local trash_path="$1"
    
    # 检查目录是否存在
    if [[ ! -d "$trash_path" ]]; then
        return 1  # 目录不存在
    fi
    
    # 检查读取权限（用于扫描回收站内容）
    if [[ ! -r "$trash_path" ]]; then
        return 2  # 没有读取权限
    fi
    
    # 检查写入权限（用于删除文件）
    if [[ ! -w "$trash_path" ]]; then
        return 3  # 没有写入权限
    fi
    
    return 0  # 所有权限检查通过
}

# ==================== 系统信息收集 ====================

# 获取系统环境的详细信息
# 返回JSON格式的系统信息，包括操作系统、内核版本、Shell版本等
get_system_info() {
    local os_type
    local kernel_version
    local shell_version
    
    # 收集各项系统信息
    os_type=$(detect_os)
    kernel_version=$(uname -r 2>/dev/null || echo "unknown")
    shell_version=$($SHELL --version 2>/dev/null | head -n1 || echo "unknown")
    
    # 输出JSON格式的系统信息
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

# ==================== 依赖检查 ====================

# 检查系统中是否安装了必要的命令工具
# 确保回收站清理操作所需的所有工具都可用
check_required_commands() {
    # 定义必要的系统命令列表
    local required_cmds=("find" "rm" "du" "wc" "stat" "date")
    local missing_cmds=()
    
    # 检查每个必要命令是否可用
    for cmd in "${required_cmds[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_cmds+=("$cmd")
        fi
    done
    
    # 如果有缺失的命令，报告错误
    if [[ ${#missing_cmds[@]} -gt 0 ]]; then
        printf "ERROR: 缺少必要的系统命令: %s\n" "${missing_cmds[*]}" >&2
        return 1
    fi
    
    return 0  # 所有必要命令都可用
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