#!/bin/bash

# 预检查引擎模块
# 功能：整合文件分析、风险评估、列表管理，提供统一的预检查接口

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security_checker.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"
source "$(dirname "${BASH_SOURCE[0]}")/file_analyzer.sh"
source "$(dirname "${BASH_SOURCE[0]}")/risk_assessor.sh"
source "$(dirname "${BASH_SOURCE[0]}")/list_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/interaction_manager.sh"

# 预检查结果存储
declare -A PRECHECK_RESULTS=()
declare -A PRECHECK_STATS=()

# 预检查配置
declare -A PRECHECK_CONFIG=(
    ["enable_file_analysis"]=true
    ["enable_risk_assessment"]=true
    ["enable_interactive_mode"]=true
    ["min_risk_threshold"]=0
    ["max_items_preview"]=50
    ["auto_mark_safe_files"]=false
)

# 初始化预检查引擎
init_precheck_engine() {
    log_info "PRECHECK_ENGINE" "初始化预检查引擎"
    
    # 初始化所有子模块
    init_file_analyzer
    init_risk_assessor
    
    # 从配置文件加载设置
    local config_value
    config_value=$(get_config "enable_risk_analysis" "true")
    PRECHECK_CONFIG["enable_risk_assessment"]="$config_value"
    
    config_value=$(get_config "interactive_mode" "true")
    PRECHECK_CONFIG["enable_interactive_mode"]="$config_value"
    
    config_value=$(get_config "min_risk_threshold" "0")
    PRECHECK_CONFIG["min_risk_threshold"]="$config_value"
    
    log_info "PRECHECK_ENGINE" "预检查引擎初始化完成"
}

# 执行完整预检查
run_full_precheck() {
    local files=("$@")
    local total_files=${#files[@]}
    
    if [[ $total_files -eq 0 ]]; then
        log_warn "PRECHECK_ENGINE" "没有文件需要预检查"
        return 1
    fi
    
    log_info "PRECHECK_ENGINE" "开始完整预检查，共 $total_files 个文件"
    
    # 重置结果
    PRECHECK_RESULTS=()
    PRECHECK_STATS=()
    
    # 初始化统计
    PRECHECK_STATS["total_files"]=$total_files
    PRECHECK_STATS["analyzed_files"]=0
    PRECHECK_STATS["high_risk_files"]=0
    PRECHECK_STATS["safe_files"]=0
    PRECHECK_STATS["total_size"]=0
    PRECHECK_STATS["start_time"]=$(date +%s)
    
    echo "正在执行预检查分析..."
    
    # 第1步：生成文件列表
    echo "步骤 1/3: 生成文件列表..."
    generate_file_list "${files[@]}"
    
    # 第2步：执行风险评估（如果启用）
    if [[ "${PRECHECK_CONFIG[enable_risk_assessment]}" == "true" ]]; then
        echo "步骤 2/3: 执行风险评估..."
        
        # 统计风险级别
        local -A risk_counts=()
        for item in "${LIST_ITEMS[@]}"; do
            local risk="${LIST_METADATA["$item:risk"]}"
            local risk_level
            risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
            risk_counts["$risk_level"]=$((risk_counts["$risk_level"] + 1))
            
            # 更新统计
            PRECHECK_STATS["analyzed_files"]=$((PRECHECK_STATS["analyzed_files"] + 1))
            
            if [[ "$risk_level" == "HIGH" ]] || [[ "$risk_level" == "CRITICAL" ]]; then
                PRECHECK_STATS["high_risk_files"]=$((PRECHECK_STATS["high_risk_files"] + 1))
            elif [[ "$risk_level" == "SAFE" ]]; then
                PRECHECK_STATS["safe_files"]=$((PRECHECK_STATS["safe_files"] + 1))
            fi
            
            # 累计文件大小
            local analysis="${LIST_METADATA["$item:analysis"]}"
            local size
            size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
            PRECHECK_STATS["total_size"]=$((PRECHECK_STATS["total_size"] + size))
        done
        
        # 存储风险统计
        for risk_level in "${!risk_counts[@]}"; do
            PRECHECK_STATS["risk_$risk_level"]="${risk_counts[$risk_level]}"
        done
    fi
    
    # 第3步：生成预检查报告
    echo "步骤 3/3: 生成预检查报告..."
    PRECHECK_STATS["end_time"]=$(date +%s)
    PRECHECK_STATS["duration"]=$((PRECHECK_STATS["end_time"] - PRECHECK_STATS["start_time"]))
    
    # 自动标记安全文件（如果启用）
    if [[ "${PRECHECK_CONFIG[auto_mark_safe_files]}" == "true" ]]; then
        auto_mark_safe_files
    fi
    
    log_info "PRECHECK_ENGINE" "预检查完成，耗时 ${PRECHECK_STATS[duration]} 秒"
    
    return 0
}

# 自动标记安全文件
auto_mark_safe_files() {
    log_info "PRECHECK_ENGINE" "自动标记安全文件"
    
    local marked_count=0
    for item in "${LIST_ITEMS[@]}"; do
        local risk="${LIST_METADATA["$item:risk"]}"
        local risk_level
        risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
        
        if [[ "$risk_level" == "SAFE" ]]; then
            SELECTION_STATE["$item"]=true
            ((marked_count++))
        fi
    done
    
    log_info "PRECHECK_ENGINE" "自动标记了 $marked_count 个安全文件"
}

# 显示预检查摘要
show_precheck_summary() {
    local show_colors="${1:-true}"
    
    echo
    if [[ "$show_colors" == "true" ]]; then
        printf "\033[1;36m\033[1m"
    fi
    echo "预检查结果摘要"
    echo "═══════════════════════════════════════════════════════════════════"
    if [[ "$show_colors" == "true" ]]; then
        printf "\033[0m"
    fi
    
    # 基本统计
    echo "📊 基本统计:"
    echo "├─ 分析文件数: ${PRECHECK_STATS[analyzed_files]:-0} / ${PRECHECK_STATS[total_files]:-0}"
    echo "├─ 总文件大小: $(format_file_size ${PRECHECK_STATS[total_size]:-0})"
    echo "├─ 处理时间: ${PRECHECK_STATS[duration]:-0} 秒"
    echo "└─ 分析速度: $(( ${PRECHECK_STATS[analyzed_files]:-0} / (${PRECHECK_STATS[duration]:-1} + 1) )) 文件/秒"
    echo
    
    # 风险分析摘要
    if [[ "${PRECHECK_CONFIG[enable_risk_assessment]}" == "true" ]]; then
        echo "⚠️  风险分析摘要:"
        
        # 使用彩色显示风险级别
        for risk_level in "CRITICAL" "HIGH" "MEDIUM" "LOW" "SAFE"; do
            local count="${PRECHECK_STATS[risk_$risk_level]:-0}"
            if [[ $count -gt 0 ]]; then
                local icon color
                case "$risk_level" in
                    "CRITICAL") icon="🔴"; color="\033[1;31m" ;;
                    "HIGH") icon="🔴"; color="\033[31m" ;;
                    "MEDIUM") icon="🟡"; color="\033[33m" ;;
                    "LOW") icon="🟢"; color="\033[32m" ;;
                    "SAFE") icon="⚪"; color="\033[37m" ;;
                esac
                
                if [[ "$show_colors" == "true" ]]; then
                    printf "$color"
                fi
                printf "├─ $icon %-8s: %d 个文件" "$risk_level" "$count"
                if [[ "$show_colors" == "true" ]]; then
                    printf "\033[0m"
                fi
                echo
            fi
        done
        echo
    fi
    
    # 建议操作
    echo "💡 建议操作:"
    
    local high_risk_total=$((${PRECHECK_STATS[risk_CRITICAL]:-0} + ${PRECHECK_STATS[risk_HIGH]:-0}))
    local safe_total="${PRECHECK_STATS[risk_SAFE]:-0}"
    
    if [[ $high_risk_total -gt 0 ]]; then
        echo "├─ ⚠️  发现 $high_risk_total 个高风险文件，建议手动检查"
    fi
    
    if [[ $safe_total -gt 0 ]]; then
        echo "├─ ✅ 发现 $safe_total 个安全文件，可以安全删除"
    fi
    
    if [[ "${PRECHECK_CONFIG[enable_interactive_mode]}" == "true" ]]; then
        echo "└─ 🖱️  建议使用交互模式进行精确选择"
    else
        echo "└─ 🤖 自动模式已启用，将按配置执行"
    fi
    echo
}

# 应用预检查过滤器
apply_precheck_filters() {
    local min_risk="${1:-${PRECHECK_CONFIG[min_risk_threshold]}}"
    
    log_debug "PRECHECK_ENGINE" "应用预检查过滤器，最低风险阈值: $min_risk"
    
    if [[ $min_risk -le 0 ]]; then
        return 0  # 不应用过滤
    fi
    
    local filtered_items=()
    
    for item in "${LIST_ITEMS[@]}"; do
        local risk="${LIST_METADATA["$item:risk"]}"
        local risk_score
        risk_score=$(echo "$risk" | grep '"overall_risk_score"' | sed 's/.*"overall_risk_score": \([^,]*\).*/\1/')
        
        if [[ $risk_score -ge $min_risk ]]; then
            filtered_items+=("$item")
        fi
    done
    
    LIST_ITEMS=("${filtered_items[@]}")
    
    log_info "PRECHECK_ENGINE" "过滤后剩余 ${#LIST_ITEMS[@]} 个项目"
}

# 启动交互式预检查
start_interactive_precheck() {
    log_info "PRECHECK_ENGINE" "启动交互式预检查"
    
    # 显示预检查摘要
    show_precheck_summary true
    
    # 询问用户是否要进入交互模式
    echo "是否要进入交互式选择模式？"
    echo " y) 是 - 精确选择要删除的文件"
    echo " n) 否 - 使用当前分析结果"
    echo " c) 取消 - 退出操作"
    echo
    
    echo -n "请选择 [y/n/c]: "
    local choice
    read -r choice
    
    case "$choice" in
        y|Y|yes|YES)
            # 运行交互式会话
            run_interactive_session
            ;;
        n|N|no|NO)
            # 直接使用预检查结果
            return 0
            ;;
        c|C|cancel|CANCEL)
            log_info "PRECHECK_ENGINE" "用户取消预检查操作"
            return 1
            ;;
        *)
            echo "无效选择，默认进入交互模式"
            run_interactive_session
            ;;
    esac
}

# 获取选中的文件列表
get_selected_files() {
    local selected_files=()
    
    for item in "${LIST_ITEMS[@]}"; do
        if [[ "${SELECTION_STATE[$item]}" == "true" ]]; then
            selected_files+=("$item")
        fi
    done
    
    printf '%s\n' "${selected_files[@]}"
}

# 生成预检查报告
generate_precheck_report() {
    local output_file="$1"
    local format="${2:-json}"
    
    log_info "PRECHECK_ENGINE" "生成预检查报告: $output_file (格式: $format)"
    
    case "$format" in
        "json")
            generate_json_report "$output_file"
            ;;
        "text")
            generate_text_report "$output_file"
            ;;
        *)
            log_error "PRECHECK_ENGINE" "不支持的报告格式: $format"
            return 1
            ;;
    esac
}

# 生成JSON格式报告
generate_json_report() {
    local output_file="$1"
    
    cat > "$output_file" <<EOF
{
    "precheck_report": {
        "timestamp": "$(date -Iseconds)",
        "version": "1.0",
        "statistics": {
            "total_files": ${PRECHECK_STATS[total_files]:-0},
            "analyzed_files": ${PRECHECK_STATS[analyzed_files]:-0},
            "high_risk_files": ${PRECHECK_STATS[high_risk_files]:-0},
            "safe_files": ${PRECHECK_STATS[safe_files]:-0},
            "total_size_bytes": ${PRECHECK_STATS[total_size]:-0},
            "processing_time_seconds": ${PRECHECK_STATS[duration]:-0}
        },
        "risk_distribution": {
            "critical": ${PRECHECK_STATS[risk_CRITICAL]:-0},
            "high": ${PRECHECK_STATS[risk_HIGH]:-0},
            "medium": ${PRECHECK_STATS[risk_MEDIUM]:-0},
            "low": ${PRECHECK_STATS[risk_LOW]:-0},
            "safe": ${PRECHECK_STATS[risk_SAFE]:-0}
        },
        "configuration": {
            "enable_risk_assessment": ${PRECHECK_CONFIG[enable_risk_assessment]},
            "enable_interactive_mode": ${PRECHECK_CONFIG[enable_interactive_mode]},
            "min_risk_threshold": ${PRECHECK_CONFIG[min_risk_threshold]},
            "auto_mark_safe_files": ${PRECHECK_CONFIG[auto_mark_safe_files]}
        }
    }
}
EOF
    
    log_info "PRECHECK_ENGINE" "JSON报告已生成: $output_file"
}

# 生成文本格式报告
generate_text_report() {
    local output_file="$1"
    
    {
        echo "回收站预检查报告"
        echo "==================="
        echo "生成时间: $(date)"
        echo "报告版本: 1.0"
        echo ""
        
        echo "基本统计:"
        echo "  总文件数: ${PRECHECK_STATS[total_files]:-0}"
        echo "  已分析: ${PRECHECK_STATS[analyzed_files]:-0}"
        echo "  高风险文件: ${PRECHECK_STATS[high_risk_files]:-0}"  
        echo "  安全文件: ${PRECHECK_STATS[safe_files]:-0}"
        echo "  总大小: $(format_file_size ${PRECHECK_STATS[total_size]:-0})"
        echo "  处理时间: ${PRECHECK_STATS[duration]:-0} 秒"
        echo ""
        
        echo "风险分布:"
        for risk_level in "CRITICAL" "HIGH" "MEDIUM" "LOW" "SAFE"; do
            local count="${PRECHECK_STATS[risk_$risk_level]:-0}"
            echo "  $risk_level: $count"
        done
        echo ""
        
        echo "配置信息:"
        echo "  风险评估: ${PRECHECK_CONFIG[enable_risk_assessment]}"
        echo "  交互模式: ${PRECHECK_CONFIG[enable_interactive_mode]}"
        echo "  风险阈值: ${PRECHECK_CONFIG[min_risk_threshold]}"
        echo "  自动标记安全文件: ${PRECHECK_CONFIG[auto_mark_safe_files]}"
        
    } > "$output_file"
    
    log_info "PRECHECK_ENGINE" "文本报告已生成: $output_file"
}

# 主预检查入口函数
main_precheck() {
    local operation="$1"
    shift
    
    case "$operation" in
        "init")
            init_precheck_engine
            ;;
        "run")
            run_full_precheck "$@"
            ;;
        "summary")
            show_precheck_summary "$1"
            ;;
        "interactive")
            start_interactive_precheck
            ;;
        "selected")
            get_selected_files
            ;;
        "report")
            generate_precheck_report "$1" "$2"
            ;;
        *)
            echo "错误: 未知操作 '$operation'" >&2
            echo "可用操作: init, run, summary, interactive, selected, report" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_precheck "$@"
fi