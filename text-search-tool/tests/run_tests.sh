#!/bin/bash

# ===============================================================================
# 文本搜索工具测试脚本
# 版本: 1.0.0
# 作者: AI Assistant  
# 描述: 对text-search.sh进行全面的功能测试
# ===============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# 测试配置
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TEXT_SEARCH_SCRIPT="${SCRIPT_DIR}/../text-search.sh"
readonly TEST_DATA_DIR="${SCRIPT_DIR}/../tests/test_data"
readonly TEST_RESULTS_DIR="${SCRIPT_DIR}/../tests/results"

# 测试统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

# 测试结果函数
test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

# 准备测试环境
setup_test_environment() {
    log_info "准备测试环境..."
    
    # 创建测试目录
    mkdir -p "$TEST_DATA_DIR" "$TEST_RESULTS_DIR"
    
    # 创建测试文件
    create_test_files
    
    # 检查脚本是否存在且可执行
    if [[ ! -f "$TEXT_SEARCH_SCRIPT" ]]; then
        log_error "找不到文本搜索脚本: $TEXT_SEARCH_SCRIPT"
        exit 1
    fi
    
    if [[ ! -x "$TEXT_SEARCH_SCRIPT" ]]; then
        log_error "文本搜索脚本没有执行权限: $TEXT_SEARCH_SCRIPT"
        exit 1
    fi
    
    log_info "测试环境准备完成"
}

# 创建测试文件
create_test_files() {
    log_info "创建测试文件..."
    
    # 创建Python测试文件
    cat > "${TEST_DATA_DIR}/test.py" << 'EOF'
#!/usr/bin/env python3
import os
import sys

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process_data(self):
        # TODO: implement error handling
        for item in self.data:
            print(f"Processing {item}")
    
    def calculate_sum(self, numbers):
        return sum(numbers)

def main():
    processor = DataProcessor()
    processor.process_data()
    
    # Test function call
    result = processor.calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")

if __name__ == "__main__":
    main()
EOF

    # 创建JavaScript测试文件
    cat > "${TEST_DATA_DIR}/test.js" << 'EOF'
// JavaScript test file
function main() {
    console.log("Hello World");
    // TODO: add validation
}

class MyClass {
    constructor() {
        this.name = "test";
    }
    
    processData() {
        console.log("Processing data...");
    }
}

function calculate(a, b) {
    return a + b;
}

main();
EOF

    # 创建Java测试文件
    cat > "${TEST_DATA_DIR}/Test.java" << 'EOF'
package com.example;

public class Test {
    public static void main(String[] args) {
        System.out.println("Hello World");
        // TODO: implement business logic
    }
    
    public void processData() {
        // function implementation here
        int result = calculate(10, 20);
        System.out.println(result);
    }
    
    private int calculate(int a, int b) {
        return a + b;
    }
}
EOF

    # 创建Shell脚本测试文件
    cat > "${TEST_DATA_DIR}/test.sh" << 'EOF'
#!/bin/bash
function main() {
    echo "Hello World"
    # TODO: implement main logic
    return 0
}

calculate() {
    local result=$(($1 + $2))
    echo $result
}

main "$@"
EOF

    # 创建文本文件
    cat > "${TEST_DATA_DIR}/README.txt" << 'EOF'
# Test Project

This is a test project for the text search tool.

## Functions
- main() function
- calculate() function
- process_data() method

## TODO Items
- TODO: Add error handling
- TODO: Implement validation
- TODO: Add documentation

## Classes
- DataProcessor class
- MyClass class
- Test class
EOF

    # 创建配置文件
    cat > "${TEST_DATA_DIR}/config.json" << 'EOF'
{
    "project": "text-search-test",
    "version": "1.0.0",
    "main": "main.py",
    "functions": [
        "main",
        "calculate",
        "process_data"
    ],
    "todo_items": [
        "TODO: Add error handling",
        "TODO: Implement validation"
    ]
}
EOF

    log_info "测试文件创建完成"
}

# 运行单个测试
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    local description="$4"
    
    ((TOTAL_TESTS++))
    log_test "运行测试: $test_name"
    
    if [[ -n "$description" ]]; then
        echo "    描述: $description"
    fi
    
    echo "    命令: $test_command"
    
    # 执行测试命令
    local output_file="${TEST_RESULTS_DIR}/${test_name}.out"
    local error_file="${TEST_RESULTS_DIR}/${test_name}.err"
    
    eval "$test_command" > "$output_file" 2> "$error_file"
    local actual_exit_code=$?
    
    # 检查退出代码
    if [[ $actual_exit_code -eq $expected_exit_code ]]; then
        test_pass "$test_name (退出代码: $actual_exit_code)"
    else
        test_fail "$test_name (期望退出代码: $expected_exit_code, 实际: $actual_exit_code)"
        echo "    错误输出: $(cat "$error_file")"
    fi
    
    echo "    输出文件: $output_file"
    echo
}

