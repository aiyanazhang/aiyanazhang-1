#!/bin/bash

# =============================================================================
# 项目内容和修改时间列表脚本
# 
# 功能：递归列出项目中的所有文件和目录，并显示其修改时间信息
# 作者：AI Assistant
# 版本：1.0.0
# =============================================================================

set -uo pipefail

# =============================================================================
# 全局变量和默认配置
# =============================================================================

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

# 默认配置
DEFAULT_FORMAT="simple"
DEFAULT_SORT="name"
DEFAULT_TIME_FORMAT="%Y-%m-%d %H:%M:%S"
DEFAULT_DEPTH=""
DEFAULT_EXCLUDE_PATTERNS=".git node_modules __pycache__ .DS_Store *.pyc *.pyo *.pyd .pytest_cache .coverage .mypy_cache"

# 运行时配置
SHOW_ALL=false
OUTPUT_FORMAT="$DEFAULT_FORMAT"
SORT_BY="$DEFAULT_SORT"
REVERSE_SORT=false
MAX_DEPTH=""
EXCLUDE_PATTERNS="$DEFAULT_EXCLUDE_PATTERNS"
INCLUDE_PATTERNS=""
TIME_FORMAT="$DEFAULT_TIME_FORMAT"
SHOW_HELP=false
TARGET_DIR="."
FOLLOW_SYMLINKS=false
SHOW_HIDDEN=false
VERBOSE=false

# 输出控制
declare -a FILE_LIST=()
declare -a DIR_LIST=()
TOTAL_FILES=0
TOTAL_DIRS=0
SCAN_START_TIME=""

# =============================================================================
# 工具函数
# =============================================================================

# 显示帮助信息
show_help() {
    cat << EOF
$SCRIPT_NAME - 项目内容和修改时间列表工具 v$VERSION

用法: $SCRIPT_NAME [选项] [目录]

选项:
  -h, --help              显示此帮助信息
  -a, --all               包含隐藏文件和目录
  -f, --format FORMAT     输出格式 [simple|detailed|table|json|csv]
                          默认: $DEFAULT_FORMAT
  -s, --sort SORT         排序方式 [name|size|mtime|atime|extension|depth]
                          默认: $DEFAULT_SORT
  -r, --reverse           反向排序
  -d, --depth DEPTH       最大递归深度 (数字)
  -e, --exclude PATTERN   排除模式 (支持通配符)
  -i, --include PATTERN   包含模式 (支持通配符)
  -t, --time-format FMT   时间格式 (strftime格式)
                          默认: "$DEFAULT_TIME_FORMAT"
  -L, --follow-symlinks   跟随符号链接
  -v, --verbose           详细输出模式

输出格式说明:
  simple   - 简洁模式：文件路径和修改时间
  detailed - 详细模式：包含大小、权限、所有时间信息
  table    - 表格模式：对齐的列格式
  json     - JSON格式：结构化数据输出
  csv      - CSV格式：逗号分隔值

示例:
  $SCRIPT_NAME                          # 简单列出当前目录
  $SCRIPT_NAME -a -f detailed          # 详细格式，包含隐藏文件
  $SCRIPT_NAME -s mtime -r             # 按修改时间倒序排列
  $SCRIPT_NAME -d 3 /home/user/project # 最多递归3层深度
  $SCRIPT_NAME -f json > files.json    # 输出JSON格式到文件

EOF
}

