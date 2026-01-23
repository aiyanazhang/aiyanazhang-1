# Java配置管理系统使用示例

本文档提供Java配置管理系统的详细使用示例。

## 基础使用示例

### 1. 配置加载器使用

```java
@Component
public class MyService {
    
    @Autowired
    private ConfigLoader configLoader;
    
    public void doSomething() {
        // 获取配置值
        String dbUrl = configLoader.getProperty("spring.datasource.url");
        
        // 获取配置值并提供默认值
        int timeout = Integer.parseInt(
            configLoader.getProperty("app.timeout", "30"));
        
        // 获取所有配置键
        Set<String> allKeys = configLoader.getAllPropertyNames();
        
        System.out.println("Database URL: " + dbUrl);
        System.out.println("Timeout: " + timeout + " seconds");
    }
}
```

### 2. 环境检测器使用

```java
@Component
public class EnvironmentAwareService {
    
    @Autowired
    private EnvironmentDetector environmentDetector;
    
    @PostConstruct
    public void initialize() {
        if (environmentDetector.isProduction()) {
            // 生产环境特殊逻辑
            enableProductionFeatures();
        } else if (environmentDetector.isDevelopment()) {
            // 开发环境特殊逻辑
            enableDevelopmentFeatures();
        }
        
        System.out.println("Current environment: " + 
            environmentDetector.getCurrentEnvironment());
    }
}
```

## 配置文件示例

### 开发环境配置 (application-dev.yml)

```yaml
# 开发环境数据库配置
spring:
  datasource:
    url: jdbc:h2:mem:devdb
    username: sa
    password: 
  h2:
    console:
      enabled: true
      path: /h2-console

# 开发环境日志配置
logging:
  level:
    root: DEBUG
    com.company: DEBUG
  pattern:
    console: "%clr(%d{HH:mm:ss.SSS}){faint} %clr(${LOG_LEVEL_PATTERN:-%5p}) %clr([%15.15t]){faint} %clr(%-40.40logger{39}){cyan} : %m%n"

# 开发环境安全配置
security:
  jwt:
    secret: dev-secret-not-for-production
    expiration: 86400
  cors:
    allowed-origins: "http://localhost:3000"
```

### 生产环境配置 (application-prod.yml)

```yaml
# 生产环境数据库配置
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

# 生产环境日志配置
logging:
  level:
    root: WARN
    com.company: INFO
  file:
    name: /var/log/app/application.log

# 生产环境安全配置
security:
  jwt:
    secret: ${JWT_SECRET}
    expiration: ${JWT_EXPIRATION:86400}
  cors:
    allowed-origins: ${CORS_ALLOWED_ORIGINS}
```

## 环境变量配置示例

### Docker环境变量文件 (.env)

```bash
# 服务器配置
SERVER_PORT=8080
CONTEXT_PATH=/api

# 数据库配置
DATABASE_URL=jdbc:mysql://mysql:3306/proddb
DATABASE_USERNAME=produser
DATABASE_PASSWORD=prodpassword

# 安全配置
JWT_SECRET=your-256-bit-secret-key-here
JWT_EXPIRATION=86400
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# 缓存配置
CACHE_TTL=600
CACHE_MAX_SIZE=10000

# 监控配置
MONITORING_INTERVAL=300
```

### Kubernetes配置示例

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  SERVER_PORT: "8080"
  MONITORING_INTERVAL: "300"
  CACHE_TTL: "600"

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-jwt-secret>
```

## 自定义配置属性

### 创建配置属性类

```java
@ConfigurationProperties(prefix = "app.custom")
@Component
public class CustomConfigProperties {
    
    private String apiUrl;
    private int timeout = 30;
    private boolean enabled = true;
    
    // getters and setters
    public String getApiUrl() { return apiUrl; }
    public void setApiUrl(String apiUrl) { this.apiUrl = apiUrl; }
    
    public int getTimeout() { return timeout; }
    public void setTimeout(int timeout) { this.timeout = timeout; }
    
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
}
```

### 在配置文件中定义

```yaml
app:
  custom:
    api-url: https://api.example.com
    timeout: 60
    enabled: true
```

### 使用配置属性

```java
@Service
public class ApiService {
    
    @Autowired
    private CustomConfigProperties config;
    
    public void callApi() {
        if (config.isEnabled()) {
            // 使用配置的API URL和超时时间
            callExternalApi(config.getApiUrl(), config.getTimeout());
        }
    }
}
```

## 条件配置示例

### 基于环境的条件配置

```java
@Configuration
public class ConditionalConfig {
    
    @Bean
    @ConditionalOnProperty(name = "app.feature.cache", havingValue = "true")
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("configCache");
    }
    
    @Bean
    @Profile("dev")
    public DataSource devDataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }
    
    @Bean
    @Profile("prod")
    public DataSource prodDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(environment.getProperty("spring.datasource.url"));
        config.setUsername(environment.getProperty("spring.datasource.username"));
        config.setPassword(environment.getProperty("spring.datasource.password"));
        return new HikariDataSource(config);
    }
}
```

## 配置验证示例

### 自定义验证注解

```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = DatabaseConfigValidator.class)
public @interface ValidDatabaseConfig {
    String message() default "Invalid database configuration";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### 验证器实现

```java
public class DatabaseConfigValidator implements ConstraintValidator<ValidDatabaseConfig, Object> {
    
    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {
        if (value instanceof DatabaseConfig) {
            DatabaseConfig config = (DatabaseConfig) value;
            return validateDatabaseConfig(config);
        }
        return false;
    }
    
    private boolean validateDatabaseConfig(DatabaseConfig config) {
        // 验证数据库配置逻辑
        return config.getUrl() != null && 
               config.getUsername() != null && 
               config.getMaxPoolSize() > 0;
    }
}
```

## 配置热更新示例

### 配置变更监听器

```java
@Component
public class ConfigChangeListener {
    
    @EventListener
    public void handleConfigChange(ConfigChangeEvent event) {
        String key = event.getKey();
        String oldValue = event.getOldValue();
        String newValue = event.getNewValue();
        
        logger.info("Configuration changed: {} = {} (was: {})", 
            key, newValue, oldValue);
        
        // 根据配置变更执行相应操作
        if ("logging.level.root".equals(key)) {
            updateLogLevel(newValue);
        } else if (key.startsWith("app.config.cache")) {
            refreshCache();
        }
    }
}
```

## 测试配置示例

### 测试配置文件 (application-test.yml)

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
    username: sa
    password: 
  jpa:
    hibernate:
      ddl-auto: create-drop

# 测试特定配置
test:
  data:
    cleanup: true
  mock:
    external-services: true
```

### 测试类配置

```java
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = {
    "app.config.cache.enabled=false",
    "app.config.monitoring.enabled=false"
})
class ConfigurationTest {
    
    @Autowired
    private ConfigLoader configLoader;
    
    @Test
    void testConfigurationLoading() {
        String dbUrl = configLoader.getProperty("spring.datasource.url");
        assertThat(dbUrl).contains("h2:mem:testdb");
    }
}
```

## 监控和健康检查

### 自定义健康检查

```java
@Component
public class ConfigHealthIndicator implements HealthIndicator {
    
    @Autowired
    private ConfigLoader configLoader;
    
    @Override
    public Health health() {
        try {
            // 检查关键配置是否可用
            String dbUrl = configLoader.getProperty("spring.datasource.url");
            if (dbUrl == null) {
                return Health.down()
                    .withDetail("reason", "Database URL not configured")
                    .build();
            }
            
            return Health.up()
                .withDetail("configSource", "OK")
                .withDetail("dbUrl", maskSensitive(dbUrl))
                .build();
                
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

这些示例展示了如何在实际项目中使用Java配置管理系统的各项功能，涵盖了从基础使用到高级特性的完整场景。