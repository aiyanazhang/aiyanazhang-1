#!/bin/bash

# ===============================================================================
# 文本内容搜索Shell脚本
# 版本: 1.0.0
# 作者: AI Assistant
# 描述: 功能强大的文本内容搜索工具，支持普通文本和正则表达式搜索
# ===============================================================================

# 脚本版本
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_NAME="text-search"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 全局变量
SEARCH_PATTERN=""
SEARCH_DIRECTORY="."
USE_REGEX=false
FILE_TYPES=""
EXCLUDE_DIRS=""
OUTPUT_FORMAT="simple"
SHOW_LINE_NUMBERS=false
COUNT_ONLY=false
FILES_ONLY=false
VERBOSE=false
COLORED_OUTPUT=true
MAX_DEPTH=10
MAX_FILE_SIZE="10M"
PARALLEL_JOBS=$(nproc 2>/dev/null || echo "4")

# 默认排除目录
DEFAULT_EXCLUDES=".git,.svn,node_modules,target,.idea,.vscode,__pycache__,.pytest_cache,build,dist,out"

# 统计变量
TOTAL_FILES_SEARCHED=0
TOTAL_MATCHES=0
SEARCH_START_TIME=""

# 临时文件
TEMP_DIR="/tmp/${SCRIPT_NAME}_$$"
RESULTS_FILE="${TEMP_DIR}/results.txt"
LOG_FILE="${TEMP_DIR}/search.log"

# 加载配置文件函数
load_config() {
    local config_file="${HOME}/.${SCRIPT_NAME}rc"
    if [[ -f "$config_file" ]]; then
        # shellcheck source=/dev/null
        source "$config_file"
        log_debug "已加载配置文件: $config_file"
    fi
}

# 日志函数
log_debug() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${CYAN}[DEBUG]${NC} $1" >&2
    fi
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG: $1" >> "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN: $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

# 清理临时文件
cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

# 信号处理
handle_interrupt() {
    echo
    log_warn "搜索被用户中断"
    
    # 终止子进程
    if [[ -n "${CHILD_PIDS[*]}" ]]; then
        log_debug "正在终止子进程: ${CHILD_PIDS[*]}"
        kill "${CHILD_PIDS[@]}" 2>/dev/null
        wait "${CHILD_PIDS[@]}" 2>/dev/null
    fi
    
    cleanup
    exit 130
}

# 子进程管理
CHILD_PIDS=()

# 错误处理函数
handle_error() {
    local error_code=$1
    local error_msg="$2"
    local file_path="$3"
    
    case $error_code in
        1)
            log_error "参数错误: $error_msg"
            show_help
            exit 1
            ;;
        2)
            log_warn "权限错误: $error_msg $(if [[ -n "$file_path" ]]; then echo "($file_path)"; fi)"
            return 0  # 继续处理其他文件
            ;;
        3)
            log_warn "文件错误: $error_msg $(if [[ -n "$file_path" ]]; then echo "($file_path)"; fi)"
            return 0  # 继续处理其他文件
            ;;
        4)
            log_error "系统错误: $error_msg"
            cleanup
            exit 4
            ;;
        5)
            log_warn "搜索超时: $error_msg"
            return 0
            ;;
        *)
            log_error "未知错误 (代码: $error_code): $error_msg"
            cleanup
            exit 255
            ;;
    esac
}

# 验证系统依赖
check_dependencies() {
    local missing_deps=()
    local required_commands=("find" "grep" "xargs" "wc" "awk" "sed")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        handle_error 4 "缺少必需的系统命令: ${missing_deps[*]}"
    fi
    
    # 检查GNU版本的find和grep (Linux)
    if [[ "$(uname)" == "Linux" ]]; then
        if ! find --version 2>/dev/null | grep -q "GNU"; then
            log_warn "建议使用GNU版本的find命令以获得最佳性能"
        fi
        if ! grep --version 2>/dev/null | grep -q "GNU"; then
            log_warn "建议使用GNU版本的grep命令以获得最佳性能"
        fi
    fi
    
    log_debug "系统依赖检查完成"
}

# 验证文件系统权限
check_filesystem_permissions() {
    local search_dir="$1"
    
    if [[ ! -e "$search_dir" ]]; then
        handle_error 3 "目录不存在" "$search_dir"
        return 1
    fi
    
    if [[ ! -d "$search_dir" ]]; then
        handle_error 3 "路径不是目录" "$search_dir"
        return 1
    fi
    
    if [[ ! -r "$search_dir" ]]; then
        handle_error 2 "没有读取权限" "$search_dir"
        return 1
    fi
    
    if [[ ! -x "$search_dir" ]]; then
        handle_error 2 "没有执行权限" "$search_dir"
        return 1
    fi
    
    log_debug "文件系统权限检查完成: $search_dir"
    return 0
}

