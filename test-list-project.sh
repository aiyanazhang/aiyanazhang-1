#!/bin/bash

# =============================================================================
# list-project.sh 测试脚本
# 
# 此脚本测试 list-project.sh 的所有功能
# =============================================================================

# set -e  # 禁用严格模式以便更好地处理错误

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST_PROJECT_SCRIPT="$SCRIPT_DIR/list-project.sh"
TEST_DIR="$SCRIPT_DIR/test_data"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $*"
    ((PASSED_TESTS++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $*"
    ((FAILED_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# 创建测试数据
create_test_data() {
    log_info "创建测试数据..."
    
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR"
    
    # 创建各种类型的文件和目录
    mkdir -p "$TEST_DIR/subdir1/subdir2"
    mkdir -p "$TEST_DIR/hidden_dir/.hidden_subdir"
    mkdir -p "$TEST_DIR/empty_dir"
    
    # 创建各种文件
    echo "Hello World" > "$TEST_DIR/test.txt"
    echo "Python code" > "$TEST_DIR/script.py"
    echo "JSON data" > "$TEST_DIR/data.json"
    echo "README content" > "$TEST_DIR/README.md"
    
    # 创建隐藏文件
    echo "hidden content" > "$TEST_DIR/.hidden_file"
    echo "config content" > "$TEST_DIR/.gitignore"
    
    # 创建子目录中的文件
    echo "nested file" > "$TEST_DIR/subdir1/nested.txt"
    echo "deep file" > "$TEST_DIR/subdir1/subdir2/deep.txt"
    echo "hidden nested" > "$TEST_DIR/hidden_dir/.hidden_subdir/hidden.txt"
    
    # 创建符号链接
    ln -sf "test.txt" "$TEST_DIR/link_to_file"
    ln -sf "subdir1" "$TEST_DIR/link_to_dir"
    
    # 设置不同的修改时间
    touch -t 202301010000 "$TEST_DIR/test.txt"
    touch -t 202302010000 "$TEST_DIR/script.py"
    touch -t 202303010000 "$TEST_DIR/data.json"
    
    log_success "测试数据创建完成"
}

# 运行单个测试
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    ((TOTAL_TESTS++))
    log_info "运行测试: $test_name"
    
    local output
    if output=$(eval "$test_command" 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$output" | grep -q "$expected_pattern"; then
            log_success "$test_name"
            return 0
        else
            log_error "$test_name - 输出不包含期望的模式: $expected_pattern"
            echo "实际输出:"
            echo "$output" | head -5
            return 1
        fi
    else
        log_error "$test_name - 命令执行失败"
        echo "错误输出:"
        echo "$output" | head -5
        return 1
    fi
}

# 测试帮助功能
test_help() {
    log_info "测试帮助功能..."
    run_test "帮助信息" \
        "'$LIST_PROJECT_SCRIPT' --help" \
        "项目内容和修改时间列表工具"
}

# 测试基本功能
test_basic_functionality() {
    log_info "测试基本功能..."
    
    run_test "简单列表" \
        "'$LIST_PROJECT_SCRIPT' '$TEST_DIR'" \
        "test.txt"
    
    run_test "包含隐藏文件" \
        "'$LIST_PROJECT_SCRIPT' -a '$TEST_DIR'" \
        ".hidden_file"
    
    run_test "限制深度" \
        "'$LIST_PROJECT_SCRIPT' -d 1 '$TEST_DIR'" \
        "test.txt"
}

# 测试输出格式
test_output_formats() {
    log_info "测试输出格式..."
    
    run_test "详细格式" \
        "'$LIST_PROJECT_SCRIPT' -f detailed '$TEST_DIR'" \
        "文件路径.*大小.*权限"
    
    run_test "JSON格式" \
        "'$LIST_PROJECT_SCRIPT' -f json '$TEST_DIR'" \
        '"scan_info"'
    
    run_test "CSV格式" \
        "'$LIST_PROJECT_SCRIPT' -f csv '$TEST_DIR'" \
        "type,path,size"
    
    run_test "表格格式" \
        "'$LIST_PROJECT_SCRIPT' -f table '$TEST_DIR'" \
        "文件路径.*大小.*权限"
}

# 测试排序功能
test_sorting() {
    log_info "测试排序功能..."
    
    run_test "按名称排序" \
        "'$LIST_PROJECT_SCRIPT' -s name '$TEST_DIR'" \
        ""
    
    run_test "按大小排序" \
        "'$LIST_PROJECT_SCRIPT' -s size '$TEST_DIR'" \
        ""
    
    run_test "按时间排序" \
        "'$LIST_PROJECT_SCRIPT' -s mtime '$TEST_DIR'" \
        ""
    
    run_test "按扩展名排序" \
        "'$LIST_PROJECT_SCRIPT' -s extension '$TEST_DIR'" \
        ""
    
    run_test "反向排序" \
        "'$LIST_PROJECT_SCRIPT' -s name -r '$TEST_DIR'" \
        ""
}

# 测试过滤功能
test_filtering() {
    log_info "测试过滤功能..."
    
    run_test "排除模式" \
        "'$LIST_PROJECT_SCRIPT' -e '*.py' '$TEST_DIR'" \
        "test.txt"
    
    run_test "包含模式" \
        "'$LIST_PROJECT_SCRIPT' -i '*.txt' '$TEST_DIR'" \
        "test.txt"
}

# 测试错误处理
test_error_handling() {
    log_info "测试错误处理..."
    
    run_test "无效目录" \
        "'$LIST_PROJECT_SCRIPT' /nonexistent/directory 2>&1 || true" \
        "目录不存在"
    
    run_test "无效格式" \
        "'$LIST_PROJECT_SCRIPT' -f invalid '$TEST_DIR' 2>&1 || true" \
        "无效的输出格式"
    
    run_test "无效排序" \
        "'$LIST_PROJECT_SCRIPT' -s invalid '$TEST_DIR' 2>&1 || true" \
        "无效的排序方式"
}

# 测试配置文件
test_config_file() {
    log_info "测试配置文件..."
    
    # 临时修改配置文件
    local temp_config="$TEST_DIR/.list-project.conf"
    cat > "$temp_config" << EOF
OUTPUT_FORMAT="json"
SORT_BY="size"
VERBOSE=true
EOF
    
    run_test "配置文件加载" \
        "cd '$TEST_DIR' && '$LIST_PROJECT_SCRIPT' ." \
        '"scan_info"'
    
    rm -f "$temp_config"
}

# 清理测试数据
cleanup_test_data() {
    log_info "清理测试数据..."
    rm -rf "$TEST_DIR"
    log_success "测试数据清理完成"
}

# 显示测试结果
show_test_results() {
    echo
    echo "==============================================="
    echo "测试结果汇总"
    echo "==============================================="
    echo "总测试数: $TOTAL_TESTS"
    echo -e "通过测试: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "失败测试: ${RED}$FAILED_TESTS${NC}"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}所有测试通过！${NC}"
        return 0
    else
        echo -e "${RED}有 $FAILED_TESTS 个测试失败${NC}"
        return 1
    fi
}

# 主测试函数
main() {
    echo "开始测试 list-project.sh ..."
    echo
    
    # 检查脚本是否存在
    if [[ ! -f "$LIST_PROJECT_SCRIPT" ]]; then
        log_error "找不到 list-project.sh 脚本: $LIST_PROJECT_SCRIPT"
        exit 1
    fi
    
    # 确保脚本可执行
    chmod +x "$LIST_PROJECT_SCRIPT"
    
    # 创建测试数据
    create_test_data
    
    # 运行所有测试
    test_help
    test_basic_functionality
    test_output_formats
    test_sorting
    test_filtering
    test_error_handling
    test_config_file
    
    # 清理
    cleanup_test_data
    
    # 显示结果
    show_test_results
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi