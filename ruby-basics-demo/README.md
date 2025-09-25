# Ruby基础用法演示项目

一个全面的Ruby编程语言基础教程演示系统，通过实际可运行的代码示例帮助初学者掌握Ruby的核心概念和基本用法。

## 🎯 项目特色

- **💡 全面覆盖**: 从基本语法到面向对象编程的完整Ruby基础知识
- **🎮 交互式学习**: 友好的命令行界面，支持逐步学习
- **📝 实践导向**: 每个概念都有可运行的代码示例
- **🎨 彩色输出**: 美观的终端输出，提升学习体验
- **⚙️ 灵活配置**: 可自定义的显示和学习设置

## 📋 系统要求

- Ruby 3.0+ (推荐)
- 支持colorize gem的终端环境

## 🚀 快速开始

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd ruby-basics-demo

# 安装Ruby gems
bundle install
```

### 运行程序

```bash
# 启动交互式菜单
ruby main.rb

# 运行所有演示
ruby main.rb --demo all

# 运行特定演示
ruby main.rb --demo basics

# 查看帮助
ruby main.rb --help
```

## 📚 学习内容

### 1. 基础语法模块
- **变量类型**: 局部变量、实例变量、类变量、全局变量
- **数据类型**: 数字、字符串、符号、布尔值、nil
- **类型转换**: 安全转换方法和类型检查

### 2. 控制结构模块
- **条件语句**: if/elsif/else, case/when, unless
- **循环结构**: while, until, for, 范围操作
- **流程控制**: break, next, redo
- **条件赋值**: ||=, &&=, 安全导航操作符

### 3. 集合操作模块
- **数组操作**: 创建、访问、修改、遍历、变换
- **哈希操作**: 键值对管理、遍历、合并、转换
- **高级特性**: 链式调用、函数式编程风格

### 4. 面向对象编程模块
- **类与对象**: 类定义、实例化、方法定义
- **继承机制**: 单继承、方法重写、super关键字
- **访问控制**: public, private, protected
- **高级特性**: 动态方法、单例方法、方法别名

### 5. 模块与混入系统
- **模块定义**: 命名空间、常量管理
- **混入机制**: include, extend, 方法查找链
- **实际应用**: 代码重用、功能组合

### 6. 块与迭代器模块
- **块语法**: 大括号和do...end语法
- **yield关键字**: 块调用和参数传递
- **常用迭代器**: each, map, select, reduce
- **高级特性**: Proc和Lambda

### 7. 文件操作模块
- **文件I/O**: 读取、写入、追加
- **目录操作**: 遍历、路径管理
- **异常处理**: 安全的文件操作

## 🎮 使用指南

### 交互式菜单

启动程序后，您将看到主菜单：

```
🏠 主菜单
────────────────────────────────────────
1. 📝 基础语法演示
2. 🔄 控制结构演示
3. 📊 集合操作演示
4. 🏗️  面向对象编程演示
5. 📦 模块与混入演示
6. 🔁 块与迭代器演示
7. 📁 文件操作演示
8. 🎯 综合应用示例
9. ❓ 关于系统
10. 🚪 退出程序
```

### 命令行模式

```bash
# 运行所有演示
ruby main.rb --demo all

# 运行基础语法演示
ruby main.rb --demo basics

# 运行面向对象演示
ruby main.rb --demo oop

# 运行集合操作演示
ruby main.rb --demo collections

# 查看版本信息
ruby main.rb --version

# 配置管理
ruby main.rb --config
```

## ⚙️ 配置选项

项目支持多种配置选项，存储在 `config/settings.yml` 中：

```yaml
display:
  colors: true              # 启用彩色输出
  clear_screen: true        # 自动清屏
  show_line_numbers: true   # 显示代码行号
  pause_after_demo: true    # 演示后暂停

demo:
  auto_run: false          # 自动运行模式
  show_explanations: true  # 显示详细说明
  detailed_output: true    # 详细输出模式

system:
  log_level: info         # 日志级别
  auto_save: true         # 自动保存配置
```

## 🧪 运行测试

```bash
# 运行所有测试
bundle exec rspec

# 运行特定测试文件
bundle exec rspec tests/basic_syntax_test.rb

# 生成测试覆盖率报告
bundle exec rspec --format documentation
```

## 📁 项目结构

```
ruby-basics-demo/
├── src/                    # 源代码目录
│   ├── basics/            # 基础语法演示
│   ├── collections/       # 集合操作演示
│   ├── oop/              # 面向对象演示
│   ├── modules/          # 模块演示
│   ├── blocks/           # 块演示
│   ├── files/            # 文件操作演示
│   └── menu_system.rb    # 菜单系统
├── config/                # 配置文件
│   └── config_manager.rb  # 配置管理器
├── tests/                 # 测试文件
├── docs/                  # 文档
├── data/                  # 数据文件
├── main.rb               # 主程序入口
├── Gemfile               # Ruby依赖配置
└── README.md             # 项目说明
```

## 🎓 学习建议

1. **按顺序学习**: 建议从基础语法开始，逐步学习各个模块
2. **动手实践**: 尝试修改演示代码，观察输出变化
3. **重复练习**: 可以多次运行演示来加深理解
4. **扩展实验**: 基于演示代码编写自己的练习

## 🤝 贡献指南

欢迎贡献代码和改进建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/new-demo`)
3. 提交更改 (`git commit -am 'Add new demo'`)
4. 推送分支 (`git push origin feature/new-demo`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为Ruby编程语言和开源社区做出贡献的开发者们！

---

🎯 **开始您的Ruby学习之旅吧！** 运行 `ruby main.rb` 开始探索Ruby的美妙世界。