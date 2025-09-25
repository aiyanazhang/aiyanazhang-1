#!/bin/bash
# Ruby基础演示项目验证脚本

echo "🔍 Ruby基础演示项目结构验证"
echo "================================"

# 检查主要目录
echo "📁 检查目录结构..."
required_dirs=("src" "config" "tests" "docs" "data" "examples")

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/ 目录存在"
    else
        echo "❌ $dir/ 目录缺失"
    fi
done

# 检查关键文件
echo -e "\n📄 检查关键文件..."
required_files=("main.rb" "Gemfile" "README.md" ".rubocop.yml")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 文件存在"
    else
        echo "❌ $file 文件缺失"
    fi
done

# 检查源代码模块
echo -e "\n🧩 检查源代码模块..."
src_modules=("basics" "collections" "oop" "modules" "blocks" "files")

for module in "${src_modules[@]}"; do
    if [ -d "src/$module" ]; then
        echo "✅ src/$module/ 模块存在"
        
        # 计算该模块中的Ruby文件数量
        file_count=$(find "src/$module" -name "*.rb" | wc -l)
        echo "   └── 包含 $file_count 个Ruby文件"
    else
        echo "❌ src/$module/ 模块缺失"
    fi
done

# 检查菜单系统
echo -e "\n🎮 检查菜单系统..."
if [ -f "src/menu_system.rb" ]; then
    echo "✅ 交互式菜单系统文件存在"
else
    echo "❌ 交互式菜单系统文件缺失"
fi

# 检查配置管理
echo -e "\n⚙️ 检查配置管理..."
if [ -f "config/config_manager.rb" ]; then
    echo "✅ 配置管理器文件存在"
else
    echo "❌ 配置管理器文件缺失"
fi

# 统计总体信息
echo -e "\n📊 项目统计..."
total_rb_files=$(find . -name "*.rb" | wc -l)
total_lines=$(find . -name "*.rb" -exec wc -l {} + | tail -1 | awk '{print $1}')

echo "总计 Ruby 文件: $total_rb_files"
echo "总计代码行数: $total_lines"

# 检查文件语法（如果Ruby可用）
echo -e "\n🔍 语法检查..."
if command -v ruby &> /dev/null; then
    echo "Ruby 已安装，进行语法检查..."
    
    syntax_errors=0
    for rb_file in $(find . -name "*.rb"); do
        if ruby -c "$rb_file" &> /dev/null; then
            echo "✅ $rb_file 语法正确"
        else
            echo "❌ $rb_file 语法错误"
            ((syntax_errors++))
        fi
    done
    
    if [ $syntax_errors -eq 0 ]; then
        echo "🎉 所有文件语法检查通过！"
    else
        echo "⚠️ 发现 $syntax_errors 个语法错误"
    fi
else
    echo "⚠️ Ruby 未安装，跳过语法检查"
    echo "请安装 Ruby 3.0+ 来运行此项目"
fi

echo -e "\n✨ 验证完成！"
echo "如需运行项目，请执行: ruby main.rb"