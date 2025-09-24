#!/bin/bash

# 日志系统模块
# 功能：操作记录、审计日志、日志轮转、结构化日志

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"

# 日志级别定义
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARN"]=2
    ["ERROR"]=3
    ["FATAL"]=4
)

# 当前日志级别（默认INFO）
CURRENT_LOG_LEVEL=1

# 日志文件句柄
LOG_FILE_HANDLE=""

# 日志格式模板
LOG_FORMAT_TEMPLATE='[%s] %s %s:%s %s - %s'

# 初始化日志系统
init_logging() {
    local log_file="${1:-}"
    local log_level="${2:-INFO}"
    
    # 获取配置的日志文件路径
    if [[ -z "$log_file" ]]; then
        log_file=$(get_config "log_file" "$HOME/.trash-cleaner.log")
    fi
    
    # 设置日志级别
    CURRENT_LOG_LEVEL=${LOG_LEVELS[$log_level]:-1}
    
    # 创建日志目录（如果不存在）
    local log_dir
    log_dir=$(dirname "$log_file")
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir" 2>/dev/null || {
            echo "ERROR: 无法创建日志目录: $log_dir" >&2
            return 1
        }
    fi
    
    # 设置日志文件句柄
    LOG_FILE_HANDLE="$log_file"
    
    # 检查是否启用日志记录
    if ! is_config_true "enable_logging"; then
        return 0
    fi
    
    # 检查日志文件是否可写
    if ! touch "$log_file" 2>/dev/null; then
        echo "ERROR: 无法写入日志文件: $log_file" >&2
        return 1
    fi
    
    # 记录日志初始化信息
    log_info "SYSTEM" "日志系统初始化完成，日志文件: $log_file"
    
    return 0
}

# 格式化时间戳
format_log_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# 获取调用者信息
get_caller_info() {
    local caller_info="${BASH_SOURCE[2]:-unknown}:${BASH_LINENO[1]:-0}"
    echo "$caller_info"
}

# 通用日志记录函数
write_log() {
    local level="$1"
    local category="$2"
    local message="$3"
    local metadata="${4:-}"
    
    # 检查日志级别
    local level_num=${LOG_LEVELS[$level]:-1}
    if [[ $level_num -lt $CURRENT_LOG_LEVEL ]]; then
        return 0
    fi
    
    # 检查是否启用日志记录
    if ! is_config_true "enable_logging"; then
        return 0
    fi
    
    # 格式化日志条目
    local timestamp
    local caller_info
    local log_entry
    
    timestamp=$(format_log_timestamp)
    caller_info=$(get_caller_info)
    
    # 构建基本日志条目
    log_entry=$(printf "$LOG_FORMAT_TEMPLATE" \
        "$timestamp" \
        "$level" \
        "$caller_info" \
        "$category" \
        "$$" \
        "$message")
    
    # 添加元数据（如果提供）
    if [[ -n "${metadata:-}" ]]; then
        log_entry="$log_entry | $metadata"
    fi
    
    # 写入日志文件
    if [[ -n "$LOG_FILE_HANDLE" ]]; then
        echo "$log_entry" >> "$LOG_FILE_HANDLE" 2>/dev/null || {
            echo "ERROR: 无法写入日志文件: $LOG_FILE_HANDLE" >&2
            return 1
        }
    fi
    
    # 如果是ERROR或FATAL级别，同时输出到标准错误
    if [[ $level_num -ge ${LOG_LEVELS["ERROR"]} ]]; then
        echo "$log_entry" >&2
    fi
    
    # 如果启用详细模式，输出到标准输出
    if is_config_true "verbose" && [[ $level_num -ge ${LOG_LEVELS["INFO"]} ]]; then
        echo "$log_entry"
    fi
    
    return 0
}

# 便捷日志记录函数
log_debug() {
    write_log "DEBUG" "${1:-GENERAL}" "$2" "${3:-}"
}

