#!/bin/bash

# 配置管理器模块
# 功能：命令行参数解析、配置文件加载、参数验证

# 默认配置值
declare -A DEFAULT_CONFIG=(
    ["default_mode"]="interactive"
    ["confirm_deletion"]="true"
    ["max_file_age_days"]="0"
    ["min_file_size_mb"]="0"
    ["enable_logging"]="true"
    ["log_retention_days"]="30"
    ["color_output"]="true"
    ["progress_bar"]="true"
    ["verbose"]="false"
    ["dry_run"]="false"
    ["clean_type"]="all"
    ["pattern"]="*"
    ["max_depth"]="20"
    ["config_file"]="$HOME/.trash-cleaner.conf"
    ["log_file"]="$HOME/.trash-cleaner.log"
    # 新增的预检查相关参数
    ["list_only"]="false"
    ["detailed_list"]="false"
    ["risk_analysis"]="true"
    ["group_by"]="type"
    ["sort_by"]="name"
    ["interactive_mode"]="true"
    ["min_risk_level"]="0"
    ["export_format"]=""
    ["export_file"]=""
    ["table_format"]="auto"
    ["display_width"]="auto"
    ["display_columns"]="name,size,time,risk,type"
    ["no_header"]="false"
    ["clear_screen"]="false"
)

# 全局配置存储
declare -A CONFIG
declare -A CLI_ARGS

# 显示帮助信息
show_help() {
    cat <<EOF
回收站清理工具 - 安全清理系统回收站内容

用法：
    $0 [选项]

选项：
    -h, --help              显示此帮助信息
    -v, --verbose           详细输出模式
    -y, --yes               自动确认，跳过交互提示
    -n, --dry-run           预览模式，不实际删除文件
    -t, --type TYPE         清理类型 (files|dirs|all)
    -d, --older-than TIME   仅清理指定时间之前的文件 (例如: 7d, 30d, 1m)
    -s, --size-limit SIZE   文件大小限制 (例如: 100M, 1G)
    -p, --pattern PATTERN   文件名匹配模式 (支持通配符)
    --max-depth DEPTH       目录遍历最大深度
    -c, --config FILE       配置文件路径
    -l, --log FILE          日志文件路径
    --no-color              禁用彩色输出
    --no-progress           禁用进度条

    # 新增的预检查和列表功能
    -L, --list-only         仅列出文件，不执行删除
    --detailed              显示详细文件信息
    -r, --risk-analysis     启用风险分析
    -g, --group-by GROUP    分组方式 (type|size|time|risk|location)
    -S, --sort-by SORT      排序方式 (name|size|time|risk|importance)
    -I, --interactive       交互式选择模式
    -m, --min-risk LEVEL    最低风险等级 (0-100)
    -x, --export FORMAT     导出列表到文件 (csv|json|txt)
    --export-file FILE      导出文件路径
    -T, --table-format FMT  表格格式 (simple|grid|fancy|auto)
    -w, --width WIDTH       显示宽度限制
    -C, --columns COLS      显示列 (name,size,time,risk,type)
    -H, --no-header         不显示表头
    --clear-screen          交互模式中清屏

时间格式：
    s, sec, second          秒
    m, min, minute          分钟
    h, hour                 小时
    d, day                  天
    w, week                 周
    M, month                月

大小格式：
    B, byte                 字节
    K, KB, kilobyte         千字节
    M, MB, megabyte         兆字节
    G, GB, gigabyte         吉字节
    T, TB, terabyte         太字节

清理类型：
    files                   仅清理文件
    dirs                    仅清理目录
    all                     清理文件和目录 (默认)

分组方式：
    type                    按文件类型分组
    size                    按文件大小分组
    time                    按修改时间分组
    risk                    按风险等级分组
    location                按文件位置分组

示例：
    $0                      交互式清理所有回收站内容
    $0 -L -r                仅列出文件并显示风险分析
    $0 --detailed -g type   显示详细信息并按类型分组
    $0 -I -m 50             交互模式，仅显示风险评分>=50的文件
    $0 -x json --export-file report.json  导出JSON格式报告
    $0 -y -t files          自动清理所有文件，跳过目录
    $0 -n -d 30d            预览30天前的文件
    $0 -s 100M -p "*.tmp"   清理大于100MB的.tmp文件

配置文件：
    配置文件使用简单的 key=value 格式，支持注释 (以 # 开头)
    默认配置文件位置: ~/.trash-cleaner.conf

EOF
}

# 解析时间字符串为秒
parse_time_to_seconds() {
    local time_str="$1"
    local number
    local unit
    
    # 提取数字和单位
    if [[ "$time_str" =~ ^([0-9]+)([a-zA-Z]*)$ ]]; then
        number="${BASH_REMATCH[1]}"
        unit="${BASH_REMATCH[2]}"
    else
        echo "ERROR: 无效的时间格式: $time_str" >&2
        return 1
    fi
    
    # 转换为秒
    case "$unit" in
        "s"|"sec"|"second"|"seconds"|"")
            echo "$number"
            ;;
        "m"|"min"|"minute"|"minutes")
            echo $((number * 60))
            ;;
        "h"|"hour"|"hours")
            echo $((number * 3600))
            ;;
        "d"|"day"|"days")
            echo $((number * 86400))
            ;;
        "w"|"week"|"weeks")
            echo $((number * 604800))
            ;;
        "M"|"month"|"months")
            echo $((number * 2592000))  # 30天
            ;;
        *)
            echo "ERROR: 未知的时间单位: $unit" >&2
            return 1
            ;;
    esac
}

