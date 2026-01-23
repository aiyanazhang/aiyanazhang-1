package com.company.config.validator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.BindingResult;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 配置验证器测试
 */
class ConfigValidatorTest {
    
    private ConfigValidator configValidator;
    private ConfigValidationContext context;
    private BindingResult bindingResult;
    
    @BeforeEach
    void setUp() {
        configValidator = new ConfigValidator();
        context = new ConfigValidationContext();
        bindingResult = new BeanPropertyBindingResult(context, "config");
    }
    
    @Test
    void testValidServerConfiguration() {
        // 设置有效的服务器配置
        context.setServerPort(8080);
        context.setServerContextPath("/api");
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasErrors());
    }
    
    @Test
    void testInvalidServerPort() {
        // 设置无效的端口号
        context.setServerPort(70000); // 超出有效范围
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("serverPort"));
    }
    
    @Test
    void testInvalidContextPath() {
        // 设置无效的上下文路径（不以/开头）
        context.setServerContextPath("api");
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("serverContextPath"));
    }
    
    @Test
    void testValidDatabaseConfiguration() {
        // 设置有效的数据库配置
        context.setDatabaseUrl("jdbc:mysql://localhost:3306/testdb");
        context.setDatabaseUsername("testuser");
        context.setDatabasePassword("testpass");
        context.setMaxPoolSize(10);
        context.setMinIdle(2);
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasFieldErrors("databaseUrl"));
        assertFalse(bindingResult.hasFieldErrors("maxPoolSize"));
        assertFalse(bindingResult.hasFieldErrors("minIdle"));
    }
    
    @Test
    void testInvalidDatabaseUrl() {
        // 设置无效的数据库URL
        context.setDatabaseUrl("invalid-url");
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("databaseUrl"));
    }
    
    @Test
    void testProductionEnvironmentValidation() {
        // 设置为生产环境
        context.setProductionEnvironment(true);
        
        // 缺少必需的数据库配置
        context.setDatabaseUrl("jdbc:mysql://localhost:3306/proddb");
        // 缺少用户名和密码
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("databaseUsername"));
        assertTrue(bindingResult.hasFieldErrors("databasePassword"));
    }
    
    @Test
    void testConnectionPoolValidation() {
        // 设置无效的连接池配置：minIdle > maxPoolSize
        context.setMaxPoolSize(5);
        context.setMinIdle(10);
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("minIdle"));
    }
    
    @Test
    void testJwtSecurityValidation() {
        // 设置生产环境
        context.setProductionEnvironment(true);
        
        // 设置太短的JWT密钥
        context.setJwtSecret("short");
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("jwtSecret"));
    }
    
    @Test
    void testValidJwtConfiguration() {
        // 设置有效的JWT配置
        context.setJwtSecret("this-is-a-very-long-secret-key-for-jwt-token-signing");
        context.setJwtExpiration(86400L); // 24小时
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasFieldErrors("jwtSecret"));
        assertFalse(bindingResult.hasFieldErrors("jwtExpiration"));
    }
    
    @Test
    void testInvalidJwtExpiration() {
        // 设置无效的JWT过期时间（太短）
        context.setJwtExpiration(100L); // 100秒，低于最小值
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("jwtExpiration"));
    }
    
    @Test
    void testCorsConfigurationValidation() {
        // 设置有效的CORS配置
        context.setCorsAllowedOrigins(new String[]{"https://example.com", "https://app.example.com"});
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasFieldErrors("corsAllowedOrigins"));
    }
    
    @Test
    void testInvalidCorsOrigin() {
        // 设置无效的CORS来源
        context.setCorsAllowedOrigins(new String[]{"invalid-url"});
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("corsAllowedOrigins"));
    }
    
    @Test
    void testProductionCorsSecurityValidation() {
        // 生产环境不应允许所有来源
        context.setProductionEnvironment(true);
        context.setCorsAllowedOrigins(new String[]{"*"});
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("corsAllowedOrigins"));
    }
    
    @Test
    void testLogLevelValidation() {
        // 测试有效的日志级别
        context.setRootLogLevel("INFO");
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasFieldErrors("rootLogLevel"));
    }
    
    @Test
    void testInvalidLogLevel() {
        // 测试无效的日志级别
        context.setRootLogLevel("INVALID");
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("rootLogLevel"));
    }
    
    @Test
    void testCacheConfigValidation() {
        // 测试有效的缓存配置
        context.setCacheTtl(300); // 5分钟
        context.setCacheMaxSize(1000);
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasFieldErrors("cacheTtl"));
        assertFalse(bindingResult.hasFieldErrors("cacheMaxSize"));
    }
    
    @Test
    void testInvalidCacheConfiguration() {
        // 测试无效的缓存配置
        context.setCacheTtl(-1); // 负值无效
        context.setCacheMaxSize(0); // 零值无效
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("cacheTtl"));
        assertTrue(bindingResult.hasFieldErrors("cacheMaxSize"));
    }
    
    @Test
    void testMonitoringIntervalValidation() {
        // 测试有效的监控间隔
        context.setMonitoringInterval(60); // 1分钟
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasFieldErrors("monitoringInterval"));
    }
    
    @Test
    void testInvalidMonitoringInterval() {
        // 测试无效的监控间隔（太短）
        context.setMonitoringInterval(1); // 1秒，太短
        
        configValidator.validate(context, bindingResult);
        
        assertTrue(bindingResult.hasErrors());
        assertTrue(bindingResult.hasFieldErrors("monitoringInterval"));
    }
    
    @Test
    void testSupportedClass() {
        // 测试验证器支持的类
        assertTrue(configValidator.supports(ConfigValidationContext.class));
        assertFalse(configValidator.supports(String.class));
    }
    
    @Test
    void testCompleteValidConfiguration() {
        // 测试完整的有效配置
        context.setServerPort(8080);
        context.setServerContextPath("/api");
        context.setDatabaseUrl("jdbc:mysql://localhost:3306/testdb");
        context.setDatabaseUsername("user");
        context.setDatabasePassword("password");
        context.setMaxPoolSize(10);
        context.setMinIdle(2);
        context.setJwtSecret("this-is-a-very-long-secret-key-for-jwt");
        context.setJwtExpiration(86400L);
        context.setCorsAllowedOrigins(new String[]{"https://example.com"});
        context.setRateLimit(100);
        context.setRootLogLevel("INFO");
        context.setLogFile("/var/log/app.log");
        context.setCacheTtl(300);
        context.setCacheMaxSize(1000);
        context.setMonitoringInterval(60);
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasErrors());
    }
}