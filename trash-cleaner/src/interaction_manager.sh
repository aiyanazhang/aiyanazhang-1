#!/bin/bash

# 交互管理器模块
# 功能：交互式用户界面、菜单操作、文件选择、确认机制

# 导入依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/list_manager.sh"

# 交互状态管理
declare -A INTERACTION_STATE=(
    ["current_view"]="overview"
    ["session_active"]=false
)

# 菜单选项定义
declare -A MAIN_MENU_OPTIONS=(
    ["1"]="🔍|查看高风险文件详情"
    ["2"]="📋|按类别选择删除"
    ["3"]="⏰|按时间范围选择"
    ["4"]="📏|按大小范围选择"
    ["5"]="🏷️|手动标记/取消标记"
    ["6"]="💾|导出文件列表"
    ["7"]="✅|确认并执行删除"
    ["8"]="❌|取消操作"
)

# 显示交互式菜单
show_interactive_menu() {
    local show_colors="${1:-true}"
    
    echo
    if [[ "$show_colors" == "true" ]]; then
        printf "\033[1;36m\033[1m"
    fi
    echo "交互式文件选择"
    echo "═══════════════════════════════════════════════════════════════════"
    if [[ "$show_colors" == "true" ]]; then
        printf "\033[0m"
    fi
    
    # 显示当前选择统计
    local selected_count=0
    local selected_size=0
    
    for item in "${LIST_ITEMS[@]}"; do
        if [[ "${SELECTION_STATE[$item]}" == "true" ]]; then
            ((selected_count++))
            local analysis="${LIST_METADATA["$item:analysis"]}"
            local size
            size=$(echo "$analysis" | grep '"size"' | sed 's/.*"size": \([^,]*\).*/\1/')
            selected_size=$((selected_size + size))
        fi
    done
    
    echo "当前选择: 删除 $selected_count 个文件 ($(format_file_size $selected_size))"
    echo
    
    # 显示菜单选项
    echo "操作选项:"
    for key in $(echo "${!MAIN_MENU_OPTIONS[@]}" | tr ' ' '\n' | sort -n); do
        local option="${MAIN_MENU_OPTIONS[$key]}"
        local icon="${option%%|*}"
        local description="${option##*|}"
        printf " %s) %s %s\n" "$key" "$icon" "$description"
    done
    echo
}

# 处理用户输入
handle_user_input() {
    local choice
    echo -n "请选择操作 [1-8]: "
    read -r choice
    
    case "$choice" in
        1)
            show_high_risk_files
            ;;
        2)
            select_by_category
            ;;
        7)
            confirm_and_execute
            ;;
        8)
            cancel_operation
            return 1
            ;;
        *)
            echo "无效选择，请重新输入"
            return 0
            ;;
    esac
    
    return 0
}

# 显示高风险文件详情
show_high_risk_files() {
    echo
    echo "🔴 高风险文件详情"
    echo "═══════════════════════════════════════════════════════════════════"
    
    local high_risk_count=0
    
    # 找出高风险文件
    for item in "${LIST_ITEMS[@]}"; do
        local risk="${LIST_METADATA["$item:risk"]}"
        local risk_level
        risk_level=$(echo "$risk" | grep '"risk_level"' | sed 's/.*"risk_level": "\([^"]*\)".*/\1/')
        
        if [[ "$risk_level" == "HIGH" ]] || [[ "$risk_level" == "CRITICAL" ]]; then
            ((high_risk_count++))
            
            # 显示文件详情
            local filename
            filename=$(basename "$item")
            printf "📄 %s (风险等级: %s)\n" "$filename" "$risk_level"
        fi
    done
    
    if [[ $high_risk_count -eq 0 ]]; then
        echo "✅ 没有发现高风险文件"
    fi
    
    echo
    echo -n "按回车键继续..."
    read -r
}

# 按类别选择文件
select_by_category() {
    echo
    echo "📋 按类别选择文件"
    echo "═══════════════════════════════════════════════════════════════════"
    
    # 统计各类别文件数量
    local -A category_stats=()
    for item in "${LIST_ITEMS[@]}"; do
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local file_type
        file_type=$(echo "$analysis" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
        category_stats["$file_type"]=$((category_stats["$file_type"] + 1))
    done
    
    # 显示类别选项
    echo "可用类别:"
    local category_index=1
    local -a category_list=()
    for category in "${!category_stats[@]}"; do
        printf " %d) %s (%d 个文件)\n" "$category_index" "$category" "${category_stats[$category]}"
        category_list+=("$category")
        ((category_index++))
    done
    
    echo " 0) 返回主菜单"
    echo
    
    echo -n "请选择类别 [0-$((category_index-1))]: "
    local choice
    read -r choice
    
    if [[ "$choice" != "0" ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -lt "$category_index" ]]; then
        local selected_category="${category_list[$((choice-1))]}"
        
        echo "选择操作:"
        echo " 1) 标记此类别所有文件为删除"
        echo " 2) 取消标记此类别所有文件"
        
        echo -n "请选择 [1-2]: "
        local action
        read -r action
        
        case "$action" in
            1)
                mark_category_files "$selected_category" true
                echo "✅ 已标记 $selected_category 类别的所有文件"
                ;;
            2)
                mark_category_files "$selected_category" false
                echo "✅ 已取消标记 $selected_category 类别的所有文件"
                ;;
        esac
    fi
    
    echo
    echo -n "按回车键继续..."
    read -r
}

# 标记/取消标记类别文件
mark_category_files() {
    local category="$1"
    local mark_state="$2"
    
    for item in "${LIST_ITEMS[@]}"; do
        local analysis="${LIST_METADATA["$item:analysis"]}"
        local file_type
        file_type=$(echo "$analysis" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
        
        if [[ "$file_type" == "$category" ]]; then
            SELECTION_STATE["$item"]="$mark_state"
        fi
    done
}

# 确认并执行删除
confirm_and_execute() {
    echo
    echo "✅ 确认删除操作"
    echo "═══════════════════════════════════════════════════════════════════"
    
    # 统计选中的文件
    local selected_files=()
    
    for item in "${LIST_ITEMS[@]}"; do
        if [[ "${SELECTION_STATE[$item]}" == "true" ]]; then
            selected_files+=("$item")
        fi
    done
    
    if [[ ${#selected_files[@]} -eq 0 ]]; then
        echo "❌ 没有选择任何文件"
        echo -n "按回车键继续..."
        read -r
        return 0
    fi
    
    echo "即将删除 ${#selected_files[@]} 个文件"
    echo
    echo "确认删除这些文件吗? 此操作不可恢复!"
    echo -n "请输入 'yes' 确认删除: "
    local confirmation
    read -r confirmation
    
    if [[ "$confirmation" == "yes" ]]; then
        echo "开始执行删除操作..."
        printf '%s\n' "${selected_files[@]}"
        echo "删除操作已提交"
        INTERACTION_STATE["session_active"]=false
        return 1
    else
        echo "删除操作已取消"
    fi
    
    echo
    echo -n "按回车键继续..."
    read -r
}

# 取消操作
cancel_operation() {
    echo
    echo "❌ 操作已取消"
    INTERACTION_STATE["session_active"]=false
    return 1
}

# 主交互循环
run_interactive_session() {
    INTERACTION_STATE["session_active"]=true
    
    # 显示概览
    show_overview true
    
    while [[ "${INTERACTION_STATE[session_active]}" == "true" ]]; do
        show_interactive_menu true
        
        if ! handle_user_input; then
            break
        fi
    done
}

# 主交互管理入口函数
main_interaction_management() {
    local operation="$1"
    shift
    
    case "$operation" in
        "run")
            run_interactive_session
            ;;
        "menu")
            show_interactive_menu "$1"
            ;;
        *)
            echo "错误: 未知操作 '$operation'" >&2
            echo "可用操作: run, menu" >&2
            return 1
            ;;
    esac
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_interaction_management "$@"
fi
