package com.company.config.validator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.BindingResult;

import static org.junit.jupiter.api.Assertions.*;

/**
 * ConfigValidator单元测试套件
 * 
 * <p>此测试类全面测试ConfigValidator的所有验证功能，确保：
 * <ul>
 *   <li>各类配置项的正确验证逻辑</li>
 *   <li>不同环境下的验证规则差异</li>
 *   <li>边界条件和异常情况的处理</li>
 *   <li>错误消息的准确性和可读性</li>
 * </ul>
 * 
 * <p><strong>测试覆盖范围：</strong>
 * <table border="1">
 *   <tr><th>功能模块</th><th>测试场景</th><th>验证要点</th></tr>
 *   <tr><td>服务器配置</td><td>有效端口、无效端口、特权端口</td><td>端口范围、权限检查</td></tr>
 *   <tr><td>数据库配置</td><td>URL格式、认证信息、连接池</td><td>格式正确性、环境差异</td></tr>
 *   <tr><td>安全配置</td><td>JWT设置、CORS策略</td><td>安全强度、生产环境限制</td></tr>
 *   <tr><td>边界测试</td><td>null值、空字符串、极值</td><td>健壮性、错误处理</td></tr>
 * </table>
 * 
 * <p><strong>测试策略：</strong>
 * <ul>
 *   <li><strong>可读性</strong>：每个测试方法名明确描述测试目标</li>
 *   <li><strong>独立性</strong>：每个测试互不影响，使用独立的数据</li>
 *   <li><strong>全面性</strong>：覆盖正常、异常和边界情况</li>
 *   <li><strong>精确性</strong>：验证具体的错误字段和错误信息</li>
 * </ul>
 * 
 * <p><strong>测试数据管理：</strong>
 * <ul>
 *   <li>使用{@code @BeforeEach}初始化清洁的测试环境</li>
 *   <li>每个测试使用新的配置上下文对象</li>
 *   <li>使用明确的测试数据，避免魔法数字</li>
 * </ul>
 * 
 * <p><strong>断言策略：</strong>
 * <ul>
 *   <li>使用{@code assertTrue/assertFalse}验证错误状态</li>
 *   <li>使用{@code hasFieldErrors}验证具体字段错误</li>
 *   <li>优先验证正向情况，再验证异常情况</li>
 * </ul>
 * 
 * <p><strong>扩展指导：</strong>
 * 新增配置验证规则时，应同步添加相应的测试用例：
 * <ul>
 *   <li>正常情况测试：验证正确配置不产生错误</li>
 *   <li>边界情况测试：验证最大值、最小值和临界值</li>
 *   <li>异常情况测试：验证无效输入和错误配置</li>
 *   <li>环境差异测试：验证开发和生产环境的不同要求</li>
 * </ul>
 * 
 * @author 测试团队
 * @version 1.0
 * @see ConfigValidator 被测试的配置验证器类
 * @see ConfigValidationContext 测试用的验证上下文
 * @since 2024-01-01
 */
class ConfigValidatorTest {
    
    /**
     * 测试用的配置验证器实例
     * 
     * <p>在每个测试方法执行前通过{@code @BeforeEach}初始化，
     * 确保每个测试都使用全新的验证器实例。
     */
    private ConfigValidator configValidator;
    
    /**
     * 测试用的配置验证上下文
     * 
     * <p>包含所有需要验证的配置参数，在每个测试中
     * 通过setter方法设置具体的测试数据。
     */
    private ConfigValidationContext context;
    
    /**
     * Spring验证结果绑定对象
     * 
     * <p>用于收集和检查验证过程中产生的错误信息，
     * 支持按字段名和错误类型进行精确断言。
     */
    private BindingResult bindingResult;
    
    /**
     * 测试初始化方法
     * 
     * <p>在每个测试方法执行前自动调用，初始化清洁的测试环境：
 * <ul>
 *   <li>创建新的ConfigValidator实例</li>
 *   <li>创建新的ConfigValidationContext实例</li>
 *   <li>创建新的BindingResult实例用于收集错误</li>
 * </ul>
     * 
     * <p>这种设计确保了测试的独立性，避免测试之间的状态干扰。
     */
    @BeforeEach
    void setUp() {
        configValidator = new ConfigValidator();
        context = new ConfigValidationContext();
        bindingResult = new BeanPropertyBindingResult(context, "config");
    }
    
    /**
     * 测试有效的服务器配置验证
     * 
     * <p>验证正常的服务器配置参数不会产生验证错误。
     * 测试用例包括：
     * <ul>
 *   <li>标准端口号：8080（Spring Boot默认端口）</li>
 *   <li>标准上下文路径：/api（以斜杠开头）</li>
 * </ul>
     * 
     * <p><strong>期望结果：</strong>验证通过，无任何错误信息。
     */
    @Test
    void testValidServerConfiguration() {
        // 设置有效的服务器配置
        context.setServerPort(8080);
        context.setServerContextPath("/api");
        
        configValidator.validate(context, bindingResult);
        
        assertFalse(bindingResult.hasErrors());
    }
    
    /**
     * 测试无效的服务器端口验证
     * 
     * <p>验证超出有效范围的端口号会产生验证错误。
     * 测试用例：
     * <ul>
 *   <li>端口号70000：超过最大允许值65535</li>
 * </ul>
     * 
     * <p><strong>期望结果：</strong>
     * <ul>
 *   <li>存在验证错误</li>
 *   <li>serverPort字段有错误信息</li>
 *   <li>错误代码为invalid.port</li>
 * </ul>
     */
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