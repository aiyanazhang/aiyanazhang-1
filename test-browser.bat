@echo off
echo ========================================
echo 测试目录浏览器脚本
echo ========================================
echo.

echo 测试1: 基本功能测试
echo 运行: directory-browser.bat -d 2
echo.
call directory-browser.bat -d 2
echo.

echo ========================================
echo 测试2: 文件过滤测试  
echo 运行: directory-browser.bat -f "txt,md"
echo.
call directory-browser.bat -f "txt,md"
echo.

echo ========================================
echo 测试3: 无预览模式测试
echo 运行: directory-browser.bat -p false
echo.
call directory-browser.bat -p false
echo.

echo ========================================
echo 测试4: 显示帮助信息
echo 运行: directory-browser.bat --help
echo.
call directory-browser.bat --help
echo.

echo ========================================
echo 所有测试完成
echo ========================================
pause