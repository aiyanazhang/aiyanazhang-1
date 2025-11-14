@echo off
echo ========================================
echo 快速功能验证测试
echo ========================================
echo.

echo 创建测试环境...
if not exist test-data mkdir test-data
cd test-data

echo 创建测试文件...
echo 这是一个测试文本文件 > sample.txt
echo {"test": "json file"} > config.json
echo @echo off > script.bat
echo # Test Markdown > readme.md

if not exist subdir mkdir subdir
cd subdir
echo 子目录文件 > subfile.txt
cd ..

echo.
echo 开始测试浏览器功能...
echo.

echo ========== 测试 1: 基本扫描 ==========
call ..\directory-browser.bat -d 2
echo.

echo ========== 测试 2: 过滤文件 ==========
call ..\directory-browser.bat -f "txt,md" -d 1
echo.

echo ========== 测试 3: 无预览模式 ==========
call ..\directory-browser.bat -p false -d 1
echo.

echo ========== 测试 4: 帮助信息 ==========
call ..\directory-browser.bat --help
echo.

cd ..
echo 清理测试环境...
rmdir /s /q test-data 2>nul

echo.
echo ========================================
echo 所有测试完成！
echo ========================================
pause