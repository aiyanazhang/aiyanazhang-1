#!/bin/bash

# 列表管理器模块
# 功能：文件列表生成、过滤排序、分组展示、导出管理

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security_checker.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"
source "$(dirname "${BASH_SOURCE[0]}")/file_analyzer.sh"
source "$(dirname "${BASH_SOURCE[0]}")/risk_assessor.sh"

# 列表数据存储
declare -a LIST_ITEMS=()
declare -A LIST_METADATA=()
declare -A SELECTION_STATE=()

# 视图模式定义
declare -A VIEW_MODES=(
    ["overview"]="概览视图"
    ["detailed"]="详细视图"
    ["risk"]="风险视图"
    ["category"]="分类视图"
    ["timeline"]="时间视图"
    ["size"]="大小视图"
)

# 颜色主题配置
declare -A COLOR_THEME=(
    ["HEADER"]="\033[1;36m"    # 青色粗体
    ["SAFE"]="\033[32m"        # 绿色
    ["LOW"]="\033[32m"         # 绿色
    ["MEDIUM"]="\033[33m"      # 黄色
    ["HIGH"]="\033[31m"        # 红色
    ["CRITICAL"]="\033[1;31m"  # 红色粗体
    ["SELECTED"]="\033[1;35m"  # 紫色粗体
    ["RESET"]="\033[0m"        # 重置
    ["BOLD"]="\033[1m"         # 粗体
)

# 生成文件列表
generate_file_list() {
    local source_files=("$@")
    local total_files=${#source_files[@]}
    
    log_info "LIST_MANAGER" "开始生成文件列表，包含 $total_files 个文件"
    
    # 清空现有列表
    LIST_ITEMS=()
    LIST_METADATA=()
    
    local current=0
    for file_path in "${source_files[@]}"; do
        ((current++))
        
        if is_config_true "progress_bar"; then
            printf "\r列表生成进度: %d/%d (%d%%)" "$current" "$total_files" $((current * 100 / total_files)) >&2
        fi
        
        # 分析文件
        local file_analysis risk_report
        file_analysis=$(analyze_file "$file_path")
        
        if [[ $? -eq 0 ]]; then
            risk_report=$(generate_risk_report "$file_analysis")
            
            # 构建列表项
            local list_item="$file_path"
            LIST_ITEMS+=("$list_item")
            
            # 存储元数据
            LIST_METADATA["$file_path:analysis"]="$file_analysis"
            LIST_METADATA["$file_path:risk"]="$risk_report"
            SELECTION_STATE["$file_path"]=false
        fi
    done
    
    if is_config_true "progress_bar"; then
        echo >&2  # 换行
    fi
    
    log_info "LIST_MANAGER" "文件列表生成完成，共 ${#LIST_ITEMS[@]} 个项目"
}

# 应用过滤器
apply_filters() {
    local filter_type="$1"
    local filter_value="$2"
    
    log_debug "LIST_MANAGER" "应用过滤器: $filter_type = $filter_value"
    
    local filtered_items=()
    
    for item in "${LIST_ITEMS[@]}"; do
        local should_include=true
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local risk="${LIST_METADATA["$item:risk"]}"
        
        case "$filter_type" in
            "type")
                local file_type
                file_type=$(echo "$analysis" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
                if [[ "$file_type" != "$filter_value" ]]; then
                    should_include=false
                fi
                ;;
            "risk")
                local risk_level
                risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
                if [[ "$risk_level" != "$filter_value" ]]; then
                    should_include=false
                fi
                ;;
            "size_min")
                local size
                size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
                if [[ $size -lt $filter_value ]]; then
                    should_include=false
                fi
                ;;
        esac
        
        if [[ "$should_include" == "true" ]]; then
            filtered_items+=("$item")
        fi
    done
    
    LIST_ITEMS=("${filtered_items[@]}")
    log_info "LIST_MANAGER" "过滤完成，剩余 ${#LIST_ITEMS[@]} 个项目"
}

# 排序文件列表
sort_files() {
    local sort_field="$1"
    local sort_order="${2:-asc}"
    
    log_debug "LIST_MANAGER" "按 $sort_field 排序 ($sort_order)"
    
    # 创建临时数组用于排序
    local -a sort_data=()
    
    # 准备排序数据
    for item in "${LIST_ITEMS[@]}"; do
        local sort_key=""
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local risk="${LIST_METADATA["$item:risk"]}"
        
        case "$sort_field" in
            "name")
                sort_key=$(basename "$item")
                ;;
            "size")
                sort_key=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
                sort_key=$(printf "%020d" "$sort_key")
                ;;
            "risk")
                sort_key=$(echo "$risk" | grep '"overall_risk_score"' | sed 's/.*"overall_risk_score": \([^,]*\).*/\1/')
                sort_key=$(printf "%03d" "$sort_key")
                ;;
        esac
        
        sort_data+=("$sort_key|$item")
    done
    
    # 执行排序
    local -a sorted_data
    if [[ "$sort_order" == "desc" ]]; then
        readarray -t sorted_data < <(printf '%s\n' "${sort_data[@]}" | sort -r)
    else
        readarray -t sorted_data < <(printf '%s\n' "${sort_data[@]}" | sort)
    fi
    
    # 重建列表
    LIST_ITEMS=()
    for entry in "${sorted_data[@]}"; do
        LIST_ITEMS+=("${entry#*|}")
    done
    
    log_info "LIST_MANAGER" "排序完成"
}

# 格式化文件大小
format_file_size() {
    local size="$1"
    
    if [[ $size -lt 1024 ]]; then
        echo "${size}B"
    elif [[ $size -lt 1048576 ]]; then
        echo "$((size / 1024))KB"
    elif [[ $size -lt 1073741824 ]]; then
        echo "$((size / 1048576))MB"
    else
        echo "$((size / 1073741824))GB"
    fi
}

# 格式化时间
format_time() {
    local timestamp="$1"
    local format="${2:-%Y-%m-%d %H:%M}"
    
    if command -v date >/dev/null 2>&1; then
        date -d "@$timestamp" +"$format" 2>/dev/null || date -r "$timestamp" +"$format" 2>/dev/null || echo "Unknown"
    else
        echo "$timestamp"
    fi
}

# 显示概览视图
show_overview() {
    local show_colors="${1:-true}"
    
    echo
    if [[ "$show_colors" == "true" ]]; then
        printf "${COLOR_THEME[HEADER]}${COLOR_THEME[BOLD]}"
    fi
    echo "回收站内容概览"
    echo "═══════════════════════════════════════════════════════════════════"
    if [[ "$show_colors" == "true" ]]; then
        printf "${COLOR_THEME[RESET]}"
    fi
    
    # 统计信息
    local total_files=${#LIST_ITEMS[@]}
    local total_size=0
    local -A risk_stats=()
    
    for item in "${LIST_ITEMS[@]}"; do
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local risk="${LIST_METADATA["$item:risk"]}"
        
        # 累计大小
        local size
        size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
        total_size=$((total_size + size))
        
        # 统计风险级别
        local risk_level
        risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
        risk_stats["$risk_level"]=$((risk_stats["$risk_level"] + 1))
    done
    
    # 显示基本统计
    echo "📊 统计信息"
    echo "├─ 总文件数: $total_files 个"
    echo "├─ 总大小: $(format_file_size $total_size)"
    echo "└─ 扫描时间: $(date)"
    echo
    
    # 显示风险分析
    echo "⚠️  风险分析"
    for risk_level in "CRITICAL" "HIGH" "MEDIUM" "LOW" "SAFE"; do
        local count=${risk_stats[$risk_level]:-0}
        if [[ $count -gt 0 ]]; then
            local icon color
            case "$risk_level" in
                "CRITICAL") icon="🔴"; color="${COLOR_THEME[CRITICAL]}" ;;
                "HIGH") icon="🔴"; color="${COLOR_THEME[HIGH]}" ;;
                "MEDIUM") icon="🟡"; color="${COLOR_THEME[MEDIUM]}" ;;
                "LOW") icon="🟢"; color="${COLOR_THEME[LOW]}" ;;
                "SAFE") icon="⚪"; color="${COLOR_THEME[SAFE]}" ;;
            esac
            
            if [[ "$show_colors" == "true" ]]; then
                printf "$color"
            fi
            printf "├─ $icon %-8s: %d 个文件" "$risk_level" "$count"
            if [[ "$show_colors" == "true" ]]; then
                printf "${COLOR_THEME[RESET]}"
            fi
            echo
        fi
    done
    echo
}

# 导出列表
export_list() {
    local output_file="$1"
    local format="${2:-json}"
    
    log_info "LIST_MANAGER" "导出列表到 $output_file (格式: $format)"
    
    case "$format" in
        "json")
            export_list_json "$output_file"
            ;;
        "csv")
            export_list_csv "$output_file"
            ;;
        "txt")
            export_list_txt "$output_file"
            ;;
        *)
            log_error "LIST_MANAGER" "不支持的导出格式: $format"
            return 1
            ;;
    esac
}

# 导出为JSON格式
export_list_json() {
    local output_file="$1"
    
    echo '{"file_list": [' > "$output_file"
    
    local first=true
    for item in "${LIST_ITEMS[@]}"; do
        if [[ "$first" != "true" ]]; then
            echo ',' >> "$output_file"
        fi
        first=false
        
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local risk="${LIST_METADATA["$item:risk"]}"
        local selected="${SELECTION_STATE[$item]}"
        
        # 合并分析和风险数据
        echo "$analysis" | sed '$ s/}$//' >> "$output_file"
        echo ",\"selected\": $selected," >> "$output_file"
        echo "$risk" | sed '1s/^{//' >> "$output_file"
    done
    
    echo ']}' >> "$output_file"
    
    log_info "LIST_MANAGER" "JSON导出完成: $output_file"
}

# 导出为CSV格式
export_list_csv() {
    local output_file="$1"
    
    # 写入表头
    echo "filename,path,type,size,mtime,risk_level,risk_score,selected" > "$output_file"
    
    for item in "${LIST_ITEMS[@]}"; do
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local risk="${LIST_METADATA["$item:risk"]}"
        local selected="${SELECTION_STATE[$item]}"
        
        # 提取数据
        local filename size mtime file_type risk_level risk_score
        filename=$(echo "$analysis" | grep '"filename"' | sed 's/.*"filename": "\([^"]*\)".*/\1/')
        size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
        mtime=$(echo "$analysis" | grep '"mtime"' | sed 's/.*"mtime": \([^,]*\).*/\1/')
        file_type=$(echo "$analysis" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
        risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
        risk_score=$(echo "$risk" | grep '"overall_risk_score"' | sed 's/.*"overall_risk_score": \([^,]*\).*/\1/')
        
        # 写入CSV行
        printf '"%s","%s","%s",%s,%s,"%s",%s,%s\n' \
            "$filename" "$item" "$file_type" "$size" "$mtime" "$risk_level" "$risk_score" "$selected" >> "$output_file"
    done
    
    log_info "LIST_MANAGER" "CSV导出完成: $output_file"
}

# 导出为文本格式
export_list_txt() {
    local output_file="$1"
    
    {
        echo "回收站文件列表报告"
        echo "===================="
        echo "生成时间: $(date)"
        echo "文件总数: ${#LIST_ITEMS[@]}"
        echo ""
        
        # 统计信息
        local total_size=0
        local -A risk_stats=()
        
        for item in "${LIST_ITEMS[@]}"; do
            local analysis="${LIST_METADATA["$item:analysis"]}"
            local risk="${LIST_METADATA["$item:risk"]}"
            
            local size risk_level
            size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
            risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
            
            total_size=$((total_size + size))
            risk_stats["$risk_level"]=$((risk_stats["$risk_level"] + 1))
        done
        
        echo "总大小: $(format_file_size $total_size)"
        echo ""
        echo "风险分布:"
        for level in "CRITICAL" "HIGH" "MEDIUM" "LOW" "SAFE"; do
            local count="${risk_stats[$level]:-0}"
            if [[ $count -gt 0 ]]; then
                echo "  $level: $count 个文件"
            fi
        done
        echo ""
        
        # 文件列表
        echo "详细文件列表:"
        echo "----------------------------------------"
        
        local count=0
        for item in "${LIST_ITEMS[@]}"; do
            ((count++))
            local analysis="${LIST_METADATA["$item:analysis"]}"
            local risk="${LIST_METADATA["$item:risk"]}"
            local selected="${SELECTION_STATE[$item]}"
            
            local filename size mtime file_type risk_level risk_score
            filename=$(echo "$analysis" | grep '"filename"' | sed 's/.*"filename": "\([^"]*\)".*/\1/')
            size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
            mtime=$(echo "$analysis" | grep '"mtime"' | sed 's/.*"mtime": \([^,]*\).*/\1/')
            file_type=$(echo "$analysis" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
            risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
            risk_score=$(echo "$risk" | grep '"overall_risk_score"' | sed 's/.*"overall_risk_score": \([^,]*\).*/\1/')
            
            local selected_mark=""
            if [[ "$selected" == "true" ]]; then
                selected_mark=" [已选中]"
            fi
            
            printf "%4d. %s%s\n" "$count" "$filename" "$selected_mark"
            printf "      路径: %s\n" "$item"
            printf "      类型: %s | 大小: %s | 风险: %s (%s)\n" \
                "$file_type" "$(format_file_size $size)" "$risk_level" "$risk_score"
            printf "      修改时间: %s\n" "$(format_time $mtime)"
            echo ""
        done
        
    } > "$output_file"
    
    log_info "LIST_MANAGER" "文本导出完成: $output_file"
}
main_list_management() {
    local operation="$1"
    shift
    
    case "$operation" in
        "generate")
            generate_file_list "$@"
            ;;
        "filter")
            apply_filters "$1" "$2"
            ;;
        "sort")
            sort_files "$1" "$2"
            ;;
        "overview")
            show_overview "$1"
            ;;
        *)
            echo "错误: 未知操作 '$operation'" >&2
            echo "可用操作: generate, filter, sort, overview" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_list_management "$@"
fi