# 资源监控函数
monitor_resources() {
    local max_memory_mb=1024  # 1GB
    local current_memory
    
    # 获取当前进程内存使用 (KB)
    if command -v ps >/dev/null 2>&1; then
        current_memory=$(ps -o rss= -p $$)
        current_memory=$((current_memory / 1024))  # 转换为MB
        
        if [[ $current_memory -gt $max_memory_mb ]]; then
            log_warn "内存使用超出限制: ${current_memory}MB > ${max_memory_mb}MB"
            return 1
        fi
        
        log_debug "当前内存使用: ${current_memory}MB"
    fi
    
    return 0
}

# 搜索超时处理
search_with_timeout() {
    local timeout_seconds=300  # 5分钟超时
    local search_cmd="$1"
    local timeout_cmd
    
    # 检查是否有timeout命令
    if command -v timeout >/dev/null 2>&1; then
        timeout_cmd="timeout ${timeout_seconds}s"
    elif command -v gtimeout >/dev/null 2>&1; then  # macOS
        timeout_cmd="gtimeout ${timeout_seconds}s"
    else
        log_debug "未找到timeout命令，将不设置搜索超时"
        eval "$search_cmd"
        return $?
    fi
    
    log_debug "使用超时命令: $timeout_cmd"
    eval "$timeout_cmd $search_cmd"
    local exit_code=$?
    
    if [[ $exit_code -eq 124 ]]; then
        handle_error 5 "搜索超时 (${timeout_seconds}秒)"
        return 124
    fi
    
    return $exit_code
}

# 设置信号处理
trap handle_interrupt SIGINT SIGTERM
trap cleanup EXIT

# 优化的并行搜索执行
execute_parallel_search() {
    local find_cmd="$1"
    local grep_cmd="$2"
    
    log_debug "开始并行搜索，作业数: $PARALLEL_JOBS"
    
    # 创建命名管道用于进程间通信
    local fifo="${TEMP_DIR}/search_fifo"
    mkfifo "$fifo" || {
        log_error "无法创建命名管道: $fifo"
        return 1
    }
    
    # 启动文件查找进程
    eval "$find_cmd" 2>"${LOG_FILE}" | while IFS= read -r file; do
        echo "$file"
    done > "$fifo" &
    local find_pid=$!
    CHILD_PIDS+=("$find_pid")
    
    # 并行处理文件
    xargs -0 -P "$PARALLEL_JOBS" -I {} sh -c "
        if [[ -f '{}' && -r '{}' ]]; then
            $grep_cmd '{}' 2>/dev/null || true
        fi
    " < <(tr '\n' '\0' < "$fifo") > "$RESULTS_FILE" 2>"${LOG_FILE}" &
    local xargs_pid=$!
    CHILD_PIDS+=("$xargs_pid")
    
    # 等待所有进程完成
    wait "$find_pid" 2>/dev/null
    local find_exit_code=$?
    
    wait "$xargs_pid" 2>/dev/null  
    local xargs_exit_code=$?
    
    # 清理命名管道
    rm -f "$fifo"
    
    # 检查退出代码
    if [[ $find_exit_code -ne 0 ]]; then
        log_warn "文件查找进程异常退出，代码: $find_exit_code"
    fi
    
    if [[ $xargs_exit_code -ne 0 ]]; then
        log_warn "并行搜索进程异常退出，代码: $xargs_exit_code"
    fi
    
    return 0
}

# 优化的串行搜索执行
execute_serial_search() {
    local find_cmd="$1"
    local grep_cmd="$2"
    
    log_debug "开始串行搜索"
    
    # 使用find -exec进行串行搜索
    eval "$find_cmd -exec $grep_cmd {} +" > "$RESULTS_FILE" 2>"${LOG_FILE}"
    return $?
}

# 智能搜索策略选择
select_search_strategy() {
    local estimated_files
    estimated_files=$(eval "$(build_find_command) -print | wc -l" 2>/dev/null || echo "0")
    
    log_debug "预估文件数量: $estimated_files"
    
    # 根据文件数量选择策略
    if [[ $estimated_files -gt 100 && $PARALLEL_JOBS -gt 1 ]]; then
        echo "parallel"
    else
        echo "serial"
    fi
}

# 缓存机制
CACHE_DIR="${HOME}/.cache/${SCRIPT_NAME}"
CACHE_EXPIRY_HOURS=24

# 初始化缓存
init_cache() {
    if [[ ! -d "$CACHE_DIR" ]]; then
        mkdir -p "$CACHE_DIR" 2>/dev/null || {
            log_debug "无法创建缓存目录: $CACHE_DIR"
            return 1
        }
    fi
    
    # 清理过期缓存
    find "$CACHE_DIR" -type f -mtime +1 -delete 2>/dev/null || true
    
    log_debug "缓存目录初始化完成: $CACHE_DIR"
}

# 生成缓存键
generate_cache_key() {
    local pattern="$1"
    local directory="$2"
    local options="$3"
    
    echo -n "${pattern}_${directory}_${options}" | sha256sum 2>/dev/null | cut -d' ' -f1 || \
        echo -n "${pattern}_${directory}_${options}" | md5sum 2>/dev/null | cut -d' ' -f1 || \
        echo "$(date +%s)_$$"
}

