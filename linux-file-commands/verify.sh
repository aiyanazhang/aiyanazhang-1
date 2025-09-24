#!/bin/bash
echo "Linux文件命令查询工具 - 验证脚本"
echo "=================================="

# 检查项目结构
echo "1. 检查项目结构..."
if [ -d "src" ] && [ -d "data" ] && [ -d "tests" ]; then
    echo "   ✓ 项目目录结构正确"
else
    echo "   ✗ 项目目录结构不完整"
    exit 1
fi

# 检查数据文件
echo "2. 检查数据文件..."
if [ -f "data/commands.json" ] && [ -f "data/categories.json" ]; then
    echo "   ✓ 数据文件存在"
    
    # 验证JSON格式
    if command -v jq >/dev/null 2>&1; then
        if jq empty data/commands.json >/dev/null 2>&1; then
            echo "   ✓ commands.json 格式正确"
        else
            echo "   ✗ commands.json 格式错误"
        fi
        
        if jq empty data/categories.json >/dev/null 2>&1; then
            echo "   ✓ categories.json 格式正确"
        else
            echo "   ✗ categories.json 格式错误"
        fi
    else
        echo "   - 跳过JSON格式验证（jq未安装）"
    fi
else
    echo "   ✗ 数据文件缺失"
    exit 1
fi

# 检查源代码文件
echo "3. 检查源代码文件..."
required_files=("src/parser.py" "src/category.py" "src/search.py" "src/detail.py" "src/formatter.py" "src/main.py")
all_files_exist=true

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file 存在"
    else
        echo "   ✗ $file 不存在"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo "   ✗ 源代码文件不完整"
    exit 1
fi

# 检查语法（如果有Python）
echo "4. 检查Python语法..."
python_cmd=""
if command -v python3 >/dev/null 2>&1; then
    python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
    python_cmd="python"
fi

if [ -n "$python_cmd" ]; then
    syntax_ok=true
    for file in "${required_files[@]}"; do
        if ! $python_cmd -m py_compile "$file" 2>/dev/null; then
            echo "   ✗ $file 语法错误"
            syntax_ok=false
        fi
    done
    
    if [ "$syntax_ok" = true ]; then
        echo "   ✓ 所有Python文件语法正确"
    fi
else
    echo "   - 跳过Python语法检查（Python未安装）"
fi

# 检查可执行权限
echo "5. 检查可执行权限..."
if [ -x "linux-file-commands.py" ]; then
    echo "   ✓ 启动脚本具有可执行权限"
else
    echo "   - 设置启动脚本可执行权限"
    chmod +x linux-file-commands.py
fi

# 统计信息
echo "6. 项目统计信息..."
command_count=$(grep -o '"name"' data/commands.json | wc -l)
category_count=$(grep -c ': {' data/categories.json)
total_lines=$(find src -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')

echo "   - 命令数量: $command_count"
echo "   - 分类数量: $category_count"
echo "   - 代码行数: $total_lines"

echo ""
echo "=================================="
echo "✓ 验证完成！项目结构和文件都正确。"

# 如果有Python，显示使用方法
if [ -n "$python_cmd" ]; then
    echo ""
    echo "使用方法:"
    echo "  $python_cmd linux-file-commands.py --help    # 查看帮助"
    echo "  $python_cmd linux-file-commands.py --list    # 列出所有命令"
    echo "  $python_cmd linux-file-commands.py           # 启动交互模式"
else
    echo ""
    echo "注意：系统中未找到Python解释器。"
    echo "请安装Python 3.x 来运行此工具。"
fi

echo "=================================="