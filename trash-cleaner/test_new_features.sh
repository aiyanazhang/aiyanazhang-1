#!/bin/bash

# 回收站清理工具测试脚本
# 测试新增的预检查和列表功能

set -euo pipefail

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRASH_CLEANER="$SCRIPT_DIR/trash-cleaner.sh"

# 测试输出目录
TEST_OUTPUT_DIR="$SCRIPT_DIR/test_output"
mkdir -p "$TEST_OUTPUT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# 输出函数
print_test_header() {
    echo -e "${BLUE}===== $1 =====${NC}"
}

print_success() {
    echo -e "${GREEN}✅ PASS:${NC} $1"
    ((TESTS_PASSED++))
}

print_failure() {
    echo -e "${RED}❌ FAIL:${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ️  INFO:${NC} $1"
}

# 运行单个测试
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    ((TESTS_TOTAL++))
    
    print_info "运行测试: $test_name"
    
    # 创建测试特定的输出目录
    local test_output_dir="$TEST_OUTPUT_DIR/${test_name// /_}"
    mkdir -p "$test_output_dir"
    
    # 执行测试命令
    local actual_exit_code=0
    if ! eval "$test_command" > "$test_output_dir/stdout.txt" 2> "$test_output_dir/stderr.txt"; then
        actual_exit_code=$?
    fi
    
    # 检查退出码
    if [[ $actual_exit_code -eq $expected_exit_code ]]; then
        print_success "$test_name (退出码: $actual_exit_code)"
        
        # 显示输出摘要
        local stdout_lines stderr_lines
        stdout_lines=$(wc -l < "$test_output_dir/stdout.txt" 2>/dev/null || echo "0")
        stderr_lines=$(wc -l < "$test_output_dir/stderr.txt" 2>/dev/null || echo "0")
        print_info "  输出: $stdout_lines 行标准输出, $stderr_lines 行错误输出"
        
        return 0
    else
        print_failure "$test_name (期望退出码: $expected_exit_code, 实际: $actual_exit_code)"
        
        # 显示错误输出
        if [[ -s "$test_output_dir/stderr.txt" ]]; then
            echo "错误输出:"
            head -10 "$test_output_dir/stderr.txt" | sed 's/^/  /'
        fi
        
        return 1
    fi
}

# 测试基本功能
test_basic_functionality() {
    print_test_header "基本功能测试"
    
    # 测试版本显示
    run_test "版本显示" "$TRASH_CLEANER --version"
    
    # 测试帮助显示
    run_test "帮助显示" "$TRASH_CLEANER --help"
    
    # 测试配置语法检查
    run_test "无效参数处理" "$TRASH_CLEANER --invalid-option" 1
}

# 测试新增的预检查功能
test_precheck_functionality() {
    print_test_header "预检查功能测试"
    
    # 测试仅列出模式
    run_test "仅列出模式" "$TRASH_CLEANER -L"
    
    # 测试详细列表模式
    run_test "详细列表模式" "$TRASH_CLEANER --detailed"
    
    # 测试风险分析
    run_test "风险分析模式" "$TRASH_CLEANER -L -r"
    
    # 测试按类型分组
    run_test "按类型分组" "$TRASH_CLEANER -L -g type"
    
    # 测试按风险排序
    run_test "按风险排序" "$TRASH_CLEANER -L -S risk"
}

# 测试导出功能
test_export_functionality() {
    print_test_header "导出功能测试"
    
    local timestamp
    timestamp=$(date "+%Y%m%d_%H%M%S")
    
    # 测试JSON导出
    local json_file="$TEST_OUTPUT_DIR/export_test_${timestamp}.json"
    run_test "JSON导出" "$TRASH_CLEANER -L -x json --export-file '$json_file'"
    
    # 验证JSON文件是否生成
    if [[ -f "$json_file" ]]; then
        print_success "JSON文件已生成: $json_file"
        print_info "  文件大小: $(wc -c < "$json_file") 字节"
    else
        print_failure "JSON文件未生成"
    fi
    
    # 测试CSV导出
    local csv_file="$TEST_OUTPUT_DIR/export_test_${timestamp}.csv"
    run_test "CSV导出" "$TRASH_CLEANER -L -x csv --export-file '$csv_file'"
    
    # 验证CSV文件是否生成
    if [[ -f "$csv_file" ]]; then
        print_success "CSV文件已生成: $csv_file"
        print_info "  文件行数: $(wc -l < "$csv_file") 行"
    else
        print_failure "CSV文件未生成"
    fi
    
    # 测试TXT导出
    local txt_file="$TEST_OUTPUT_DIR/export_test_${timestamp}.txt"
    run_test "TXT导出" "$TRASH_CLEANER -L -x txt --export-file '$txt_file'"
    
    # 验证TXT文件是否生成
    if [[ -f "$txt_file" ]]; then
        print_success "TXT文件已生成: $txt_file"
        print_info "  文件行数: $(wc -l < "$txt_file") 行"
    else
        print_failure "TXT文件未生成"
    fi
}

