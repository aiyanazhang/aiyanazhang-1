#!/bin/bash
# Hello World系统集成测试脚本

echo "========================================="
echo "Hello World Python脚本系统集成测试"
echo "========================================="

cd /data/workspace/aiyanazhang-1/hello-world-system

failed_tests=0
total_tests=0

# 函数：运行测试并检查结果
run_test() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "测试 $test_name ... "
    total_tests=$((total_tests + 1))
    
    result=$(eval "$command" 2>&1)
    
    if [[ "$result" == *"$expected"* ]]; then
        echo "✓ 通过"
    else
        echo "✗ 失败"
        echo "  期望包含: $expected"
        echo "  实际输出: $result"
        failed_tests=$((failed_tests + 1))
    fi
}

# 基础功能测试
echo -e "\n1. 基础功能测试"
echo "--------------------------------"
run_test "默认问候" "python3 main.py" "Hello, World!"
run_test "个性化问候" "python3 main.py --name TestUser" "Hello, TestUser!"
run_test "中文问候" "python3 main.py --name 张三 --language zh" "你好，张三！"
run_test "详细模式" "python3 main.py --verbose" "Welcome to the Hello World System"

# 输出格式测试
echo -e "\n2. 输出格式测试"
echo "--------------------------------"
run_test "JSON格式" "python3 main.py --format json" '"greeting"'
run_test "XML格式" "python3 main.py --format xml" "<greeting"
run_test "文本格式" "python3 main.py --format text" "Hello, World!"

# 参数组合测试
echo -e "\n3. 参数组合测试"
echo "--------------------------------"
run_test "中文+JSON" "python3 main.py --name 测试 --language zh --format json" '"message": "你好，测试！"'
run_test "英文+XML+详细" "python3 main.py --name Test --language en --format xml --verbose" '<verbose>true</verbose>'

# 错误处理测试
echo -e "\n4. 错误处理测试"
echo "--------------------------------"
run_test "无效语言" "python3 main.py --language invalid 2>&1" "error:"
run_test "无效格式" "python3 main.py --format invalid 2>&1" "error:"

# 特殊字符测试
echo -e "\n5. 特殊字符测试"
echo "--------------------------------"
run_test "HTML转义" "python3 main.py --name '<script>'" "&lt;script&gt;"
run_test "长名称截断" "python3 main.py --name '$(printf "a%.0s" {1..100})'" "aaa..."

# 配置文件测试
echo -e "\n6. 配置文件测试"
echo "--------------------------------"
run_test "使用配置文件" "python3 main.py --config config/config.json" "Hello, World!"

# 帮助和版本测试
echo -e "\n7. 帮助和版本测试"
echo "--------------------------------"
run_test "帮助信息" "python3 main.py --help" "usage:"
run_test "版本信息" "python3 main.py --version" "1.0.0"

# 单元测试
echo -e "\n8. 单元测试"
echo "--------------------------------"
echo -n "运行单元测试 ... "
if python3 tests/test_all.py >/dev/null 2>&1; then
    echo "✓ 通过"
else
    echo "✗ 失败"
    failed_tests=$((failed_tests + 1))
fi
total_tests=$((total_tests + 1))

# 代码质量检查
echo -e "\n9. 代码质量检查"
echo "--------------------------------"
echo -n "语法检查 ... "
syntax_errors=0
for file in main.py src/*.py tests/*.py; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        syntax_errors=$((syntax_errors + 1))
    fi
done

if [ $syntax_errors -eq 0 ]; then
    echo "✓ 通过"
else
    echo "✗ 失败 ($syntax_errors 个文件有语法错误)"
    failed_tests=$((failed_tests + 1))
fi
total_tests=$((total_tests + 1))

# 文件结构检查
echo -e "\n10. 文件结构检查"
echo "--------------------------------"
required_files=(
    "main.py"
    "src/args_parser.py"
    "src/greeting.py" 
    "src/output.py"
    "src/config.py"
    "src/i18n.py"
    "config/config.json"
    "tests/test_all.py"
    "README.md"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files=$((missing_files + 1))
    fi
done

echo -n "文件完整性检查 ... "
if [ $missing_files -eq 0 ]; then
    echo "✓ 通过"
else
    echo "✗ 失败 ($missing_files 个必需文件缺失)"
    failed_tests=$((failed_tests + 1))
fi
total_tests=$((total_tests + 1))

# 性能测试
echo -e "\n11. 性能测试"
echo "--------------------------------"
echo -n "基本性能测试 ... "
start_time=$(date +%s.%N)
for i in {1..10}; do
    python3 main.py --name "User$i" >/dev/null 2>&1
done
end_time=$(date +%s.%N)
execution_time=$(echo "$end_time - $start_time" | bc -l)

# 如果执行时间小于5秒认为通过
if (( $(echo "$execution_time < 5.0" | bc -l) )); then
    echo "✓ 通过 (${execution_time}s)"
else
    echo "✗ 失败 (${execution_time}s，超过5秒)"
    failed_tests=$((failed_tests + 1))
fi
total_tests=$((total_tests + 1))

# 测试结果汇总
echo -e "\n========================================="
echo "测试结果汇总"
echo "========================================="
passed_tests=$((total_tests - failed_tests))
echo "总测试数: $total_tests"
echo "通过: $passed_tests"
echo "失败: $failed_tests"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n🎉 所有测试通过！Hello World系统运行正常。"
    exit 0
else
    echo -e "\n❌ 有 $failed_tests 个测试失败，请检查相关功能。"
    exit 1
fi