# 解析大小字符串为字节
parse_size_to_bytes() {
    local size_str="$1"
    local number
    local unit
    
    # 提取数字和单位
    if [[ "$size_str" =~ ^([0-9]+)([a-zA-Z]*)$ ]]; then
        number="${BASH_REMATCH[1]}"
        unit="${BASH_REMATCH[2]}"
    else
        echo "ERROR: 无效的大小格式: $size_str" >&2
        return 1
    fi
    
    # 转换为字节
    case "$unit" in
        "B"|"byte"|"bytes"|"")
            echo "$number"
            ;;
        "K"|"KB"|"kilobyte"|"kilobytes")
            echo $((number * 1024))
            ;;
        "M"|"MB"|"megabyte"|"megabytes")
            echo $((number * 1024 * 1024))
            ;;
        "G"|"GB"|"gigabyte"|"gigabytes")
            echo $((number * 1024 * 1024 * 1024))
            ;;
        "T"|"TB"|"terabyte"|"terabytes")
            echo $((number * 1024 * 1024 * 1024 * 1024))
            ;;
        *)
            echo "ERROR: 未知的大小单位: $unit" >&2
            return 1
            ;;
    esac
}

# 验证清理类型
validate_clean_type() {
    local type="$1"
    
    case "$type" in
        "files"|"dirs"|"all")
            return 0
            ;;
        *)
            echo "ERROR: 无效的清理类型: $type" >&2
            echo "有效类型: files, dirs, all" >&2
            return 1
            ;;
    esac
}

# 加载配置文件
load_config_file() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        echo "WARNING: 配置文件不存在: $config_file" >&2
        return 1
    fi
    
    if [[ ! -r "$config_file" ]]; then
        echo "ERROR: 无法读取配置文件: $config_file" >&2
        return 1
    fi
    
    echo "加载配置文件: $config_file"
    
    # 读取配置文件，忽略注释和空行
    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        # 跳过注释和空行
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue
        
        # 清理key和value的空白字符
        key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # 移除value两端的引号
        value=$(echo "$value" | sed 's/^["'\'']*//;s/["'\'']*$//')
        
        if [[ -n "$key" ]] && [[ -n "$value" ]]; then
            CONFIG["$key"]="$value"
        fi
    done < "$config_file"
    
    return 0
}

# 初始化配置（使用默认值）
init_config() {
    # 复制默认配置到CONFIG数组
    for key in "${!DEFAULT_CONFIG[@]}"; do
        CONFIG["$key"]="${DEFAULT_CONFIG[$key]}"
    done
}

