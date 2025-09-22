#!/bin/bash

# 回收站清理工具 - 主入口脚本
# 版本: 1.0.0
# 描述: 安全、高效、跨平台的回收站清理工具
# 作者: trash-cleaner 开发团队

set -euo pipefail  # 严格错误处理

# 脚本根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"

# 版本信息
VERSION="1.0.0"
BUILD_DATE="$(date '+%Y-%m-%d')"

# 导入所有核心模块
source "$SRC_DIR/system_detector.sh"
source "$SRC_DIR/security_checker.sh"
source "$SRC_DIR/config_manager.sh"
source "$SRC_DIR/trash_scanner.sh"
source "$SRC_DIR/cleanup_executor.sh"
source "$SRC_DIR/logger.sh"
source "$SRC_DIR/ui.sh"
# 新增的预检查和列表管理模块
source "$SRC_DIR/file_analyzer.sh"
source "$SRC_DIR/risk_assessor.sh"
source "$SRC_DIR/list_manager.sh"
source "$SRC_DIR/interaction_manager.sh"
source "$SRC_DIR/precheck_engine.sh"

# 应用程序状态
declare -A APP_STATE=(
    ["initialized"]=false
    ["config_loaded"]=false
    ["logging_enabled"]=false
    ["operation_mode"]="interactive"
    ["exit_code"]=0
)

# 显示版本信息
show_version() {
    cat <<EOF
trash-cleaner v$VERSION (构建日期: $BUILD_DATE)

一个安全、高效的跨平台回收站清理工具

特性:
• 跨平台支持 (Linux, macOS, Windows)
• 多层安全验证机制
• 灵活的过滤和筛选选项
• 详细的操作日志和审计
• 友好的用户交互界面
• 预览模式支持

许可: MIT License
项目主页: https://github.com/trash-cleaner/trash-cleaner
EOF
}

# 应用初始化
initialize_application() {
    log_info "APP" "开始初始化应用程序"
    
    # 检查必要的依赖
    if ! check_required_commands; then
        log_fatal "APP" "缺少必要的系统命令"
        return 1
    fi
    
    # 检查运行环境
    local os_type
    os_type=$(detect_os)
    if [[ "$os_type" == "unknown" ]]; then
        log_fatal "APP" "不支持的操作系统"
        return 1
    fi
    
    log_info "APP" "检测到操作系统: $os_type"
    
    # 创建安全沙箱
    if ! create_security_sandbox; then
        log_error "APP" "无法创建安全沙箱"
        return 1
    fi
    
    APP_STATE["initialized"]=true
    log_info "APP" "应用程序初始化完成"
    
    return 0
}

# 加载和验证配置
setup_configuration() {
    log_info "APP" "开始配置设置"
    
    # 执行配置管理
    if ! main_config_management "$@"; then
        log_error "APP" "配置管理失败"
        return 1
    fi
    
    APP_STATE["config_loaded"]=true
    
    # 根据配置设置操作模式
    if is_config_true "dry_run"; then
        APP_STATE["operation_mode"]="preview"
        log_info "APP" "运行模式: 预览模式"
    elif ! is_config_true "confirm_deletion"; then
        APP_STATE["operation_mode"]="automatic"
        log_info "APP" "运行模式: 自动模式"
    else
        APP_STATE["operation_mode"]="interactive"
        log_info "APP" "运行模式: 交互模式"
    fi
    
    log_info "APP" "配置设置完成"
    return 0
}

# 初始化日志系统
setup_logging() {
    local log_file
    local log_level="INFO"
    
    log_file=$(get_config "log_file")
    
    if is_config_true "verbose"; then
        log_level="DEBUG"
    fi
    
    # 初始化日志系统
    if init_logging "$log_file" "$log_level"; then
        APP_STATE["logging_enabled"]=true
        log_info "APP" "日志系统初始化成功"
        
        # 记录应用启动信息
        log_system_info "STARTUP" "应用程序启动" "version=$VERSION, pid=$$"
        
        # 检查是否需要日志轮转
        rotate_logs "$log_file"
        
        # 清理过期日志
        cleanup_old_logs "$(dirname "$log_file")"
        
        return 0
    else
        echo "WARNING: 日志系统初始化失败，继续运行但不记录日志" >&2
        return 1
    fi
}

# 执行预检查
perform_pre_checks() {
    log_info "APP" "执行预检查"
    
    # 检测可用的回收站路径
    local os_type trash_paths
    os_type=$(detect_os)
    
    log_info "APP" "扫描回收站路径"
    mapfile -t trash_paths < <(get_trash_paths "$os_type")
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        print_status "error" "未找到回收站目录"
        log_error "APP" "未找到可用的回收站目录"
        return 1
    fi
    
    # 验证回收站访问权限
    local accessible_paths=()
    for path in "${trash_paths[@]}"; do
        if verify_trash_access "$path"; then
            accessible_paths+=("$path")
            print_status "success" "发现可访问的回收站: $path"
            log_info "APP" "回收站路径可访问: $path"
        else
            print_status "warning" "回收站路径不可访问: $path"
            log_warn "APP" "回收站路径访问受限: $path"
        fi
    done
    
    if [[ ${#accessible_paths[@]} -eq 0 ]]; then
        print_status "error" "没有可访问的回收站目录"
        log_error "APP" "所有回收站目录都不可访问"
        return 1
    fi
    
    log_info "APP" "预检查完成，找到 ${#accessible_paths[@]} 个可用回收站"
    return 0
}

# 执行预检查操作
execute_precheck_operation() {
    log_operation_start "PRECHECK_OPERATION" "开始执行预检查操作"
    
    local start_time
    start_time=$(date +%s)
    
    # 显示操作开始信息
    print_title "回收站预检查工具 v$VERSION" "box"
    
    # 执行系统检测
    local os_type trash_paths
    os_type=$(detect_os)
    
    print_status "info" "操作系统: $os_type"
    print_status "info" "工作模式: 预检查模式"
    
    # 获取可访问的回收站路径
    mapfile -t trash_paths < <(main_detect_system)
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        print_status "error" "没有找到可访问的回收站目录"
        log_operation_end "PRECHECK_OPERATION" "FAILED" "no_accessible_trash"
        return 1
    fi
    
    print_status "info" "找到 ${#trash_paths[@]} 个回收站目录"
    
    # 扫描回收站内容
    print_status "info" "正在扫描回收站内容..."
    
    if ! scan_trash_directories "${trash_paths[@]}"; then
        print_status "error" "扫描回收站失败"
        log_operation_end "PRECHECK_OPERATION" "FAILED" "scan_failed"
        return 1
    fi
    
    # 检查是否有内容需要处理
    local total_items=$((SCAN_STATS["total_files"] + SCAN_STATS["total_dirs"]))
    
    if [[ $total_items -eq 0 ]]; then
        print_status "info" "回收站为空，无内容可分析"
        log_operation_end "PRECHECK_OPERATION" "SUCCESS" "nothing_to_analyze"
        return 0
    fi
    
    # 获取清理类型和匹配的项目
    local clean_type matching_items
    clean_type=$(get_config "clean_type" "all")
    mapfile -t matching_items < <(get_matching_items "$clean_type")
    
    if [[ ${#matching_items[@]} -eq 0 ]]; then
        print_status "warning" "没有找到匹配条件的项目"
        log_operation_end "PRECHECK_OPERATION" "SUCCESS" "no_matching_items"
        return 0
    fi
    
    print_status "info" "找到 ${#matching_items[@]} 个匹配项目"
    
    # 初始化预检查引擎
    print_status "info" "初始化预检查引擎..."
    init_precheck_engine
    
    # 执行完整预检查
    print_status "info" "正在执行文件分析和风险评估..."
    if ! run_full_precheck "${matching_items[@]}"; then
        print_status "error" "预检查失败"
        log_operation_end "PRECHECK_OPERATION" "FAILED" "precheck_failed"
        return 1
    fi
    
    # 处理不同的操作模式
    if is_config_true "list_only"; then
        # 仅列出模式
        handle_list_only_mode
    elif is_config_true "detailed_list"; then
        # 详细列表模式
        handle_detailed_list_mode
    elif [[ -n "$(get_config "export_format")" ]]; then
        # 导出模式
        handle_export_mode
    elif is_config_true "interactive_mode"; then
        # 交互模式
        handle_interactive_mode
    else
        # 默认显示概览
        show_precheck_summary true
    fi
    
    local end_time duration
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    print_status "success" "预检查操作完成"
    print_status "info" "处理时间: $(format_duration_human $duration)"
    
    log_performance "PRECHECK_DURATION" "$duration" "seconds"
    log_operation_end "PRECHECK_OPERATION" "SUCCESS" "items_analyzed=${#matching_items[@]}"
    
    return 0
}

# 处理仅列出模式
handle_list_only_mode() {
    print_status "info" "仅列出模式：显示文件列表"
    
    # 显示概览
    show_overview "$(get_config "color_output" "true")"
    
    # 应用排序
    local sort_by sort_order
    sort_by=$(get_config "sort_by" "name")
    sort_order=$(get_config "sort_order" "asc")
    sort_files "$sort_by" "$sort_order"
    
    # 显示简单列表
    echo
    echo "文件列表："
    local count=0
    for item in "${LIST_ITEMS[@]}"; do
        ((count++))
        printf "%4d) %s\n" "$count" "$(basename "$item")"
    done
}

# 处理详细列表模式
handle_detailed_list_mode() {
    print_status "info" "详细列表模式：显示详细信息"
    
    # 显示预检查摘要
    show_precheck_summary "$(get_config "color_output" "true")"
    
    # 应用排序
    local sort_by sort_order
    sort_by=$(get_config "sort_by" "risk")
    sort_order="desc"  # 按风险降序
    sort_files "$sort_by" "$sort_order"
}

# 处理导出模式
handle_export_mode() {
    local export_format export_file
    export_format=$(get_config "export_format")
    export_file=$(get_config "export_file")
    
    # 如果没有指定导出文件，生成默认文件名
    if [[ -z "$export_file" ]]; then
        local timestamp
        timestamp=$(date "+%Y%m%d_%H%M%S")
        export_file="trash_analysis_${timestamp}.${export_format}"
    fi
    
    print_status "info" "导出模式：将结果导出到 $export_file"
    
    # 执行导出
    if export_list "$export_file" "$export_format"; then
        print_status "success" "导出成功: $export_file"
    else
        print_status "error" "导出失败"
        return 1
    fi
    
    # 同时显示概览
    if ! is_config_true "no_header"; then
        show_precheck_summary "$(get_config "color_output" "true")"
    fi
}

# 处理交互模式
handle_interactive_mode() {
    print_status "info" "交互模式：启动交互式选择"
    
    # 启动交互式预检查
    if start_interactive_precheck; then
        # 获取用户选中的文件
        local selected_files
        mapfile -t selected_files < <(get_selected_files)
        
        if [[ ${#selected_files[@]} -gt 0 ]]; then
            print_status "info" "用户选中了 ${#selected_files[@]} 个文件"
            
            # 如果不是仅预览模式，可以执行删除
            if ! is_config_true "dry_run"; then
                print_status "info" "即将执行删除操作..."
                # 这里可以调用实际的删除功能
                # batch_delete_items "${selected_files[@]}"
                print_status "success" "模拟删除操作完成"
            else
                print_status "info" "预览模式，不执行实际删除"
            fi
        else
            print_status "info" "用户未选择任何文件"
        fi
    else
        print_status "info" "用户取消了交互操作"
    fi
}

# 执行主要操作
execute_main_operation() {
    log_operation_start "MAIN_CLEANUP" "开始执行回收站清理操作"
    
    local start_time
    start_time=$(date +%s)
    
    # 显示操作开始信息
    print_title "回收站清理工具 v$VERSION" "box"
    
    # 执行系统检测
    local os_type trash_paths
    os_type=$(detect_os)
    
    print_status "info" "操作系统: $os_type"
    print_status "info" "工作模式: ${APP_STATE[operation_mode]}"
    
    # 获取可访问的回收站路径
    mapfile -t trash_paths < <(main_detect_system)
    
    if [[ ${#trash_paths[@]} -eq 0 ]]; then
        print_status "error" "没有找到可访问的回收站目录"
        log_operation_end "MAIN_CLEANUP" "FAILED" "no_accessible_trash"
        return 1
    fi
    
    print_status "info" "找到 ${#trash_paths[@]} 个回收站目录"
    
    # 扫描回收站内容
    print_status "info" "正在扫描回收站内容..."
    
    if ! scan_trash_directories "${trash_paths[@]}"; then
        print_status "error" "扫描回收站失败"
        log_operation_end "MAIN_CLEANUP" "FAILED" "scan_failed"
        return 1
    fi
    
    # 显示扫描结果
    show_scan_statistics false
    
    # 检查是否有内容需要清理
    local total_items=$((SCAN_STATS["total_files"] + SCAN_STATS["total_dirs"]))
    
    if [[ $total_items -eq 0 ]]; then
        print_status "info" "回收站为空，无需清理"
        log_operation_end "MAIN_CLEANUP" "SUCCESS" "nothing_to_clean"
        return 0
    fi
    
    # 获取清理类型
    local clean_type
    clean_type=$(get_config "clean_type" "all")
    
    # 获取匹配的项目
    local matching_items
    mapfile -t matching_items < <(get_matching_items "$clean_type")
    
    if [[ ${#matching_items[@]} -eq 0 ]]; then
        print_status "warning" "没有找到匹配清理条件的项目"
        log_operation_end "MAIN_CLEANUP" "SUCCESS" "no_matching_items"
        return 0
    fi
    
    print_status "info" "找到 ${#matching_items[@]} 个匹配项目"
    
    # 根据操作模式处理
    case "${APP_STATE[operation_mode]}" in
        "preview")
            print_status "info" "预览模式：显示将要清理的内容"
            ;;
            
        "interactive")
            if ! confirm_prompt "确认删除这些项目？" "n" 30; then
                print_status "info" "用户取消操作"
                log_operation_end "MAIN_CLEANUP" "CANCELLED" "user_cancelled"
                return 0
            fi
            ;;
            
        "automatic")
            print_status "info" "自动模式：开始清理"
            ;;
    esac
    
    # 执行清理操作
    if batch_delete_items "${matching_items[@]}"; then
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        print_status "success" "清理操作完成"
        print_status "info" "处理时间: $(format_duration_human $duration)"
        
        # 显示详细结果
        show_cleanup_results
        
        log_performance "CLEANUP_DURATION" "$duration" "seconds"
        log_operation_end "MAIN_CLEANUP" "SUCCESS" "items_processed=${#matching_items[@]}"
        
        return 0
    else
        print_status "error" "清理操作失败"
        log_operation_end "MAIN_CLEANUP" "FAILED" "cleanup_execution_failed"
        return 1
    fi
}

# 清理和退出
cleanup_and_exit() {
    local exit_code="${1:-0}"
    
    log_info "APP" "开始应用程序清理"
    
    # 清理安全沙箱
    cleanup_security_sandbox
    
    # 如果启用了日志记录，记录退出信息
    if [[ "${APP_STATE[logging_enabled]}" == "true" ]]; then
        log_system_info "SHUTDOWN" "应用程序退出" "exit_code=$exit_code"
    fi
    
    # 生成操作摘要（如果需要）
    if is_config_true "verbose" && [[ "${APP_STATE[logging_enabled]}" == "true" ]]; then
        echo
        print_title "操作日志摘要" "simple"
        generate_log_summary "$(get_config "log_file")" "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')"
    fi
    
    exit "$exit_code"
}

# 错误处理
handle_error() {
    local error_code="$1"
    local error_message="${2:-未知错误}"
    local line_number="${3:-unknown}"
    
    print_status "error" "发生错误: $error_message (行号: $line_number)"
    log_error "APP" "应用程序错误: $error_message" "line=$line_number, code=$error_code"
    
    APP_STATE["exit_code"]="$error_code"
    cleanup_and_exit "$error_code"
}

# 信号处理
handle_signal() {
    local signal="$1"
    
    echo
    print_status "warning" "收到信号 $signal，正在安全退出..."
    log_warn "APP" "收到中断信号: $signal"
    
    APP_STATE["exit_code"]=130
    cleanup_and_exit 130
}

# 设置信号和错误处理
setup_error_handling() {
    # 设置错误陷阱
    trap 'handle_error $? "脚本执行错误" $LINENO' ERR
    
    # 设置信号处理
    trap 'handle_signal SIGINT' INT
    trap 'handle_signal SIGTERM' TERM
    trap 'handle_signal SIGHUP' HUP
    
    # 设置退出清理
    trap 'cleanup_and_exit ${APP_STATE[exit_code]}' EXIT
}

# 主函数
main() {
    # 设置错误处理
    setup_error_handling
    
    # 处理特殊命令行参数
    case "${1:-}" in
        --version|-V)
            show_version
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
    esac
    
    # 应用初始化序列
    print_status "info" "初始化回收站清理工具..."
    
    # 1. 配置设置
    if ! setup_configuration "$@"; then
        handle_error 1 "配置设置失败"
    fi
    
    # 2. 初始化日志系统
    setup_logging
    
    # 3. 应用初始化
    if ! initialize_application; then
        handle_error 1 "应用程序初始化失败"
    fi
    
    # 4. 执行预检查
    if ! perform_pre_checks; then
        handle_error 1 "预检查失败"
    fi
    
    # 5. 检查是否仅为列表模式或预检查模式
    if is_config_true "list_only" || is_config_true "detailed_list" || [[ -n "$(get_config "export_format")" ]]; then
        if ! execute_precheck_operation; then
            handle_error 1 "预检查操作失败"
        fi
        APP_STATE["exit_code"]=0
        return 0
    fi
    
    # 6. 执行主要操作
    if ! execute_main_operation; then
        handle_error 1 "主要操作失败"
    fi
    
    # 成功完成
    print_status "success" "所有操作已完成"
    APP_STATE["exit_code"]=0
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi