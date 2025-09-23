# Python多线程基础演示项目

## 🎯 项目概述

本项目是一个全面的Python多线程基础演示系统，旨在通过实际的代码示例帮助学习者掌握Python多线程编程的核心概念和最佳实践。

## ✨ 主要特性

- 📚 **全面覆盖**: 涵盖线程创建、管理、同步、通信等所有核心概念
- 🎭 **交互式演示**: 提供友好的命令行界面，可选择性运行不同演示
- 💡 **实用场景**: 包含真实应用场景的综合演示
- 🔧 **易于扩展**: 模块化设计，便于添加新的演示内容
- 📖 **详细注释**: 每个示例都包含详细的代码注释和说明

## 🚀 快速开始

### 1. 环境要求

- Python 3.6+
- 支持threading模块的Python环境

### 2. 安装依赖

```bash
cd python-threading-demo
pip install -r requirements.txt
```

### 3. 运行演示

#### 完整演示系统
```bash
python main.py
```

#### 快速入门示例
```bash
python examples/quick_start.py
```

#### 测试项目
```bash
python test_project.py
```

## 项目结构

```
python-threading-demo/
├── src/                     # 源代码目录
│   ├── core/               # 核心功能模块
│   │   ├── creation/       # 线程创建模块
│   │   ├── management/     # 线程管理模块
│   │   ├── synchronization/ # 线程同步模块
│   │   └── communication/  # 线程通信模块
│   ├── demos/              # 演示场景
│   │   ├── scenarios/      # 各种演示场景
│   │   └── controller/     # 演示控制器
│   └── utils/              # 工具模块
│       ├── monitoring/     # 监控工具
│       └── logging/        # 日志工具
├── tests/                  # 测试文件
├── config/                 # 配置文件
├── docs/                   # 文档
├── examples/               # 使用示例
├── requirements.txt        # 依赖文件
└── README.md              # 项目说明
```

## 安装和运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行演示

```bash
python main.py
```

## 功能特性

### 1. 线程创建演示
- 基础线程创建（函数式）
- 线程类继承创建
- 线程池创建和管理

### 2. 线程管理演示
- 线程状态监控
- 线程生命周期管理
- 线程异常处理

### 3. 线程同步演示
- 互斥锁（Lock/RLock）
- 条件变量（Condition）
- 信号量（Semaphore）
- 读写锁演示

### 4. 线程通信演示
- 队列通信（Queue/LifoQueue/PriorityQueue）
- 事件通信（Event）
- 共享变量和局部存储

### 5. 实际应用场景
- 并发计算任务
- 生产者-消费者模式
- 资源池管理
- 任务调度系统
- 网络爬虫模拟

### 6. 性能监控演示
- CPU和内存使用率监控
- 线程数量和状态统计
- 性能指标历史记录和分析

### 7. 高级日志演示
- 结构化日志记录系统
- 日志分析和统计
- 错误模式识别和报告

## 目标用户

- Python初学者学习多线程编程
- 需要了解线程管理技术的开发者
- 希望掌握多线程同步机制的程序员

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License