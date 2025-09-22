#!/bin/bash

# 文件分析器模块
# 功能：智能文件分析、类型识别、元数据提取、风险评估

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/system_detector.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security_checker.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config_manager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"

# 文件分析结果存储
declare -A FILE_ANALYSIS_CACHE=()
declare -A FILE_TYPE_MAPPING=()
declare -A IMPORTANT_EXTENSIONS=()

# 初始化文件类型映射
init_file_type_mapping() {
    # 文档类型
    FILE_TYPE_MAPPING["doc"]="document"
    FILE_TYPE_MAPPING["docx"]="document"
    FILE_TYPE_MAPPING["pdf"]="document"
    FILE_TYPE_MAPPING["txt"]="document"
    FILE_TYPE_MAPPING["rtf"]="document"
    FILE_TYPE_MAPPING["odt"]="document"
    FILE_TYPE_MAPPING["pages"]="document"
    
    # 表格类型
    FILE_TYPE_MAPPING["xls"]="spreadsheet"
    FILE_TYPE_MAPPING["xlsx"]="spreadsheet"
    FILE_TYPE_MAPPING["csv"]="spreadsheet"
    FILE_TYPE_MAPPING["ods"]="spreadsheet"
    FILE_TYPE_MAPPING["numbers"]="spreadsheet"
    
    # 演示文稿
    FILE_TYPE_MAPPING["ppt"]="presentation"
    FILE_TYPE_MAPPING["pptx"]="presentation"
    FILE_TYPE_MAPPING["key"]="presentation"
    FILE_TYPE_MAPPING["odp"]="presentation"
    
    # 图片类型
    FILE_TYPE_MAPPING["jpg"]="image"
    FILE_TYPE_MAPPING["jpeg"]="image"
    FILE_TYPE_MAPPING["png"]="image"
    FILE_TYPE_MAPPING["gif"]="image"
    FILE_TYPE_MAPPING["bmp"]="image"
    FILE_TYPE_MAPPING["svg"]="image"
    FILE_TYPE_MAPPING["tiff"]="image"
    FILE_TYPE_MAPPING["webp"]="image"
    FILE_TYPE_MAPPING["ico"]="image"
    FILE_TYPE_MAPPING["raw"]="image"
    FILE_TYPE_MAPPING["cr2"]="image"
    FILE_TYPE_MAPPING["nef"]="image"
    
    # 音频类型
    FILE_TYPE_MAPPING["mp3"]="audio"
    FILE_TYPE_MAPPING["wav"]="audio"
    FILE_TYPE_MAPPING["flac"]="audio"
    FILE_TYPE_MAPPING["aac"]="audio"
    FILE_TYPE_MAPPING["ogg"]="audio"
    FILE_TYPE_MAPPING["wma"]="audio"
    FILE_TYPE_MAPPING["m4a"]="audio"
    
    # 视频类型
    FILE_TYPE_MAPPING["mp4"]="video"
    FILE_TYPE_MAPPING["avi"]="video"
    FILE_TYPE_MAPPING["mkv"]="video"
    FILE_TYPE_MAPPING["wmv"]="video"
    FILE_TYPE_MAPPING["flv"]="video"
    FILE_TYPE_MAPPING["webm"]="video"
    FILE_TYPE_MAPPING["mov"]="video"
    FILE_TYPE_MAPPING["3gp"]="video"
    
    # 压缩文件
    FILE_TYPE_MAPPING["zip"]="archive"
    FILE_TYPE_MAPPING["rar"]="archive"
    FILE_TYPE_MAPPING["7z"]="archive"
    FILE_TYPE_MAPPING["tar"]="archive"
    FILE_TYPE_MAPPING["gz"]="archive"
    FILE_TYPE_MAPPING["bz2"]="archive"
    FILE_TYPE_MAPPING["xz"]="archive"
    FILE_TYPE_MAPPING["dmg"]="archive"
    FILE_TYPE_MAPPING["iso"]="archive"
    
    # 程序文件
    FILE_TYPE_MAPPING["exe"]="executable"
    FILE_TYPE_MAPPING["msi"]="executable"
    FILE_TYPE_MAPPING["deb"]="executable"
    FILE_TYPE_MAPPING["rpm"]="executable"
    FILE_TYPE_MAPPING["pkg"]="executable"
    FILE_TYPE_MAPPING["app"]="executable"
    
    # 代码文件
    FILE_TYPE_MAPPING["c"]="code"
    FILE_TYPE_MAPPING["cpp"]="code"
    FILE_TYPE_MAPPING["h"]="code"
    FILE_TYPE_MAPPING["py"]="code"
    FILE_TYPE_MAPPING["js"]="code"
    FILE_TYPE_MAPPING["html"]="code"
    FILE_TYPE_MAPPING["css"]="code"
    FILE_TYPE_MAPPING["php"]="code"
    FILE_TYPE_MAPPING["java"]="code"
    FILE_TYPE_MAPPING["sh"]="code"
    FILE_TYPE_MAPPING["bash"]="code"
    FILE_TYPE_MAPPING["sql"]="code"
    FILE_TYPE_MAPPING["xml"]="code"
    FILE_TYPE_MAPPING["json"]="code"
    FILE_TYPE_MAPPING["yaml"]="code"
    FILE_TYPE_MAPPING["yml"]="code"
    
    # 配置文件
    FILE_TYPE_MAPPING["conf"]="config"
    FILE_TYPE_MAPPING["cfg"]="config"
    FILE_TYPE_MAPPING["ini"]="config"
    FILE_TYPE_MAPPING["plist"]="config"
    FILE_TYPE_MAPPING["properties"]="config"
    
    # 临时和缓存文件
    FILE_TYPE_MAPPING["tmp"]="temporary"
    FILE_TYPE_MAPPING["temp"]="temporary"
    FILE_TYPE_MAPPING["cache"]="temporary"
    FILE_TYPE_MAPPING["log"]="temporary"
    FILE_TYPE_MAPPING["bak"]="temporary"
    FILE_TYPE_MAPPING["old"]="temporary"
    FILE_TYPE_MAPPING["swp"]="temporary"
    FILE_TYPE_MAPPING["~"]="temporary"
}

# 初始化重要文件扩展名
init_important_extensions() {
    # 高重要性文件扩展名及其权重
    IMPORTANT_EXTENSIONS["docx"]=90
    IMPORTANT_EXTENSIONS["xlsx"]=90
    IMPORTANT_EXTENSIONS["pptx"]=85
    IMPORTANT_EXTENSIONS["pdf"]=85
    IMPORTANT_EXTENSIONS["key"]=80
    IMPORTANT_EXTENSIONS["numbers"]=80
    IMPORTANT_EXTENSIONS["pages"]=80
    IMPORTANT_EXTENSIONS["json"]=75
    IMPORTANT_EXTENSIONS["xml"]=70
    IMPORTANT_EXTENSIONS["sql"]=70
    IMPORTANT_EXTENSIONS["plist"]=65
    IMPORTANT_EXTENSIONS["conf"]=60
    IMPORTANT_EXTENSIONS["cfg"]=60
    IMPORTANT_EXTENSIONS["ini"]=55
}

# 检测文件类型
detect_file_type() {
    local file_path="$1"
    
    # 获取文件扩展名
    local extension=""
    if [[ "$file_path" =~ \.([^.]+)$ ]]; then
        extension="${BASH_REMATCH[1],,}"  # 转换为小写
    fi
    
    # 查找映射的文件类型
    local file_type="${FILE_TYPE_MAPPING[$extension]:-unknown}"
    
    # 如果无法通过扩展名确定，尝试使用file命令
    if [[ "$file_type" == "unknown" ]] && command -v file >/dev/null 2>&1; then
        local mime_type
        mime_type=$(file -b --mime-type "$file_path" 2>/dev/null)
        
        case "$mime_type" in
            text/*)
                file_type="document"
                ;;
            image/*)
                file_type="image"
                ;;
            audio/*)
                file_type="audio"
                ;;
            video/*)
                file_type="video"
                ;;
            application/pdf)
                file_type="document"
                ;;
            application/zip|application/x-rar*|application/x-7z*)
                file_type="archive"
                ;;
            application/x-executable)
                file_type="executable"
                ;;
        esac
    fi
    
    echo "$file_type"
}

# 提取文件元数据
extract_metadata() {
    local file_path="$1"
    local metadata_json=""
    
    if [[ ! -e "$file_path" ]]; then
        echo "{\"error\": \"file_not_found\"}"
        return 1
    fi
    
    # 基本文件信息
    local filename basename dirname extension
    filename=$(basename "$file_path")
    basename="${filename%.*}"
    dirname=$(dirname "$file_path")
    extension="${filename##*.}"
    
    # 获取文件统计信息
    local size mtime atime permissions
    if command -v stat >/dev/null 2>&1; then
        # Linux格式
        if stat -c "%s %Y %X %a" "$file_path" >/dev/null 2>&1; then
            local stat_info
            stat_info=$(stat -c "%s %Y %X %a" "$file_path" 2>/dev/null)
            size=$(echo "$stat_info" | cut -d' ' -f1)
            mtime=$(echo "$stat_info" | cut -d' ' -f2)
            atime=$(echo "$stat_info" | cut -d' ' -f3)
            permissions=$(echo "$stat_info" | cut -d' ' -f4)
        # macOS格式
        elif stat -f "%z %m %a %p" "$file_path" >/dev/null 2>&1; then
            local stat_info
            stat_info=$(stat -f "%z %m %a %p" "$file_path" 2>/dev/null)
            size=$(echo "$stat_info" | cut -d' ' -f1)
            mtime=$(echo "$stat_info" | cut -d' ' -f2)
            atime=$(echo "$stat_info" | cut -d' ' -f3)
            permissions=$(echo "$stat_info" | cut -d' ' -f4)
        fi
    fi
    
    # 设置默认值
    size="${size:-0}"
    mtime="${mtime:-0}"
    atime="${atime:-0}"
    permissions="${permissions:-644}"
    
    # 检测文件类型
    local file_type category
    file_type=$(detect_file_type "$file_path")
    category="$file_type"
    
    # 检查是否为隐藏文件
    local is_hidden=false
    if [[ "$filename" =~ ^\..*$ ]]; then
        is_hidden=true
    fi
    
    # 检查是否为系统文件
    local is_system=false
    case "$dirname" in
        */System/*|*/Library/*|*/Windows/*|*/Program\ Files/*)
            is_system=true
            ;;
    esac
    
    # 构建JSON格式的元数据
    metadata_json=$(cat <<EOF
{
    "path": "$file_path",
    "filename": "$filename",
    "basename": "$basename",
    "dirname": "$dirname",
    "extension": "$extension",
    "type": "$file_type",
    "category": "$category",
    "size": $size,
    "mtime": $mtime,
    "atime": $atime,
    "permissions": "$permissions",
    "is_hidden": $is_hidden,
    "is_system": $is_system,
    "analysis_time": $(date +%s)
}
EOF
)
    
    echo "$metadata_json"
}

# 计算文件重要性评分
calculate_importance_score() {
    local metadata_json="$1"
    local score=0
    
    # 解析元数据（简单的grep/sed方式，生产环境建议使用jq）
    local file_type extension size mtime dirname is_hidden is_system
    file_type=$(echo "$metadata_json" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
    extension=$(echo "$metadata_json" | grep '"extension"' | sed 's/.*"extension": "\([^"]*\)".*/\1/')
    size=$(echo "$metadata_json" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
    mtime=$(echo "$metadata_json" | grep '"mtime"' | sed 's/.*"mtime": \([^,]*\).*/\1/')
    dirname=$(echo "$metadata_json" | grep '"dirname"' | sed 's/.*"dirname": "\([^"]*\)".*/\1/')
    is_hidden=$(echo "$metadata_json" | grep '"is_hidden"' | sed 's/.*"is_hidden": \([^,]*\).*/\1/')
    is_system=$(echo "$metadata_json" | grep '"is_system"' | sed 's/.*"is_system": \([^,]*\).*/\1/')
    
    # 文件类型评分 (权重: 30%)
    case "$file_type" in
        "document"|"spreadsheet"|"presentation")
            score=$((score + 30))
            ;;
        "code"|"config")
            score=$((score + 25))
            ;;
        "image"|"audio"|"video")
            score=$((score + 15))
            ;;
        "archive")
            score=$((score + 20))
            ;;
        "executable")
            score=$((score + 10))
            ;;
        "temporary")
            score=$((score + 0))
            ;;
        *)
            score=$((score + 5))
            ;;
    esac
    
    # 扩展名特殊评分 (权重: 15%)
    if [[ -n "${IMPORTANT_EXTENSIONS[$extension]:-}" ]]; then
        local ext_score="${IMPORTANT_EXTENSIONS[$extension]}"
        score=$((score + ext_score * 15 / 100))
    fi
    
    # 文件大小评分 (权重: 20%)
    # 适中大小的文件通常更重要
    if [[ $size -gt 0 ]]; then
        if [[ $size -ge 1024 ]] && [[ $size -le 104857600 ]]; then  # 1KB - 100MB
            score=$((score + 20))
        elif [[ $size -gt 104857600 ]] && [[ $size -le 1073741824 ]]; then  # 100MB - 1GB
            score=$((score + 15))
        elif [[ $size -lt 1024 ]]; then  # 小于1KB
            score=$((score + 5))
        else  # 大于1GB
            score=$((score + 10))
        fi
    fi
    
    # 修改时间评分 (权重: 25%)
    local current_time age_days
    current_time=$(date +%s)
    age_days=$(( (current_time - mtime) / 86400 ))
    
    if [[ $age_days -le 7 ]]; then      # 最近一周
        score=$((score + 25))
    elif [[ $age_days -le 30 ]]; then   # 最近一个月
        score=$((score + 20))
    elif [[ $age_days -le 90 ]]; then   # 最近三个月
        score=$((score + 15))
    elif [[ $age_days -le 365 ]]; then  # 最近一年
        score=$((score + 10))
    else                                 # 超过一年
        score=$((score + 5))
    fi
    
    # 文件位置评分 (权重: 10%)
    case "$dirname" in
        */Desktop*|*/Documents*|*/Downloads*)
            score=$((score + 10))
            ;;
        */Pictures*|*/Music*|*/Videos*)
            score=$((score + 8))
            ;;
        */Applications*|*/Program*)
            score=$((score + 6))
            ;;
        *)
            score=$((score + 3))
            ;;
    esac
    
    # 隐藏文件和系统文件调整
    if [[ "$is_hidden" == "true" ]]; then
        score=$((score - 5))
    fi
    
    if [[ "$is_system" == "true" ]]; then
        score=$((score + 15))  # 系统文件重要性更高
    fi
    
    # 确保评分在0-100范围内
    if [[ $score -gt 100 ]]; then
        score=100
    elif [[ $score -lt 0 ]]; then
        score=0
    fi
    
    echo "$score"
}

# 查找关联文件
find_related_files() {
    local file_path="$1"
    local base_dir
    base_dir=$(dirname "$file_path")
    local filename basename extension
    filename=$(basename "$file_path")
    basename="${filename%.*}"
    extension="${filename##*.}"
    
    local related_files=()
    
    # 查找同名不同扩展名的文件
    while IFS= read -r -d '' related_file; do
        related_files+=("$related_file")
    done < <(find "$base_dir" -maxdepth 1 -name "${basename}.*" -not -path "$file_path" -print0 2>/dev/null)
    
    # 查找备份文件
    while IFS= read -r -d '' backup_file; do
        related_files+=("$backup_file")
    done < <(find "$base_dir" -maxdepth 1 \( -name "${filename}.bak" -o -name "${filename}.backup" -o -name "${filename}.old" -o -name "${filename}~" \) -print0 2>/dev/null)
    
    # 输出关联文件列表（JSON数组格式）
    if [[ ${#related_files[@]} -gt 0 ]]; then
        printf '['
        for i in "${!related_files[@]}"; do
            if [[ $i -gt 0 ]]; then
                printf ','
            fi
            printf '"%s"' "${related_files[$i]}"
        done
        printf ']'
    else
        printf '[]'
    fi
}

# 检查备份是否存在
check_backup_exists() {
    local file_path="$1"
    local base_dir filename
    base_dir=$(dirname "$file_path")
    filename=$(basename "$file_path")
    
    # 检查常见的备份文件模式
    local backup_patterns=(
        "${filename}.bak"
        "${filename}.backup"
        "${filename}.old"
        "${filename}~"
        ".${filename}.swp"
        "${filename%.*}.backup.${filename##*.}"
    )
    
    for pattern in "${backup_patterns[@]}"; do
        if [[ -e "$base_dir/$pattern" ]]; then
            echo "true"
            return 0
        fi
    done
    
    # 检查常见的备份目录
    local backup_dirs=("backup" "backups" ".backup" "bak")
    for backup_dir in "${backup_dirs[@]}"; do
        if [[ -e "$base_dir/$backup_dir/$filename" ]]; then
            echo "true"
            return 0
        fi
    done
    
    echo "false"
    return 1
}

# 生成文件签名
generate_file_signature() {
    local file_path="$1"
    
    if [[ ! -f "$file_path" ]]; then
        echo "not_a_file"
        return 1
    fi
    
    # 使用MD5或SHA256生成文件签名
    local signature=""
    if command -v md5sum >/dev/null 2>&1; then
        signature=$(md5sum "$file_path" 2>/dev/null | cut -d' ' -f1)
    elif command -v md5 >/dev/null 2>&1; then
        signature=$(md5 -q "$file_path" 2>/dev/null)
    elif command -v shasum >/dev/null 2>&1; then
        signature=$(shasum -a 256 "$file_path" 2>/dev/null | cut -d' ' -f1)
    else
        # 如果没有哈希工具，使用文件大小和修改时间作为简单签名
        if command -v stat >/dev/null 2>&1; then
            local size mtime
            if stat -c "%s %Y" "$file_path" >/dev/null 2>&1; then
                local stat_info
                stat_info=$(stat -c "%s %Y" "$file_path" 2>/dev/null)
                signature="${stat_info// /_}"
            elif stat -f "%z %m" "$file_path" >/dev/null 2>&1; then
                local stat_info
                stat_info=$(stat -f "%z %m" "$file_path" 2>/dev/null)
                signature="${stat_info// /_}"
            fi
        fi
    fi
    
    echo "$signature"
}

# 主要分析函数
analyze_file() {
    local file_path="$1"
    local force_refresh="${2:-false}"
    
    # 检查缓存
    local cache_key="$file_path"
    if [[ "$force_refresh" != "true" ]] && [[ -n "${FILE_ANALYSIS_CACHE[$cache_key]:-}" ]]; then
        echo "${FILE_ANALYSIS_CACHE[$cache_key]}"
        return 0
    fi
    
    log_debug "FILE_ANALYZER" "开始分析文件: $file_path"
    
    # 提取基本元数据
    local metadata
    metadata=$(extract_metadata "$file_path")
    
    if [[ $? -ne 0 ]]; then
        log_error "FILE_ANALYZER" "元数据提取失败: $file_path"
        echo "{\"error\": \"metadata_extraction_failed\"}"
        return 1
    fi
    
    # 计算重要性评分
    local importance_score
    importance_score=$(calculate_importance_score "$metadata")
    
    # 查找关联文件
    local related_files
    related_files=$(find_related_files "$file_path")
    
    # 检查备份存在性
    local backup_exists
    backup_exists=$(check_backup_exists "$file_path")
    
    # 生成文件签名
    local file_signature
    file_signature=$(generate_file_signature "$file_path")
    
    # 构建完整的分析结果
    local analysis_result
    analysis_result=$(echo "$metadata" | sed '$ s/}$//' | cat - <<EOF
,
    "importance_score": $importance_score,
    "related_files": $related_files,
    "backup_exists": $backup_exists,
    "file_signature": "$file_signature"
}
EOF
)
    
    # 缓存结果
    FILE_ANALYSIS_CACHE["$cache_key"]="$analysis_result"
    
    log_debug "FILE_ANALYZER" "文件分析完成: $file_path (评分: $importance_score)"
    
    echo "$analysis_result"
}

# 批量分析文件
batch_analyze_files() {
    local files=("$@")
    local total_files=${#files[@]}
    local current=0
    
    log_info "FILE_ANALYZER" "开始批量分析 $total_files 个文件"
    
    for file_path in "${files[@]}"; do
        ((current++))
        
        if is_config_true "progress_bar"; then
            printf "\r文件分析进度: %d/%d (%d%%)" "$current" "$total_files" $((current * 100 / total_files)) >&2
        fi
        
        analyze_file "$file_path"
    done
    
    if is_config_true "progress_bar"; then
        echo >&2  # 换行
    fi
    
    log_info "FILE_ANALYZER" "批量分析完成"
}

# 清理分析缓存
clear_analysis_cache() {
    FILE_ANALYSIS_CACHE=()
    log_info "FILE_ANALYZER" "分析缓存已清理"
}

# 获取缓存统计
get_cache_stats() {
    local cache_size=${#FILE_ANALYSIS_CACHE[@]}
    echo "缓存条目数: $cache_size"
}

# 模块初始化
init_file_analyzer() {
    log_info "FILE_ANALYZER" "初始化文件分析器模块"
    
    init_file_type_mapping
    init_important_extensions
    
    log_info "FILE_ANALYZER" "文件分析器模块初始化完成"
}

# 导出分析结果为JSON格式
export_analysis_results() {
    local output_file="$1"
    local files=("${@:2}")
    
    echo '{"file_analysis_results": [' > "$output_file"
    
    local first=true
    for file_path in "${files[@]}"; do
        if [[ "$first" != "true" ]]; then
            echo ',' >> "$output_file"
        fi
        first=false
        
        local analysis_result
        analysis_result=$(analyze_file "$file_path")
        echo "$analysis_result" >> "$output_file"
    done
    
    echo ']}' >> "$output_file"
    
    log_info "FILE_ANALYZER" "分析结果已导出到: $output_file"
}

# 主分析入口函数
main_file_analysis() {
    local operation="$1"
    shift
    
    case "$operation" in
        "init")
            init_file_analyzer
            ;;
        "analyze")
            analyze_file "$@"
            ;;
        "batch")
            batch_analyze_files "$@"
            ;;
        "export")
            export_analysis_results "$@"
            ;;
        "clear-cache")
            clear_analysis_cache
            ;;
        "cache-stats")
            get_cache_stats
            ;;
        *)
            echo "错误: 未知操作 '$operation'" >&2
            echo "可用操作: init, analyze, batch, export, clear-cache, cache-stats" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_file_analysis "$@"
fi