# 解析命令行参数
parse_command_line() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                CLI_ARGS["verbose"]="true"
                shift
                ;;
            -y|--yes)
                CLI_ARGS["confirm_deletion"]="false"
                shift
                ;;
            -n|--dry-run)
                CLI_ARGS["dry_run"]="true"
                shift
                ;;
            -t|--type)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["clean_type"]="$2"
                    shift 2
                else
                    echo "ERROR: --type 需要参数" >&2
                    return 1
                fi
                ;;
            -d|--older-than)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["older_than"]="$2"
                    shift 2
                else
                    echo "ERROR: --older-than 需要参数" >&2
                    return 1
                fi
                ;;
            -s|--size-limit)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["size_limit"]="$2"
                    shift 2
                else
                    echo "ERROR: --size-limit 需要参数" >&2
                    return 1
                fi
                ;;
            -p|--pattern)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["pattern"]="$2"
                    shift 2
                else
                    echo "ERROR: --pattern 需要参数" >&2
                    return 1
                fi
                ;;
            --max-depth)
                if [[ -n "$2" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    CLI_ARGS["max_depth"]="$2"
                    shift 2
                else
                    echo "ERROR: --max-depth 需要数字参数" >&2
                    return 1
                fi
                ;;
            -c|--config)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["config_file"]="$2"
                    shift 2
                else
                    echo "ERROR: --config 需要参数" >&2
                    return 1
                fi
                ;;
            -l|--log)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["log_file"]="$2"
                    shift 2
                else
                    echo "ERROR: --log 需要参数" >&2
                    return 1
                fi
                ;;
            --no-color)
                CLI_ARGS["color_output"]="false"
                shift
                ;;
            --no-progress)
                CLI_ARGS["progress_bar"]="false"
                shift
                ;;
            # 新增的预检查相关参数
            -L|--list-only)
                CLI_ARGS["list_only"]="true"
                shift
                ;;
            --detailed)
                CLI_ARGS["detailed_list"]="true"
                shift
                ;;
            -r|--risk-analysis)
                CLI_ARGS["risk_analysis"]="true"
                shift
                ;;
            -g|--group-by)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["group_by"]="$2"
                    shift 2
                else
                    echo "ERROR: --group-by 需要参数" >&2
                    return 1
                fi
                ;;
            -S|--sort-by)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["sort_by"]="$2"
                    shift 2
                else
                    echo "ERROR: --sort-by 需要参数" >&2
                    return 1
                fi
                ;;
            -I|--interactive)
                CLI_ARGS["interactive_mode"]="true"
                shift
                ;;
            -m|--min-risk)
                if [[ -n "$2" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    CLI_ARGS["min_risk_level"]="$2"
                    shift 2
                else
                    echo "ERROR: --min-risk 需要数字参数 (0-100)" >&2
                    return 1
                fi
                ;;
            -x|--export)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["export_format"]="$2"
                    shift 2
                else
                    echo "ERROR: --export 需要参数 (csv|json|txt)" >&2
                    return 1
                fi
                ;;
            --export-file)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["export_file"]="$2"
                    shift 2
                else
                    echo "ERROR: --export-file 需要参数" >&2
                    return 1
                fi
                ;;
            -T|--table-format)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["table_format"]="$2"
                    shift 2
                else
                    echo "ERROR: --table-format 需要参数" >&2
                    return 1
                fi
                ;;
            -w|--width)
                if [[ -n "$2" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    CLI_ARGS["display_width"]="$2"
                    shift 2
                else
                    echo "ERROR: --width 需要数字参数" >&2
                    return 1
                fi
                ;;
            -C|--columns)
                if [[ -n "$2" ]]; then
                    CLI_ARGS["display_columns"]="$2"
                    shift 2
                else
                    echo "ERROR: --columns 需要参数" >&2
                    return 1
                fi
                ;;
            -H|--no-header)
                CLI_ARGS["no_header"]="true"
                shift
                ;;
            --clear-screen)
                CLI_ARGS["clear_screen"]="true"
                shift
                ;;
            --)
                shift
                break
                ;;
            -*)
                echo "ERROR: 未知选项: $1" >&2
                echo "使用 -h 或 --help 查看帮助信息" >&2
                return 1
                ;;
            *)
                echo "ERROR: 不支持位置参数: $1" >&2
                return 1
                ;;
        esac
    done
    
    return 0
}

# 应用命令行参数覆盖配置
apply_cli_overrides() {
    for key in "${!CLI_ARGS[@]}"; do
        CONFIG["$key"]="${CLI_ARGS[$key]}"
    done
}

# 验证配置参数
validate_config() {
    local errors=0
    
    # 验证清理类型
    if ! validate_clean_type "${CONFIG[clean_type]}"; then
        ((errors++))
    fi
    
    # 验证时间参数
    if [[ -n "${CONFIG[older_than]:-}" ]]; then
        if ! parse_time_to_seconds "${CONFIG[older_than]}" > /dev/null; then
            ((errors++))
        fi
    fi
    
    # 验证大小参数
    if [[ -n "${CONFIG[size_limit]:-}" ]]; then
        if ! parse_size_to_bytes "${CONFIG[size_limit]}" > /dev/null; then
            ((errors++))
        fi
    fi
    
    # 验证数字参数
    local numeric_params=("max_file_age_days" "min_file_size_mb" "log_retention_days" "max_depth")
    for param in "${numeric_params[@]}"; do
        if [[ -n "${CONFIG[$param]:-}" ]] && ! [[ "${CONFIG[$param]}" =~ ^[0-9]+$ ]]; then
            echo "ERROR: $param 必须是数字: ${CONFIG[$param]}" >&2
            ((errors++))
        fi
    done
    
    # 验证布尔参数
    local boolean_params=("confirm_deletion" "enable_logging" "color_output" "progress_bar" "verbose" "dry_run")
    for param in "${boolean_params[@]}"; do
        if [[ -n "${CONFIG[$param]:-}" ]]; then
            case "${CONFIG[$param]}" in
                "true"|"false"|"yes"|"no"|"1"|"0") ;;
                *)
                    echo "ERROR: $param 必须是布尔值: ${CONFIG[$param]}" >&2
                    ((errors++))
                    ;;
            esac
        fi
    done
    
    return $errors
}

# 规范化布尔值
normalize_boolean() {
    local value="$1"
    
    case "$value" in
        "true"|"yes"|"1") echo "true" ;;
        "false"|"no"|"0") echo "false" ;;
        *) echo "$value" ;;
    esac
}

# 标准化配置值
normalize_config() {
    # 规范化布尔值
    local boolean_params=("confirm_deletion" "enable_logging" "color_output" "progress_bar" "verbose" "dry_run")
    for param in "${boolean_params[@]}"; do
        if [[ -n "${CONFIG[$param]:-}" ]]; then
            CONFIG["$param"]=$(normalize_boolean "${CONFIG[$param]}")
        fi
    done
    
    # 确保路径为绝对路径
    local path_params=("config_file" "log_file")
    for param in "${path_params[@]}"; do
        if [[ -n "${CONFIG[$param]:-}" ]]; then
            # 展开 ~ 为家目录
            CONFIG["$param"]="${CONFIG[$param]/#~/$HOME}"
            
            # 如果不是绝对路径，转换为绝对路径
            if [[ "${CONFIG[$param]:0:1}" != "/" ]]; then
                CONFIG["$param"]="$PWD/${CONFIG[$param]}"
            fi
        fi
    done
}

# 显示当前配置
show_config() {
    echo "当前配置："
    for key in $(printf '%s\n' "${!CONFIG[@]}" | sort); do
        echo "  $key = ${CONFIG[$key]}"
    done
}

# 获取配置值
get_config() {
    local key="$1"
    local default_value="${2:-}"
    
    echo "${CONFIG[$key]:-$default_value}"
}

# 设置配置值
set_config() {
    local key="$1"
    local value="$2"
    
    CONFIG["$key"]="$value"
}

# 检查配置值是否为真
is_config_true() {
    local key="$1"
    local value="${CONFIG[$key]:-false}"
    
    [[ "$value" == "true" ]]
}

# 主配置管理函数
main_config_management() {
    local config_file
    
    # 初始化默认配置
    init_config
    
    # 解析命令行参数
    if ! parse_command_line "$@"; then
        return 1
    fi
    
    # 确定配置文件路径
    config_file="${CLI_ARGS[config_file]:-${CONFIG[config_file]}}"
    
    # 加载配置文件（如果存在）
    if [[ -f "$config_file" ]]; then
        load_config_file "$config_file"
    fi
    
    # 应用命令行参数覆盖
    apply_cli_overrides
    
    # 标准化配置值
    normalize_config
    
    # 验证配置
    if ! validate_config; then
        echo "ERROR: 配置验证失败" >&2
        return 1
    fi
    
    # 如果启用详细模式，显示配置
    if is_config_true "verbose"; then
        show_config
    fi
    
    return 0
}

# 如果直接运行此脚本，执行主配置管理函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_config_management "$@"
fi