# 日志函数
log_info() {
    if [[ "$VERBOSE" == true ]]; then
        echo "[INFO] $*" >&2
    fi
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_warning() {
    echo "[WARNING] $*" >&2
}

# 获取当前时间戳
get_timestamp() {
    date '+%Y-%m-%dT%H:%M:%SZ'
}

# 格式化文件大小
format_size() {
    local size=$1
    if [[ $size -eq 0 ]]; then
        echo "0B"
    elif [[ $size -lt 1024 ]]; then
        echo "${size}B"
    elif [[ $size -lt 1048576 ]]; then
        echo "$(( size / 1024 ))KB"
    elif [[ $size -lt 1073741824 ]]; then
        echo "$(( size / 1048576 ))MB"
    else
        echo "$(( size / 1073741824 ))GB"
    fi
}

# 格式化时间
format_time() {
    local timestamp=$1
    date -d "@$timestamp" +"$TIME_FORMAT" 2>/dev/null || echo "N/A"
}

# =============================================================================
# 配置管理
# =============================================================================

# 加载配置文件
load_config() {
    local config_files=(
        "./.list-project.conf"
        "$HOME/.list-project.conf"
        "/etc/list-project.conf"
    )
    
    for config_file in "${config_files[@]}"; do
        if [[ -f "$config_file" ]]; then
            log_info "加载配置文件: $config_file"
            # shellcheck source=/dev/null
            source "$config_file"
            break
        fi
    done
}

# 加载环境变量配置
load_env_config() {
    [[ -n "${LIST_PROJECT_FORMAT:-}" ]] && OUTPUT_FORMAT="$LIST_PROJECT_FORMAT"
    [[ -n "${LIST_PROJECT_EXCLUDE:-}" ]] && EXCLUDE_PATTERNS="$LIST_PROJECT_EXCLUDE"
    [[ -n "${LIST_PROJECT_TIME_FORMAT:-}" ]] && TIME_FORMAT="$LIST_PROJECT_TIME_FORMAT"
}

# =============================================================================
# 参数解析
# =============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                SHOW_HELP=true
                shift
                ;;
            -a|--all)
                SHOW_ALL=true
                SHOW_HIDDEN=true
                shift
                ;;
            -f|--format)
                if [[ -n "${2:-}" ]]; then
                    OUTPUT_FORMAT="$2"
                    shift 2
                else
                    log_error "选项 $1 需要一个参数"
                    exit 1
                fi
                ;;
            -s|--sort)
                if [[ -n "${2:-}" ]]; then
                    SORT_BY="$2"
                    shift 2
                else
                    log_error "选项 $1 需要一个参数"
                    exit 1
                fi
                ;;
            -r|--reverse)
                REVERSE_SORT=true
                shift
                ;;
            -d|--depth)
                if [[ -n "${2:-}" ]]; then
                    MAX_DEPTH="$2"
                    shift 2
                else
                    log_error "选项 $1 需要一个参数"
                    exit 1
                fi
                ;;
            -e|--exclude)
                if [[ -n "${2:-}" ]]; then
                    EXCLUDE_PATTERNS="$EXCLUDE_PATTERNS $2"
                    shift 2
                else
                    log_error "选项 $1 需要一个参数"
                    exit 1
                fi
                ;;
            -i|--include)
                if [[ -n "${2:-}" ]]; then
                    INCLUDE_PATTERNS="$INCLUDE_PATTERNS $2"
                    shift 2
                else
                    log_error "选项 $1 需要一个参数"
                    exit 1
                fi
                ;;
            -t|--time-format)
                if [[ -n "${2:-}" ]]; then
                    TIME_FORMAT="$2"
                    shift 2
                else
                    log_error "选项 $1 需要一个参数"
                    exit 1
                fi
                ;;
            -L|--follow-symlinks)
                FOLLOW_SYMLINKS=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -*)
                log_error "未知选项: $1"
                exit 1
                ;;
            *)
                TARGET_DIR="$1"
                shift
                ;;
        esac
    done
}

# 验证参数
validate_arguments() {
    # 验证输出格式
    case "$OUTPUT_FORMAT" in
        simple|detailed|table|json|csv)
            ;;
        *)
            log_error "无效的输出格式: $OUTPUT_FORMAT"
            log_error "支持的格式: simple, detailed, table, json, csv"
            exit 1
            ;;
    esac
    
    # 验证排序方式
    case "$SORT_BY" in
        name|size|mtime|atime|extension|depth)
            ;;
        *)
            log_error "无效的排序方式: $SORT_BY"
            log_error "支持的排序: name, size, mtime, atime, extension, depth"
            exit 1
            ;;
    esac
    
    # 验证目录
    if [[ ! -d "$TARGET_DIR" ]]; then
        log_error "目录不存在: $TARGET_DIR"
        exit 1
    fi
    
    # 验证深度
    if [[ -n "$MAX_DEPTH" ]] && ! [[ "$MAX_DEPTH" =~ ^[0-9]+$ ]]; then
        log_error "深度必须是数字: $MAX_DEPTH"
        exit 1
    fi
}

# =============================================================================
# 文件过滤和匹配
# =============================================================================

# 检查文件是否匹配排除模式
should_exclude() {
    local file_path="$1"
    local file_name
    file_name="$(basename "$file_path")"
    
    # 检查排除模式
    for pattern in $EXCLUDE_PATTERNS; do
        case "$file_name" in
            $pattern)
                return 0  # 应该排除
                ;;
        esac
        # 也检查完整路径
        case "$file_path" in
            */$pattern/* | */$pattern)
                return 0  # 应该排除
                ;;
        esac
    done
    
    return 1  # 不应该排除
}

# 检查文件是否匹配包含模式
should_include() {
    local file_path="$1"
    local file_name
    file_name="$(basename "$file_path")"
    
    # 如果没有包含模式，默认包含
    if [[ -z "$INCLUDE_PATTERNS" ]]; then
        return 0
    fi
    
    # 检查包含模式
    for pattern in $INCLUDE_PATTERNS; do
        case "$file_name" in
            $pattern)
                return 0  # 应该包含
                ;;
        esac
    done
    
    return 1  # 不应该包含
}

# 检查是否为隐藏文件
is_hidden() {
    local file_name
    file_name="$(basename "$1")"
    [[ "$file_name" == .* ]]
}

# =============================================================================
# 文件信息提取
# =============================================================================

# 获取文件信息
get_file_info() {
    local file_path="$1"
    local file_info
    
    if [[ ! -e "$file_path" ]]; then
        log_warning "文件不存在: $file_path"
        return 1
    fi
    
    # 使用stat获取文件信息
    if ! file_info=$(stat -c "%F|%s|%a|%Y|%X|%Z|%n" "$file_path" 2>/dev/null); then
        log_warning "无法获取文件信息: $file_path"
        return 1
    fi
    
    echo "$file_info"
}

# 解析文件信息
parse_file_info() {
    local info="$1"
    local file_type size permissions mtime atime ctime file_path
    
    IFS='|' read -r file_type size permissions mtime atime ctime file_path <<< "$info"
    
    echo "type:$file_type"
    echo "size:$size"
    echo "permissions:$permissions"
    echo "mtime:$mtime"
    echo "atime:$atime"
    echo "ctime:$ctime"
    echo "path:$file_path"
}

# =============================================================================
# 文件遍历
# =============================================================================

# 递归遍历目录
traverse_directory() {
    local dir="$1"
    local current_depth="${2:-0}"
    local visited_dirs="${3:-}"
    
    # 检查深度限制
    if [[ -n "$MAX_DEPTH" ]] && [[ $current_depth -gt $MAX_DEPTH ]]; then
        return 0
    fi
    
    # 获取绝对路径以检测循环
    local abs_dir
    abs_dir="$(cd "$dir" 2>/dev/null && pwd)" || {
        log_warning "无法访问目录: $dir"
        return 1
    }
    
    # 检测循环引用
    if [[ "$visited_dirs" == *"|$abs_dir|"* ]]; then
        log_warning "检测到循环引用，跳过: $dir"
        return 0
    fi
    
    visited_dirs="$visited_dirs|$abs_dir|"
    
    log_info "遍历目录: $dir (深度: $current_depth)"
    
    # 遍历当前目录中的文件和子目录
    while IFS= read -r -d '' file; do
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file" 2>/dev/null)" || rel_path="$file"
        
        # 检查是否为隐藏文件
        if is_hidden "$file" && [[ "$SHOW_HIDDEN" != true ]]; then
            continue
        fi
        
        # 检查排除模式
        if should_exclude "$rel_path"; then
            log_info "排除文件: $rel_path"
            continue
        fi
        
        # 检查包含模式
        if ! should_include "$rel_path"; then
            log_info "文件不匹配包含模式: $rel_path"
            continue
        fi
        
        # 处理符号链接
        if [[ -L "$file" ]]; then
            if [[ "$FOLLOW_SYMLINKS" != true ]]; then
                # 将符号链接作为文件处理
                process_file "$file" "$current_depth"
                continue
            else
                # 跟随符号链接
                local target
                target="$(readlink -f "$file" 2>/dev/null)" || {
                    log_warning "无法解析符号链接: $file"
                    continue
                }
                
                if [[ -d "$target" ]]; then
                    traverse_directory "$target" $((current_depth + 1)) "$visited_dirs"
                else
                    process_file "$target" "$current_depth"
                fi
                continue
            fi
        fi
        
        if [[ -d "$file" ]]; then
            # 处理目录
            process_directory "$file" "$current_depth"
            # 递归遍历子目录
            traverse_directory "$file" $((current_depth + 1)) "$visited_dirs"
        else
            # 处理文件
            process_file "$file" "$current_depth"
        fi
        
    done < <(find "$dir" -maxdepth 1 -mindepth 1 -print0 2>/dev/null | sort -z)
}

# 处理单个文件
process_file() {
    local file_path="$1"
    local depth="$2"
    
    local file_info
    if file_info=$(get_file_info "$file_path"); then
        FILE_LIST+=("$depth|$file_info")
        ((TOTAL_FILES++))
        log_info "添加文件: $file_path"
    fi
}

# 处理目录
process_directory() {
    local dir_path="$1"
    local depth="$2"
    
    local dir_info
    if dir_info=$(get_file_info "$dir_path"); then
        DIR_LIST+=("$depth|$dir_info")
        ((TOTAL_DIRS++))
        log_info "添加目录: $dir_path"
    fi
}

# =============================================================================
# 排序功能
# =============================================================================

# 获取文件扩展名
get_extension() {
    local filename="$1"
    local extension="${filename##*.}"
    if [[ "$extension" == "$filename" ]]; then
        echo ""  # 没有扩展名
    else
        echo "$extension"
    fi
}

# 生成排序键
generate_sort_key() {
    local item="$1"
    local depth file_type size permissions mtime atime ctime file_path
    
    IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
    
    case "$SORT_BY" in
        "name")
            echo "$(basename "$file_path")"
            ;;
        "size")
            printf "%020d" "$size"  # 填充零使数字排序正确
            ;;
        "mtime")
            printf "%020d" "$mtime"
            ;;
        "atime")
            printf "%020d" "$atime"
            ;;
        "extension")
            local ext
            ext=$(get_extension "$(basename "$file_path")")
            echo "$ext"
            ;;
        "depth")
            printf "%03d" "$depth"
            ;;
        *)
            echo "$(basename "$file_path")"
            ;;
    esac
}

# 排序文件列表
sort_file_list() {
    local -a sorted_list
    local -a sort_keys
    local i key
    
    # 生成排序键
    for i in "${!FILE_LIST[@]}"; do
        key=$(generate_sort_key "${FILE_LIST[$i]}")
        sort_keys[i]="$key|$i"
    done
    
    # 排序
    local sorted_indices
    if [[ "$REVERSE_SORT" == true ]]; then
        # 倒序排序
        sorted_indices=$(printf '%s\n' "${sort_keys[@]}" | sort -t'|' -k1,1r | cut -d'|' -f2)
    else
        # 正序排序
        sorted_indices=$(printf '%s\n' "${sort_keys[@]}" | sort -t'|' -k1,1 | cut -d'|' -f2)
    fi
    
    # 重新构建数组
    local -a new_list
    while IFS= read -r idx; do
        new_list+=("${FILE_LIST[$idx]}")
    done <<< "$sorted_indices"
    
    FILE_LIST=("${new_list[@]}")
}

# 排序目录列表
sort_dir_list() {
    local -a sorted_list
    local -a sort_keys
    local i key
    
    # 生成排序键
    for i in "${!DIR_LIST[@]}"; do
        key=$(generate_sort_key "${DIR_LIST[$i]}")
        sort_keys[i]="$key|$i"
    done
    
    # 排序
    local sorted_indices
    if [[ "$REVERSE_SORT" == true ]]; then
        # 倒序排序
        sorted_indices=$(printf '%s\n' "${sort_keys[@]}" | sort -t'|' -k1,1r | cut -d'|' -f2)
    else
        # 正序排序
        sorted_indices=$(printf '%s\n' "${sort_keys[@]}" | sort -t'|' -k1,1 | cut -d'|' -f2)
    fi
    
    # 重新构建数组
    local -a new_list
    while IFS= read -r idx; do
        new_list+=("${DIR_LIST[$idx]}")
    done <<< "$sorted_indices"
    
    DIR_LIST=("${new_list[@]}")
}

