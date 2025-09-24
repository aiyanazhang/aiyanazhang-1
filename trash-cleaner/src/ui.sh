#!/bin/bash

# 用户交互界面模块
# 功能：格式化输出、交互式提示、进度显示、表格展示

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"

# UI常量定义
declare -A UI_SYMBOLS=(
    ["CHECK"]="✓"
    ["CROSS"]="✗"
    ["ARROW"]="→"
    ["BULLET"]="•"
    ["WARNING"]="⚠"
    ["INFO"]="ℹ"
    ["QUESTION"]="?"
    ["TREE_BRANCH"]="├─"
    ["TREE_LAST"]="└─"
    ["TREE_VERTICAL"]="│"
    ["PROGRESS_FULL"]="█"
    ["PROGRESS_EMPTY"]="░"
    ["SPINNER1"]="⠋"
    ["SPINNER2"]="⠙"
    ["SPINNER3"]="⠹"
    ["SPINNER4"]="⠸"
    ["SPINNER5"]="⠼"
    ["SPINNER6"]="⠴"
    ["SPINNER7"]="⠦"
    ["SPINNER8"]="⠧"
)

# 终端尺寸
TERMINAL_WIDTH=$(tput cols 2>/dev/null || echo "80")
TERMINAL_HEIGHT=$(tput lines 2>/dev/null || echo "24")

# 检查终端能力
check_terminal_capabilities() {
    local capabilities=()
    
    # 检查颜色支持
    if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
        local colors
        colors=$(tput colors 2>/dev/null || echo "0")
        if [[ $colors -ge 8 ]]; then
            capabilities+=("color")
        fi
    fi
    
    # 检查UTF-8支持
    if [[ "${LANG:-}" =~ UTF-8 ]] || [[ "${LC_ALL:-}" =~ UTF-8 ]]; then
        capabilities+=("utf8")
    fi
    
    # 检查交互式终端
    if [[ -t 0 ]] && [[ -t 1 ]]; then
        capabilities+=("interactive")
    fi
    
    printf '%s\n' "${capabilities[@]}"
}

# 获取颜色代码
get_color() {
    local color_name="$1"
    local fallback="${2:-}"
    
    if ! is_config_true "color_output"; then
        echo "$fallback"
        return 1
    fi
    
    case "$color_name" in
        "red") tput setaf 1 2>/dev/null || echo -e "\033[31m" ;;
        "green") tput setaf 2 2>/dev/null || echo -e "\033[32m" ;;
        "yellow") tput setaf 3 2>/dev/null || echo -e "\033[33m" ;;
        "blue") tput setaf 4 2>/dev/null || echo -e "\033[34m" ;;
        "purple") tput setaf 5 2>/dev/null || echo -e "\033[35m" ;;
        "cyan") tput setaf 6 2>/dev/null || echo -e "\033[36m" ;;
        "white") tput setaf 7 2>/dev/null || echo -e "\033[37m" ;;
        "bold") tput bold 2>/dev/null || echo -e "\033[1m" ;;
        "dim") tput dim 2>/dev/null || echo -e "\033[2m" ;;
        "underline") tput smul 2>/dev/null || echo -e "\033[4m" ;;
        "reset") tput sgr0 2>/dev/null || echo -e "\033[0m" ;;
        *) echo "$fallback" ;;
    esac
}

# 格式化带颜色的文本
format_text() {
    local color="$1"
    local text="$2"
    local reset_after="${3:-true}"
    
    local color_code
    local reset_code=""
    
    color_code=$(get_color "$color")
    
    if [[ "$reset_after" == "true" ]]; then
        reset_code=$(get_color "reset")
    fi
    
    printf "%s%s%s" "$color_code" "$text" "$reset_code"
}

# 打印标题
print_title() {
    local title="$1"
    local style="${2:-simple}"  # simple, box, line
    
    case "$style" in
        "box")
            local title_len=${#title}
            local box_width=$((title_len + 4))
            
            printf "┌%*s┐\n" $((box_width-2)) | tr ' ' '─'
            printf "│ %s │\n" "$(format_text "bold" "$title")"
            printf "└%*s┘\n" $((box_width-2)) | tr ' ' '─'
            ;;
            
        "line")
            local line_char="="
            local line_width=$((TERMINAL_WIDTH > 80 ? 80 : TERMINAL_WIDTH))
            
            printf "%*s\n" "$line_width" | tr ' ' "$line_char"
            printf "%s\n" "$(format_text "bold" "$title")"
            printf "%*s\n" "$line_width" | tr ' ' "$line_char"
            ;;
            
        "simple"|*)
            printf "%s\n" "$(format_text "bold" "$title")"
            ;;
    esac
    
    echo
}

# 打印状态消息
print_status() {
    local status="$1"
    local message="$2"
    local details="${3:-}"
    
    local symbol=""
    local color=""
    
    case "$status" in
        "success"|"ok"|"done")
            symbol="${UI_SYMBOLS[CHECK]}"
            color="green"
            ;;
        "error"|"fail"|"failed")
            symbol="${UI_SYMBOLS[CROSS]}"
            color="red"
            ;;
        "warning"|"warn")
            symbol="${UI_SYMBOLS[WARNING]}"
            color="yellow"
            ;;
        "info")
            symbol="${UI_SYMBOLS[INFO]}"
            color="blue"
            ;;
        "question")
            symbol="${UI_SYMBOLS[QUESTION]}"
            color="cyan"
            ;;
        *)
            symbol="${UI_SYMBOLS[BULLET]}"
            color="white"
            ;;
    esac
    
    printf "%s %s" "$(format_text "$color" "$symbol")" "$message"
    
    if [[ -n "$details" ]]; then
        printf " %s" "$(format_text "dim" "($details)")"
    fi
    
    echo
}

# 显示表格
show_table() {
    local -n headers_ref=$1
    local -n data_ref=$2
    local title="${3:-}"
    
    if [[ -n "$title" ]]; then
        print_title "$title" "simple"
    fi
    
    # 计算列宽
    local -a col_widths=()
    local num_cols=${#headers_ref[@]}
    
    # 初始化列宽为标题宽度
    for ((i=0; i<num_cols; i++)); do
        col_widths[i]=${#headers_ref[i]}
    done
    
    # 计算数据列的最大宽度
    for row_data in "${data_ref[@]}"; do
        IFS='|' read -ra cols <<< "$row_data"
        for ((i=0; i<num_cols && i<${#cols[@]}; i++)); do
            local col_len=${#cols[i]}
            if [[ $col_len -gt ${col_widths[i]} ]]; then
                col_widths[i]=$col_len
            fi
        done
    done
    
    # 打印表头
    local separator=""
    for ((i=0; i<num_cols; i++)); do
        printf "│ %-*s " "${col_widths[i]}" "$(format_text "bold" "${headers_ref[i]}")"
        separator+="├$(printf "%*s" $((col_widths[i]+2)) | tr ' ' '─')"
    done
    echo "│"
    
    # 打印分隔线
    echo "${separator%?}┤"
    
    # 打印数据行
    for row_data in "${data_ref[@]}"; do
        IFS='|' read -ra cols <<< "$row_data"
        for ((i=0; i<num_cols; i++)); do
            local cell_data="${cols[i]:-}"
            printf "│ %-*s " "${col_widths[i]}" "$cell_data"
        done
        echo "│"
    done
    
    echo
}

# 显示统计信息面板
show_stats_panel() {
    local title="$1"
    local -n stats_ref=$2
    
    print_title "$title" "box"
    
    # 计算最大键长度用于对齐
    local max_key_len=0
    for key in "${!stats_ref[@]}"; do
        if [[ ${#key} -gt $max_key_len ]]; then
            max_key_len=${#key}
        fi
    done
    
    # 显示统计信息
    for key in $(printf '%s\n' "${!stats_ref[@]}" | sort); do
        local value="${stats_ref[$key]}"
        printf "  %-*s: %s\n" "$max_key_len" "$key" "$(format_text "cyan" "$value")"
    done
    
    echo
}

# 交互式确认提示
confirm_prompt() {
    local message="$1"
    local default="${2:-n}"  # y, n, 或空
    local timeout="${3:-0}"  # 超时秒数，0表示无超时
    
    local prompt_text="$message"
    
    # 构建提示文本
    case "$default" in
        "y"|"Y"|"yes"|"YES")
            prompt_text+=" [Y/n]"
            ;;
        "n"|"N"|"no"|"NO")
            prompt_text+=" [y/N]"
            ;;
        *)
            prompt_text+=" [y/n]"
            ;;
    esac
    
    # 添加超时提示
    if [[ $timeout -gt 0 ]]; then
        prompt_text+=" (${timeout}秒超时)"
    fi
    
    prompt_text+=": "
    
    local response=""
    
    # 处理超时
    if [[ $timeout -gt 0 ]]; then
        # 使用read的超时功能
        if ! read -t "$timeout" -p "$prompt_text" -r response; then
            echo
            log_info "UI" "用户确认超时，使用默认值: $default"
            response="$default"
        fi
    else
        # 无超时的正常读取
        read -p "$prompt_text" -r response
    fi
    
    # 处理空输入
    if [[ -z "$response" ]]; then
        response="$default"
    fi
    
    # 判断响应
    case "$response" in
        [yY]|[yY][eE][sS]|"true"|"1")
            return 0
            ;;
        [nN]|[nN][oO]|"false"|"0")
            return 1
            ;;
        *)
            # 无效输入，递归重试
            print_status "warning" "无效输入，请输入 y(是) 或 n(否)"
            confirm_prompt "$message" "$default" "$timeout"
            return $?
            ;;
    esac
}

# 选择菜单
show_menu() {
    local title="$1"
    local -n options_ref=$2
    local default="${3:-1}"
    
    print_title "$title" "simple"
    
    # 显示选项
    for ((i=0; i<${#options_ref[@]}; i++)); do
        local option_num=$((i+1))
        local marker=" "
        
        if [[ $option_num -eq $default ]]; then
            marker="$(format_text "green" "*")"
        fi
        
        printf "%s %d) %s\n" "$marker" "$option_num" "${options_ref[i]}"
    done
    
    echo
    
    # 获取用户选择
    while true; do
        read -p "请选择 [1-${#options_ref[@]}] (默认: $default): " -r choice
        
        # 使用默认值
        if [[ -z "$choice" ]]; then
            choice="$default"
        fi
        
        # 验证输入
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le ${#options_ref[@]} ]]; then
            return $((choice-1))  # 返回数组索引
        else
            print_status "error" "无效选择，请输入 1-${#options_ref[@]} 之间的数字"
        fi
    done
}

# 进度指示器（旋转器）
show_spinner() {
    local message="$1"
    local duration="${2:-5}"  # 持续时间（秒）
    
    if ! is_config_true "progress_bar"; then
        return 0
    fi
    
    local spinner_chars=("${UI_SYMBOLS[SPINNER1]}" "${UI_SYMBOLS[SPINNER2]}" "${UI_SYMBOLS[SPINNER3]}" "${UI_SYMBOLS[SPINNER4]}" "${UI_SYMBOLS[SPINNER5]}" "${UI_SYMBOLS[SPINNER6]}" "${UI_SYMBOLS[SPINNER7]}" "${UI_SYMBOLS[SPINNER8]}")
    local i=0
    local end_time=$(($(date +%s) + duration))
    
    # 隐藏光标
    tput civis 2>/dev/null
    
    while [[ $(date +%s) -lt $end_time ]]; do
        printf "\r%s %s" "${spinner_chars[i]}" "$message"
        i=$(((i+1) % ${#spinner_chars[@]}))
        sleep 0.1
    done
    
    # 清除行并显示光标
    printf "\r%*s\r" $((${#message}+2)) ""
    tput cnorm 2>/dev/null
}

# 文件大小格式化（人类可读）
format_size_human() {
    local size="$1"
    local precision="${2:-1}"
    
    if [[ $size -ge 1099511627776 ]]; then
        # TB
        printf "%.${precision}f TB" "$(echo "scale=3; $size / 1099511627776" | bc 2>/dev/null || awk "BEGIN {printf \"%.3f\", $size/1099511627776}")"
    elif [[ $size -ge 1073741824 ]]; then
        # GB
        printf "%.${precision}f GB" "$(echo "scale=3; $size / 1073741824" | bc 2>/dev/null || awk "BEGIN {printf \"%.3f\", $size/1073741824}")"
    elif [[ $size -ge 1048576 ]]; then
        # MB
        printf "%.${precision}f MB" "$(echo "scale=3; $size / 1048576" | bc 2>/dev/null || awk "BEGIN {printf \"%.3f\", $size/1048576}")"
    elif [[ $size -ge 1024 ]]; then
        # KB
        printf "%.${precision}f KB" "$(echo "scale=3; $size / 1024" | bc 2>/dev/null || awk "BEGIN {printf \"%.3f\", $size/1024}")"
    else
        printf "%d B" "$size"
    fi
}

# 时间格式化（人类可读）
format_duration_human() {
    local seconds="$1"
    
    if [[ $seconds -ge 3600 ]]; then
        local hours=$((seconds / 3600))
        local mins=$(((seconds % 3600) / 60))
        local secs=$((seconds % 60))
        printf "%d小时%d分钟%d秒" "$hours" "$mins" "$secs"
    elif [[ $seconds -ge 60 ]]; then
        local mins=$((seconds / 60))
        local secs=$((seconds % 60))
        printf "%d分钟%d秒" "$mins" "$secs"
    else
        printf "%d秒" "$seconds"
    fi
}

# 显示操作摘要
show_operation_summary() {
    local operation_name="$1"
    local -n summary_data_ref=$2
    
    print_title "操作摘要: $operation_name" "line"
    
    # 基本统计信息
    local headers=("项目" "数量" "大小")
    local table_data=()
    
    # 构建表格数据
    for key in "${!summary_data_ref[@]}"; do
        local value="${summary_data_ref[$key]}"
        
        # 特殊处理大小相关的值
        if [[ "$key" =~ size|Size ]]; then
            value=$(format_size_human "$value")
        fi
        
        table_data+=("$key|$value|")
    done
    
    # 显示表格
    show_table headers table_data
    
    return 0
}

# 实时进度条
show_realtime_progress() {
    local current="$1"
    local total="$2"
    local label="${3:-处理中}"
    local show_percentage="${4:-true}"
    local show_eta="${5:-false}"
    
    if ! is_config_true "progress_bar"; then
        return 0
    fi
    
    local width=40
    local progress=0
    
    if [[ $total -gt 0 ]]; then
        progress=$((current * 100 / total))
    fi
    
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    # 构建进度条
    local bar=""
    for ((i=0; i<filled; i++)); do
        bar+="${UI_SYMBOLS[PROGRESS_FULL]}"
    done
    for ((i=0; i<empty; i++)); do
        bar+="${UI_SYMBOLS[PROGRESS_EMPTY]}"
    done
    
    # 显示进度条
    printf "\r%s: [%s]" "$label" "$(format_text "cyan" "$bar")"
    
    # 显示百分比
    if [[ "$show_percentage" == "true" ]]; then
        printf " %3d%%" "$progress"
    fi
    
    # 显示计数
    printf " (%d/%d)" "$current" "$total"
    
    # 如果完成，换行
    if [[ $current -eq $total ]]; then
        echo
    fi
}

# 显示错误详情
show_error_details() {
    local error_title="$1"
    local -n errors_ref=$2
    
    if [[ ${#errors_ref[@]} -eq 0 ]]; then
        return 0
    fi
    
    print_title "$error_title" "simple"
    
    for error in "${errors_ref[@]}"; do
        print_status "error" "$error"
    done
    
    echo
}

# 清屏和重置终端
clear_screen() {
    local method="${1:-clear}"  # clear, reset, home
    
    case "$method" in
        "clear")
            clear 2>/dev/null || printf "\033[2J\033[H"
            ;;
        "reset")
            reset 2>/dev/null || printf "\033c"
            ;;
        "home")
            tput home 2>/dev/null || printf "\033[H"
            ;;
    esac
}

# 等待用户按键
wait_for_keypress() {
    local message="${1:-按任意键继续...}"
    
    printf "%s" "$message"
    read -n1 -s -r
    echo
}

# 主UI管理函数
main_ui() {
    local action="$1"
    
    case "$action" in
        "test")
            # UI组件测试
            print_title "UI组件测试" "box"
            
            print_status "success" "这是成功消息"
            print_status "error" "这是错误消息"
            print_status "warning" "这是警告消息"
            print_status "info" "这是信息消息"
            
            local test_headers=("列1" "列2" "列3")
            local test_data=("数据1|数据2|数据3" "长数据项|短|中等长度数据")
            show_table test_headers test_data "测试表格"
            
            if confirm_prompt "是否继续测试"; then
                print_status "info" "用户选择继续"
            fi
            ;;
            
        "capabilities")
            # 显示终端能力
            local capabilities
            mapfile -t capabilities < <(check_terminal_capabilities)
            
            print_title "终端能力检测" "simple"
            for capability in "${capabilities[@]}"; do
                print_status "info" "支持: $capability"
            done
            ;;
            
        *)
            echo "用法: $0 {test|capabilities}" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主UI函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_ui "$@"
fi