log_info() {
    write_log "INFO" "${1:-GENERAL}" "$2" "${3:-}"
}

log_warn() {
    write_log "WARN" "${1:-GENERAL}" "$2" "${3:-}"
}

log_error() {
    write_log "ERROR" "${1:-GENERAL}" "$2" "${3:-}"
}

log_fatal() {
    write_log "FATAL" "${1:-GENERAL}" "$2" "${3:-}"
}

# 记录操作开始
log_operation_start() {
    local operation="$1"
    local details="${2:-}"
    
    local metadata="operation=start"
    if [[ -n "$details" ]]; then
        metadata="$metadata, details=$details"
    fi
    
    log_info "OPERATION" "开始执行操作: $operation" "$metadata"
}

# 记录操作完成
log_operation_end() {
    local operation="$1"
    local status="${2:-SUCCESS}"
    local details="${3:-}"
    
    local metadata="operation=end, status=$status"
    if [[ -n "$details" ]]; then
        metadata="$metadata, details=$details"
    fi
    
    if [[ "$status" == "SUCCESS" ]]; then
        log_info "OPERATION" "操作完成: $operation" "$metadata"
    else
        log_error "OPERATION" "操作失败: $operation" "$metadata"
    fi
}

# 记录安全事件
log_security_event() {
    local event_type="$1"
    local description="$2"
    local severity="${3:-WARN}"
    local path="${4:-}"
    
    local metadata="event_type=$event_type"
    if [[ -n "$path" ]]; then
        metadata="$metadata, path=$path"
    fi
    
    write_log "$severity" "SECURITY" "$description" "$metadata"
}

# 记录文件操作
log_file_operation() {
    local operation="$1"  # SCAN, DELETE, SKIP
    local file_path="$2"
    local status="${3:-SUCCESS}"
    local size="${4:-0}"
    local details="${5:-}"
    
    local metadata="operation=$operation, status=$status, size=$size"
    if [[ -n "$details" ]]; then
        metadata="$metadata, details=$details"
    fi
    
    local level="INFO"
    if [[ "$status" != "SUCCESS" ]]; then
        level="WARN"
    fi
    
    write_log "$level" "FILE_OP" "$operation: $(basename "$file_path")" "$metadata"
}

# 记录系统信息
log_system_info() {
    local info_type="$1"
    local description="$2"
    local data="${3:-}"
    
    local metadata="info_type=$info_type"
    if [[ -n "$data" ]]; then
        metadata="$metadata, data=$data"
    fi
    
    log_info "SYSTEM" "$description" "$metadata"
}

# 记录性能指标
log_performance() {
    local metric_name="$1"
    local metric_value="$2"
    local unit="${3:-}"
    local details="${4:-}"
    
    local metadata="metric=$metric_name, value=$metric_value"
    if [[ -n "$unit" ]]; then
        metadata="$metadata, unit=$unit"
    fi
    if [[ -n "$details" ]]; then
        metadata="$metadata, details=$details"
    fi
    
    log_info "PERFORMANCE" "$metric_name: $metric_value $unit" "$metadata"
}

# 记录配置变更
log_config_change() {
    local config_key="$1"
    local old_value="$2"
    local new_value="$3"
    local source="${4:-USER}"
    
    local metadata="key=$config_key, old_value=$old_value, new_value=$new_value, source=$source"
    
    log_info "CONFIG" "配置变更: $config_key = $new_value" "$metadata"
}

# 日志轮转
rotate_logs() {
    local log_file="${1:-$LOG_FILE_HANDLE}"
    local max_size="${2:-10485760}"  # 默认10MB
    local max_files="${3:-5}"        # 默认保留5个历史文件
    
    if [[ ! -f "$log_file" ]]; then
        return 0
    fi
    
    # 检查文件大小
    local file_size
    file_size=$(stat -c "%s" "$log_file" 2>/dev/null || stat -f "%z" "$log_file" 2>/dev/null || echo "0")
    
    if [[ $file_size -lt $max_size ]]; then
        return 0  # 文件还没有达到轮转大小
    fi
    
    # 执行轮转
    log_info "SYSTEM" "开始日志轮转，当前文件大小: $(format_file_size $file_size)"
    
    # 删除最老的日志文件
    local oldest_log="${log_file}.${max_files}"
    if [[ -f "$oldest_log" ]]; then
        rm -f "$oldest_log"
    fi
    
    # 轮转现有日志文件
    for ((i=max_files-1; i>=1; i--)); do
        local current_log="${log_file}.$i"
        local next_log="${log_file}.$((i+1))"
        
        if [[ -f "$current_log" ]]; then
            mv "$current_log" "$next_log"
        fi
    done
    
    # 轮转当前日志文件
    if [[ -f "$log_file" ]]; then
        mv "$log_file" "${log_file}.1"
        touch "$log_file"
        chmod 644 "$log_file"
    fi
    
    log_info "SYSTEM" "日志轮转完成"
    
    return 0
}

# 清理过期日志
cleanup_old_logs() {
    local log_dir="${1:-$(dirname "$LOG_FILE_HANDLE")}"
    local retention_days="${2:-$(get_config "log_retention_days" "30")}"
    
    if [[ ! -d "$log_dir" ]]; then
        return 0
    fi
    
    log_info "SYSTEM" "清理 $retention_days 天前的日志文件"
    
    local deleted_count=0
    
    # 查找并删除过期的日志文件
    while IFS= read -r -d '' old_log; do
        if rm -f "$old_log"; then
            ((deleted_count++))
            log_debug "SYSTEM" "删除过期日志: $(basename "$old_log")"
        fi
    done < <(find "$log_dir" -name "*.log*" -type f -mtime +$retention_days -print0 2>/dev/null)
    
    if [[ $deleted_count -gt 0 ]]; then
        log_info "SYSTEM" "清理完成，删除了 $deleted_count 个过期日志文件"
    else
        log_debug "SYSTEM" "没有找到需要清理的过期日志文件"
    fi
    
    return 0
}

# 生成日志摘要报告
generate_log_summary() {
    local log_file="${1:-$LOG_FILE_HANDLE}"
    local since_time="${2:-$(date -d '1 day ago' '+%Y-%m-%d %H:%M:%S')}"
    
    if [[ ! -f "$log_file" ]]; then
        echo "日志文件不存在: $log_file" >&2
        return 1
    fi
    
    local temp_file="/tmp/log_summary_$$"
    
    # 提取指定时间之后的日志条目
    awk -v since="$since_time" '
    $0 ~ /^\[/ {
        log_time = substr($0, 2, 19)
        if (log_time >= since) {
            print $0
        }
    }' "$log_file" > "$temp_file"
    
    if [[ ! -s "$temp_file" ]]; then
        echo "在指定时间 ($since_time) 之后没有找到日志条目"
        rm -f "$temp_file"
        return 0
    fi
    
    echo "日志摘要报告 (自 $since_time)"
    echo "========================================"
    
    # 统计各级别日志数量
    echo "日志级别统计:"
    for level in DEBUG INFO WARN ERROR FATAL; do
        local count
        count=$(grep -c " $level " "$temp_file" 2>/dev/null || echo "0")
        printf "  %-5s: %d\n" "$level" "$count"
    done
    
    echo
    
    # 统计各类别日志数量
    echo "日志类别统计:"
    awk '{
        match($0, / [A-Z_]+ /, arr)
        if (arr[0]) {
            category = substr(arr[0], 2, length(arr[0])-2)
            categories[category]++
        }
    }
    END {
        for (cat in categories) {
            printf "  %-12s: %d\n", cat, categories[cat]
        }
    }' "$temp_file" | sort -k2,2nr
    
    echo
    
    # 显示错误和警告
    local error_count
    error_count=$(grep -c " ERROR \| FATAL " "$temp_file" 2>/dev/null || echo "0")
    
    if [[ $error_count -gt 0 ]]; then
        echo "错误和致命错误:"
        grep " ERROR \| FATAL " "$temp_file" | tail -10
        echo
    fi
    
    local warn_count
    warn_count=$(grep -c " WARN " "$temp_file" 2>/dev/null || echo "0")
    
    if [[ $warn_count -gt 0 ]]; then
        echo "最近的警告:"
        grep " WARN " "$temp_file" | tail -5
        echo
    fi
    
    # 清理临时文件
    rm -f "$temp_file"
    
    return 0
}