# 运行基本功能测试
test_basic_functionality() {
    log_info "开始基本功能测试..."
    
    # 测试1: 帮助信息
    run_test "help" \
        "$TEXT_SEARCH_SCRIPT --help" \
        0 \
        "显示帮助信息"
    
    # 测试2: 版本信息
    run_test "version" \
        "$TEXT_SEARCH_SCRIPT --version" \
        0 \
        "显示版本信息"
    
    # 测试3: 无参数运行（应该失败）
    run_test "no_args" \
        "$TEXT_SEARCH_SCRIPT" \
        1 \
        "无参数运行应该返回错误"
    
    # 测试4: 基本文本搜索
    run_test "basic_text_search" \
        "$TEXT_SEARCH_SCRIPT -p 'function' -d '$TEST_DATA_DIR'" \
        0 \
        "基本文本搜索"
    
    # 测试5: 显示行号
    run_test "line_numbers" \
        "$TEXT_SEARCH_SCRIPT -p 'TODO' -d '$TEST_DATA_DIR' -n" \
        0 \
        "显示行号搜索"
    
    # 测试6: 计数模式
    run_test "count_mode" \
        "$TEXT_SEARCH_SCRIPT -p 'function' -d '$TEST_DATA_DIR' -c" \
        0 \
        "计数模式搜索"
    
    # 测试7: 只显示文件名
    run_test "files_only" \
        "$TEXT_SEARCH_SCRIPT -p 'main' -d '$TEST_DATA_DIR' -l" \
        0 \
        "只显示文件名"
}

# 运行正则表达式测试
test_regex_functionality() {
    log_info "开始正则表达式测试..."
    
    # 测试1: 基本正则表达式
    run_test "basic_regex" \
        "$TEXT_SEARCH_SCRIPT -p '^function' -d '$TEST_DATA_DIR' -r" \
        0 \
        "基本正则表达式搜索"
    
    # 测试2: 复杂正则表达式
    run_test "complex_regex" \
        "$TEXT_SEARCH_SCRIPT -p 'class\s+\w+' -d '$TEST_DATA_DIR' -r" \
        0 \
        "复杂正则表达式搜索"
    
    # 测试3: 正则表达式与行号
    run_test "regex_with_lines" \
        "$TEXT_SEARCH_SCRIPT -p 'TODO.*implement' -d '$TEST_DATA_DIR' -r -n" \
        0 \
        "正则表达式与行号"
}

# 运行文件类型过滤测试
test_file_type_filtering() {
    log_info "开始文件类型过滤测试..."
    
    # 测试1: Python文件
    run_test "python_files" \
        "$TEXT_SEARCH_SCRIPT -p 'def' -d '$TEST_DATA_DIR' -t 'py'" \
        0 \
        "搜索Python文件"
    
    # 测试2: JavaScript文件
    run_test "javascript_files" \
        "$TEXT_SEARCH_SCRIPT -p 'function' -d '$TEST_DATA_DIR' -t 'js'" \
        0 \
        "搜索JavaScript文件"
    
    # 测试3: 多种文件类型
    run_test "multiple_types" \
        "$TEXT_SEARCH_SCRIPT -p 'main' -d '$TEST_DATA_DIR' -t 'py,js,java'" \
        0 \
        "搜索多种文件类型"
    
    # 测试4: 文本文件
    run_test "text_files" \
        "$TEXT_SEARCH_SCRIPT -p 'TODO' -d '$TEST_DATA_DIR' -t 'txt'" \
        0 \
        "搜索文本文件"
}

# 运行输出格式测试
test_output_formats() {
    log_info "开始输出格式测试..."
    
    # 测试1: 简单格式（默认）
    run_test "simple_format" \
        "$TEXT_SEARCH_SCRIPT -p 'function' -d '$TEST_DATA_DIR' -o simple" \
        0 \
        "简单格式输出"
    
    # 测试2: 详细格式
    run_test "detail_format" \
        "$TEXT_SEARCH_SCRIPT -p 'class' -d '$TEST_DATA_DIR' -o detail" \
        0 \
        "详细格式输出"
    
    # 测试3: JSON格式
    run_test "json_format" \
        "$TEXT_SEARCH_SCRIPT -p 'TODO' -d '$TEST_DATA_DIR' -o json" \
        0 \
        "JSON格式输出"
}

