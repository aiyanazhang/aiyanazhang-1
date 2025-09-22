#!/bin/bash

# 回收站清理工具测试套件
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"
TEST_DATA_DIR="$SCRIPT_DIR/test_data"

# 测试统计
declare -A TEST_STATS=(["total"]=0 ["passed"]=0 ["failed"]=0)
declare -a FAILED_TESTS=()

# 颜色
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

# 测试辅助函数
print_test_result() {
    local test_name="$1" status="$2" message="${3:-}"
    case "$status" in
        "PASS")
            echo -e "  ${GREEN}✓ PASS${RESET}: $test_name"
            TEST_STATS["passed"]=$((TEST_STATS["passed"] + 1))
            ;;
        "FAIL")
            echo -e "  ${RED}✗ FAIL${RESET}: $test_name"
            [[ -n "$message" ]] && echo -e "    ${RED}错误: $message${RESET}"
            FAILED_TESTS+=("$test_name")
            TEST_STATS["failed"]=$((TEST_STATS["failed"] + 1))
            ;;
    esac
    TEST_STATS["total"]=$((TEST_STATS["total"] + 1))
}

assert_equals() {
    local expected="$1" actual="$2" test_name="$3"
    if [[ "$expected" == "$actual" ]]; then
        print_test_result "$test_name" "PASS"
    else
        print_test_result "$test_name" "FAIL" "期望: '$expected', 实际: '$actual'"
    fi
}

# 设置测试环境
setup_test_environment() {
    mkdir -p "$TEST_DATA_DIR/trash_test" "$TEST_DATA_DIR/config_test"
    echo "test file" > "$TEST_DATA_DIR/trash_test/test.txt"
    mkdir -p "$TEST_DATA_DIR/trash_test/test_dir"
    cat > "$TEST_DATA_DIR/config_test/test.conf" <<EOF
default_mode=interactive
clean_type=all
enable_logging=true
EOF
}

cleanup_test_environment() {
    [[ -d "$TEST_DATA_DIR" ]] && rm -rf "$TEST_DATA_DIR"
}

# 系统检测测试
test_system_detection() {
    echo -e "\n=== 系统检测测试 ==="
    source "$SRC_DIR/system_detector.sh"
    
    local os_type=$(detect_os)
    [[ "$os_type" != "unknown" ]] && print_test_result "操作系统检测" "PASS" || print_test_result "操作系统检测" "FAIL"
    
    check_required_commands && print_test_result "必要命令检查" "PASS" || print_test_result "必要命令检查" "FAIL"
}

# 安全检查测试
test_security_checks() {
    echo -e "\n=== 安全检查测试 ==="
    source "$SRC_DIR/security_checker.sh"
    
    is_path_dangerous "/" && print_test_result "危险路径检测" "PASS" || print_test_result "危险路径检测" "FAIL"
    check_user_privileges "user" && print_test_result "用户权限检查" "PASS" || print_test_result "用户权限检查" "FAIL"
}

# 配置管理测试
test_config_management() {
    echo -e "\n=== 配置管理测试 ==="
    source "$SRC_DIR/config_manager.sh"
    
    init_config
    local default_mode=$(get_config "default_mode")
    assert_equals "interactive" "$default_mode" "默认配置获取"
    
    local seconds=$(parse_time_to_seconds "1d")
    assert_equals "86400" "$seconds" "时间解析"
    
    local bytes=$(parse_size_to_bytes "1M")
    assert_equals "1048576" "$bytes" "大小解析"
}

# 扫描器测试
test_trash_scanner() {
    echo -e "\n=== 扫描器测试 ==="
    source "$SRC_DIR/trash_scanner.sh"
    
    clear_scan_results
    scan_directory_recursive "$TEST_DATA_DIR/trash_test" 10 && print_test_result "目录扫描" "PASS" || print_test_result "目录扫描" "FAIL"
    
    calculate_scan_statistics
    [[ ${SCAN_STATS["total_files"]} -gt 0 ]] && print_test_result "文件统计" "PASS" || print_test_result "文件统计" "FAIL"
}

# 清理执行器测试
test_cleanup_executor() {
    echo -e "\n=== 清理执行器测试 ==="
    source "$SRC_DIR/cleanup_executor.sh"
    
    local test_file="$TEST_DATA_DIR/trash_test/delete_test.txt"
    echo "delete me" > "$test_file"
    
    safe_delete_file "$test_file" "true" && print_test_result "预览模式删除" "PASS" || print_test_result "预览模式删除" "FAIL"
    [[ -f "$test_file" ]] && print_test_result "预览模式文件保留" "PASS" || print_test_result "预览模式文件保留" "FAIL"
}

# 日志系统测试
test_logging_system() {
    echo -e "\n=== 日志系统测试 ==="
    source "$SRC_DIR/logger.sh"
    
    local test_log_file="$TEST_DATA_DIR/test.log"
    init_logging "$test_log_file" "INFO" && print_test_result "日志系统初始化" "PASS" || print_test_result "日志系统初始化" "FAIL"
    
    log_info "TEST" "测试日志"
    [[ -f "$test_log_file" ]] && grep -q "测试日志" "$test_log_file" && print_test_result "日志记录" "PASS" || print_test_result "日志记录" "FAIL"
}

# 用户界面测试
test_user_interface() {
    echo -e "\n=== 用户界面测试 ==="
    source "$SRC_DIR/ui.sh"
    
    set_config "color_output" "true"
    local color_code=$(get_color "red")
    [[ -n "$color_code" ]] && print_test_result "颜色功能" "PASS" || print_test_result "颜色功能" "FAIL"
    
    local formatted_size=$(format_size_human 1048576)
    [[ "$formatted_size" =~ MB ]] && print_test_result "大小格式化" "PASS" || print_test_result "大小格式化" "FAIL"
}

# 主脚本测试
test_main_script() {
    echo -e "\n=== 主脚本测试 ==="
    local main_script="$PROJECT_ROOT/trash-cleaner.sh"
    
    [[ -f "$main_script" ]] && print_test_result "主脚本存在" "PASS" || print_test_result "主脚本存在" "FAIL"
    "$main_script" --help >/dev/null 2>&1 && print_test_result "帮助信息" "PASS" || print_test_result "帮助信息" "FAIL"
    "$main_script" --version >/dev/null 2>&1 && print_test_result "版本信息" "PASS" || print_test_result "版本信息" "FAIL"
}

# 显示测试摘要
show_test_summary() {
    echo -e "\n=== 测试摘要 ==="
    echo "总测试数: ${TEST_STATS[total]}"
    echo -e "通过: ${GREEN}${TEST_STATS[passed]}${RESET}"
    echo -e "失败: ${RED}${TEST_STATS[failed]}${RESET}"
    
    if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
        echo -e "\n失败的测试:"
        printf '%s\n' "${FAILED_TESTS[@]}"
    fi
    
    [[ ${TEST_STATS[failed]} -eq 0 ]] && echo -e "\n${GREEN}所有测试通过！${RESET}" || echo -e "\n${RED}有测试失败！${RESET}"
}

# 主函数
main() {
    echo "开始回收站清理工具测试套件..."
    setup_test_environment
    
    test_system_detection
    test_security_checks
    test_config_management
    test_trash_scanner
    test_cleanup_executor
    test_logging_system
    test_user_interface
    test_main_script
    
    show_test_summary
    cleanup_test_environment
    
    [[ ${TEST_STATS[failed]} -eq 0 ]] && exit 0 || exit 1
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"