# 导出日志为JSON格式
export_logs_as_json() {
    local log_file="${1:-$LOG_FILE_HANDLE}"
    local output_file="${2:-}"
    local since_time="${3:-}"
    
    if [[ ! -f "$log_file" ]]; then
        echo "日志文件不存在: $log_file" >&2
        return 1
    fi
    
    local temp_file="/tmp/log_json_$$"
    
    # 设置输出目标
    local output_target
    if [[ -n "$output_file" ]]; then
        output_target="$output_file"
    else
        output_target="/dev/stdout"
    fi
    
    # 开始JSON数组
    echo '[' > "$temp_file"
    
    local first_entry=true
    
    # 解析日志文件并转换为JSON
    while IFS= read -r line; do
        if [[ "$line" =~ ^\[([^\]]+)\]\ ([A-Z]+)\ ([^:]+):([0-9]+)\ ([A-Z_]+)\ ([0-9]+)\ -\ (.+)$ ]]; then
            local timestamp="${BASH_REMATCH[1]}"
            local level="${BASH_REMATCH[2]}"
            local source="${BASH_REMATCH[3]}"
            local line_num="${BASH_REMATCH[4]}"
            local category="${BASH_REMATCH[5]}"
            local pid="${BASH_REMATCH[6]}"
            local message="${BASH_REMATCH[7]}"
            
            # 检查时间过滤条件
            if [[ -n "$since_time" ]] && [[ "$timestamp" < "$since_time" ]]; then
                continue
            fi
            
            # 添加逗号分隔符（除了第一个条目）
            if [[ "$first_entry" == "false" ]]; then
                echo ',' >> "$temp_file"
            fi
            first_entry=false
            
            # 生成JSON条目
            cat >> "$temp_file" <<EOF
  {
    "timestamp": "$timestamp",
    "level": "$level",
    "source": "$source",
    "line": $line_num,
    "category": "$category",
    "pid": $pid,
    "message": "$message"
  }
EOF
        fi
    done < "$log_file"
    
    # 结束JSON数组
    echo ']' >> "$temp_file"
    
    # 输出结果
    cat "$temp_file" > "$output_target"
    
    # 清理临时文件
    rm -f "$temp_file"
    
    return 0
}

# 设置日志轮转定时任务
setup_log_rotation() {
    local interval="${1:-daily}"  # daily, weekly, monthly
    
    log_info "SYSTEM" "设置日志轮转: $interval"
    
    # 这里可以添加cron任务设置逻辑
    # 由于安全考虑，暂时只记录日志
    
    return 0
}

# 主日志管理函数
main_logging() {
    local action="${1:-init}"
    
    case "$action" in
        "init")
            init_logging "$2" "$3"
            ;;
        "rotate")
            rotate_logs "$2" "$3" "$4"
            ;;
        "cleanup")
            cleanup_old_logs "$2" "$3"
            ;;
        "summary")
            generate_log_summary "$2" "$3"
            ;;
        "export")
            export_logs_as_json "$2" "$3" "$4"
            ;;
        *)
            echo "用法: $0 {init|rotate|cleanup|summary|export} [参数...]" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主日志管理函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_logging "$@"
fi