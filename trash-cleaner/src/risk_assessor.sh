#!/bin/bash

# 风险评估器模块
# 功能：智能风险评估、重要性分析、依赖关系检查、恢复难度评估

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security_checker.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"
source "$(dirname "${BASH_SOURCE[0]}")/file_analyzer.sh"

# 风险级别定义
declare -A RISK_LEVELS=(
    ["SAFE"]=0
    ["LOW"]=25
    ["MEDIUM"]=50
    ["HIGH"]=75
    ["CRITICAL"]=90
)

# 风险因子权重配置
declare -A RISK_WEIGHT_FACTORS=(
    ["file_type"]=0.30
    ["file_size"]=0.20
    ["modification_time"]=0.25
    ["file_location"]=0.15
    ["file_relationships"]=0.10
)

# 重要目录模式
declare -a IMPORTANT_DIRECTORY_PATTERNS=(
    "*/Desktop*"
    "*/Documents*"
    "*/Projects*"
    "*/Work*"
    "*/Important*"
    "*/Backup*"
    "*/Config*"
    "*/Settings*"
)

# 系统文件模式
declare -a SYSTEM_FILE_PATTERNS=(
    "*/System/*"
    "*/Library/*"
    "*/Windows/*"
    "*/Program Files*"
    "*/usr/bin/*"
    "*/etc/*"
    "*/var/*"
    "*.sys"
    "*.dll"
    "*.dylib"
    "*.so"
)

# 评估文件重要性
assess_file_importance() {
    local file_analysis_json="$1"
    local importance_score=0
    
    # 解析文件分析结果
    local file_type extension size mtime dirname importance_base
    file_type=$(echo "$file_analysis_json" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
    extension=$(echo "$file_analysis_json" | grep '"extension"' | sed 's/.*"extension": "\([^"]*\)".*/\1/')
    size=$(echo "$file_analysis_json" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
    mtime=$(echo "$file_analysis_json" | grep '"mtime"' | sed 's/.*"mtime": \([^,]*\).*/\1/')
    dirname=$(echo "$file_analysis_json" | grep '"dirname"' | sed 's/.*"dirname": "\([^"]*\)".*/\1/')
    importance_base=$(echo "$file_analysis_json" | grep '"importance_score"' | sed 's/.*"importance_score": \([^,]*\).*/\1/')
    
    # 使用文件分析器的基础重要性评分
    importance_score=${importance_base:-0}
    
    # 附加重要性因素评估
    
    # 1. 检查特殊文件名模式
    local filename
    filename=$(echo "$file_analysis_json" | grep '"filename"' | sed 's/.*"filename": "\([^"]*\)".*/\1/')
    
    case "$filename" in
        *重要*|*important*|*Important*|*IMPORTANT*)
            importance_score=$((importance_score + 15))
            ;;
        *项目*|*project*|*Project*|*PROJECT*)
            importance_score=$((importance_score + 12))
            ;;
        *配置*|*config*|*Config*|*CONFIG*)
            importance_score=$((importance_score + 10))
            ;;
        *备份*|*backup*|*Backup*|*BACKUP*)
            importance_score=$((importance_score + 10))
            ;;
        *最终*|*final*|*Final*|*FINAL*)
            importance_score=$((importance_score + 8))
            ;;
    esac
    
    # 2. 检查是否在重要目录中
    for pattern in "${IMPORTANT_DIRECTORY_PATTERNS[@]}"; do
        if [[ "$dirname" == $pattern ]]; then
            importance_score=$((importance_score + 10))
            break
        fi
    done
    
    # 3. 检查文件访问频率（基于访问时间）
    local atime current_time days_since_access
    atime=$(echo "$file_analysis_json" | grep '"atime"' | sed 's/.*"atime": \([^,]*\).*/\1/')
    current_time=$(date +%s)
    days_since_access=$(( (current_time - atime) / 86400 ))
    
    if [[ $days_since_access -le 7 ]]; then
        importance_score=$((importance_score + 8))
    elif [[ $days_since_access -le 30 ]]; then
        importance_score=$((importance_score + 5))
    fi
    
    # 确保评分在合理范围内
    if [[ $importance_score -gt 100 ]]; then
        importance_score=100
    elif [[ $importance_score -lt 0 ]]; then
        importance_score=0
    fi
    
    echo "$importance_score"
}

# 检测系统文件
detect_system_files() {
    local file_path="$1"
    
    # 检查是否匹配系统文件模式
    for pattern in "${SYSTEM_FILE_PATTERNS[@]}"; do
        if [[ "$file_path" == $pattern ]]; then
            echo "true"
            return 0
        fi
    done
    
    # 检查文件权限（系统文件通常有特殊权限）
    if [[ -f "$file_path" ]]; then
        local permissions
        if command -v stat >/dev/null 2>&1; then
            if stat -c "%a" "$file_path" >/dev/null 2>&1; then
                permissions=$(stat -c "%a" "$file_path" 2>/dev/null)
            elif stat -f "%p" "$file_path" >/dev/null 2>&1; then
                permissions=$(stat -f "%p" "$file_path" 2>/dev/null)
                permissions=$(printf "%o" "$permissions")
            fi
        fi
        
        # 检查是否有执行权限或特殊权限
        if [[ "$permissions" =~ ^[4567][0-9][0-9]$ ]] || [[ "$permissions" =~ ^[0-9][4567][0-9]$ ]]; then
            echo "true"
            return 0
        fi
    fi
    
    echo "false"
    return 1
}

# 检查文件依赖关系
check_file_dependencies() {
    local file_path="$1"
    local dependencies=[]
    
    # 检查关联文件（从文件分析结果中获取）
    local analysis_result
    analysis_result=$(analyze_file "$file_path")
    local related_files
    related_files=$(echo "$analysis_result" | grep '"related_files"' | sed 's/.*"related_files": \(\[.*\]\).*/\1/')
    
    if [[ "$related_files" != "[]" ]]; then
        dependencies="$related_files"
    fi
    
    # 检查配置文件依赖
    local filename extension
    filename=$(basename "$file_path")
    extension="${filename##*.}"
    
    case "$extension" in
        "app"|"exe")
            # 应用程序可能依赖配置文件
            local app_name="${filename%.*}"
            local base_dir
            base_dir=$(dirname "$file_path")
            
            # 查找可能的配置文件
            local config_files=()
            while IFS= read -r -d '' config_file; do
                config_files+=("\"$config_file\"")
            done < <(find "$base_dir" -maxdepth 2 \( -name "${app_name}.cfg" -o -name "${app_name}.conf" -o -name "${app_name}.ini" -o -name "${app_name}.plist" \) -print0 2>/dev/null)
            
            if [[ ${#config_files[@]} -gt 0 ]]; then
                dependencies="[$(IFS=,; echo "${config_files[*]}")]"
            fi
            ;;
    esac
    
    echo "$dependencies"
}

# 评估恢复难度
evaluate_recovery_difficulty() {
    local file_analysis_json="$1"
    local difficulty_score=0
    
    # 解析文件信息
    local file_type backup_exists size
    file_type=$(echo "$file_analysis_json" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
    backup_exists=$(echo "$file_analysis_json" | grep '"backup_exists"' | sed 's/.*"backup_exists": \([^,]*\).*/\1/')
    size=$(echo "$file_analysis_json" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
    
    # 基于文件类型的恢复难度
    case "$file_type" in
        "document"|"spreadsheet"|"presentation")
            difficulty_score=80  # 文档类文件恢复困难
            ;;
        "image"|"video"|"audio")
            difficulty_score=60  # 媒体文件有一定恢复可能
            ;;
        "code"|"config")
            difficulty_score=90  # 代码和配置文件恢复很困难
            ;;
        "archive")
            difficulty_score=70  # 压缩文件恢复中等难度
            ;;
        "temporary"|"cache")
            difficulty_score=20  # 临时文件容易重新生成
            ;;
        *)
            difficulty_score=50  # 其他文件中等难度
            ;;
    esac
    
    # 备份存在性影响恢复难度
    if [[ "$backup_exists" == "true" ]]; then
        difficulty_score=$((difficulty_score - 30))
    fi
    
    # 文件大小影响恢复难度（越大越难恢复）
    if [[ $size -gt 1073741824 ]]; then  # > 1GB
        difficulty_score=$((difficulty_score + 20))
    elif [[ $size -gt 104857600 ]]; then  # > 100MB
        difficulty_score=$((difficulty_score + 10))
    fi
    
    # 确保评分在0-100范围内
    if [[ $difficulty_score -gt 100 ]]; then
        difficulty_score=100
    elif [[ $difficulty_score -lt 0 ]]; then
        difficulty_score=0
    fi
    
    echo "$difficulty_score"
}

# 生成风险报告
generate_risk_report() {
    local file_analysis_json="$1"
    
    # 获取各项风险评估结果
    local importance_score system_file dependencies recovery_difficulty
    importance_score=$(assess_file_importance "$file_analysis_json")
    
    local file_path
    file_path=$(echo "$file_analysis_json" | grep '"path"' | sed 's/.*"path": "\([^"]*\)".*/\1/')
    system_file=$(detect_system_files "$file_path")
    dependencies=$(check_file_dependencies "$file_path")
    recovery_difficulty=$(evaluate_recovery_difficulty "$file_analysis_json")
    
    # 计算综合风险评分
    local overall_risk_score
    overall_risk_score=$((importance_score * 70 / 100 + recovery_difficulty * 30 / 100))
    
    # 确定风险等级
    local risk_level risk_color
    if [[ $overall_risk_score -ge 85 ]]; then
        risk_level="CRITICAL"
        risk_color="red"
    elif [[ $overall_risk_score -ge 70 ]]; then
        risk_level="HIGH"
        risk_color="red"
    elif [[ $overall_risk_score -ge 50 ]]; then
        risk_level="MEDIUM"
        risk_color="yellow"
    elif [[ $overall_risk_score -ge 25 ]]; then
        risk_level="LOW"
        risk_color="green"
    else
        risk_level="SAFE"
        risk_color="green"
    fi
    
    # 生成风险原因列表
    local risk_reasons=()
    
    if [[ $importance_score -ge 70 ]]; then
        risk_reasons+=("\"high_importance\"")
    fi
    
    if [[ "$system_file" == "true" ]]; then
        risk_reasons+=("\"system_file\"")
    fi
    
    if [[ "$dependencies" != "[]" ]]; then
        risk_reasons+=("\"has_dependencies\"")
    fi
    
    if [[ $recovery_difficulty -ge 70 ]]; then
        risk_reasons+=("\"difficult_to_recover\"")
    fi
    
    local backup_exists
    backup_exists=$(echo "$file_analysis_json" | grep '"backup_exists"' | sed 's/.*"backup_exists": \([^,]*\).*/\1/')
    if [[ "$backup_exists" == "false" ]]; then
        risk_reasons+=("\"no_backup\"")
    fi
    
    # 构建风险报告JSON
    local risk_reasons_json="[$(IFS=,; echo "${risk_reasons[*]}")]"
    
    cat <<EOF
{
    "file_path": "$file_path",
    "overall_risk_score": $overall_risk_score,
    "risk_level": "$risk_level",
    "risk_color": "$risk_color",
    "importance_score": $importance_score,
    "recovery_difficulty": $recovery_difficulty,
    "is_system_file": $system_file,
    "dependencies": $dependencies,
    "risk_reasons": $risk_reasons_json,
    "assessment_time": $(date +%s)
}
EOF
}

# 建议替代方案
suggest_alternatives() {
    local risk_report_json="$1"
    local suggestions=()
    
    # 解析风险报告
    local risk_level backup_exists
    risk_level=$(echo "$risk_report_json" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
    
    local file_analysis
    local file_path
    file_path=$(echo "$risk_report_json" | grep '"file_path"' | sed 's/.*"file_path": "\([^"]*\)".*/\1/')
    file_analysis=$(analyze_file "$file_path")
    backup_exists=$(echo "$file_analysis" | grep '"backup_exists"' | sed 's/.*"backup_exists": \([^,]*\).*/\1/')
    
    case "$risk_level" in
        "CRITICAL"|"HIGH")
            suggestions+=("\"create_backup_before_deletion\"")
            suggestions+=("\"manual_review_recommended\"")
            if [[ "$backup_exists" == "false" ]]; then
                suggestions+=("\"backup_not_found_proceed_with_caution\"")
            fi
            ;;
        "MEDIUM")
            suggestions+=("\"consider_backup\"")
            suggestions+=("\"review_file_content\"")
            ;;
        "LOW")
            suggestions+=("\"safe_to_delete\"")
            ;;
        "SAFE")
            suggestions+=("\"recommended_for_deletion\"")
            ;;
    esac
    
    # 检查文件大小
    local size
    size=$(echo "$file_analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
    if [[ $size -gt 1073741824 ]]; then  # > 1GB
        suggestions+=("\"large_file_consider_storage_benefit\"")
    fi
    
    # 检查修改时间
    local mtime current_time days_old
    mtime=$(echo "$file_analysis" | grep '"mtime"' | sed 's/.*"mtime": \([^,]*\).*/\1/')
    current_time=$(date +%s)
    days_old=$(( (current_time - mtime) / 86400 ))
    
    if [[ $days_old -gt 365 ]]; then
        suggestions+=("\"old_file_likely_unused\"")
    elif [[ $days_old -le 7 ]]; then
        suggestions+=("\"recently_modified_check_importance\"")
    fi
    
    # 输出建议JSON数组
    local suggestions_json="[$(IFS=,; echo "${suggestions[*]}")]"
    echo "$suggestions_json"
}

# 批量风险评估
batch_risk_assessment() {
    local files=("$@")
    local total_files=${#files[@]}
    local current=0
    
    log_info "RISK_ASSESSOR" "开始批量风险评估 $total_files 个文件"
    
    # 风险统计
    local -A risk_stats=(
        ["SAFE"]=0
        ["LOW"]=0
        ["MEDIUM"]=0
        ["HIGH"]=0
        ["CRITICAL"]=0
    )
    
    echo '{"risk_assessment_results": ['
    
    local first=true
    for file_path in "${files[@]}"; do
        ((current++))
        
        if is_config_true "progress_bar"; then
            printf "\r风险评估进度: %d/%d (%d%%)" "$current" "$total_files" $((current * 100 / total_files)) >&2
        fi
        
        # 分析文件
        local file_analysis
        file_analysis=$(analyze_file "$file_path")
        
        if [[ $? -eq 0 ]]; then
            # 生成风险报告
            local risk_report
            risk_report=$(generate_risk_report "$file_analysis")
            
            # 生成建议
            local suggestions
            suggestions=$(suggest_alternatives "$risk_report")
            
            # 更新统计
            local risk_level
            risk_level=$(echo "$risk_report" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
            risk_stats["$risk_level"]=$((risk_stats["$risk_level"] + 1))
            
            # 输出结果
            if [[ "$first" != "true" ]]; then
                echo ','
            fi
            first=false
            
            # 合并风险报告和建议
            echo "$risk_report" | sed '$ s/}$//' | cat - <<EOF
,
    "suggestions": $suggestions
}
EOF
        fi
    done
    
    echo '],'
    
    # 输出风险统计
    cat <<EOF
"risk_statistics": {
    "total_files": $total_files,
    "safe": ${risk_stats["SAFE"]},
    "low_risk": ${risk_stats["LOW"]},
    "medium_risk": ${risk_stats["MEDIUM"]},
    "high_risk": ${risk_stats["HIGH"]},
    "critical_risk": ${risk_stats["CRITICAL"]}
},
"assessment_time": $(date +%s)
}
EOF
    
    if is_config_true "progress_bar"; then
        echo >&2  # 换行
    fi
    
    log_info "RISK_ASSESSOR" "批量风险评估完成"
}

# 设置风险权重因子
set_risk_weight_factors() {
    local factor_name="$1"
    local weight_value="$2"
    
    if [[ -n "${RISK_WEIGHT_FACTORS[$factor_name]:-}" ]]; then
        RISK_WEIGHT_FACTORS["$factor_name"]="$weight_value"
        log_info "RISK_ASSESSOR" "风险权重因子已更新: $factor_name = $weight_value"
    else
        log_error "RISK_ASSESSOR" "未知的风险权重因子: $factor_name"
        return 1
    fi
}

# 获取风险配置
get_risk_configuration() {
    echo "风险权重因子配置:"
    for factor in "${!RISK_WEIGHT_FACTORS[@]}"; do
        echo "  $factor: ${RISK_WEIGHT_FACTORS[$factor]}"
    done
    
    echo ""
    echo "风险级别阈值:"
    for level in "${!RISK_LEVELS[@]}"; do
        echo "  $level: ${RISK_LEVELS[$level]}"
    done
}

# 模块初始化
init_risk_assessor() {
    log_info "RISK_ASSESSOR" "初始化风险评估器模块"
    
    # 初始化文件分析器（依赖）
    init_file_analyzer
    
    # 从配置文件加载自定义风险权重（如果存在）
    local config_weight
    config_weight=$(get_config "risk_weight_file_type" "0.30")
    RISK_WEIGHT_FACTORS["file_type"]="$config_weight"
    
    config_weight=$(get_config "risk_weight_file_size" "0.20")
    RISK_WEIGHT_FACTORS["file_size"]="$config_weight"
    
    config_weight=$(get_config "risk_weight_modification_time" "0.25")
    RISK_WEIGHT_FACTORS["modification_time"]="$config_weight"
    
    config_weight=$(get_config "risk_weight_file_location" "0.15")
    RISK_WEIGHT_FACTORS["file_location"]="$config_weight"
    
    config_weight=$(get_config "risk_weight_file_relationships" "0.10")
    RISK_WEIGHT_FACTORS["file_relationships"]="$config_weight"
    
    log_info "RISK_ASSESSOR" "风险评估器模块初始化完成"
}

# 主风险评估入口函数
main_risk_assessment() {
    local operation="$1"
    shift
    
    case "$operation" in
        "init")
            init_risk_assessor
            ;;
        "assess")
            local file_path="$1"
            local file_analysis
            file_analysis=$(analyze_file "$file_path")
            generate_risk_report "$file_analysis"
            ;;
        "batch")
            batch_risk_assessment "$@"
            ;;
        "config")
            get_risk_configuration
            ;;
        "set-weight")
            set_risk_weight_factors "$1" "$2"
            ;;
        *)
            echo "错误: 未知操作 '$operation'" >&2
            echo "可用操作: init, assess, batch, config, set-weight" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_risk_assessment "$@"
fi