#!/bin/bash

# 回收站扫描器模块
# 功能：扫描回收站内容、文件统计、筛选过滤

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security_checker.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"

# 扫描结果存储
declare -a SCAN_RESULTS_FILES=()
declare -a SCAN_RESULTS_DIRS=()
declare -A SCAN_STATS=(
    ["total_files"]=0
    ["total_dirs"]=0
    ["total_size"]=0
    ["oldest_file"]=""
    ["newest_file"]=""
    ["largest_file"]=""
    ["largest_file_size"]=0
)

# 扫描单个文件或目录
scan_item() {
    local item_path="$1"
    local item_type="$2"  # file 或 dir
    local stats_ref="${3:-}"  # 统计信息数组引用
    
    if [[ ! -e "$item_path" ]]; then
        return 1
    fi
    
    # 获取文件信息
    local size=0
    local mtime=""
    local file_info
    
    if file_info=$(stat -c "%s %Y" "$item_path" 2>/dev/null); then
        size=$(echo "$file_info" | cut -d' ' -f1)
        mtime=$(echo "$file_info" | cut -d' ' -f2)
    elif file_info=$(stat -f "%z %m" "$item_path" 2>/dev/null); then
        # macOS 格式
        size=$(echo "$file_info" | cut -d' ' -f1)
        mtime=$(echo "$file_info" | cut -d' ' -f2)
    else
        # 回退方案
        if [[ -f "$item_path" ]]; then
            size=$(wc -c < "$item_path" 2>/dev/null || echo "0")
        fi
        mtime=$(date +%s)
    fi
    
    # 创建项目信息
    local item_info="$item_path|$item_type|$size|$mtime"
    
    # 根据类型添加到相应数组
    if [[ "$item_type" == "file" ]]; then
        SCAN_RESULTS_FILES+=("$item_info")
    else
        SCAN_RESULTS_DIRS+=("$item_info")
    fi
    
    return 0
}

# 递归扫描目录
scan_directory_recursive() {
    local dir_path="$1"
    local max_depth="${2:-0}"  # 0表示无限制
    local current_depth="${3:-0}"
    
    # 检查深度限制
    if [[ $max_depth -gt 0 ]] && [[ $current_depth -ge $max_depth ]]; then
        return 0
    fi
    
    # 检查目录是否存在且可访问
    if [[ ! -d "$dir_path" ]] || [[ ! -r "$dir_path" ]]; then
        echo "WARNING: 无法访问目录: $dir_path" >&2
        return 1
    fi
    
    # 扫描当前目录的内容
    local item_count=0
    
    # 使用 find 命令进行高效扫描
    while IFS= read -r -d '' item; do
        # 跳过当前目录本身
        [[ "$item" == "$dir_path" ]] && continue
        
        if [[ -f "$item" ]]; then
            scan_item "$item" "file"
        elif [[ -d "$item" ]]; then
            scan_item "$item" "dir"
        fi
        
        ((item_count++))
        
        # 每处理1000个项目显示进度
        if [[ $((item_count % 1000)) -eq 0 ]]; then
            echo "已扫描 $item_count 个项目..." >&2
        fi
        
    done < <(find "$dir_path" -mindepth 1 $([ $max_depth -gt 0 ] && echo "-maxdepth $max_depth") -print0 2>/dev/null)
    
    return 0
}

# 应用时间过滤器
apply_time_filter() {
    local older_than_seconds="$1"
    local current_time
    current_time=$(date +%s)
    
    if [[ $older_than_seconds -le 0 ]]; then
        return 0  # 不应用时间过滤
    fi
    
    local cutoff_time=$((current_time - older_than_seconds))
    local filtered_files=()
    local filtered_dirs=()
    
    # 过滤文件
    for item_info in "${SCAN_RESULTS_FILES[@]}"; do
        local mtime=$(echo "$item_info" | cut -d'|' -f4)
        if [[ $mtime -lt $cutoff_time ]]; then
            filtered_files+=("$item_info")
        fi
    done
    
    # 过滤目录
    for item_info in "${SCAN_RESULTS_DIRS[@]}"; do
        local mtime=$(echo "$item_info" | cut -d'|' -f4)
        if [[ $mtime -lt $cutoff_time ]]; then
            filtered_dirs+=("$item_info")
        fi
    done
    
    # 更新结果数组
    SCAN_RESULTS_FILES=("${filtered_files[@]}")
    SCAN_RESULTS_DIRS=("${filtered_dirs[@]}")
}

# 应用大小过滤器
apply_size_filter() {
    local min_size_bytes="$1"
    local max_size_bytes="${2:-0}"  # 0表示无上限
    
    if [[ $min_size_bytes -le 0 ]] && [[ $max_size_bytes -le 0 ]]; then
        return 0  # 不应用大小过滤
    fi
    
    local filtered_files=()
    
    # 只对文件应用大小过滤（目录大小计算复杂）
    for item_info in "${SCAN_RESULTS_FILES[@]}"; do
        local size=$(echo "$item_info" | cut -d'|' -f3)
        local include_item=true
        
        # 检查最小大小
        if [[ $min_size_bytes -gt 0 ]] && [[ $size -lt $min_size_bytes ]]; then
            include_item=false
        fi
        
        # 检查最大大小
        if [[ $max_size_bytes -gt 0 ]] && [[ $size -gt $max_size_bytes ]]; then
            include_item=false
        fi
        
        if [[ "$include_item" == "true" ]]; then
            filtered_files+=("$item_info")
        fi
    done
    
    # 更新文件结果数组
    SCAN_RESULTS_FILES=("${filtered_files[@]}")
}

# 应用模式过滤器
apply_pattern_filter() {
    local pattern="$1"
    
    if [[ -z "$pattern" ]] || [[ "$pattern" == "*" ]]; then
        return 0  # 不应用模式过滤
    fi
    
    local filtered_files=()
    local filtered_dirs=()
    
    # 过滤文件
    for item_info in "${SCAN_RESULTS_FILES[@]}"; do
        local path=$(echo "$item_info" | cut -d'|' -f1)
        local filename=$(basename "$path")
        
        # 使用 bash 的模式匹配
        if [[ "$filename" == $pattern ]]; then
            filtered_files+=("$item_info")
        fi
    done
    
    # 过滤目录
    for item_info in "${SCAN_RESULTS_DIRS[@]}"; do
        local path=$(echo "$item_info" | cut -d'|' -f1)
        local dirname=$(basename "$path")
        
        if [[ "$dirname" == $pattern ]]; then
            filtered_dirs+=("$item_info")
        fi
    done
    
    # 更新结果数组
    SCAN_RESULTS_FILES=("${filtered_files[@]}")
    SCAN_RESULTS_DIRS=("${filtered_dirs[@]}")
}

# 计算扫描统计信息
calculate_scan_statistics() {
    local total_files=${#SCAN_RESULTS_FILES[@]}
    local total_dirs=${#SCAN_RESULTS_DIRS[@]}
    local total_size=0
    local oldest_time=9999999999
    local newest_time=0
    local largest_size=0
    local oldest_file=""
    local newest_file=""
    local largest_file=""
    
    # 统计文件信息
    for item_info in "${SCAN_RESULTS_FILES[@]}"; do
        local path=$(echo "$item_info" | cut -d'|' -f1)
        local size=$(echo "$item_info" | cut -d'|' -f3)
        local mtime=$(echo "$item_info" | cut -d'|' -f4)
        
        # 累计大小
        total_size=$((total_size + size))
        
        # 查找最老文件
        if [[ $mtime -lt $oldest_time ]]; then
            oldest_time=$mtime
            oldest_file="$path"
        fi
        
        # 查找最新文件
        if [[ $mtime -gt $newest_time ]]; then
            newest_time=$mtime
            newest_file="$path"
        fi
        
        # 查找最大文件
        if [[ $size -gt $largest_size ]]; then
            largest_size=$size
            largest_file="$path"
        fi
    done
    
    # 更新统计信息
    SCAN_STATS["total_files"]=$total_files
    SCAN_STATS["total_dirs"]=$total_dirs
    SCAN_STATS["total_size"]=$total_size
    SCAN_STATS["oldest_file"]="$oldest_file"
    SCAN_STATS["newest_file"]="$newest_file"
    SCAN_STATS["largest_file"]="$largest_file"
    SCAN_STATS["largest_file_size"]=$largest_size
}

# 格式化文件大小
format_file_size() {
    local size="$1"
    
    if [[ $size -ge 1099511627776 ]]; then
        # TB
        echo "$(( size / 1099511627776 )).$(( (size % 1099511627776) / 109951162777 ))TB"
    elif [[ $size -ge 1073741824 ]]; then
        # GB
        echo "$(( size / 1073741824 )).$(( (size % 1073741824) / 107374182 ))GB"
    elif [[ $size -ge 1048576 ]]; then
        # MB
        echo "$(( size / 1048576 )).$(( (size % 1048576) / 104857 ))MB"
    elif [[ $size -ge 1024 ]]; then
        # KB
        echo "$(( size / 1024 )).$(( (size % 1024) / 102 ))KB"
    else
        echo "${size}B"
    fi
}

# 格式化时间戳
format_timestamp() {
    local timestamp="$1"
    
    if [[ $timestamp -eq 0 ]] || [[ -z "$timestamp" ]]; then
        echo "未知"
    else
        date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "未知"
    fi
}

# 显示扫描统计信息
show_scan_statistics() {
    local show_details="${1:-false}"
    
    echo "扫描统计信息："
    echo "├─ 文件总数: ${SCAN_STATS[total_files]}"
    echo "├─ 目录总数: ${SCAN_STATS[total_dirs]}"
    echo "├─ 总大小: $(format_file_size ${SCAN_STATS[total_size]})"
    
    if [[ "${SCAN_STATS[total_files]}" -gt 0 ]]; then
        echo "├─ 最老文件: $(basename "${SCAN_STATS[oldest_file]}")"
        echo "├─ 最新文件: $(basename "${SCAN_STATS[newest_file]}")"
        echo "└─ 最大文件: $(basename "${SCAN_STATS[largest_file]}") ($(format_file_size ${SCAN_STATS[largest_file_size]}))"
    else
        echo "└─ 没有找到文件"
    fi
    
    if [[ "$show_details" == "true" ]]; then
        echo
        echo "详细信息："
        
        if [[ "${SCAN_STATS[oldest_file]}" != "" ]]; then
            echo "  最老文件时间: $(format_timestamp $oldest_time)"
        fi
        
        if [[ "${SCAN_STATS[newest_file]}" != "" ]]; then
            echo "  最新文件时间: $(format_timestamp $newest_time)"
        fi
    fi
}

# 获取匹配项目列表
get_matching_items() {
    local item_type="${1:-all}"  # files, dirs, all
    
    case "$item_type" in
        "files")
            printf '%s\n' "${SCAN_RESULTS_FILES[@]}"
            ;;
        "dirs")
            printf '%s\n' "${SCAN_RESULTS_DIRS[@]}"
            ;;
        "all")
            printf '%s\n' "${SCAN_RESULTS_FILES[@]}" "${SCAN_RESULTS_DIRS[@]}"
            ;;
        *)
            echo "ERROR: 无效的项目类型: $item_type" >&2
            return 1
            ;;
    esac
}

# 清空扫描结果
clear_scan_results() {
    SCAN_RESULTS_FILES=()
    SCAN_RESULTS_DIRS=()
    
    # 重置统计信息
    SCAN_STATS["total_files"]=0
    SCAN_STATS["total_dirs"]=0
    SCAN_STATS["total_size"]=0
    SCAN_STATS["oldest_file"]=""
    SCAN_STATS["newest_file"]=""
    SCAN_STATS["largest_file"]=""
    SCAN_STATS["largest_file_size"]=0
}

# 扫描回收站主函数
scan_trash_directories() {
    local trash_paths=("$@")
    local total_scanned=0
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        echo "ERROR: 没有指定回收站路径" >&2
        return 1
    fi
    
    # 清空之前的扫描结果
    clear_scan_results
    
    echo "开始扫描回收站..."
    
    # 扫描每个回收站路径
    for trash_path in "${trash_paths[@]}"; do
        echo "扫描: $trash_path"
        
        # 安全检查
        if ! perform_comprehensive_security_check "$trash_path" "read" "user"; then
            echo "跳过不安全的路径: $trash_path" >&2
            continue
        fi
        
        # 获取最大深度配置
        local max_depth
        max_depth=$(get_config "max_depth" "0")
        
        # 执行递归扫描
        if scan_directory_recursive "$trash_path" "$max_depth"; then
            ((total_scanned++))
        fi
    done
    
    if [[ $total_scanned -eq 0 ]]; then
        echo "ERROR: 没有成功扫描任何回收站目录" >&2
        return 1
    fi
    
    echo "完成目录扫描，应用过滤器..."
    
    # 应用过滤器
    local older_than_config
    older_than_config=$(get_config "older_than" "")
    if [[ -n "$older_than_config" ]]; then
        local older_than_seconds
        if older_than_seconds=$(parse_time_to_seconds "$older_than_config"); then
            echo "应用时间过滤器: $older_than_config"
            apply_time_filter "$older_than_seconds"
        fi
    fi
    
    local size_limit_config
    size_limit_config=$(get_config "size_limit" "")
    if [[ -n "$size_limit_config" ]]; then
        local size_limit_bytes
        if size_limit_bytes=$(parse_size_to_bytes "$size_limit_config"); then
            echo "应用大小过滤器: $size_limit_config"
            apply_size_filter "$size_limit_bytes"
        fi
    fi
    
    local pattern_config
    pattern_config=$(get_config "pattern" "*")
    if [[ "$pattern_config" != "*" ]]; then
        echo "应用模式过滤器: $pattern_config"
        apply_pattern_filter "$pattern_config"
    fi
    
    # 计算最终统计信息
    calculate_scan_statistics
    
    echo "扫描完成！"
    return 0
}

# 主函数：扫描器
main_scanner() {
    local os_type
    local trash_paths
    
    # 检测系统并获取回收站路径
    os_type=$(detect_os)
    mapfile -t trash_paths < <(main_detect_system)
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        echo "ERROR: 未找到可访问的回收站目录" >&2
        return 1
    fi
    
    # 执行扫描
    if scan_trash_directories "${trash_paths[@]}"; then
        show_scan_statistics true
        return 0
    else
        return 1
    fi
}

# 如果直接运行此脚本，执行主扫描函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_scanner "$@"
fi