# =============================================================================
# 输出格式化
# =============================================================================

# 简洁模式输出
output_simple() {
    local item depth file_type size permissions mtime atime ctime file_path
    
    # 输出目录
    for item in "${DIR_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        local formatted_time
        formatted_time=$(format_time "$mtime")
        printf "%-40s %s\n" "$rel_path/" "$formatted_time"
    done
    
    # 输出文件
    for item in "${FILE_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        local formatted_time
        formatted_time=$(format_time "$mtime")
        printf "%-40s %s\n" "$rel_path" "$formatted_time"
    done
}

# 详细模式输出
output_detailed() {
    printf "%-40s %-8s %-12s %-20s %-20s %-20s\n" \
        "文件路径" "大小" "权限" "修改时间" "访问时间" "状态时间"
    printf "%-40s %-8s %-12s %-20s %-20s %-20s\n" \
        "========================================" "========" "============" "====================" "====================" "===================="
    
    local item depth file_type size permissions mtime atime ctime file_path
    
    # 输出目录
    for item in "${DIR_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        local formatted_mtime formatted_atime formatted_ctime
        formatted_mtime=$(format_time "$mtime")
        formatted_atime=$(format_time "$atime")
        formatted_ctime=$(format_time "$ctime")
        
        printf "%-40s %-8s %-12s %-20s %-20s %-20s\n" \
            "$rel_path/" "-" "$(printf '%o' "0x$permissions")" "$formatted_mtime" "$formatted_atime" "$formatted_ctime"
    done
    
    # 输出文件
    for item in "${FILE_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        local formatted_size formatted_mtime formatted_atime formatted_ctime
        formatted_size=$(format_size "$size")
        formatted_mtime=$(format_time "$mtime")
        formatted_atime=$(format_time "$atime")
        formatted_ctime=$(format_time "$ctime")
        
        printf "%-40s %-8s %-12s %-20s %-20s %-20s\n" \
            "$rel_path" "$formatted_size" "$(printf '%o' "0x$permissions")" "$formatted_mtime" "$formatted_atime" "$formatted_ctime"
    done
}

# 表格模式输出
output_table() {
    output_detailed  # 表格模式和详细模式相同
}

# JSON模式输出
output_json() {
    local scan_end_time
    scan_end_time=$(date +%s.%N)
    local scan_duration
    scan_duration=$(echo "$scan_end_time - $SCAN_START_TIME" | bc -l 2>/dev/null || echo "0")
    
    echo "{"
    echo "  \"scan_info\": {"
    echo "    \"timestamp\": \"$(get_timestamp)\","
    echo "    \"total_files\": $TOTAL_FILES,"
    echo "    \"total_directories\": $TOTAL_DIRS,"
    echo "    \"scan_duration\": \"${scan_duration}s\""
    echo "  },"
    echo "  \"files\": ["
    
    local first=true
    local item depth file_type size permissions mtime atime ctime file_path
    
    # 输出目录
    for item in "${DIR_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        
        if [[ "$first" != true ]]; then
            echo ","
        fi
        first=false
        
        echo "    {"
        echo "      \"path\": \"$rel_path\","
        echo "      \"type\": \"directory\","
        echo "      \"size\": null,"
        echo "      \"permissions\": \"$(printf '%o' "0x$permissions")\","
        echo "      \"mtime\": \"$(date -d "@$mtime" --iso-8601=seconds 2>/dev/null || echo "null")\","
        echo "      \"atime\": \"$(date -d "@$atime" --iso-8601=seconds 2>/dev/null || echo "null")\","
        echo "      \"ctime\": \"$(date -d "@$ctime" --iso-8601=seconds 2>/dev/null || echo "null")\""
        echo -n "    }"
    done
    
    # 输出文件
    for item in "${FILE_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        
        if [[ "$first" != true ]]; then
            echo ","
        fi
        first=false
        
        echo "    {"
        echo "      \"path\": \"$rel_path\","
        echo "      \"type\": \"file\","
        echo "      \"size\": $size,"
        echo "      \"permissions\": \"$(printf '%o' "0x$permissions")\","
        echo "      \"mtime\": \"$(date -d "@$mtime" --iso-8601=seconds 2>/dev/null || echo "null")\","
        echo "      \"atime\": \"$(date -d "@$atime" --iso-8601=seconds 2>/dev/null || echo "null")\","
        echo "      \"ctime\": \"$(date -d "@$ctime" --iso-8601=seconds 2>/dev/null || echo "null")\""
        echo -n "    }"
    done
    
    echo ""
    echo "  ]"
    echo "}"
}