# 测试参数组合
test_parameter_combinations() {
    print_test_header "参数组合测试"
    
    # 测试多个参数组合
    run_test "详细+分组+排序" "$TRASH_CLEANER --detailed -g type -S size"
    
    # 测试风险阈值
    run_test "风险阈值过滤" "$TRASH_CLEANER -L -m 50"
    
    # 测试禁用颜色输出
    run_test "禁用颜色输出" "$TRASH_CLEANER -L --no-color"
    
    # 测试禁用表头
    run_test "禁用表头" "$TRASH_CLEANER -L -H"
}

# 测试错误处理
test_error_handling() {
    print_test_header "错误处理测试"
    
    # 测试无效的分组方式
    run_test "无效分组方式" "$TRASH_CLEANER -L -g invalid" 1
    
    # 测试无效的排序方式  
    run_test "无效排序方式" "$TRASH_CLEANER -L -S invalid" 1
    
    # 测试无效的导出格式
    run_test "无效导出格式" "$TRASH_CLEANER -L -x invalid" 1
    
    # 测试无效的风险阈值
    run_test "无效风险阈值" "$TRASH_CLEANER -L -m abc" 1
}

# 性能测试
test_performance() {
    print_test_header "性能测试"
    
    print_info "开始性能测试..."
    
    local start_time end_time duration
    start_time=$(date +%s)
    
    # 运行一个复杂的测试用例
    if run_test "性能测试" "$TRASH_CLEANER --detailed -r -g type -S risk" 0; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        
        print_success "性能测试完成，耗时: ${duration}秒"
        
        if [[ $duration -le 10 ]]; then
            print_success "性能表现良好 (<= 10秒)"
        elif [[ $duration -le 30 ]]; then
            print_info "性能表现一般 (<= 30秒)"
        else
            print_failure "性能表现较差 (> 30秒)"
        fi
    fi
}

# 生成测试报告
generate_test_report() {
    local report_file="$TEST_OUTPUT_DIR/test_report_$(date "+%Y%m%d_%H%M%S").txt"
    
    {
        echo "回收站清理工具测试报告"
        echo "========================"
        echo "测试时间: $(date)"
        echo "测试环境: $(uname -a)"
        echo ""
        echo "测试结果统计:"
        echo "  总测试数: $TESTS_TOTAL"
        echo "  通过: $TESTS_PASSED"
        echo "  失败: $TESTS_FAILED"
        echo "  成功率: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%"
        echo ""
        
        if [[ $TESTS_FAILED -gt 0 ]]; then
            echo "失败的测试:"
            # 这里可以添加失败测试的详细信息
        fi
        
        echo ""
        echo "测试输出文件位置: $TEST_OUTPUT_DIR"
        
    } > "$report_file"
    
    print_info "测试报告已生成: $report_file"
}

# 主测试函数
main() {
    echo -e "${BLUE}回收站清理工具 - 功能测试套件${NC}"
    echo "================================"
    echo ""
    
    # 检查测试环境
    if [[ ! -f "$TRASH_CLEANER" ]]; then
        print_failure "找不到trash-cleaner.sh文件: $TRASH_CLEANER"
        exit 1
    fi
    
    if [[ ! -x "$TRASH_CLEANER" ]]; then
        print_info "设置执行权限: $TRASH_CLEANER"
        chmod +x "$TRASH_CLEANER"
    fi
    
    print_info "测试输出目录: $TEST_OUTPUT_DIR"
    print_info "开始测试..."
    echo ""
    
    # 运行所有测试
    test_basic_functionality
    echo ""
    
    test_precheck_functionality
    echo ""
    
    test_export_functionality
    echo ""
    
    test_parameter_combinations
    echo ""
    
    test_error_handling
    echo ""
    
    test_performance
    echo ""
    
    # 显示测试结果摘要
    echo -e "${BLUE}测试结果摘要${NC}"
    echo "=============="
    echo "总测试数: $TESTS_TOTAL"
    echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "失败: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        local success_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
        echo "成功率: ${success_rate}%"
        
        if [[ $success_rate -ge 90 ]]; then
            echo -e "${GREEN}✅ 测试结果优秀！${NC}"
        elif [[ $success_rate -ge 70 ]]; then
            echo -e "${YELLOW}⚠️  测试结果良好${NC}"
        else
            echo -e "${RED}❌ 测试结果需要改进${NC}"
        fi
    fi
    
    echo ""
    
    # 生成测试报告
    generate_test_report
    
    # 返回适当的退出码
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# 如果直接运行此脚本，执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi