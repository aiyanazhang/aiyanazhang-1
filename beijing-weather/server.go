package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
)

func main() {
    // 设置静态文件服务
    fs := http.FileServer(http.Dir("."))
    http.Handle("/", fs)

    // 获取端口，默认8000
    port := "8000"
    if len(os.Args) > 1 {
        port = os.Args[1]
    }

    fmt.Printf("服务器启动在端口 %s\n", port)
    fmt.Printf("访问地址: http://localhost:%s\n", port)
    
    // 启动服务器
    log.Fatal(http.ListenAndServe(":"+port, nil))
}