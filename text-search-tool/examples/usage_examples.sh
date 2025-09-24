#!/bin/bash

# ===============================================================================
# 文本搜索工具使用示例
# 版本: 1.0.0
# 作者: AI Assistant
# 描述: 展示text-search.sh的各种使用场景和最佳实践
# ===============================================================================

# 脚本路径（根据实际情况调整）
SCRIPT_PATH="$(dirname "$0")/../text-search.sh"

echo "=== 文本搜索工具使用示例 ==="
echo

# 1. 基本搜索示例
echo "1. 基本文本搜索"
echo "命令: $SCRIPT_PATH -p 'function'"
echo "说明: 搜索包含'function'的所有文件"
echo

# 2. 正则表达式搜索
echo "2. 正则表达式搜索"
echo "命令: $SCRIPT_PATH -p '^class\s+\w+' -r"
echo "说明: 搜索以'class'开头后跟空格和单词的行"
echo

# 3. 文件类型过滤
echo "3. 文件类型过滤"
echo "命令: $SCRIPT_PATH -p 'import' -t 'py,js'"
echo "说明: 只在Python和JavaScript文件中搜索'import'"
echo

# 4. 显示行号
echo "4. 显示行号"
echo "命令: $SCRIPT_PATH -p 'TODO' -n"
echo "说明: 搜索TODO并显示行号"
echo

# 5. 计数模式
echo "5. 计数模式"
echo "命令: $SCRIPT_PATH -p 'function' -c"
echo "说明: 只显示每个文件中'function'的出现次数"
echo

# 6. 详细输出格式
echo "6. 详细输出格式"
echo "命令: $SCRIPT_PATH -p 'main' -o detail"
echo "说明: 以详细格式显示搜索结果，包含文件信息"
echo

# 7. JSON输出格式
echo "7. JSON输出格式"
echo "命令: $SCRIPT_PATH -p 'error' -o json"
echo "说明: 以JSON格式输出结果，便于程序处理"
echo

# 8. 排除目录
echo "8. 排除目录"
echo "命令: $SCRIPT_PATH -p 'config' -e '.git,node_modules,target'"
echo "说明: 搜索'config'但排除版本控制和构建目录"
echo

# 9. 并行搜索
echo "9. 并行搜索"
echo "命令: $SCRIPT_PATH -p 'data' -j 4"
echo "说明: 使用4个并行作业进行搜索"
echo

# 10. 限制搜索深度
echo "10. 限制搜索深度"
echo "命令: $SCRIPT_PATH -p 'test' --max-depth 3"
echo "说明: 只搜索3层深度内的文件"
echo

# 实际执行一些示例（如果脚本存在）
if [[ -f "$SCRIPT_PATH" && -x "$SCRIPT_PATH" ]]; then
    echo "=== 实际执行示例 ==="
    echo
    
    echo "执行: 搜索当前目录中的'function'"
    $SCRIPT_PATH -p 'function' 2>/dev/null || echo "搜索完成"
    echo
    
    echo "执行: 显示帮助信息"
    $SCRIPT_PATH --help
    echo
    
    echo "执行: 显示版本信息"
    $SCRIPT_PATH --version
    echo
else
    echo "注意: 脚本文件不存在或没有执行权限: $SCRIPT_PATH"
fi

echo "=== 更多高级示例 ==="
echo

cat << 'EOF'
高级搜索模式:

1. 查找空函数:
   ./text-search.sh -p 'function\s+\w+\s*\(\)\s*\{\s*\}' -r

2. 查找长行（超过80字符）:
   ./text-search.sh -p '.{81,}' -r

3. 查找邮箱地址:
   ./text-search.sh -p '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' -r

4. 查找IP地址:
   ./text-search.sh -p '([0-9]{1,3}\.){3}[0-9]{1,3}' -r

5. 查找注释中的TODO/FIXME:
   ./text-search.sh -p '(//|#|\*)\s*(TODO|FIXME|XXX|HACK)' -r

6. 查找函数调用:
   ./text-search.sh -p '\w+\s*\(' -r

7. 查找SQL注入风险:
   ./text-search.sh -p 'SELECT.*FROM.*WHERE.*\+|\$_GET|\$_POST' -r

8. 查找密码相关代码:
   ./text-search.sh -p 'password|passwd|pwd' -i

实际项目使用场景:

1. 代码审查 - 查找潜在问题:
   ./text-search.sh -p '(console\.log|print|debug|alert)' -r -t 'js,py,java'

2. 安全审计 - 查找硬编码凭据:
   ./text-search.sh -p '(password|secret|token|key)\s*=\s*["\'][^"\']+["\']' -r

3. 重构准备 - 查找废弃API:
   ./text-search.sh -p 'deprecated|obsolete|legacy' -i

4. 文档检查 - 查找未完成内容:
   ./text-search.sh -p 'TODO|FIXME|XXX|TBD' -t 'md,txt,rst'

5. 配置审核 - 查找配置文件:
   ./text-search.sh -p 'database|connection|server' -t 'conf,ini,json,yaml,yml'

6. 性能优化 - 查找性能热点:
   ./text-search.sh -p 'loop|foreach|while|for\s*\(' -r

7. 测试覆盖 - 查找测试文件:
   ./text-search.sh -p 'test|spec|assert' -t 'py,js,java' -d tests/

与其他工具结合使用:

1. 与git结合:
   git ls-files | xargs -I {} ./text-search.sh -p 'pattern' {}

2. 与find结合:
   find . -name "*.py" -exec ./text-search.sh -p 'import' {} \;

3. 与xargs结合:
   ./text-search.sh -p 'function' -l | xargs wc -l

4. 与awk结合:
   ./text-search.sh -p 'error' -c | awk '{sum+=$1} END {print sum}'

5. 与sed结合替换:
   ./text-search.sh -p 'old_function' -l | xargs sed -i 's/old_function/new_function/g'

性能优化建议:

1. 使用文件类型过滤减少搜索范围
2. 排除不必要的目录（如node_modules, .git）
3. 在多核系统上使用并行搜索
4. 对大文件设置大小限制
5. 使用缓存机制（脚本内置）

监控和日志:

1. 查看详细执行信息:
   ./text-search.sh -p 'pattern' -v

2. 记录搜索历史:
   ./text-search.sh -p 'pattern' -v 2>&1 | tee search.log

3. 性能测试:
   time ./text-search.sh -p 'pattern' -j 8

4. 内存使用监控:
   /usr/bin/time -v ./text-search.sh -p 'pattern'
EOF

echo
echo "=== 脚本完成 ==="
echo "更多信息请参阅: docs/USER_GUIDE.md"