# 检查缓存
check_cache() {
    local cache_key="$1"
    local cache_file="${CACHE_DIR}/${cache_key}"
    
    if [[ -f "$cache_file" ]]; then
        local cache_age
        cache_age=$(( $(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0) ))
        local max_age=$((CACHE_EXPIRY_HOURS * 3600))
        
        if [[ $cache_age -lt $max_age ]]; then
            log_debug "使用缓存结果: $cache_file (年龄: ${cache_age}秒)"
            cp "$cache_file" "$RESULTS_FILE"
            return 0
        else
            log_debug "缓存已过期，删除: $cache_file"
            rm -f "$cache_file"
        fi
    fi
    
    return 1
}

# 保存到缓存
save_to_cache() {
    local cache_key="$1"
    local cache_file="${CACHE_DIR}/${cache_key}"
    
    if [[ -f "$RESULTS_FILE" ]]; then
        cp "$RESULTS_FILE" "$cache_file" 2>/dev/null && \
            log_debug "结果已保存到缓存: $cache_file"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
${WHITE}用法: $0 [选项] -p <搜索模式>${NC}

${YELLOW}描述:${NC}
    功能强大的文本内容搜索工具，支持普通文本和正则表达式搜索

${YELLOW}必需参数:${NC}
    ${GREEN}-p, --pattern${NC} <模式>    搜索模式（文本或正则表达式）

${YELLOW}可选参数:${NC}
    ${GREEN}-d, --directory${NC} <路径>  搜索目录（默认: 当前目录）
    ${GREEN}-r, --regex${NC}            启用正则表达式模式
    ${GREEN}-t, --type${NC} <类型>      文件类型过滤（如: txt,log,py）
    ${GREEN}-e, --exclude${NC} <目录>   排除目录（如: .git,node_modules）
    ${GREEN}-o, --output${NC} <格式>    输出格式（simple/detail/json）
    ${GREEN}-n, --line-number${NC}      显示行号
    ${GREEN}-c, --count${NC}            只显示匹配计数
    ${GREEN}-l, --files-only${NC}       只显示文件名
    ${GREEN}-v, --verbose${NC}          详细输出模式
    ${GREEN}--no-color${NC}             禁用彩色输出
    ${GREEN}--max-depth${NC} <深度>     最大搜索深度（默认: 10）
    ${GREEN}--max-size${NC} <大小>      最大文件大小（默认: 10M）
    ${GREEN}-j, --jobs${NC} <数量>      并行作业数（默认: CPU核心数）
    ${GREEN}-h, --help${NC}             显示此帮助信息
    ${GREEN}--version${NC}              显示版本信息

${YELLOW}使用示例:${NC}
    ${CYAN}# 基本文本搜索${NC}
    $0 -p "function main"

    ${CYAN}# 正则表达式搜索${NC}
    $0 -p "^class\\s+\\w+" -r

    ${CYAN}# 指定目录和文件类型${NC}
    $0 -p "TODO" -d /project/src -t "py,js,java"

    ${CYAN}# 排除目录，显示详细信息${NC}
    $0 -p "error" -e ".git,node_modules" -o detail -n

    ${CYAN}# JSON格式输出${NC}
    $0 -p "import" -o json

EOF
}

# 显示版本信息
show_version() {
    echo "${SCRIPT_NAME} version ${SCRIPT_VERSION}"
}

# 验证参数
validate_arguments() {
    if [[ -z "$SEARCH_PATTERN" ]]; then
        log_error "搜索模式不能为空"
        show_help
        exit 1
    fi

    if [[ ! -d "$SEARCH_DIRECTORY" ]]; then
        log_error "搜索目录不存在或不可访问: $SEARCH_DIRECTORY"
        exit 3
    fi

    if [[ ! -r "$SEARCH_DIRECTORY" ]]; then
        log_error "没有读取搜索目录的权限: $SEARCH_DIRECTORY"
        exit 2
    fi

    if [[ "$OUTPUT_FORMAT" != "simple" && "$OUTPUT_FORMAT" != "detail" && "$OUTPUT_FORMAT" != "json" ]]; then
        log_error "无效的输出格式: $OUTPUT_FORMAT (支持: simple, detail, json)"
        exit 1
    fi

    if ! [[ "$MAX_DEPTH" =~ ^[0-9]+$ ]] || [[ "$MAX_DEPTH" -lt 1 ]]; then
        log_error "无效的最大深度值: $MAX_DEPTH"
        exit 1
    fi

    if ! [[ "$PARALLEL_JOBS" =~ ^[0-9]+$ ]] || [[ "$PARALLEL_JOBS" -lt 1 ]]; then
        log_error "无效的并行作业数: $PARALLEL_JOBS"
        exit 1
    fi
}

# 解析文件类型参数
parse_file_types() {
    if [[ -n "$FILE_TYPES" ]]; then
        # 转换逗号分隔的扩展名为find命令的-name参数
        local types_array
        IFS=',' read -ra types_array <<< "$FILE_TYPES"
        local find_patterns=()
        
        for type in "${types_array[@]}"; do
            type=$(echo "$type" | tr '[:upper:]' '[:lower:]' | sed 's/^\.*//')
            find_patterns+=("-name" "*.${type}")
        done
        
        # 使用-o (OR) 连接多个模式
        local find_type_args=""
        for ((i=0; i<${#find_patterns[@]}; i+=2)); do
            if [[ $i -gt 0 ]]; then
                find_type_args+=" -o "
            fi
            find_type_args+="${find_patterns[i]} ${find_patterns[i+1]}"
        done
        
        echo "\\( $find_type_args \\)"
    fi
}

# 解析排除目录参数
parse_exclude_dirs() {
    local excludes="$DEFAULT_EXCLUDES"
    if [[ -n "$EXCLUDE_DIRS" ]]; then
        excludes+=",${EXCLUDE_DIRS}"
    fi
    
    local exclude_array
    IFS=',' read -ra exclude_array <<< "$excludes"
    local find_excludes=()
    
    for exclude in "${exclude_array[@]}"; do
        exclude=$(echo "$exclude" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [[ -n "$exclude" ]]; then
            find_excludes+=("-path" "*/${exclude}" "-prune" "-o")
        fi
    done
    
    if [[ ${#find_excludes[@]} -gt 0 ]]; then
        printf '%s ' "${find_excludes[@]}"
    fi
}

# 主要脚本逻辑从这里开始...
main() {
    # 创建临时目录
    mkdir -p "$TEMP_DIR"
    
    # 加载配置文件
    load_config
    
    # 解析命令行参数
    parse_arguments "$@"
    
    # 验证参数
    validate_arguments
    
    # 记录搜索开始时间
    SEARCH_START_TIME=$(date +%s.%N)
    
    log_info "开始搜索: 模式='$SEARCH_PATTERN', 目录='$SEARCH_DIRECTORY'"
    
    # 执行搜索
    execute_search
    
    # 处理结果
    process_results
    
    # 显示统计信息
    show_statistics
}

# 执行搜索函数（重构版）
execute_search() {
    log_info "正在构建搜索命令..."
    
    # 检查系统依赖
    check_dependencies
    
    # 验证搜索目录权限
    if ! check_filesystem_permissions "$SEARCH_DIRECTORY"; then
        return 1
    fi
    
    # 初始化缓存
    init_cache
    
    # 生成缓存键
    local cache_options="${USE_REGEX}_${FILE_TYPES}_${EXCLUDE_DIRS}_${MAX_DEPTH}"
    local cache_key
    cache_key=$(generate_cache_key "$SEARCH_PATTERN" "$SEARCH_DIRECTORY" "$cache_options")
    
    # 检查缓存
    if check_cache "$cache_key"; then
        log_info "使用缓存结果"
    else
        # 构建搜索命令
        local find_cmd
        find_cmd=$(build_find_command)
        
        local grep_cmd
        grep_cmd=$(build_grep_command)
        
        log_debug "Find命令: $find_cmd"
        log_debug "Grep命令: $grep_cmd"
        
        # 显示搜索进度
        if [[ "$VERBOSE" == true ]]; then
            echo -e "${CYAN}正在搜索...${NC}"
        fi
        
        # 选择搜索策略
        local strategy
        strategy=$(select_search_strategy)
        log_debug "选择搜索策略: $strategy"
        
        # 执行搜索
        local exit_code=0
        case "$strategy" in
            "parallel")
                if ! execute_parallel_search "$find_cmd" "$grep_cmd"; then
                    log_warn "并行搜索失败，回退到串行搜索"
                    execute_serial_search "$find_cmd" "$grep_cmd"
                    exit_code=$?
                fi
                ;;
            "serial")
                execute_serial_search "$find_cmd" "$grep_cmd"
                exit_code=$?
                ;;
        esac
        
        # 监控资源使用
        monitor_resources
        
        # 保存到缓存
        save_to_cache "$cache_key"
        
        log_debug "搜索完成，退出码: $exit_code"
    fi
    
    # 统计搜索的文件数
    TOTAL_FILES_SEARCHED=$(eval "$(build_find_command)" 2>/dev/null | wc -l)
    
    # 统计匹配数
    if [[ "$COUNT_ONLY" == true ]]; then
        TOTAL_MATCHES=$(awk '{sum += $1} END {print sum+0}' "$RESULTS_FILE")
    elif [[ "$FILES_ONLY" == true ]]; then
        TOTAL_MATCHES=$(wc -l < "$RESULTS_FILE")
    else
        TOTAL_MATCHES=$(wc -l < "$RESULTS_FILE")
    fi
    
    log_debug "搜索文件数: $TOTAL_FILES_SEARCHED, 匹配数: $TOTAL_MATCHES"
    
    return 0
}

# 解析命令行参数函数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--pattern)
                SEARCH_PATTERN="$2"
                shift 2
                ;;
            -d|--directory)
                SEARCH_DIRECTORY="$2"
                shift 2
                ;;
            -r|--regex)
                USE_REGEX=true
                shift
                ;;
            -t|--type)
                FILE_TYPES="$2"
                shift 2
                ;;
            -e|--exclude)
                EXCLUDE_DIRS="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -n|--line-number)
                SHOW_LINE_NUMBERS=true
                shift
                ;;
            -c|--count)
                COUNT_ONLY=true
                shift
                ;;
            -l|--files-only)
                FILES_ONLY=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --no-color)
                COLORED_OUTPUT=false
                shift
                ;;
            --max-depth)
                MAX_DEPTH="$2"
                shift 2
                ;;
            --max-size)
                MAX_FILE_SIZE="$2"
                shift 2
                ;;
            -j|--jobs)
                PARALLEL_JOBS="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                show_version
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                log_error "意外的参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 处理颜色输出设置
    if [[ "$COLORED_OUTPUT" == false ]]; then
        # 重新定义颜色变量（非 readonly）
        unset RED GREEN YELLOW BLUE PURPLE CYAN WHITE NC
        RED=''
        GREEN=''
        YELLOW=''
        BLUE=''
        PURPLE=''
        CYAN=''
        WHITE=''
        NC=''
    fi

    # 处理并行作业数自动检测
    if [[ "$PARALLEL_JOBS" == "0" ]]; then
        PARALLEL_JOBS=$(nproc 2>/dev/null || echo "4")
    fi

    log_debug "解析的参数: 模式='$SEARCH_PATTERN', 目录='$SEARCH_DIRECTORY', 正则=$USE_REGEX"
    log_debug "文件类型='$FILE_TYPES', 排除='$EXCLUDE_DIRS', 输出格式='$OUTPUT_FORMAT'"
    log_debug "并行作业数=$PARALLEL_JOBS, 最大深度=$MAX_DEPTH"
}

# 构建find命令
build_find_command() {
    local find_cmd="find '$SEARCH_DIRECTORY'"
    
    # 添加最大深度限制
    find_cmd+=" -maxdepth $MAX_DEPTH"
    
    # 添加排除目录
    local exclude_args
    exclude_args=$(parse_exclude_dirs)
    if [[ -n "$exclude_args" ]]; then
        find_cmd+=" $exclude_args"
    fi
    
    # 添加文件类型过滤
    local type_args
    type_args=$(parse_file_types)
    if [[ -n "$type_args" ]]; then
        find_cmd+=" $type_args"
    else
        find_cmd+=" -type f"
    fi
    
    # 添加文件大小限制
    find_cmd+=" -size -$MAX_FILE_SIZE"
    
    # 添加可读文件过滤
    find_cmd+=" -readable"
    
    echo "$find_cmd"
}

# 构建grep命令
build_grep_command() {
    local grep_cmd="grep"
    
    # 设置搜索模式
    if [[ "$USE_REGEX" == true ]]; then
        grep_cmd+=" -E"  # 扩展正则表达式
    else
        grep_cmd+=" -F"  # 固定字符串搜索
    fi
    
    # 添加其他选项
    if [[ "$SHOW_LINE_NUMBERS" == true ]]; then
        grep_cmd+=" -n"
    fi
    
    if [[ "$COUNT_ONLY" == true ]]; then
        grep_cmd+=" -c"
    fi
    
    if [[ "$FILES_ONLY" == true ]]; then
        grep_cmd+=" -l"
    fi
    
    # 添加颜色输出（仅在终端输出时）
    if [[ "$COLORED_OUTPUT" == true && -t 1 ]]; then
        grep_cmd+=" --color=always"
    fi
    
    # 添加搜索模式
    grep_cmd+=" -- '$SEARCH_PATTERN'"
    
    echo "$grep_cmd"
}

# 优化的并行搜索执行
execute_parallel_search() {
    local find_cmd="$1"
    local grep_cmd="$2"
    
    log_debug "开始并行搜索，作业数: $PARALLEL_JOBS"
    
    # 创建命名管道用于进程间通信
    local fifo="${TEMP_DIR}/search_fifo"
    mkfifo "$fifo" || {
        log_error "无法创建命名管道: $fifo"
        return 1
    }
    
    # 启动文件查找进程
    eval "$find_cmd" 2>"${LOG_FILE}" | while IFS= read -r file; do
        echo "$file"
    done > "$fifo" &
    local find_pid=$!
    CHILD_PIDS+=("$find_pid")
    
    # 并行处理文件
    xargs -0 -P "$PARALLEL_JOBS" -I {} sh -c "
        if [[ -f '{}' && -r '{}' ]]; then
            $grep_cmd '{}' 2>/dev/null || true
        fi
    " < <(tr '\n' '\0' < "$fifo") > "$RESULTS_FILE" 2>"${LOG_FILE}" &
    local xargs_pid=$!
    CHILD_PIDS+=("$xargs_pid")
    
    # 等待所有进程完成
    wait "$find_pid" 2>/dev/null
    local find_exit_code=$?
    
    wait "$xargs_pid" 2>/dev/null  
    local xargs_exit_code=$?
    
    # 清理命名管道
    rm -f "$fifo"
    
    # 检查退出代码
    if [[ $find_exit_code -ne 0 ]]; then
        log_warn "文件查找进程异常退出，代码: $find_exit_code"
    fi
    
    if [[ $xargs_exit_code -ne 0 ]]; then
        log_warn "并行搜索进程异常退出，代码: $xargs_exit_code"
    fi
    
    return 0
}

# 优化的串行搜索执行
execute_serial_search() {
    local find_cmd="$1"
    local grep_cmd="$2"
    
    log_debug "开始串行搜索"
    
    # 使用find -exec进行串行搜索
    eval "$find_cmd -exec $grep_cmd {} +" > "$RESULTS_FILE" 2>"${LOG_FILE}"
    return $?
}

# 智能搜索策略选择
select_search_strategy() {
    local estimated_files
    estimated_files=$(eval "$(build_find_command) -print | wc -l" 2>/dev/null || echo "0")
    
    log_debug "预估文件数量: $estimated_files"
    
    # 根据文件数量选择策略
    if [[ $estimated_files -gt 100 && $PARALLEL_JOBS -gt 1 ]]; then
        echo "parallel"
    else
        echo "serial"
    fi
}

# 缓存机制
CACHE_DIR="${HOME}/.cache/${SCRIPT_NAME}"
CACHE_EXPIRY_HOURS=24

# 初始化缓存
init_cache() {
    if [[ ! -d "$CACHE_DIR" ]]; then
        mkdir -p "$CACHE_DIR" 2>/dev/null || {
            log_debug "无法创建缓存目录: $CACHE_DIR"
            return 1
        }
    fi
    
    # 清理过期缓存
    find "$CACHE_DIR" -type f -mtime +1 -delete 2>/dev/null || true
    
    log_debug "缓存目录初始化完成: $CACHE_DIR"
}

# 生成缓存键
generate_cache_key() {
    local pattern="$1"
    local directory="$2"
    local options="$3"
    
    echo -n "${pattern}_${directory}_${options}" | sha256sum 2>/dev/null | cut -d' ' -f1 || \
        echo -n "${pattern}_${directory}_${options}" | md5sum 2>/dev/null | cut -d' ' -f1 || \
        echo "$(date +%s)_$$"
}

# 检查缓存
check_cache() {
    local cache_key="$1"
    local cache_file="${CACHE_DIR}/${cache_key}"
    
    if [[ -f "$cache_file" ]]; then
        local cache_age
        cache_age=$(( $(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0) ))
        local max_age=$((CACHE_EXPIRY_HOURS * 3600))
        
        if [[ $cache_age -lt $max_age ]]; then
            log_debug "使用缓存结果: $cache_file (年龄: ${cache_age}秒)"
            cp "$cache_file" "$RESULTS_FILE"
            return 0
        else
            log_debug "缓存已过期，删除: $cache_file"
            rm -f "$cache_file"
        fi
    fi
    
    return 1
}

# 保存到缓存
save_to_cache() {
    local cache_key="$1"
    local cache_file="${CACHE_DIR}/${cache_key}"
    
    if [[ -f "$RESULTS_FILE" ]]; then
        cp "$RESULTS_FILE" "$cache_file" 2>/dev/null && \
            log_debug "结果已保存到缓存: $cache_file"
    fi
}

# 处理结果函数
process_results() {
    if [[ ! -f "$RESULTS_FILE" ]] || [[ ! -s "$RESULTS_FILE" ]]; then
        if [[ "$OUTPUT_FORMAT" == "json" ]]; then
            output_json_empty
        else
            echo -e "${YELLOW}没有找到匹配的结果${NC}"
        fi
        return
    fi
    
    case "$OUTPUT_FORMAT" in
        "simple")
            output_simple_format
            ;;
        "detail")
            output_detail_format
            ;;
        "json")
            output_json_format
            ;;
        *)
            log_error "未知的输出格式: $OUTPUT_FORMAT"
            output_simple_format
            ;;
    esac
}

# 简单格式输出
output_simple_format() {
    if [[ "$COLORED_OUTPUT" == true ]]; then
        # 高亮显示文件名和匹配内容
        while IFS= read -r line; do
            if [[ "$line" =~ ^([^:]+):(.*)$ ]]; then
                local file="${BASH_REMATCH[1]}"
                local content="${BASH_REMATCH[2]}"
                echo -e "${BLUE}${file}${NC}:${content}"
            else
                echo "$line"
            fi
        done < "$RESULTS_FILE"
    else
        cat "$RESULTS_FILE"
    fi
}

# 详细格式输出
output_detail_format() {
    local current_file=""
    local file_matches=0
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^([^:]+):(.*)$ ]]; then
            local file="${BASH_REMATCH[1]}"
            local content="${BASH_REMATCH[2]}"
            
            if [[ "$file" != "$current_file" ]]; then
                if [[ -n "$current_file" ]]; then
                    echo -e "${GREEN}匹配数: $file_matches${NC}"
                    echo
                fi
                
                current_file="$file"
                file_matches=0
                
                echo -e "${WHITE}文件: $file${NC}"
                if [[ -f "$file" ]]; then
                    local file_size
                    file_size=$(du -h "$file" 2>/dev/null | cut -f1)
                    local file_modified
                    file_modified=$(stat -c '%y' "$file" 2>/dev/null | cut -d. -f1)
                    echo -e "${CYAN}大小: $file_size${NC}"
                    echo -e "${CYAN}修改时间: $file_modified${NC}"
                fi
                echo "---"
            fi
            
            ((file_matches++))
            echo "$content"
        fi
    done < "$RESULTS_FILE"
    
    if [[ -n "$current_file" ]]; then
        echo -e "${GREEN}匹配数: $file_matches${NC}"
    fi
}

# JSON格式输出
output_json_format() {
    local search_end_time
    search_end_time=$(date +%s.%N)
    local search_duration
    search_duration=$(echo "$search_end_time - $SEARCH_START_TIME" | bc -l 2>/dev/null || echo "0")
    
    echo "{"
    echo "  \"search_summary\": {"
    echo "    \"pattern\": \"$(echo "$SEARCH_PATTERN" | sed 's/"/\\"/g')\","
    echo "    \"directory\": \"$SEARCH_DIRECTORY\","
    echo "    \"regex_mode\": $USE_REGEX,"
    echo "    \"total_files\": $TOTAL_FILES_SEARCHED,"
    echo "    \"total_matches\": $TOTAL_MATCHES,"
    echo "    \"search_time\": \"${search_duration}s\""
    echo "  },"
    echo "  \"results\": ["
    
    local current_file=""
    local first_file=true
    local first_match=true
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^([^:]+):([0-9]+:)?(.*)$ ]]; then
            local file="${BASH_REMATCH[1]}"
            local line_num="${BASH_REMATCH[2]}"
            local content="${BASH_REMATCH[3]}"
            
            line_num=${line_num%:}  # 移除尾部的冒号
            
            if [[ "$file" != "$current_file" ]]; then
                if [[ -n "$current_file" ]]; then
                    echo
                    echo "      ]"
                    echo "    }"
                fi
                
                if [[ "$first_file" == false ]]; then
                    echo ","
                fi
                
                current_file="$file"
                first_file=false
                first_match=true
                
                echo "    {"
                echo "      \"file\": \"$(echo "$file" | sed 's/"/\\"/g')\","
                echo "      \"matches\": ["
            fi
            
            if [[ "$first_match" == false ]]; then
                echo ","
            fi
            first_match=false
            
            echo -n "        {"
            if [[ -n "$line_num" ]]; then
                echo -n "\"line\": $line_num, "
            fi
            echo "\"content\": \"$(echo "$content" | sed 's/"/\\"/g; s/\\/\\\\/g')\"}"
        fi
    done < "$RESULTS_FILE"
    
    if [[ -n "$current_file" ]]; then
        echo
        echo "      ]"
        echo "    }"
    fi
    
    echo
    echo "  ]"
    echo "}"
}

# JSON空结果输出
output_json_empty() {
    local search_end_time
    search_end_time=$(date +%s.%N)
    local search_duration
    search_duration=$(echo "$search_end_time - $SEARCH_START_TIME" | bc -l 2>/dev/null || echo "0")
    
    echo "{"
    echo "  \"search_summary\": {"
    echo "    \"pattern\": \"$(echo "$SEARCH_PATTERN" | sed 's/"/\\"/g')\","
    echo "    \"directory\": \"$SEARCH_DIRECTORY\","
    echo "    \"regex_mode\": $USE_REGEX,"
    echo "    \"total_files\": $TOTAL_FILES_SEARCHED,"
    echo "    \"total_matches\": 0,"
    echo "    \"search_time\": \"${search_duration}s\""
    echo "  },"
    echo "  \"results\": []"
    echo "}"
}

# 显示统计信息函数
show_statistics() {
    # 如果是JSON格式输出，统计信息已经包含在JSON中
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        return
    fi
    
    # 如果只显示计数或只显示文件名，不需要额外统计
    if [[ "$COUNT_ONLY" == true ]] || [[ "$FILES_ONLY" == true ]]; then
        return
    fi
    
    local search_end_time
    search_end_time=$(date +%s.%N)
    local search_duration
    search_duration=$(echo "$search_end_time - $SEARCH_START_TIME" | bc -l 2>/dev/null || echo "0")
    
    echo
    echo -e "${WHITE}=== 搜索统计 ===${NC}"
    echo -e "${GREEN}搜索模式:${NC} $SEARCH_PATTERN"
    echo -e "${GREEN}搜索目录:${NC} $SEARCH_DIRECTORY"
    echo -e "${GREEN}搜索模式:${NC} $(if [[ "$USE_REGEX" == true ]]; then echo "正则表达式"; else echo "文本匹配"; fi)"
    echo -e "${GREEN}搜索文件数:${NC} $TOTAL_FILES_SEARCHED"
    echo -e "${GREEN}匹配结果数:${NC} $TOTAL_MATCHES"
    echo -e "${GREEN}搜索耗时:${NC} ${search_duration}秒"
    
    if [[ -n "$FILE_TYPES" ]]; then
        echo -e "${GREEN}文件类型:${NC} $FILE_TYPES"
    fi
    
    if [[ -n "$EXCLUDE_DIRS" ]]; then
        echo -e "${GREEN}排除目录:${NC} $EXCLUDE_DIRS"
    fi
    
    echo -e "${GREEN}并行作业数:${NC} $PARALLEL_JOBS"
    echo -e "${WHITE}===============${NC}"
}

# 如果脚本被直接执行，调用main函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

# 用户体验功能 - 进度显示和彩色输出

# 进度显示函数
show_progress() {
    local current="$1"
    local total="$2"
    local message="$3"
    
    if [[ "$VERBOSE" == true && -t 2 ]]; then
        local percentage=0
        if [[ $total -gt 0 ]]; then
            percentage=$(( (current * 100) / total ))
        fi
        
        local bar_length=30
        local filled_length=$(( (current * bar_length) / total ))
        local bar=""
        
        for ((i=0; i<filled_length; i++)); do
            bar+="█"
        done
        
        for ((i=filled_length; i<bar_length; i++)); do
            bar+="░"
        done
        
        printf "\r${CYAN}[%s] %d%% (%d/%d) %s${NC}" "$bar" "$percentage" "$current" "$total" "$message" >&2
        
        if [[ $current -eq $total ]]; then
            echo >&2  # 新行
        fi
    fi
}

# 动态状态显示
show_spinner() {
    local pid=$1
    local message="$2"
    local delay=0.1
    local spinstr='|/-\'
    
    if [[ "$VERBOSE" == true && -t 2 ]]; then
        while [[ -d "/proc/$pid" ]]; do
            local temp=${spinstr#?}
            printf "\r${CYAN}[%c] %s${NC}" "$spinstr" "$message" >&2
            local spinstr=$temp${spinstr%"$temp"}
            sleep $delay
        done
        printf "\r${GREEN}[✓] %s ${NC}\n" "$message" >&2
    fi
}

# 增强的彩色输出
highlight_matches() {
    local line="$1"
    local pattern="$2"
    local use_regex="$3"
    
    if [[ "$COLORED_OUTPUT" != true ]]; then
        echo "$line"
        return
    fi
    
    # 使用sed进行匹配高亮
    if [[ "$use_regex" == true ]]; then
        echo "$line" | sed -E "s/($pattern)/${RED}\\1${NC}/g"
    else
        # 转义特殊字符用于字面量匹配
        local escaped_pattern
        escaped_pattern=$(echo "$pattern" | sed 's/[[\.^$(){}*+?|]/\\&/g')
        echo "$line" | sed "s/$escaped_pattern/${RED}&${NC}/g"
    fi
}

# 统计信息强化显示
show_enhanced_statistics() {
    local search_end_time
    search_end_time=$(date +%s.%N)
    local search_duration
    search_duration=$(echo "$search_end_time - $SEARCH_START_TIME" | bc -l 2>/dev/null || echo "0")
    
    # 计算搜索速度
    local files_per_second=0
    if [[ $(echo "$search_duration > 0" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        files_per_second=$(echo "scale=2; $TOTAL_FILES_SEARCHED / $search_duration" | bc -l 2>/dev/null || echo "0")
    fi
    
    echo
    echo -e "${WHITE}┌$(printf '%*s' 50 | tr ' ' '─')┐${NC}"
    echo -e "${WHITE}│$(printf '%*s' 18 ' ')搜索统计$(printf '%*s' 18 ' ')│${NC}"
    echo -e "${WHITE}├$(printf '%*s' 50 | tr ' ' '─')┤${NC}"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "搜索模式" "$SEARCH_PATTERN"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "搜索目录" "$SEARCH_DIRECTORY"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "模式类型" "$(if [[ "$USE_REGEX" == true ]]; then echo "正则表达式"; else echo "文本匹配"; fi)"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "搜索文件数" "$TOTAL_FILES_SEARCHED"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "匹配结果数" "$TOTAL_MATCHES"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "搜索耗时" "${search_duration}秒"
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "搜索速度" "${files_per_second}文件/秒"
    
    if [[ -n "$FILE_TYPES" ]]; then
        printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "文件类型" "$FILE_TYPES"
    fi
    
    if [[ -n "$EXCLUDE_DIRS" ]]; then
        printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "排除目录" "$EXCLUDE_DIRS"
    fi
    
    printf "${WHITE}│${NC} ${GREEN}%-20s${NC} ${WHITE}:${NC} %-25s ${WHITE}│${NC}\n" "并行作业数" "$PARALLEL_JOBS"
    echo -e "${WHITE}└$(printf '%*s' 50 | tr ' ' '─')┘${NC}"
}