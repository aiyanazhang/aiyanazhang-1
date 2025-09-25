# ConfigValidator API 文档

## 概述

ConfigValidator是Java配置管理系统中的核心验证组件，负责验证应用程序配置项的有效性，确保系统在不同环境（开发、测试、生产）下的配置安全性和一致性。

## 核心组件

### ConfigValidator 类

**包路径**: `com.company.config.validator.ConfigValidator`

**类型**: `@Component`

**实现接口**: `org.springframework.validation.Validator`

#### 主要功能

- 服务器配置验证（端口号、上下文路径等）
- 数据库配置验证（连接URL、用户名、密码、连接池等）
- 安全配置验证（JWT密钥、CORS设置、限流配置等）
- 日志配置验证（日志级别、文件路径等）
- 自定义配置验证（缓存、监控等）

#### 核心方法

##### `validate(Object target, Errors errors)`

执行配置验证的主要入口方法。

**参数:**
- `target`: 待验证的配置对象，必须是 ConfigValidationContext 实例
- `errors`: 错误收集器，用于存储验证过程中发现的所有错误

**验证流程:**
1. 服务器配置验证 - 验证端口号有效性、上下文路径格式
2. 数据库配置验证 - 验证数据库连接URL、认证信息、连接池参数
3. 安全配置验证 - 验证JWT设置、CORS策略、限流配置
4. 日志配置验证 - 验证日志级别、文件路径有效性
5. 自定义配置验证 - 验证缓存设置、监控参数等应用特定配置

##### `supports(Class<?> clazz)`

检查此验证器是否支持指定的类型。

**参数:**
- `clazz`: 要检查的类类型

**返回值:**
- `true`: 如果类型为ConfigValidationContext
- `false`: 否则

### ConfigValidationContext 类

**包路径**: `com.company.config.validator.ConfigValidationContext`

**类型**: 数据载体类（POJO）

#### 配置分类

##### 服务器配置参数组

| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `serverPort` | `Integer` | 服务器监听端口号 | 1-65535，特权端口需要权限 |
| `serverContextPath` | `String` | 应用上下文路径 | 必须以"/"开头 |

##### 数据库配置参数组

| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `databaseUrl` | `String` | JDBC数据库连接URL | 符合JDBC URL格式 |
| `databaseUsername` | `String` | 数据库用户名 | 生产环境必需 |
| `databasePassword` | `String` | 数据库密码 | 生产环境必需 |
| `maxPoolSize` | `Integer` | 连接池最大大小 | 1-100 |
| `minIdle` | `Integer` | 最小空闲连接数 | ≤ maxPoolSize |

##### 安全配置参数组

| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `jwtSecret` | `String` | JWT签名密钥 | 生产环境≥32字符 |
| `jwtExpiration` | `Long` | JWT过期时间(秒) | 300-604800 |
| `corsAllowedOrigins` | `String[]` | CORS允许的来源 | 有效URL，生产环境禁止"*" |
| `rateLimit` | `Integer` | 限流设置(次/分钟) | 1-10000 |

##### 日志配置参数组

| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `rootLogLevel` | `String` | 根日志级别 | TRACE/DEBUG/INFO/WARN/ERROR/OFF |
| `logFile` | `String` | 日志文件路径 | 有效文件路径 |

##### 自定义配置参数组

| 字段 | 类型 | 描述 | 验证规则 |
|------|------|------|----------|
| `cacheTtl` | `Integer` | 缓存TTL(秒) | 1-86400 |
| `cacheMaxSize` | `Integer` | 缓存最大容量 | 1-100000 |
| `monitoringInterval` | `Integer` | 监控间隔(秒) | 5-3600 |

##### 环境信息

| 字段 | 类型 | 描述 | 影响 |
|------|------|------|------|
| `productionEnvironment` | `boolean` | 是否为生产环境 | 影响验证规则的严格程度 |

## 环境特定验证规则

### 开发环境 (productionEnvironment = false)

- 数据库认证信息可选
- JWT密钥可为空，无长度要求
- CORS允许使用"*"通配符
- 日志级别建议DEBUG

### 生产环境 (productionEnvironment = true)

- 数据库用户名和密码必需
- JWT密钥必需且≥32字符
- CORS禁止"*"，必须明确指定域名
- 日志级别建议INFO或WARN

## 错误代码说明

| 错误代码 | 描述 | 触发条件 |
|----------|------|----------|
| `invalid.port` | 端口号无效 | 端口号不在1-65535范围内 |
| `privileged.port` | 特权端口 | 尝试使用<1024端口但无权限 |
| `invalid.context.path` | 上下文路径无效 | 路径不以"/"开头 |
| `invalid.database.url` | 数据库URL无效 | URL格式不符合JDBC规范 |
| `required.database.username` | 缺少数据库用户名 | 生产环境未提供用户名 |
| `required.database.password` | 缺少数据库密码 | 生产环境未提供密码 |
| `invalid.pool.config` | 连接池配置无效 | minIdle > maxPoolSize |
| `required.jwt.secret` | 缺少JWT密钥 | 生产环境未提供JWT密钥 |
| `weak.jwt.secret` | JWT密钥过弱 | 生产环境密钥长度<32字符 |
| `invalid.cors.origin` | CORS来源无效 | CORS来源URL格式错误 |
| `insecure.cors.config` | CORS配置不安全 | 生产环境使用"*"通配符 |
| `invalid.log.level` | 日志级别无效 | 不是有效的日志级别 |
| `invalid.log.file` | 日志文件路径无效 | 文件路径格式错误 |
| `invalid.range` | 数值范围无效 | 数值不在有效范围内 |

## 使用示例

### 基本用法

```java
// 创建配置上下文
ConfigValidationContext context = new ConfigValidationContext();

// 设置服务器配置
context.setServerPort(8080);
context.setServerContextPath("/api");

// 设置数据库配置
context.setDatabaseUrl("jdbc:mysql://localhost:3306/mydb");
context.setDatabaseUsername("user");
context.setDatabasePassword("password");

// 设置环境标识
context.setProductionEnvironment(false);

// 进行验证
BeanPropertyBindingResult errors = new BeanPropertyBindingResult(context, "config");
ConfigValidator validator = new ConfigValidator();
validator.validate(context, errors);

// 检查验证结果
if (errors.hasErrors()) {
    logger.error("配置验证失败: {}", errors.getAllErrors());
} else {
    logger.info("配置验证通过");
}
```

### Spring集成用法

```java
@Component
public class ConfigValidationService {
    
    @Autowired
    private ConfigValidator configValidator;
    
    public void validateApplicationConfig(ConfigValidationContext config) {
        BeanPropertyBindingResult errors = new BeanPropertyBindingResult(config, "config");
        configValidator.validate(config, errors);
        
        if (errors.hasErrors()) {
            throw new ConfigurationException("Configuration validation failed", errors);
        }
    }
}
```

## 最佳实践

### 配置验证时机

1. **应用启动时**: 在应用完全启动前验证所有配置
2. **配置变更时**: 动态配置更新时重新验证
3. **环境切换时**: 部署到不同环境时验证环境特定规则

### 错误处理策略

1. **启动阶段**: 配置验证失败应阻止应用启动
2. **运行阶段**: 配置验证失败应记录日志并使用默认值
3. **监控集成**: 配置验证结果应集成到监控系统

### 性能考虑

1. **验证频率**: 避免过于频繁的配置验证
2. **缓存策略**: 对验证结果进行适当缓存
3. **异步验证**: 非关键配置可以异步验证

### 安全建议

1. **敏感信息**: 生产环境严格验证敏感配置
2. **权限控制**: 限制配置验证的访问权限
3. **审计日志**: 记录所有配置验证活动

## 扩展指南

### 添加新的验证规则

1. 在ConfigValidationContext中添加新字段
2. 在ConfigValidator中添加相应的验证逻辑
3. 添加对应的测试用例
4. 更新文档说明

### 自定义验证器

可以继承ConfigValidator并重写特定的验证方法：

```java
@Component
public class CustomConfigValidator extends ConfigValidator {
    
    @Override
    protected void validateCustomConfig(ConfigValidationContext context, Errors errors) {
        super.validateCustomConfig(context, errors);
        
        // 添加自定义验证逻辑
        validateBusinessSpecificConfig(context, errors);
    }
    
    private void validateBusinessSpecificConfig(ConfigValidationContext context, Errors errors) {
        // 业务特定的验证逻辑
    }
}
```

## 版本历史

- **v1.0** (2024-01-01): 初始版本，包含核心验证功能
- 支持服务器、数据库、安全、日志和自定义配置验证
- 环境敏感的验证规则
- 全面的错误处理和报告机制