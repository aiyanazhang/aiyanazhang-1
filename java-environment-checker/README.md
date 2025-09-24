# Java Environment Checker

一个用于检查本地Java环境配置的综合工具，帮助开发者快速了解和诊断当前系统的Java运行环境状态。

## 功能特性

### 🔍 **环境检查功能**
- **系统信息收集**: 操作系统、架构、用户信息、编码设置
- **Java版本检测**: 当前Java版本、JVM信息、运行时环境详情
- **环境变量分析**: JAVA_HOME、PATH、CLASSPATH等关键变量检查
- **路径配置验证**: Java可执行文件、库文件、配置文件完整性检查

### 🔎 **高级扫描功能**
- **多版本Java扫描**: 自动发现系统中所有已安装的JDK/JRE版本
- **安装完整性验证**: 检查Java安装的完整性和有效性
- **构建工具检测**: Maven、Gradle、Ant等开发工具环境检查

### 🩺 **智能诊断功能**
- **配置问题诊断**: 自动识别常见的Java环境配置问题
- **兼容性检查**: 版本兼容性和架构匹配性验证
- **解决方案建议**: 针对发现的问题提供具体的解决建议

### 📊 **多格式输出**
- **控制台输出**: 人类可读的格式化文本输出
- **JSON格式**: 结构化数据，便于程序化处理
- **HTML报告**: 带样式的可视化报告，便于分享和存档

## 安装

### 要求
- Java 8 或更高版本
- 支持 Windows、macOS、Linux

### 下载和安装

1. **下载预编译版本**
   ```bash
   # 下载最新版本
   wget https://github.com/company/java-environment-checker/releases/latest/download/java-env-checker.jar
   ```

2. **从源码构建**
   ```bash
   git clone https://github.com/company/java-environment-checker.git
   cd java-environment-checker
   mvn clean package
   ```

## 使用方法

### 基本使用

```bash
# 基本检查（默认详细模式）
java -jar java-env-checker.jar

# 或使用便捷脚本
./java-env-checker.sh    # Linux/macOS
java-env-checker.bat     # Windows
```

### 命令行选项

```bash
java -jar java-env-checker.jar [OPTIONS]

选项:
  -h, --help                显示帮助信息
  -v, --version            显示版本信息
  -m, --mode <MODE>        检查模式: quick, detailed, diagnostic, scan
  -f, --format <FORMAT>    输出格式: console, json, html
  -o, --output <FILE>      输出文件路径
  -q, --quiet              静默模式，最小输出
  -d, --debug              启用调试输出
```

### 检查模式

#### 1. 快速检查 (quick)
```bash
java -jar java-env-checker.jar --mode quick
```
- 基本Java环境信息
- 当前活动Java版本
- 关键环境变量状态

#### 2. 详细检查 (detailed) - 默认
```bash
java -jar java-env-checker.jar --mode detailed
```
- 完整的环境信息收集
- 诊断问题检测
- 配置建议提供

#### 3. 诊断模式 (diagnostic)
```bash
java -jar java-env-checker.jar --mode diagnostic
```
- 专注于问题诊断
- 详细的错误分析
- 解决方案建议

#### 4. 扫描模式 (scan)
```bash
java -jar java-env-checker.jar --mode scan
```
- 扫描所有Java安装
- 版本对比分析
- 安装完整性检查

### 输出格式

#### 控制台输出 (默认)
```bash
java -jar java-env-checker.jar --format console
```

#### JSON格式
```bash
java -jar java-env-checker.jar --format json --output report.json
```

#### HTML报告
```bash
java -jar java-env-checker.jar --format html --output report.html
```

## 使用示例

### 示例1: 基本环境检查
```bash
java -jar java-env-checker.jar
```