# CSV模式输出
output_csv() {
    echo "type,path,size,permissions,mtime,atime,ctime"
    
    local item depth file_type size permissions mtime atime ctime file_path
    
    # 输出目录
    for item in "${DIR_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        local formatted_mtime formatted_atime formatted_ctime
        formatted_mtime=$(format_time "$mtime")
        formatted_atime=$(format_time "$atime")
        formatted_ctime=$(format_time "$ctime")
        
        echo "directory,\"$rel_path\",,\"$(printf '%o' "0x$permissions")\",\"$formatted_mtime\",\"$formatted_atime\",\"$formatted_ctime\""
    done
    
    # 输出文件
    for item in "${FILE_LIST[@]}"; do
        IFS='|' read -r depth file_type size permissions mtime atime ctime file_path <<< "$item"
        local rel_path
        rel_path="$(realpath --relative-to="$TARGET_DIR" "$file_path" 2>/dev/null)" || rel_path="$file_path"
        local formatted_mtime formatted_atime formatted_ctime
        formatted_mtime=$(format_time "$mtime")
        formatted_atime=$(format_time "$atime")
        formatted_ctime=$(format_time "$ctime")
        
        echo "file,\"$rel_path\",$size,\"$(printf '%o' "0x$permissions")\",\"$formatted_mtime\",\"$formatted_atime\",\"$formatted_ctime\""
    done
}

# 根据输出格式调用相应函数
generate_output() {
    case "$OUTPUT_FORMAT" in
        "simple")
            output_simple
            ;;
        "detailed")
            output_detailed
            ;;
        "table")
            output_table
            ;;
        "json")
            output_json
            ;;
        "csv")
            output_csv
            ;;
        *)
            log_error "不支持的输出格式: $OUTPUT_FORMAT"
            exit 1
            ;;
    esac
}

# =============================================================================
# 主程序入口点
# =============================================================================

main() {
    # 记录开始时间
    SCAN_START_TIME=$(date +%s.%N)
    
    # 加载配置
    load_config
    load_env_config
    
    # 解析参数
    parse_arguments "$@"
    
    # 显示帮助
    if [[ "$SHOW_HELP" == true ]]; then
        show_help
        exit 0
    fi
    
    # 验证参数
    validate_arguments
    
    log_info "开始扫描目录: $TARGET_DIR"
    log_info "输出格式: $OUTPUT_FORMAT"
    log_info "排序方式: $SORT_BY"
    log_info "最大深度: ${MAX_DEPTH:-无限制}"
    log_info "包含隐藏文件: $SHOW_HIDDEN"
    log_info "跟随符号链接: $FOLLOW_SYMLINKS"
    
    # 开始文件遍历
    log_info "开始遍历文件和目录..."
    
    # 清空数组
    FILE_LIST=()
    DIR_LIST=()
    TOTAL_FILES=0
    TOTAL_DIRS=0
    
    # 遍历目标目录
    traverse_directory "$TARGET_DIR" 0
    
    # 计算扫描时间
    local scan_end_time
    scan_end_time=$(date +%s.%N)
    local scan_duration
    scan_duration=$(echo "$scan_end_time - $SCAN_START_TIME" | bc -l 2>/dev/null || echo "unknown")
    
    log_info "扫描完成，共发现 $TOTAL_FILES 个文件，$TOTAL_DIRS 个目录"
    log_info "扫描耗时: ${scan_duration}s"
    
    log_info "开始排序..."
    
    # 排序文件和目录列表
    if [[ ${#FILE_LIST[@]} -gt 0 ]]; then
        sort_file_list
        log_info "文件列表排序完成"
    fi
    
    if [[ ${#DIR_LIST[@]} -gt 0 ]]; then
        sort_dir_list
        log_info "目录列表排序完成"
    fi
    
    # 生成输出
    log_info "生成输出..."
    generate_output
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi