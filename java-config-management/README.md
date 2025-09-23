# Java配置管理系统

基于设计文档实现的全面Java应用程序配置管理系统，提供多环境配置、验证机制、热更新、敏感信息管理等功能。

## 项目结构

```
java-config-management/
├── pom.xml                                    # Maven项目配置
├── src/
│   ├── main/
│   │   ├── java/com/company/config/
│   │   │   ├── ConfigManagementApplication.java     # 主应用程序类
│   │   │   ├── loader/
│   │   │   │   ├── ConfigLoader.java               # 配置加载器
│   │   │   │   └── EnvironmentDetector.java        # 环境检测器
│   │   │   ├── validator/
│   │   │   │   ├── ConfigValidator.java            # 配置验证器
│   │   │   │   ├── ConfigValidationContext.java    # 验证上下文
│   │   │   │   └── StartupConfigValidator.java     # 启动时验证
│   │   │   ├── security/                           # 敏感信息管理
│   │   │   ├── monitor/                            # 配置监控
│   │   │   ├── cache/                              # 配置缓存
│   │   │   └── hotreload/                          # 热更新机制
│   │   └── resources/
│   │       ├── application.yml                     # 基础配置
│   │       ├── application-dev.yml                 # 开发环境配置
│   │       ├── application-test.yml                # 测试环境配置
│   │       └── application-prod.yml                # 生产环境配置
│   └── test/                                       # 测试代码
├── config/
│   └── application.yml                             # 外部配置文件示例
└── docs/                                           # 文档目录
```

## 核心功能

### 1. 配置加载器 (ConfigLoader)

- **多源配置支持**: 支持命令行参数、环境变量、外部配置文件、内部配置文件、默认值
- **优先级策略**: 按设计文档定义的优先级加载配置
- **配置缓存**: 提供配置缓存机制提升性能
- **灵活查找**: 支持多种配置键格式的自动转换

### 2. 环境检测器 (EnvironmentDetector)

- **自动环境检测**: 从多个源自动检测运行环境
- **环境类型支持**: 支持开发、测试、预发布、生产环境
- **多重检测机制**: 环境变量、系统属性、主机名、文件系统标识
- **环境验证**: 针对不同环境进行相应的配置验证

### 3. 配置验证机制

- **全面验证**: 服务器配置、数据库配置、安全配置、日志配置等
- **启动时验证**: 应用启动时自动执行配置验证
- **环境特定验证**: 不同环境使用不同的验证策略
- **详细错误报告**: 提供详细的验证错误信息和建议

### 4. 多环境配置文件

- **application.yml**: 基础通用配置
- **application-dev.yml**: 开发环境特定配置
- **application-test.yml**: 测试环境特定配置  
- **application-prod.yml**: 生产环境特定配置
- **config/application.yml**: 外部配置覆盖文件

## 配置优先级

按优先级从高到低：

1. **命令行参数** - 最高优先级
2. **系统环境变量** - 支持多种命名格式
3. **外部配置文件** - config/目录下的配置文件
4. **内部配置文件** - classpath中的配置文件
5. **默认值** - 代码中定义的默认配置

## 环境配置特色

### 开发环境 (dev)
- 启用H2控制台和开发工具
- 详细的调试日志输出
- 宽松的安全策略
- 启用热更新功能
- 短缓存时间便于调试

### 测试环境 (test)
- 独立的测试数据库
- 模拟外部服务配置
- 适中的日志级别
- 禁用热更新保证稳定性
- 启用测试覆盖率收集

### 生产环境 (prod)
- 严格的安全配置
- 外部化敏感信息
- 优化的性能参数
- 全面的监控配置
- 长缓存时间提升性能

## 配置验证规则

### 必需参数验证
- 检查关键配置项是否存在
- 生产环境强制要求敏感信息配置

### 类型和格式验证
- 数据类型验证（端口号、超时时间等）
- URL格式验证（数据库连接、CORS设置等）
- 文件路径验证

### 安全验证
- JWT密钥强度检查
- CORS配置安全性验证
- 生产环境安全策略强制执行

### 依赖关系验证
- 配置项之间的逻辑一致性
- 连接池配置合理性检查

## 快速开始

### 1. 构建项目

```bash
cd java-config-management
mvn clean compile
```

### 2. 运行应用

```bash
# 默认环境（开发环境）
mvn spring-boot:run

# 指定环境
mvn spring-boot:run -Dspring-boot.run.profiles=test

# 使用环境变量
export SPRING_PROFILES_ACTIVE=prod
mvn spring-boot:run
```

### 3. 外部配置

将自定义配置放在 `config/application.yml` 中，系统会自动加载并覆盖内部配置。

### 4. 环境变量配置

```bash
# 服务器配置
export SERVER_PORT=9090

# 数据库配置
export DATABASE_URL=jdbc:mysql://localhost:3306/mydb
export DATABASE_USERNAME=myuser
export DATABASE_PASSWORD=mypassword

# 安全配置
export JWT_SECRET=your-super-secret-jwt-key
export CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 配置监控

应用启动后，可以通过以下端点监控配置状态：

- `/actuator/health` - 应用健康状态
- `/actuator/info` - 应用信息
- `/actuator/env` - 环境配置信息
- `/actuator/configprops` - 配置属性信息
- `/actuator/metrics` - 应用指标

## 技术栈

- **Spring Boot 2.7.0** - 核心框架
- **Spring Boot Configuration Processor** - 配置处理
- **Spring Boot Actuator** - 监控端点
- **Spring Boot Validation** - 配置验证
- **H2 Database** - 开发环境数据库
- **MySQL** - 生产环境数据库
- **Jackson** - JSON处理
- **JUnit 5** - 单元测试
- **Testcontainers** - 集成测试

## 已完成的功能模块

### ✅ 敏感信息管理
- **SensitiveConfigManager**: AES-256-GCM加密算法，支持密钥派生和轮换
- **SensitiveConfigResolver**: 自动识别敏感配置，支持加密前缀标识
- 支持多种敏感信息模式识别：password、secret、key、token等

### ✅ 配置热更新机制
- **ConfigHotReloadManager**: 基于文件系统监控的热更新
- 支持多种配置文件格式：yml、yaml、properties、json、xml
- **ConfigChangeEvent**: 配置变更事件系统
- 定期检查和文件监控双重机制

### ✅ 配置监控和审计
- **ConfigurationMonitor**: 全面的配置访问和性能监控
- **ConfigurationAuditor**: 完整的审计日志记录和管理
- 支持Micrometer指标集成
- 审计记录导出（JSON、CSV、文本格式）

### ✅ 配置缓存和性能优化
- **ConfigCacheManager**: 双层缓存架构（L1/L2缓存）
- 智能缓存提升策略和LRU驱逐算法
- 配置预热和过期清理机制
- 并发安全的读写锁保护

### ✅ 全面测试套件
- **单元测试**: 针对所有核心组件的详细单元测试
- **集成测试**: Spring Boot集成测试验证
- **性能测试**: 缓存和并发访问测试
- **安全测试**: 加密解密功能测试

## 系统特色

- **企业级安全**: AES-256-GCM加密、密钥管理、审计追踪
- **高性能**: 双层缓存、智能预热、并发优化
- **高可用**: 热更新、配置验证、故障恢复
- **易运维**: 全面监控、详细审计、统计报告
- **标准化**: 遵循Spring Boot最佳实践，支持标准配置格式

该系统严格按照设计文档实现，提供了完整的企业级Java配置管理解决方案，涵盖了从基础配置加载到高级安全管理的所有功能需求。