输出示例:
```
================================================================================
Java Environment Check Report
Generated at: Mon Oct 23 14:30:25 CST 2023
================================================================================

SYSTEM INFORMATION
----------------------------------------
Operating System    : macOS
OS Version          : 13.6
Architecture        : x86_64
User Name           : developer
User Home           : /Users/developer
Working Directory   : /Users/developer/projects
Temp Directory      : /var/folders/tmp
File Encoding       : UTF-8
System Encoding     : UTF-8

JAVA ENVIRONMENT
----------------------------------------
Java Version        : 17.0.8
Spec Version        : 17
Vendor              : Eclipse Adoptium
Java Home           : /Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
VM Name             : OpenJDK 64-Bit Server VM
VM Version          : 17.0.8+7
VM Vendor           : Eclipse Adoptium
Runtime Name        : OpenJDK Runtime Environment
Runtime Version     : 17.0.8+7

DIAGNOSTIC RESULTS
----------------------------------------
Summary: 0 Error(s), 1 Warning(s), 2 Info

WARNINGS:
  • PATH does not contain Java bin directory
    Solution: Add /Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin to your PATH variable

INFORMATION:
  • Using Java 17 (LTS version)
    Solution: You are using a Long Term Support version - excellent choice!

  • Multiple Java installations found (3 installations)
    Solution: Use JAVA_HOME to specify which installation to use
```

### 示例2: 生成JSON报告
```bash
java -jar java-env-checker.jar --format json --output env-report.json
```

### 示例3: 诊断模式检查
```bash
java -jar java-env-checker.jar --mode diagnostic --format html --output diagnostic-report.html
```

### 示例4: 静默模式扫描
```bash
java -jar java-env-checker.jar --mode scan --quiet --format json --output scan-results.json
```

## 项目结构

```
java-environment-checker/
├── src/
│   ├── main/java/com/company/envchecker/
│   │   ├── analyzer/           # 环境变量分析器
│   │   ├── checker/           # 路径配置检查器
│   │   ├── collector/         # 系统信息收集器
│   │   ├── detector/          # Java版本检测器
│   │   ├── diagnostic/        # 诊断引擎
│   │   ├── formatter/         # 输出格式化器
│   │   ├── model/            # 数据模型
│   │   ├── scanner/          # JDK/JRE扫描器
│   │   └── JavaEnvironmentChecker.java  # 主应用程序
│   ├── main/resources/
│   │   └── application.properties
│   └── test/java/            # 单元测试
├── docs/                     # 文档
├── examples/                 # 使用示例
├── config/                   # 配置文件
├── pom.xml                  # Maven配置
├── java-env-checker.sh      # Linux/macOS启动脚本
├── java-env-checker.bat     # Windows启动脚本
└── README.md               # 项目说明
```

## API 参考

### 核心组件

#### SystemInfoCollector
收集操作系统和硬件信息
```java
SystemInfoCollector collector = new SystemInfoCollector();
SystemInfo systemInfo = collector.collectSystemInfo();
```

#### JavaVersionDetector
检测Java版本和JVM信息
```java
JavaVersionDetector detector = new JavaVersionDetector();
JavaEnvironmentInfo javaInfo = detector.detectJavaEnvironment();
```

#### JdkJreScanner
扫描系统中的Java安装
```java
JdkJreScanner scanner = new JdkJreScanner();
List<JavaInstallationInfo> installations = scanner.scanJavaInstallations();
```

#### EnvironmentDiagnostic
环境诊断和问题检测
```java
EnvironmentDiagnostic diagnostic = new EnvironmentDiagnostic();
List<DiagnosticResult> results = diagnostic.diagnose(javaInfo, envInfo, installations);
```

## 开发

### 构建项目
```bash
mvn clean compile
```

### 运行测试
```bash
mvn test
```

### 打包应用
```bash
mvn clean package
```

### 本地运行
```bash
java -cp target/classes com.company.envchecker.JavaEnvironmentChecker
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (2023-10-23)
- 初始版本发布
- 实现基本的Java环境检查功能
- 支持多种输出格式
- 提供环境诊断和问题建议

## 支持

如果您遇到任何问题或有改进建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索现有的 [Issues](https://github.com/company/java-environment-checker/issues)
3. 创建新的 Issue 描述您的问题

## 致谢

感谢所有为这个项目做出贡献的开发者和测试人员。

---

**Java Environment Checker** - 让Java环境检查变得简单高效！