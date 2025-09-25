package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
    "time"
)

// 日志中间件
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // 记录请求开始
        log.Printf("[%s] %s %s - 开始处理", 
            time.Now().Format("2006-01-02 15:04:05"),
            r.Method, r.URL.Path)
        
        // 创建响应记录器
        lrw := &loggingResponseWriter{
            ResponseWriter: w,
            statusCode:     200,
        }
        
        // 处理请求
        next.ServeHTTP(lrw, r)
        
        // 记录请求完成
        duration := time.Since(start)
        log.Printf("[%s] %s %s - 完成 [状态:%d] [耗时:%v] [客户端:%s] [用户代理:%s]",
            time.Now().Format("2006-01-02 15:04:05"),
            r.Method, r.URL.Path, lrw.statusCode, duration,
            r.RemoteAddr, r.UserAgent())
    })
}

// 响应记录器
type loggingResponseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (lrw *loggingResponseWriter) WriteHeader(code int) {
    lrw.statusCode = code
    lrw.ResponseWriter.WriteHeader(code)
}

func main() {
    // 设置日志格式
    log.SetFlags(log.LstdFlags)
    
    // 设置静态文件服务
    fs := http.FileServer(http.Dir("."))
    
    // 添加日志中间件
    http.Handle("/", loggingMiddleware(fs))

    // 获取端口，默认8000
    port := "8000"
    if len(os.Args) > 1 {
        port = os.Args[1]
    }

    fmt.Printf("🌤️  北京朝阳区天气显示页面\n")
    fmt.Printf("================================\n")
    fmt.Printf("服务器启动时间: %s\n", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Printf("监听端口: %s\n", port)
    fmt.Printf("访问地址: http://localhost:%s\n", port)
    fmt.Printf("测试地址: http://localhost:%s/test.html\n", port)
    fmt.Printf("================================\n")
    fmt.Printf("服务器正在运行中，按 Ctrl+C 停止...\n\n")
    
    // 启动服务器
    log.Printf("[%s] 服务器开始监听端口 %s", time.Now().Format("2006-01-02 15:04:05"), port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}