# 运行错误处理测试
test_error_handling() {
    log_info "开始错误处理测试..."
    
    # 测试1: 无效目录
    run_test "invalid_directory" \
        "$TEXT_SEARCH_SCRIPT -p 'test' -d '/nonexistent/directory'" \
        3 \
        "无效目录应该返回错误"
    
    # 测试2: 无效输出格式
    run_test "invalid_format" \
        "$TEXT_SEARCH_SCRIPT -p 'test' -d '$TEST_DATA_DIR' -o invalid" \
        1 \
        "无效输出格式应该返回错误"
    
    # 测试3: 无效并行作业数
    run_test "invalid_jobs" \
        "$TEXT_SEARCH_SCRIPT -p 'test' -d '$TEST_DATA_DIR' -j 0" \
        1 \
        "无效并行作业数应该返回错误"
    
    # 测试4: 空搜索模式
    run_test "empty_pattern" \
        "$TEXT_SEARCH_SCRIPT -p '' -d '$TEST_DATA_DIR'" \
        1 \
        "空搜索模式应该返回错误"
}

# 运行性能测试
test_performance() {
    log_info "开始性能测试..."
    
    # 测试1: 详细模式
    run_test "verbose_mode" \
        "$TEXT_SEARCH_SCRIPT -p 'function' -d '$TEST_DATA_DIR' -v" \
        0 \
        "详细模式搜索"
    
    # 测试2: 并行搜索
    run_test "parallel_search" \
        "$TEXT_SEARCH_SCRIPT -p 'main' -d '$TEST_DATA_DIR' -j 2" \
        0 \
        "并行搜索测试"
    
    # 测试3: 深度限制
    run_test "depth_limit" \
        "$TEXT_SEARCH_SCRIPT -p 'function' -d '$TEST_DATA_DIR' --max-depth 1" \
        0 \
        "搜索深度限制"
}

# 验证测试结果
verify_test_results() {
    log_info "验证测试结果..."
    
    # 检查基本搜索是否有输出
    local basic_output="${TEST_RESULTS_DIR}/basic_text_search.out"
    if [[ -f "$basic_output" && -s "$basic_output" ]]; then
        test_pass "基本搜索产生了输出"
    else
        test_fail "基本搜索没有产生输出"
    fi
    
    # 检查JSON输出格式
    local json_output="${TEST_RESULTS_DIR}/json_format.out"
    if [[ -f "$json_output" ]]; then
        if python3 -m json.tool "$json_output" >/dev/null 2>&1; then
            test_pass "JSON输出格式有效"
        else
            test_fail "JSON输出格式无效"
        fi
    fi
    
    # 检查帮助信息
    local help_output="${TEST_RESULTS_DIR}/help.out"
    if [[ -f "$help_output" ]]; then
        if grep -q "用法:" "$help_output" && grep -q "选项" "$help_output"; then
            test_pass "帮助信息包含必要内容"
        else
            test_fail "帮助信息内容不完整"
        fi
    fi
}

# 清理测试环境
cleanup_test_environment() {
    log_info "清理测试环境..."
    
    # 询问是否保留测试结果
    echo -n "是否保留测试结果? (y/N): "
    read -r keep_results
    
    if [[ "$keep_results" != "y" && "$keep_results" != "Y" ]]; then
        rm -rf "$TEST_RESULTS_DIR"
        log_info "测试结果已清理"
    else
        log_info "测试结果保留在: $TEST_RESULTS_DIR"
    fi
}

# 显示测试报告
show_test_report() {
    echo
    echo -e "${WHITE}=============== 测试报告 ===============${NC}"
    echo -e "${CYAN}总测试数:${NC} $TOTAL_TESTS"
    echo -e "${GREEN}通过:${NC} $PASSED_TESTS"
    echo -e "${RED}失败:${NC} $FAILED_TESTS"
    
    local success_rate=0
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    fi
    
    echo -e "${CYAN}成功率:${NC} ${success_rate}%"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}🎉 所有测试通过！${NC}"
    else
        echo -e "${RED}❌ 有 $FAILED_TESTS 个测试失败${NC}"
        echo -e "${YELLOW}请检查测试结果目录获取详细信息: $TEST_RESULTS_DIR${NC}"
    fi
    
    echo -e "${WHITE}======================================${NC}"
}

# 主函数
main() {
    echo -e "${WHITE}文本搜索工具测试套件${NC}"
    echo -e "${CYAN}开始执行自动化测试...${NC}"
    echo
    
    # 设置测试环境
    setup_test_environment
    
    # 运行各种测试
    test_basic_functionality
    test_regex_functionality
    test_file_type_filtering
    test_output_formats
    test_error_handling
    test_performance
    
    # 验证结果
    verify_test_results
    
    # 显示报告
    show_test_report
    
    # 清理环境
    cleanup_test_environment
    
    # 返回适当的退出代码
    if [[ $FAILED_TESTS -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi