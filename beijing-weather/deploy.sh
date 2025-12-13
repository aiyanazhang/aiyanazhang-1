#!/bin/bash

# 北京朝阳区天气显示页面 - 部署脚本
# 用于本地开发和生产部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "北京朝阳区天气显示页面 - 部署脚本"
    echo ""
    echo "用法: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "命令:"
    echo "  start       启动开发服务器"
    echo "  build       构建生产版本"
    echo "  test        运行测试"
    echo "  deploy      部署到生产环境"
    echo "  clean       清理临时文件"
    echo "  help        显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  -p, --port PORT    指定端口 (默认: 8000)"
    echo "  -h, --help         显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start               # 启动开发服务器"
    echo "  $0 start -p 3000       # 在端口3000启动服务器"
    echo "  $0 build               # 构建生产版本"
    echo "  $0 test                # 运行测试"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Go是否安装
    if ! command -v go &> /dev/null; then
        log_error "Go未安装，请先安装Go"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 启动开发服务器
start_dev_server() {
    local port=${1:-8000}
    
    log_info "启动开发服务器 (端口: $port)..."
    
    # 检查端口是否被占用
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $port 已被占用"
        read -p "是否终止占用进程并继续? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "终止占用端口 $port 的进程..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        else
            log_error "启动失败：端口被占用"
            exit 1
        fi
    fi
    
    log_info "正在启动服务器..."
    echo ""
    echo "=================================="
    echo "🌤️  北京朝阳区天气显示页面"
    echo "=================================="
    echo "本地访问地址:"
    echo "  主页面: http://localhost:$port"
    echo "  测试页面: http://localhost:$port/test.html"
    echo ""
    echo "按 Ctrl+C 停止服务器"
    echo "=================================="
    echo ""
    
    # 启动Go服务器
    go run server.go $port
}

# 构建生产版本
build_production() {
    log_info "构建生产版本..."
    
    # 创建构建目录
    local build_dir="dist"
    rm -rf $build_dir
    mkdir -p $build_dir
    
    log_info "复制文件..."
    
    # 复制HTML文件
    cp index.html $build_dir/
    
    # 复制CSS文件（可以在这里添加压缩步骤）
    mkdir -p $build_dir/src/css
    cp src/css/*.css $build_dir/src/css/
    
    # 复制JavaScript文件（可以在这里添加压缩步骤）
    mkdir -p $build_dir/src/js
    cp src/js/*.js $build_dir/src/js/
    
    # 复制图片资源
    if [ -d "src/images" ]; then
        mkdir -p $build_dir/src/images
        cp -r src/images/* $build_dir/src/images/
    fi
    
    # 创建生产配置
    log_info "优化生产配置..."
    
    # 在生产版本中禁用调试
    sed -i.bak 's/ENABLED: true/ENABLED: false/g' $build_dir/src/js/config.js
    sed -i.bak 's/LOG_LEVEL: '\''info'\''/LOG_LEVEL: '\''error'\''/g' $build_dir/src/js/config.js
    rm $build_dir/src/js/config.js.bak
    
    # 创建部署说明
    cat > $build_dir/README.md << EOF
# 北京朝阳区天气显示页面 - 生产版本

这是构建好的生产版本，可以直接部署到静态文件服务器。

## 部署方式

### 1. 上传到静态托管服务
- GitHub Pages
- Netlify  
- Vercel
- 阿里云OSS
- 腾讯云COS

### 2. 配置Web服务器
- Nginx
- Apache
- Caddy

### 3. 使用容器部署
\`\`\`bash
# 使用nginx镜像
docker run -d -p 80:80 -v \$(pwd):/usr/share/nginx/html nginx
\`\`\`

## 注意事项

1. 确保配置了正确的API密钥
2. 启用HTTPS以确保安全
3. 配置适当的缓存策略
4. 监控API使用量

## 文件结构
\`\`\`
dist/
├── index.html              # 主页面
├── src/                    # 源文件
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件  
│   └── images/            # 图片资源
└── README.md              # 部署说明
\`\`\`
EOF
    
    log_success "生产版本构建完成: $build_dir/"
    
    # 显示构建统计
    log_info "构建统计:"
    echo "  文件数量: $(find $build_dir -type f | wc -l)"
    echo "  总大小: $(du -sh $build_dir | cut -f1)"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 启动临时服务器进行测试
    log_info "启动测试服务器..."
    go run server.go 8080 &
    SERVER_PID=$!
    
    # 等待服务器启动
    sleep 2
    
    # 检查服务器是否启动成功
    if ! curl -s http://localhost:8080 > /dev/null; then
        log_error "测试服务器启动失败"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    log_info "运行基础测试..."
    
    # 测试主页面
    if curl -s http://localhost:8080 | grep -q "北京朝阳区天气"; then
        log_success "主页面测试通过"
    else
        log_error "主页面测试失败"
    fi
    
    # 测试CSS文件
    if curl -s http://localhost:8080/src/css/styles.css | grep -q "weather-app"; then
        log_success "CSS文件测试通过"
    else
        log_error "CSS文件测试失败"
    fi
    
    # 测试JavaScript文件
    if curl -s http://localhost:8080/src/js/config.js | grep -q "WeatherConfig"; then
        log_success "JavaScript文件测试通过"
    else
        log_error "JavaScript文件测试失败"
    fi
    
    # 测试页面
    if curl -s http://localhost:8080/test.html | grep -q "测试页面"; then
        log_success "测试页面可访问"
    else
        log_error "测试页面访问失败"
    fi
    
    # 关闭测试服务器
    kill $SERVER_PID 2>/dev/null || true
    
    log_success "所有测试完成"
}

# 部署到生产环境
deploy_production() {
    log_info "部署到生产环境..."
    
    # 确保先构建
    if [ ! -d "dist" ]; then
        log_info "未找到构建文件，先执行构建..."
        build_production
    fi
    
    log_warning "这是一个示例部署脚本"
    log_info "请根据实际部署环境修改此脚本"
    
    echo ""
    echo "支持的部署目标:"
    echo "1. GitHub Pages"
    echo "2. Netlify"
    echo "3. Vercel"
    echo "4. 自建服务器"
    echo ""
    
    read -p "请选择部署目标 [1-4]: " -n 1 -r
    echo ""
    
    case $REPLY in
        1)
            log_info "GitHub Pages部署说明:"
            echo "1. 将dist目录内容推送到gh-pages分支"
            echo "2. 在仓库设置中启用GitHub Pages"
            echo "3. 选择gh-pages分支作为源"
            ;;
        2)
            log_info "Netlify部署说明:"
            echo "1. 将dist目录拖拽到 https://app.netlify.com/drop"
            echo "2. 或者连接Git仓库自动部署"
            ;;
        3)
            log_info "Vercel部署说明:"
            echo "1. 安装Vercel CLI: npm i -g vercel"
            echo "2. 在dist目录运行: vercel"
            ;;
        4)
            log_info "自建服务器部署说明:"
            echo "1. 将dist目录上传到服务器"
            echo "2. 配置Web服务器指向该目录"
            echo "3. 确保HTTPS配置正确"
            ;;
        *)
            log_warning "无效选择"
            ;;
    esac
}

# 清理临时文件
clean_files() {
    log_info "清理临时文件..."
    
    # 清理构建文件
    if [ -d "dist" ]; then
        rm -rf dist
        log_success "已删除构建目录"
    fi
    
    # 清理日志文件
    if [ -f "server.log" ]; then
        rm -f server.log
        log_success "已删除日志文件"
    fi
    
    log_success "清理完成"
}

# 主函数
main() {
    local command=""
    local port=8000
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            start)
                command="start"
                shift
                ;;
            build)
                command="build"
                shift
                ;;
            test)
                command="test"
                shift
                ;;
            deploy)
                command="deploy"
                shift
                ;;
            clean)
                command="clean"
                shift
                ;;
            help|--help|-h)
                show_help
                exit 0
                ;;
            -p|--port)
                port="$2"
                shift 2
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定命令，显示帮助
    if [ -z "$command" ]; then
        show_help
        exit 0
    fi
    
    # 检查依赖
    check_dependencies
    
    # 执行对应命令
    case $command in
        start)
            start_dev_server $port
            ;;
        build)
            build_production
            ;;
        test)
            run_tests
            ;;
        deploy)
            deploy_production
            ;;
        clean)
            clean_files
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"