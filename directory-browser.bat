@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 目录文件浏览批处理脚本
REM 版本: 1.0
REM 作者: AI Assistant
REM 描述: 递归浏览并显示当前目录下所有文件的结构和内容
REM ========================================

REM 设置控制台编码为UTF-8
chcp 65001 >nul 2>&1

REM 全局变量定义
set "SCRIPT_VERSION=1.0"
set "SCRIPT_NAME=Directory Browser"
set "CONFIG_FILE=browser_config.ini"
set "LOG_FILE=browser.log"

REM 默认配置参数
set "MAX_DEPTH=-1"
set "SHOW_HIDDEN=false"
set "PREVIEW_LINES=10"
set "MAX_FILE_SIZE=1024"
set "LOG_LEVEL=INFO"
set "SHOW_SIZE=true"
set "ENABLE_PREVIEW=true"
set "INTERACTIVE_MODE=false"
set "FILE_FILTER="

REM 显示字符定义
set "TREE_BRANCH=├──"
set "TREE_LAST=└──"
set "TREE_VERTICAL=│   "
set "TREE_SPACE=    "

REM 统计变量
set /a TOTAL_FILES=0
set /a TOTAL_DIRS=0
set /a TOTAL_SIZE=0

REM 颜色代码定义
set "COLOR_DIR=94"
set "COLOR_FILE=37"
set "COLOR_PREVIEW=36"
set "COLOR_ERROR=91"
set "COLOR_SUCCESS=92"
set "COLOR_WARNING=93"

REM 主程序入口
call :main %*
goto :eof

REM ========================================
REM 主程序函数
REM ========================================
:main
    call :log_message "INFO" "启动目录浏览器 v%SCRIPT_VERSION%"
    call :parse_arguments %*
    call :load_config
    call :initialize_display
    call :scan_directory "%CD%" 0 ""
    call :show_summary
    if "%INTERACTIVE_MODE%"=="true" call :interactive_mode
    call :log_message "INFO" "程序执行完成"
    goto :eof

REM ========================================
REM 参数解析模块
REM ========================================
:parse_arguments
    :arg_loop
    if "%~1"=="" goto :arg_done
    
    if /i "%~1"=="-d" (
        set "MAX_DEPTH=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--depth" (
        set "MAX_DEPTH=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="-s" (
        set "SHOW_SIZE=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--size" (
        set "SHOW_SIZE=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="-h" (
        set "SHOW_HIDDEN=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--hidden" (
        set "SHOW_HIDDEN=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="-f" (
        set "FILE_FILTER=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--filter" (
        set "FILE_FILTER=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="-p" (
        set "ENABLE_PREVIEW=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--preview" (
        set "ENABLE_PREVIEW=%~2"
        shift
        shift
        goto :arg_loop
    )
    if /i "%~1"=="-i" (
        set "INTERACTIVE_MODE=true"
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--interactive" (
        set "INTERACTIVE_MODE=true"
        shift
        goto :arg_loop
    )
    if /i "%~1"=="--help" (
        call :show_help
        exit /b 0
    )
    
    REM 未知参数
    call :log_message "WARNING" "未知参数: %~1"
    shift
    goto :arg_loop
    
    :arg_done
    goto :eof

REM ========================================
REM 配置管理器
REM ========================================
:load_config
    if exist "%CONFIG_FILE%" (
        call :log_message "INFO" "加载配置文件: %CONFIG_FILE%"
        for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
            set "%%a=%%b"
        )
    ) else (
        call :log_message "INFO" "使用默认配置"
    )
    goto :eof

:save_config
    echo MAX_DEPTH=%MAX_DEPTH% > "%CONFIG_FILE%"
    echo SHOW_HIDDEN=%SHOW_HIDDEN% >> "%CONFIG_FILE%"
    echo PREVIEW_LINES=%PREVIEW_LINES% >> "%CONFIG_FILE%"
    echo MAX_FILE_SIZE=%MAX_FILE_SIZE% >> "%CONFIG_FILE%"
    echo LOG_LEVEL=%LOG_LEVEL% >> "%CONFIG_FILE%"
    call :log_message "INFO" "配置已保存到: %CONFIG_FILE%"
    goto :eof

REM ========================================
REM 日志记录器
REM ========================================
:log_message
    set "log_level=%~1"
    set "log_msg=%~2"
    set "timestamp=%date% %time%"
    
    REM 检查日志级别
    if /i "%LOG_LEVEL%"=="DEBUG" goto :log_write
    if /i "%LOG_LEVEL%"=="INFO" (
        if /i "%log_level%"=="DEBUG" goto :eof
        goto :log_write
    )
    if /i "%LOG_LEVEL%"=="WARNING" (
        if /i "%log_level%"=="DEBUG" goto :eof
        if /i "%log_level%"=="INFO" goto :eof
        goto :log_write
    )
    if /i "%LOG_LEVEL%"=="ERROR" (
        if /i "%log_level%"=="ERROR" goto :log_write
        goto :eof
    )
    
    :log_write
    echo [%timestamp%] [%log_level%] %log_msg% >> "%LOG_FILE%"
    goto :eof

REM ========================================
REM 显示初始化
REM ========================================
:initialize_display
    cls
    call :print_color %COLOR_SUCCESS% "========================================="
    call :print_color %COLOR_SUCCESS% "    %SCRIPT_NAME% v%SCRIPT_VERSION%"
    call :print_color %COLOR_SUCCESS% "========================================="
    echo.
    call :print_color %COLOR_DIR% "扫描目录: %CD%"
    if not "%MAX_DEPTH%"=="-1" (
        call :print_color %COLOR_DIR% "最大深度: %MAX_DEPTH%"
    )
    if not "%FILE_FILTER%"=="" (
        call :print_color %COLOR_DIR% "文件过滤: %FILE_FILTER%"
    )
    echo.
    goto :eof

REM ========================================
REM 目录扫描引擎
REM ========================================
:scan_directory
    set "current_path=%~1"
    set /a "current_depth=%~2"
    set "prefix=%~3"
    
    REM 验证路径是否存在
    if not exist "%current_path%" (
        call :log_message "ERROR" "路径不存在: %current_path%"
        goto :eof
    )
    
    REM 检查深度限制
    if not "%MAX_DEPTH%"=="-1" (
        if %current_depth% geq %MAX_DEPTH% goto :eof
    )
    
    REM 获取目录中的所有项目并排序
    set "temp_file=%TEMP%\dir_browser_%RANDOM%.tmp"
    
    REM 先处理文件
    dir "%current_path%" /b /a-d /on 2>nul > "%temp_file%"
    if exist "%temp_file%" (
        for /f "usebackq delims=" %%f in ("%temp_file%") do (
            call :process_file "%current_path%\%%f" "%prefix%" "false"
        )
        del "%temp_file%" 2>nul
    )
    
    REM 再处理子目录
    dir "%current_path%" /b /ad /on 2>nul > "%temp_file%"
    if exist "%temp_file%" (
        for /f "usebackq delims=" %%d in ("%temp_file%") do (
            call :process_directory "%current_path%\%%d" %current_depth% "%prefix%" "%%d"
        )
        del "%temp_file%" 2>nul
    )
    
    goto :eof

REM ========================================
REM 文件处理函数
REM ========================================
:process_file
    set "file_path=%~1"
    set "prefix=%~2"
    set "is_last=%~3"
    
    REM 获取文件名
    for %%f in ("%file_path%") do set "file_name=%%~nxf"
    
    REM 检查隐藏文件
    if "%SHOW_HIDDEN%"=="false" (
        for %%f in ("%file_path%") do (
            if "%%~af" neq "%%~af" (
                if "%%~af:~0,1"=="h" goto :eof
            )
        )
    )
    
    REM 应用文件过滤器
    if not "%FILE_FILTER%"=="" (
        call :check_file_filter "%file_path%"
        if !filter_result!==false goto :eof
    )
    
    REM 增加文件计数
    set /a TOTAL_FILES+=1
    
    REM 显示文件
    if "%is_last%"=="true" (
        call :print_color %COLOR_FILE% "%prefix%%TREE_LAST% %file_name%"
    ) else (
        call :print_color %COLOR_FILE% "%prefix%%TREE_BRANCH% %file_name%"
    )
    
    REM 显示文件信息
    if "%SHOW_SIZE%"=="true" (
        call :get_file_info "%file_path%"
    )
    
    REM 预览文件内容
    if "%ENABLE_PREVIEW%"=="true" (
        call :preview_file_content "%file_path%" "%prefix%" 2>nul
    )
    
    goto :eof

REM ========================================
REM 目录处理函数
REM ========================================
:process_directory
    set "dir_path=%~1"
    set /a "depth=%~2"
    set "prefix=%~3"
    set "dir_name=%~4"
    
    REM 检查隐藏目录
    if "%SHOW_HIDDEN%"=="false" (
        for %%d in ("%dir_path%") do (
            if "%%~ad" neq "%%~ad" (
                if "%%~ad:~0,1"=="h" goto :eof
            )
        )
    )
    
    REM 增加目录计数
    set /a TOTAL_DIRS+=1
    
    REM 显示目录
    call :print_color %COLOR_DIR% "%prefix%%TREE_BRANCH% [DIR] %dir_name%"
    
    REM 递归扫描子目录
    set /a "next_depth=%depth%+1"
    call :scan_directory "%dir_path%" %next_depth% "%prefix%%TREE_VERTICAL%"
    
    goto :eof

REM ========================================
REM 文件分类器和过滤器
REM ========================================
:check_file_filter
    set "file_path=%~1"
    set "filter_result=true"
    
    if "%FILE_FILTER%"=="" goto :eof
    
    for %%f in ("%file_path%") do set "file_ext=%%~xf"
    set "file_ext=%file_ext:~1%"
    
    set "filter_result=false"
    for %%e in (%FILE_FILTER%) do (
        if /i "%file_ext%"=="%%e" set "filter_result=true"
    )
    
    goto :eof

:get_file_type
    set "file_path=%~1"
    for %%f in ("%file_path%") do set "file_ext=%%~xf"
    set "file_ext=%file_ext:~1%"
    
    REM 文本文件类型
    for %%e in (txt md log) do (
        if /i "%file_ext%"=="%%e" (
            set "file_type=text"
            goto :eof
        )
    )
    
    REM 配置文件类型
    for %%e in (ini conf cfg) do (
        if /i "%file_ext%"=="%%e" (
            set "file_type=config"
            goto :eof
        )
    )
    
    REM 脚本文件类型
    for %%e in (bat cmd ps1) do (
        if /i "%file_ext%"=="%%e" (
            set "file_type=script"
            goto :eof
        )
    )
    
    REM 数据文件类型
    for %%e in (json xml csv) do (
        if /i "%file_ext%"=="%%e" (
            set "file_type=data"
            goto :eof
        )
    )
    
    REM 代码文件类型
    for %%e in (py js html css java cpp c) do (
        if /i "%file_ext%"=="%%e" (
            set "file_type=code"
            goto :eof
        )
    )
    
    set "file_type=binary"
    goto :eof

REM ========================================
REM 文件信息获取
REM ========================================
:get_file_info
    set "file_path=%~1"
    
    for %%f in ("%file_path%") do (
        set "file_size=%%~zf"
        set "file_date=%%~tf"
    )
    
    call :format_file_size %file_size%
    echo     大小: %formatted_size% ^| 修改时间: %file_date%
    
    goto :eof

:format_file_size
    set /a "size=%~1"
    
    if %size% lss 1024 (
        set "formatted_size=%size% B"
        goto :eof
    )
    
    set /a "size_kb=%size%/1024"
    if %size_kb% lss 1024 (
        set "formatted_size=%size_kb% KB"
        goto :eof
    )
    
    set /a "size_mb=%size_kb%/1024"
    if %size_mb% lss 1024 (
        set "formatted_size=%size_mb% MB"
        goto :eof
    )
    
    set /a "size_gb=%size_mb%/1024"
    set "formatted_size=%size_gb% GB"
    goto :eof

REM ========================================
REM 内容预览器
REM ========================================
:preview_file_content
    set "file_path=%~1"
    set "prefix=%~2"
    
    REM 检查文件大小
    for %%f in ("%file_path%") do set /a "file_size=%%~zf/1024"
    if %file_size% gtr %MAX_FILE_SIZE% (
        call :print_color %COLOR_WARNING% "%prefix%    [文件过大，跳过预览]"
        goto :eof
    )
    
    REM 获取文件类型
    call :get_file_type "%file_path%"
    
    REM 根据文件类型决定预览行数
    set /a "lines_to_show=%PREVIEW_LINES%"
    if "%file_type%"=="script" set /a "lines_to_show=5"
    if "%file_type%"=="data" set /a "lines_to_show=5"
    if "%file_type%"=="code" set /a "lines_to_show=5"
    
    if "%file_type%"=="binary" (
        call :print_color %COLOR_WARNING% "%prefix%    [二进制文件，无法预览]"
        goto :eof
    )
    
    REM 显示文件内容预览
    echo %prefix%    --- 内容预览 ---
    
    set /a "line_count=0"
    for /f "usebackq delims=" %%l in ("%file_path%") do (
        if !line_count! lss %lines_to_show% (
            echo %prefix%    %%l
            set /a "line_count+=1"
        ) else (
            goto :preview_done
        )
    )
    
    :preview_done
    if %line_count% equ %lines_to_show% (
        echo %prefix%    [...]
    )
    
    goto :eof

REM ========================================
REM 用户交互控制器
REM ========================================
:interactive_mode
    echo.
    call :print_color %COLOR_SUCCESS% "========================================="
    call :print_color %COLOR_SUCCESS% "进入交互模式"
    call :print_color %COLOR_SUCCESS% "========================================="
    call :show_interactive_help
    
    :interactive_loop
    echo.
    set /p "user_input=请输入命令 (h=帮助, q=退出): "
    
    if /i "%user_input%"=="q" goto :eof
    if /i "%user_input%"=="quit" goto :eof
    if /i "%user_input%"=="exit" goto :eof
    
    if /i "%user_input%"=="h" (
        call :show_interactive_help
        goto :interactive_loop
    )
    if /i "%user_input%"=="help" (
        call :show_interactive_help
        goto :interactive_loop
    )
    
    if /i "%user_input%"=="s" (
        call :search_files
        goto :interactive_loop
    )
    if /i "%user_input%"=="search" (
        call :search_files
        goto :interactive_loop
    )
    
    if /i "%user_input%"=="f" (
        call :configure_filter
        goto :interactive_loop
    )
    if /i "%user_input%"=="filter" (
        call :configure_filter
        goto :interactive_loop
    )
    
    if /i "%user_input%"=="r" (
        call :rescan_directory
        goto :interactive_loop
    )
    if /i "%user_input%"=="rescan" (
        call :rescan_directory
        goto :interactive_loop
    )
    
    call :print_color %COLOR_ERROR% "未知命令: %user_input%"
    goto :interactive_loop

:show_interactive_help
    echo.
    echo 可用命令:
    echo   h, help    - 显示此帮助信息
    echo   s, search  - 搜索文件名
    echo   f, filter  - 配置文件过滤器
    echo   r, rescan  - 重新扫描目录
    echo   q, quit    - 退出程序
    goto :eof

:search_files
    set /p "search_term=请输入搜索关键词: "
    if "%search_term%"=="" goto :eof
    
    echo.
    call :print_color %COLOR_SUCCESS% "搜索结果:"
    
    for /f "delims=" %%f in ('dir /s /b "*%search_term%*" 2^>nul') do (
        echo   %%f
    )
    goto :eof

:configure_filter
    echo.
    echo 当前过滤器: %FILE_FILTER%
    set /p "new_filter=请输入新的文件扩展名过滤器 (用逗号分隔): "
    set "FILE_FILTER=%new_filter%"
    call :print_color %COLOR_SUCCESS% "过滤器已更新为: %FILE_FILTER%"
    goto :eof

:rescan_directory
    echo.
    call :print_color %COLOR_SUCCESS% "重新扫描目录..."
    set /a TOTAL_FILES=0
    set /a TOTAL_DIRS=0
    call :scan_directory "%CD%" 0 ""
    call :show_summary
    goto :eof

REM ========================================
REM 显示摘要信息
REM ========================================
:show_summary
    echo.
    call :print_color %COLOR_SUCCESS% "========================================="
    call :print_color %COLOR_SUCCESS% "扫描完成统计"
    call :print_color %COLOR_SUCCESS% "========================================="
    echo 总文件数: %TOTAL_FILES%
    echo 总目录数: %TOTAL_DIRS%
    echo 扫描路径: %CD%
    if not "%MAX_DEPTH%"=="-1" echo 扫描深度: %MAX_DEPTH%
    echo.
    goto :eof

REM ========================================
REM 帮助信息显示
REM ========================================
:show_help
    echo.
    echo %SCRIPT_NAME% v%SCRIPT_VERSION%
    echo.
    echo 用法: %~nx0 [选项]
    echo.
    echo 选项:
    echo   -d, --depth ^<数字^>      设置最大扫描深度 (默认: 无限制)
    echo   -s, --size ^<true/false^> 显示文件大小信息 (默认: true)
    echo   -h, --hidden ^<true/false^> 包含隐藏文件 (默认: false)
    echo   -f, --filter ^<扩展名^>   文件扩展名过滤器 (如: txt,log)
    echo   -p, --preview ^<true/false^> 启用内容预览 (默认: true)
    echo   -i, --interactive       启用交互模式
    echo   --help                  显示此帮助信息
    echo.
    echo 示例:
    echo   %~nx0 -d 3 -f "txt,log" -i
    echo   %~nx0 --depth 2 --preview false
    echo.
    goto :eof

REM ========================================
 REM 辅助函数
REM ========================================
:print_color
    set "color_code=%~1"
    set "message=%~2"
    
    REM 简化输出，避免ANSI转义序列问题
    echo %message%
    goto :eof

REM 安全的字符串处理函数
:safe_echo
    set "msg=%~1"
    REM 处理特殊字符
    set "msg=%msg:&=^&%"
    set "msg=%msg:|=^|%"
    set "msg=%msg:<=^<%"
    set "msg=%msg:>=^>%"
    echo %msg%
    goto :eof

REM 错误处理函数
:handle_error
    set "error_msg=%~1"
    set "error_code=%~2"
    if "%error_code%"=="" set "error_code=1"
    
    echo.
    echo [错误] %error_msg%
    call :log_message "ERROR" "%error_msg%"
    
    if "%INTERACTIVE_MODE%"=="true" (
        echo.
        pause
    )
    goto :eof

REM 路径验证函数
:validate_path
    set "check_path=%~1"
    set "path_valid=false"
    
    if exist "%check_path%" set "path_valid=true"
    goto :eof