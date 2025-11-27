#!/bin/bash

# ================================================================
# 垃圾清理工具 - 日志系统模块
# ================================================================
#
# 功能说明：
#   这是一个专业的Bash日志系统，为垃圾清理工具提供全面的日志记录功能。
#   支持多级别日志、结构化记录、操作审计、安全事件记录等企业级功能。
#
# 主要功能：
#   - 多级别日志记录（DEBUG、INFO、WARN、ERROR、FATAL）
#   - 结构化日志格式和元数据支持
#   - 操作审计跟踪（开始、结束、状态）
#   - 安全事件记录和告警
#   - 性能指标记录和分析
#   - 文件操作详细记录
#   - 日志轮转和大小控制
#   - 多输出通道（文件、标准输出、标准错误）
#
# 作者: AI Assistant
# 版本: 1.0
# 创建时间: 2024
# 最后修改: 2025-09-25
# ================================================================

# 导入依赖模块 - 需要配置管理器来获取日志相关配置
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"

# 日志级别定义 - 使用关联数组定义标准日志级别和对应的数值
# 数值越大表示级别越高，用于过滤和比较
declare -A LOG_LEVELS=(
    ["DEBUG"]=0     # 调试信息，详细的执行过程
    ["INFO"]=1      # 一般信息，正常的操作记录
    ["WARN"]=2      # 警告信息，需要注意但不影响执行
    ["ERROR"]=3     # 错误信息，影响功能但程序可继续
    ["FATAL"]=4     # 致命错误，程序需要终止
)

# 当前日志级别（默认INFO）- 只记录不低于此级别的日志
CURRENT_LOG_LEVEL=1

# 日志文件句柄 - 存储当前使用的日志文件路径
LOG_FILE_HANDLE=""

# 日志格式模板 - 定义统一的日志条目格式
# 格式：[时间戳] 级别 文件:行号 分类 进程ID - 消息
LOG_FORMAT_TEMPLATE='[%s] %s %s:%s %s - %s'

# ================================================================
# 日志系统初始化函数
# ================================================================
# 功能：初始化日志系统，设置日志文件、级别和相关参数
# 参数：
#   $1 - 日志文件路径（可选，默认从配置文件获取）
#   $2 - 日志级别（可选，默认INFO）
# 返回值：
#   0 - 初始化成功
#   1 - 初始化失败（目录创建或文件权限问题）
# ================================================================
init_logging() {
    local log_file="${1:-}"
    local log_level="${2:-INFO}"
    
    # 获取配置的日志文件路径，如果未指定则使用默认路径
    if [[ -z "$log_file" ]]; then
        log_file=$(get_config "log_file" "$HOME/.trash-cleaner.log")
    fi
    
    # 设置当前日志级别，如果级别无效则使用默认值
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
    
    # 设置日志文件句柄为全局可用
    LOG_FILE_HANDLE="$log_file"
    
    # 检查是否启用日志记录，如果禁用则直接返回
    if ! is_config_true "enable_logging"; then
        return 0
    fi
    
    # 检查日志文件是否可写，通过touch命令测试
    if ! touch "$log_file" 2>/dev/null; then
        echo "ERROR: 无法写入日志文件: $log_file" >&2
        return 1
    fi
    
    # 记录日志系统初始化信息
    log_info "SYSTEM" "日志系统初始化完成，日志文件: $log_file"
    
    return 0
}

# ================================================================
# 日志时间戳格式化函数
# ================================================================
# 功能：生成标准格式的时间戳，用于日志条目
# 返回值：格式化的时间字符串 (YYYY-MM-DD HH:MM:SS)
# ================================================================
format_log_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# ================================================================
# 获取调用者信息函数
# ================================================================
# 功能：获取调用日志函数的文件名和行号，用于调试和问题定位
# 返回值：文件名:行号 格式的字符串
# 注意：使用BASH_SOURCE[2]和BASH_LINENO[1]来获取真正的调用者信息
# ================================================================
get_caller_info() {
    local caller_info="${BASH_SOURCE[2]:-unknown}:${BASH_LINENO[1]:-0}"
    echo "$caller_info"
}

# ================================================================
# 通用日志记录函数
# ================================================================
# 功能：核心日志记录函数，负责处理所有日志的格式化、过滤和输出
# 参数：
#   $1 - 日志级别 (DEBUG/INFO/WARN/ERROR/FATAL)
#   $2 - 日志分类/模块名称
#   $3 - 日志消息内容
#   $4 - 元数据（可选，用于结构化日志）
# 返回值：
#   0 - 记录成功
#   1 - 记录失败
# 特性：
#   - 自动过滤低于当前级别的日志
#   - 支持多输出通道（文件、标准输出、标准错误）
#   - 自动添加调用者信息和进程ID
# ================================================================
write_log() {
    local level="$1"
    local category="$2"
    local message="$3"
    local metadata="${4:-}"
    
    # 检查日志级别是否达到记录要求，低于当前级别的日志将被忽略
    local level_num=${LOG_LEVELS[$level]:-1}
    if [[ $level_num -lt $CURRENT_LOG_LEVEL ]]; then
        return 0
    fi
    
    # 检查是否在全局配置中启用了日志记录
    if ! is_config_true "enable_logging"; then
        return 0
    fi
    
    # 格式化日志条目的各个组件
    local timestamp
    local caller_info
    local log_entry
    
    timestamp=$(format_log_timestamp)
    caller_info=$(get_caller_info)
    
    # 构建基本日志条目，使用统一的格式模板
    log_entry=$(printf "$LOG_FORMAT_TEMPLATE" \
        "$timestamp" \
        "$level" \
        "$caller_info" \
        "$category" \
        "$$" \
        "$message")
    
    # 添加元数据（如果提供）- 用于结构化日志和数据分析
    if [[ -n "${metadata:-}" ]]; then
        log_entry="$log_entry | $metadata"
    fi
    
    # 写入日志文件，使用追加模式保留历史记录
    if [[ -n "$LOG_FILE_HANDLE" ]]; then
        echo "$log_entry" >> "$LOG_FILE_HANDLE" 2>/dev/null || {
            echo "ERROR: 无法写入日志文件: $LOG_FILE_HANDLE" >&2
            return 1
        }
    fi
    
    # 如果是ERROR或FATAL级别，同时输出到标准错误以确保及时可见
    if [[ $level_num -ge ${LOG_LEVELS["ERROR"]} ]]; then
        echo "$log_entry" >&2
    fi
    
    # 如果启用详细模式，将INFO及以上级别的日志输出到标准输出
    if is_config_true "verbose" && [[ $level_num -ge ${LOG_LEVELS["INFO"]} ]]; then
        echo "$log_entry"
    fi
    
    return 0
}

# ================================================================
# 便捷日志记录函数组
# ================================================================
# 功能：为不同日志级别提供简化的调用接口
# 参数：
#   $1 - 日志分类/模块名称（可选，默认GENERAL）
#   $2 - 日志消息内容
#   $3 - 元数据（可选）
# ================================================================

# 调试级别日志 - 用于详细的程序执行跟踪
log_debug() {
    write_log "DEBUG" "${1:-GENERAL}" "$2" "${3:-}"
}

# 信息级别日志 - 用于记录正常的程序操作
log_info() {
    write_log "INFO" "${1:-GENERAL}" "$2" "${3:-}"
}

# 警告级别日志 - 用于记录需要注意但不影响功能的情况
log_warn() {
    write_log "WARN" "${1:-GENERAL}" "$2" "${3:-}"
}

# 错误级别日志 - 用于记录影响功能但程序可继续的错误
log_error() {
    write_log "ERROR" "${1:-GENERAL}" "$2" "${3:-}"
}

# 致命错误级别日志 - 用于记录导致程序需要终止的严重错误
log_fatal() {
    write_log "FATAL" "${1:-GENERAL}" "$2" "${3:-}"
}

# ================================================================
# 操作审计日志函数组
# ================================================================
# 功能：提供操作级别的审计日志，用于跟踪关键操作的开始和结束
# 用途：系统监控、性能分析、问题排查和安全审计
# ================================================================

# 记录操作开始
# 参数：
#   $1 - 操作名称（必需）
#   $2 - 操作详细信息（可选）
log_operation_start() {
    local operation="$1"
    local details="${2:-}"
    
    local metadata="operation=start"
    if [[ -n "$details" ]]; then
        metadata="$metadata, details=$details"
    fi
    
    log_info "OPERATION" "开始执行操作: $operation" "$metadata"
}

# 记录操作结束
# 参数：
#   $1 - 操作名称（必需）
#   $2 - 操作状态（可选，默认SUCCESS）
#   $3 - 操作详细信息（可选）
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

# ================================================================
# 安全事件日志函数
# ================================================================
# 功能：记录安全相关的事件，用于安全审计和威胁检测
# 参数：
#   $1 - 事件类型（必需）
#   $2 - 事件描述（必需）
#   $3 - 严重程度（可选，默认WARN）
#   $4 - 相关路径（可选）
# ================================================================
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

# ================================================================
# 文件操作日志函数
# ================================================================
# 功能：记录具体的文件操作，用于操作审计和问题追踪
# 参数：
#   $1 - 操作类型 (SCAN/DELETE/SKIP/MOVE等)
#   $2 - 文件路径
#   $3 - 操作状态（可选，默认SUCCESS）
#   $4 - 文件大小（可选，默认0）
#   $5 - 额外详细信息（可选）
# ================================================================
log_file_operation() {
    local operation="$1"  # 操作类型：SCAN, DELETE, SKIP
    local file_path="$2"
    local status="${3:-SUCCESS}"
    local size="${4:-0}"
    local details="${5:-}"
    
    local metadata="operation=$operation, status=$status, size=$size"
    if [[ -n "$details" ]]; then
        metadata="$metadata, details=$details"
    fi
    
    # 根据操作状态选择适当的日志级别
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

# ================================================================
# 日志轮转函数
# ================================================================
# 功能：当日志文件超过指定大小时进行轮转，防止日志文件过大
# 参数：
#   $1 - 日志文件路径（可选，默认使用当前日志文件）
#   $2 - 最大文件大小（可选，默认10MB）
#   $3 - 最大保留文件数（可选，默认5个）
# 返回值：0-成功
# ================================================================
rotate_logs() {
    local log_file="${1:-$LOG_FILE_HANDLE}"
    local max_size="${2:-10485760}"  # 默认10MB
    local max_files="${3:-5}"        # 默认保疙5个历史文件
    
    if [[ ! -f "$log_file" ]]; then
        return 0
    fi
    
    # 检查文件大小，兼容Linux和macOS的stat命令
    local file_size
    file_size=$(stat -c "%s" "$log_file" 2>/dev/null || stat -f "%z" "$log_file" 2>/dev/null || echo "0")
    
    if [[ $file_size -lt $max_size ]]; then
        return 0  # 文件还没有达到轮转大小
    fi
    
    # 执行轮转操作
    log_info "SYSTEM" "开始日志轮转，当前文件大小: $(format_file_size $file_size)"
    
    # 删除最老的日志文件
    local oldest_log="${log_file}.${max_files}"
    if [[ -f "$oldest_log" ]]; then
        rm -f "$oldest_log"
    fi
    
    # 轮转现有日志文件，从最新到最老依次重命名
    for ((i=max_files-1; i>=1; i--)); do
        local current_log="${log_file}.$i"
        local next_log="${log_file}.$((i+1))"
        
        if [[ -f "$current_log" ]]; then
            mv "$current_log" "$next_log"
        fi
    done
    
    # 轮转当前日志文件并创建新文件
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