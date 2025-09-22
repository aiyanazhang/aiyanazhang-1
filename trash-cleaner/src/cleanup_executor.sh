#!/bin/bash

# 清理执行器模块
# 功能：执行文件删除操作、进度显示、错误处理

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security_checker.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/trash_scanner.sh"

# 清理操作统计
declare -A CLEANUP_STATS=(
    ["total_items"]=0
    ["processed_items"]=0
    ["successful_deletions"]=0
    ["failed_deletions"]=0
    ["skipped_items"]=0
    ["total_size_freed"]=0
    ["start_time"]=0
    ["end_time"]=200
)

# 失败项目列表
declare -a FAILED_ITEMS=()
declare -a SKIPPED_ITEMS=()

# 颜色代码（如果支持彩色输出）
declare -A COLORS=(
    ["RED"]="\033[31m"
    ["GREEN"]="\033[32m"
    ["YELLOW"]="\033[33m"
    ["BLUE"]="\033[34m"
    ["PURPLE"]="\033[35m"
    ["CYAN"]="\033[36m"
    ["WHITE"]="\033[37m"
    ["RESET"]="\033[0m"
    ["BOLD"]="\033[1m"
)

# 检查是否启用彩色输出
use_colors() {
    if is_config_true "color_output" && [[ -t 1 ]]; then
        return 0
    else
        # 禁用颜色
        for key in "${!COLORS[@]}"; do
            COLORS["$key"]=""
        done
        return 1
    fi
}

# 打印彩色文本
print_colored() {
    local color="$1"
    local text="$2"
    
    printf "${COLORS[$color]}%s${COLORS[RESET]}" "$text"
}

# 显示进度条
show_progress() {
    local current="$1"
    local total="$2"
    local prefix="${3:-进度}"
    local width=50
    
    if ! is_config_true "progress_bar"; then
        return 0
    fi
    
    if [[ $total -eq 0 ]]; then
        return 0
    fi
    
    local progress=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    printf "\r%s: [" "$prefix"
    printf "%*s" "$filled" | tr ' ' '█'
    printf "%*s" "$empty" | tr ' ' '░'
    printf "] %d%% (%d/%d)" "$progress" "$current" "$total"
    
    if [[ $current -eq $total ]]; then
        echo  # 完成时换行
    fi
}

# 安全删除单个文件
safe_delete_file() {
    local file_path="$1"
    local dry_run="${2:-false}"
    
    # 再次验证文件路径安全性
    if ! perform_comprehensive_security_check "$file_path" "delete" "user"; then
        echo "安全检查失败: $file_path" >&2
        return 1
    fi
    
    # 检查文件是否存在
    if [[ ! -e "$file_path" ]]; then
        echo "文件不存在: $file_path" >&2
        return 2
    fi
    
    # 获取文件大小（用于统计）
    local file_size=0
    if [[ -f "$file_path" ]]; then
        if command -v stat >/dev/null 2>&1; then
            file_size=$(stat -c "%s" "$file_path" 2>/dev/null || stat -f "%z" "$file_path" 2>/dev/null || echo "0")
        else
            file_size=$(wc -c < "$file_path" 2>/dev/null || echo "0")
        fi
    fi
    
    # 如果是预览模式，不实际删除
    if [[ "$dry_run" == "true" ]]; then
        if is_config_true "verbose"; then
            print_colored "BLUE" "[预览] "
            echo "将删除: $file_path ($(format_file_size $file_size))"
        fi
        return 0
    fi
    
    # 执行删除操作
    if rm -f "$file_path" 2>/dev/null; then
        if is_config_true "verbose"; then
            print_colored "GREEN" "✓ "
            echo "已删除文件: $(basename "$file_path")"
        fi
        
        # 更新统计信息
        CLEANUP_STATS["total_size_freed"]=$((CLEANUP_STATS["total_size_freed"] + file_size))
        return 0
    else
        if is_config_true "verbose"; then
            print_colored "RED" "✗ "
            echo "删除失败: $(basename "$file_path")"
        fi
        return 3
    fi
}

# 安全删除目录
safe_delete_directory() {
    local dir_path="$1"
    local dry_run="${2:-false}"
    
    # 再次验证目录路径安全性
    if ! perform_comprehensive_security_check "$dir_path" "delete" "user"; then
        echo "安全检查失败: $dir_path" >&2
        return 1
    fi
    
    # 检查目录是否存在
    if [[ ! -d "$dir_path" ]]; then
        echo "目录不存在: $dir_path" >&2
        return 2
    fi
    
    # 如果是预览模式，不实际删除
    if [[ "$dry_run" == "true" ]]; then
        if is_config_true "verbose"; then
            print_colored "BLUE" "[预览] "
            echo "将删除目录: $dir_path"
        fi
        return 0
    fi
    
    # 执行删除操作（递归删除）
    if rm -rf "$dir_path" 2>/dev/null; then
        if is_config_true "verbose"; then
            print_colored "GREEN" "✓ "
            echo "已删除目录: $(basename "$dir_path")"
        fi
        return 0
    else
        if is_config_true "verbose"; then
            print_colored "RED" "✗ "
            echo "删除失败: $(basename "$dir_path")"
        fi
        return 3
    fi
}

# 处理单个项目
process_item() {
    local item_info="$1"
    local dry_run="${2:-false}"
    
    # 解析项目信息：path|type|size|mtime
    local path=$(echo "$item_info" | cut -d'|' -f1)
    local type=$(echo "$item_info" | cut -d'|' -f2)
    local size=$(echo "$item_info" | cut -d'|' -f3)
    local mtime=$(echo "$item_info" | cut -d'|' -f4)
    
    # 更新处理计数
    CLEANUP_STATS["processed_items"]=$((CLEANUP_STATS["processed_items"] + 1))
    
    local result=0
    
    # 根据类型执行相应的删除操作
    case "$type" in
        "file")
            safe_delete_file "$path" "$dry_run"
            result=$?
            ;;
        "dir")
            safe_delete_directory "$path" "$dry_run"
            result=$?
            ;;
        *)
            echo "ERROR: 未知的项目类型: $type" >&2
            result=4
            ;;
    esac
    
    # 统计结果
    case $result in
        0)
            CLEANUP_STATS["successful_deletions"]=$((CLEANUP_STATS["successful_deletions"] + 1))
            ;;
        1|2|3)
            CLEANUP_STATS["failed_deletions"]=$((CLEANUP_STATS["failed_deletions"] + 1))
            FAILED_ITEMS+=("$path:$result")
            ;;
        4)
            CLEANUP_STATS["skipped_items"]=$((CLEANUP_STATS["skipped_items"] + 1))
            SKIPPED_ITEMS+=("$path:未知类型")
            ;;
    esac
    
    return $result
}

# 用户确认提示
confirm_deletion() {
    local total_items="$1"
    local total_size="$2"
    
    # 如果设置了自动确认，跳过提示
    if ! is_config_true "confirm_deletion"; then
        return 0
    fi
    
    echo
    print_colored "YELLOW" "警告: "
    echo "即将删除 $total_items 个项目，总大小 $(format_file_size $total_size)"
    echo
    
    while true; do
        read -p "确认执行删除操作？[y/N] " -r response
        case "$response" in
            [yY]|[yY][eE][sS])
                return 0
                ;;
            [nN]|[nN][oO]|"")
                echo "操作已取消"
                return 1
                ;;
            *)
                echo "请输入 y(是) 或 n(否)"
                ;;
        esac
    done
}

# 批处理删除操作
batch_delete_items() {
    local items=("$@")
    local total_items=${#items[@]}
    local dry_run
    
    # 检查是否为预览模式
    dry_run=$(is_config_true "dry_run" && echo "true" || echo "false")
    
    if [[ $total_items -eq 0 ]]; then
        echo "没有找到要删除的项目"
        return 0
    fi
    
    # 初始化统计信息
    CLEANUP_STATS["total_items"]=$total_items
    CLEANUP_STATS["processed_items"]=0
    CLEANUP_STATS["successful_deletions"]=0
    CLEANUP_STATS["failed_deletions"]=0
    CLEANUP_STATS["skipped_items"]=0
    CLEANUP_STATS["total_size_freed"]=0
    CLEANUP_STATS["start_time"]=$(date +%s)
    
    # 清空失败和跳过列表
    FAILED_ITEMS=()
    SKIPPED_ITEMS=()
    
    echo "开始处理 $total_items 个项目..."
    
    # 处理每个项目
    local current_item=0
    for item_info in "${items[@]}"; do
        ((current_item++))
        
        # 显示进度
        show_progress "$current_item" "$total_items" "清理进度"
        
        # 处理项目
        process_item "$item_info" "$dry_run"
        
        # 简短延迟，避免过快的操作
        sleep 0.01
    done
    
    CLEANUP_STATS["end_time"]=$(date +%s)
    
    echo
    if [[ "$dry_run" == "true" ]]; then
        print_colored "BLUE" "预览完成！"
    else
        print_colored "GREEN" "清理完成！"
    fi
    echo
    
    return 0
}

# 显示清理结果统计
show_cleanup_results() {
    local start_time="${CLEANUP_STATS[start_time]}"
    local end_time="${CLEANUP_STATS[end_time]}"
    local duration=$((end_time - start_time))
    
    echo "清理结果统计："
    echo "├─ 处理项目: ${CLEANUP_STATS[processed_items]}/${CLEANUP_STATS[total_items]}"
    
    if is_config_true "dry_run"; then
        echo "├─ 预览项目: ${CLEANUP_STATS[successful_deletions]}"
    else
        echo "├─ 成功删除: ${CLEANUP_STATS[successful_deletions]}"
        echo "├─ 释放空间: $(format_file_size ${CLEANUP_STATS[total_size_freed]})"
    fi
    
    echo "├─ 删除失败: ${CLEANUP_STATS[failed_deletions]}"
    echo "├─ 跳过项目: ${CLEANUP_STATS[skipped_items]}"
    echo "└─ 处理时间: ${duration}秒"
    
    # 显示失败项目详情
    if [[ ${#FAILED_ITEMS[@]} -gt 0 ]]; then
        echo
        print_colored "RED" "失败项目详情："
        for failed_item in "${FAILED_ITEMS[@]}"; do
            local path=$(echo "$failed_item" | cut -d':' -f1)
            local error_code=$(echo "$failed_item" | cut -d':' -f2)
            
            case "$error_code" in
                1) echo "  ✗ $path (安全检查失败)" ;;
                2) echo "  ✗ $path (文件不存在)" ;;
                3) echo "  ✗ $path (删除操作失败)" ;;
                *) echo "  ✗ $path (未知错误: $error_code)" ;;
            esac
        done
    fi
    
    # 显示跳过项目详情
    if [[ ${#SKIPPED_ITEMS[@]} -gt 0 ]]; then
        echo
        print_colored "YELLOW" "跳过项目详情："
        for skipped_item in "${SKIPPED_ITEMS[@]}"; do
            local path=$(echo "$skipped_item" | cut -d':' -f1)
            local reason=$(echo "$skipped_item" | cut -d':' -f2)
            echo "  ⏭️  $path ($reason)"
        done
    fi
}

# 清理特定类型的项目
cleanup_by_type() {
    local clean_type="${1:-all}"
    local trash_paths=("${@:2}")
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        echo "ERROR: 没有指定回收站路径" >&2
        return 1
    fi
    
    # 初始化颜色支持
    use_colors
    
    echo "开始清理回收站..."
    echo "清理类型: $clean_type"
    
    # 扫描回收站内容
    if ! scan_trash_directories "${trash_paths[@]}"; then
        echo "ERROR: 扫描回收站失败" >&2
        return 1
    fi
    
    # 获取匹配的项目
    local matching_items
    mapfile -t matching_items < <(get_matching_items "$clean_type")
    
    if [[ ${#matching_items[@]} -eq 0 ]]; then
        echo "没有找到匹配的项目进行清理"
        return 0
    fi
    
    # 显示即将清理的内容摘要
    echo
    show_scan_statistics false
    
    # 用户确认（除非是预览模式）
    if ! is_config_true "dry_run"; then
        if ! confirm_deletion "${#matching_items[@]}" "${SCAN_STATS[total_size]}"; then
            return 1
        fi
    fi
    
    # 执行批量删除
    batch_delete_items "${matching_items[@]}"
    
    # 显示结果
    show_cleanup_results
    
    return 0
}

# 紧急停止清理（信号处理）
emergency_stop() {
    echo
    print_colored "RED" "收到停止信号，正在安全停止清理操作..."
    
    # 显示当前进度
    show_cleanup_results
    
    exit 130
}

# 设置信号处理器
setup_signal_handlers() {
    trap emergency_stop SIGINT SIGTERM
}

# 主清理函数
main_cleanup() {
    local clean_type os_type trash_paths
    
    # 设置信号处理
    setup_signal_handlers
    
    # 获取清理类型配置
    clean_type=$(get_config "clean_type" "all")
    
    # 检测系统并获取回收站路径
    os_type=$(detect_os)
    mapfile -t trash_paths < <(main_detect_system)
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        echo "ERROR: 未找到可访问的回收站目录" >&2
        return 1
    fi
    
    # 执行清理
    cleanup_by_type "$clean_type" "${trash_paths[@]}"
    
    return $?
}

# 如果直接运行此脚本，执行主清理函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_cleanup "$@"
fi
