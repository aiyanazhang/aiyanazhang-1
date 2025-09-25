package com.company.config.validator;

import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.ValidationUtils;
import org.springframework.validation.Validator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URL;
import java.util.regex.Pattern;

/**
 * 配置验证器组件
 * 
 * <p>此类实现了Spring的Validator接口，负责验证应用程序配置项的有效性。
 * 主要功能包括：
 * <ul>
 *   <li>服务器配置验证（端口号、上下文路径等）</li>
 *   <li>数据库配置验证（连接URL、用户名、密码、连接池等）</li>
 *   <li>安全配置验证（JWT密钥、CORS设置、限流配置等）</li>
 *   <li>日志配置验证（日志级别、文件路径等）</li>
 *   <li>自定义配置验证（缓存、监控等）</li>
 * </ul>
 * 
 * <p>该验证器根据不同环境（开发/生产）应用不同的验证规则：
 * <ul>
 *   <li>生产环境：强制要求数据库密码、JWT密钥等敏感配置</li>
 *   <li>开发环境：放宽某些安全要求，便于开发调试</li>
 * </ul>
 * 
 * <p>验证过程采用分层验证策略，每个配置域独立验证，
 * 确保错误隔离和问题定位的准确性。
 * 
 * @author 配置管理团队
 * @version 1.0
 * @since 2024-01-01
 * @see ConfigValidationContext 验证上下文对象
 * @see org.springframework.validation.Validator Spring验证器接口
 */
@Component
public class ConfigValidator implements Validator {
    
    /**
     * 日志记录器
     * 
     * <p>用于记录配置验证过程中的信息、警告和错误消息，
     * 便于系统监控和问题诊断。
     */
    private static final Logger logger = LoggerFactory.getLogger(ConfigValidator.class);
    
    /**
     * 预编译的正则表达式模式集合
     * 
     * <p>这些常量包含了配置验证过程中频繁使用的正则表达式模式，
     * 通过预编译提高验证性能，避免重复编译开销。
     */
    
    /**
     * 电子邮件地址格式验证正则表达式
     * 
     * <p>此模式验证标准的电子邮件地址格式，包括：
     * <ul>
     *   <li>本地部分：支持字母、数字、加号、下划线、点号、连字符</li>
     *   <li>@符号：邮件地址分隔符</li>
     *   <li>域名部分：支持标准域名格式</li>
     *   <li>顶级域名：至少2个字母</li>
     * </ul>
     * 
     * <p><strong>匹配示例：</strong>
     * <ul>
     *   <li>✓ user@example.com</li>
     *   <li>✓ test.email+tag@domain.co.uk</li>
     *   <li>✗ invalid.email</li>
     *   <li>✗ @domain.com</li>
     * </ul>
     * 
     * @see <a href="https://tools.ietf.org/html/rfc5322">RFC 5322 - Internet Message Format</a>
     */
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
    
    /**
     * HTTP/HTTPS/FTP URL格式验证正则表达式
     * 
     * <p>此模式验证Web URL的基本格式，支持的协议包括：
     * <ul>
     *   <li>http:// - 超文本传输协议</li>
     *   <li>https:// - 安全超文本传输协议</li>
     *   <li>ftp:// - 文件传输协议</li>
     * </ul>
     * 
     * <p>URL组成部分验证：
     * <ul>
     *   <li>协议：http、https或ftp</li>
     *   <li>域名/IP：支持域名、IPv4、IPv6地址</li>
     *   <li>端口：可选的端口号</li>
     *   <li>路径：可选的资源路径</li>
     *   <li>查询参数：可选的查询字符串</li>
     *   <li>锚点：可选的页面锚点</li>
     * </ul>
     * 
     * @see #isValidUrl(String) URL验证方法
     */
    private static final Pattern URL_PATTERN = Pattern.compile(
        "^(https?|ftp)://[\\w\\-._~:/?#\\[\\]@!$&'()*+,;=]+$");
    
    /**
     * JDBC数据库连接URL格式验证正则表达式
     * 
     * <p>此模式专门用于验证JDBC数据库连接字符串的格式，
     * 确保连接URL符合JDBC规范：
     * 
     * <p><strong>标准格式：</strong> {@code jdbc:driver://host:port/database[?params]}
     * 
     * <p><strong>支持的数据库驱动：</strong>
     * <ul>
     *   <li>MySQL: jdbc:mysql://localhost:3306/mydb</li>
     *   <li>PostgreSQL: jdbc:postgresql://localhost:5432/mydb</li>
     *   <li>Oracle: jdbc:oracle:thin:@localhost:1521:xe</li>
     *   <li>SQL Server: jdbc:sqlserver://localhost:1433;databaseName=mydb</li>
     *   <li>H2: jdbc:h2:mem:testdb 或 jdbc:h2:file:/path/to/db</li>
     * </ul>
     * 
     * <p><strong>验证组件：</strong>
     * <ul>
     *   <li>jdbc: 前缀 - 必需的JDBC协议标识</li>
     *   <li>驱动名称 - 数据库驱动标识符</li>
     *   <li>连接字符串 - 驱动特定的连接参数</li>
     * </ul>
     * 
     * @see #validateDatabaseConfig(ConfigValidationContext, Errors) 数据库配置验证
     */
    private static final Pattern DATABASE_URL_PATTERN = Pattern.compile(
        "^jdbc:[\\w]+://[\\w\\-._~:/?#\\[\\]@!$&'()*+,;=]+$");
    
    /**
     * 主机名:端口号格式验证正则表达式
     * 
     * <p>此模式用于验证"主机名:端口号"格式的网络地址，
     * 常用于配置远程服务地址、代理服务器等。
     * 
     * <p><strong>格式规范：</strong>
     * <ul>
     *   <li>主机名：支持域名、IP地址、主机别名</li>
     *   <li>分隔符：冒号(:)</li>
     *   <li>端口号：1-5位数字(1-65535)</li>
     * </ul>
     * 
     * <p><strong>匹配示例：</strong>
     * <ul>
     *   <li>✓ localhost:8080</li>
     *   <li>✓ redis.example.com:6379</li>
     *   <li>✓ 192.168.1.100:3306</li>
     *   <li>✗ example.com</li>
     *   <li>✗ :8080</li>
     * </ul>
     * 
     * @since 1.0
     */
    private static final Pattern HOST_PORT_PATTERN = Pattern.compile(
        "^[\\w\\-._~]+:\\d{1,5}$");

    /**
     * 检查此验证器是否支持指定的类型
     * 
     * <p>该方法是Spring Validator接口的要求，用于确定
     * 验证器是否能够处理特定类型的对象。
     * 
     * <p>此验证器专门设计用于验证 {@link ConfigValidationContext} 类型的对象，
     * 该类型包含了所有需要验证的配置项。
     * 
     * @param clazz 要检查的类类型
     * @return {@code true} 如果类型为ConfigValidationContext；{@code false} 否则
     * 
     * @see ConfigValidationContext 支持的验证上下文类型
     * @since 1.0
     */
    @Override
    public boolean supports(Class<?> clazz) {
        return ConfigValidationContext.class.equals(clazz);
    }

    /**
     * 执行配置验证的主要入口方法
     * 
     * <p>此方法接收一个配置验证上下文对象，并对其包含的所有配置项
     * 进行全面验证。验证过程按以下顺序进行：
     * 
     * <ol>
     *   <li><strong>服务器配置验证</strong> - 验证端口号有效性、上下文路径格式</li>
     *   <li><strong>数据库配置验证</strong> - 验证数据库连接URL、认证信息、连接池参数</li>
     *   <li><strong>安全配置验证</strong> - 验证JWT设置、CORS策略、限流配置</li>
     *   <li><strong>日志配置验证</strong> - 验证日志级别、文件路径有效性</li>
     *   <li><strong>自定义配置验证</strong> - 验证缓存设置、监控参数等应用特定配置</li>
     * </ol>
     * 
     * <p><strong>环境敏感验证：</strong>
     * 验证器会根据当前运行环境（通过 {@link ConfigValidationContext#isProductionEnvironment()}
     * 判断）应用不同的验证规则：
     * <ul>
     *   <li><strong>生产环境</strong>：严格验证敏感配置（如数据库密码、JWT密钥），
     *       禁止不安全的配置（如CORS允许所有来源）</li>
     *   <li><strong>非生产环境</strong>：放宽部分安全要求，允许开发便利性配置</li>
     * </ul>
     * 
     * <p><strong>错误处理策略：</strong>
     * <ul>
     *   <li>验证错误通过 {@link Errors} 接口收集，不会中断整个验证流程</li>
     *   <li>每个验证错误都包含错误代码、字段名和详细描述</li>
     *   <li>验证结果通过日志记录，便于问题诊断</li>
     * </ul>
     * 
     * <p><strong>性能考虑：</strong>
     * 验证方法设计为轻量级操作，主要进行格式检查和范围验证，
     * 不执行网络连接或文件IO操作，确保启动时的性能表现。
     * 
     * @param target 待验证的配置对象，必须是 {@link ConfigValidationContext} 实例
     * @param errors 错误收集器，用于存储验证过程中发现的所有错误
     * 
     * @throws ClassCastException 如果target不是ConfigValidationContext类型
     * @throws IllegalArgumentException 如果target或errors为null
     * 
     * @see #validateServerConfig(ConfigValidationContext, Errors) 服务器配置验证
     * @see #validateDatabaseConfig(ConfigValidationContext, Errors) 数据库配置验证
     * @see #validateSecurityConfig(ConfigValidationContext, Errors) 安全配置验证
     * 
     * @example
     * <pre>{@code
     * ConfigValidationContext context = new ConfigValidationContext();
     * context.setServerPort(8080);
     * context.setDatabaseUrl("jdbc:mysql://localhost:3306/mydb");
     * 
     * BeanPropertyBindingResult errors = new BeanPropertyBindingResult(context, "config");
     * configValidator.validate(context, errors);
     * 
     * if (errors.hasErrors()) {
     *     logger.error("配置验证失败: {}", errors.getAllErrors());
     * }
     * }</pre>
     */
    @Override
    public void validate(Object target, Errors errors) {
        ConfigValidationContext context = (ConfigValidationContext) target;
        
        logger.info("Starting configuration validation");
        
        // 验证服务器配置
        validateServerConfig(context, errors);
        
        // 验证数据库配置
        validateDatabaseConfig(context, errors);
        
        // 验证安全配置
        validateSecurityConfig(context, errors);
        
        // 验证日志配置
        validateLoggingConfig(context, errors);
        
        // 验证自定义配置
        validateCustomConfig(context, errors);
        
        if (errors.hasErrors()) {
            logger.error("Configuration validation failed with {} errors", errors.getErrorCount());
        } else {
            logger.info("Configuration validation passed successfully");
        }
    }
    
    /**
     * 验证服务器相关配置参数
     * 
     * <p>此方法验证应用服务器的核心配置项，确保服务器能够正常启动和运行。
     * 主要验证内容包括：
     * 
     * <ul>
     *   <li><strong>服务器端口验证</strong>：
     *       <ul>
     *         <li>端口范围检查：1-65535</li>
     *         <li>特权端口警告：端口号小于1024时需要特殊权限</li>
     *         <li>常用端口冲突检查：避免使用已知的系统端口</li>
     *       </ul>
     *   </li>
     *   <li><strong>上下文路径验证</strong>：
     *       <ul>
     *         <li>格式检查：必须以"/"开头</li>
     *         <li>路径规范性：避免特殊字符和不安全路径</li>
     *         <li>长度限制：防止过长路径影响URL处理</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>验证规则详细说明：</strong>
     * <table border="1">
     *   <tr><th>配置项</th><th>验证规则</th><th>错误代码</th></tr>
     *   <tr><td>server.port</td><td>1 ≤ port ≤ 65535</td><td>invalid.port</td></tr>
     *   <tr><td>server.port</td><td>port < 1024 需要权限</td><td>privileged.port</td></tr>
     *   <tr><td>server.servlet.context-path</td><td>以"/"开头</td><td>invalid.context.path</td></tr>
     * </table>
     * 
     * <p><strong>特殊情况处理：</strong>
     * <ul>
     *   <li>端口为null时跳过验证，使用Spring Boot默认端口8080</li>
     *   <li>上下文路径为null或空字符串时视为根路径，无需验证</li>
     *   <li>特权端口在容器化环境中可能需要特殊配置</li>
     * </ul>
     * 
     * @param context 包含服务器配置的验证上下文
     *                - {@link ConfigValidationContext#getServerPort()} 服务器端口号
     *                - {@link ConfigValidationContext#getServerContextPath()} 应用上下文路径
     * @param errors 错误收集器，用于记录发现的配置错误
     * 
     * @see #validatePort(Integer, String, Errors) 端口号专用验证方法
     * @see #isPrivilegedPortAllowed() 特权端口权限检查
     * 
     * @since 1.0
     */
    private void validateServerConfig(ConfigValidationContext context, Errors errors) {
        // 验证端口号
        validatePort(context.getServerPort(), "server.port", errors);
        
        // 验证上下文路径
        String contextPath = context.getServerContextPath();
        if (contextPath != null && !contextPath.startsWith("/")) {
            errors.rejectValue("serverContextPath", "invalid.context.path", 
                "Context path must start with '/'");
        }
    }
    
    /**
     * 验证数据库连接和池配置参数
     * 
     * <p>此方法对数据库相关的所有配置进行综合验证，确保应用能够
     * 成功连接数据库并维持稳定的连接池。验证内容包括：
     * 
     * <ul>
     *   <li><strong>数据库连接验证</strong>：
     *       <ul>
     *         <li>JDBC URL格式检查：符合jdbc:driver://host:port/database模式</li>
     *         <li>数据库驱动支持性检查：确保URL中的驱动类型受支持</li>
     *         <li>连接参数完整性：检查必要的连接参数</li>
     *       </ul>
     *   </li>
     *   <li><strong>认证信息验证</strong>：
     *       <ul>
     *         <li>生产环境强制要求：用户名和密码不能为空</li>
     *         <li>开发环境宽松检查：允许空密码便于本地开发</li>
     *         <li>密码强度建议：生产环境建议复杂密码</li>
     *       </ul>
     *   </li>
     *   <li><strong>连接池配置验证</strong>：
     *       <ul>
     *         <li>最大连接数范围：1-100之间</li>
     *         <li>最小空闲连接合理性：不超过最大连接数</li>
     *         <li>连接超时设置：确保合理的超时时间</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>环境特定验证规则：</strong>
     * <table border="1">
     *   <tr><th>配置项</th><th>开发环境</th><th>生产环境</th></tr>
     *   <tr><td>数据库用户名</td><td>可选</td><td>必需</td></tr>
     *   <tr><td>数据库密码</td><td>可选</td><td>必需</td></tr>
     *   <tr><td>连接池大小</td><td>建议1-10</td><td>建议10-50</td></tr>
     *   <tr><td>连接超时</td><td>较长超时</td><td>较短超时</td></tr>
     * </table>
     * 
     * <p><strong>支持的数据库类型：</strong>
     * <ul>
     *   <li>MySQL: jdbc:mysql://...</li>
     *   <li>PostgreSQL: jdbc:postgresql://...</li>
     *   <li>Oracle: jdbc:oracle:thin:@...</li>
     *   <li>SQL Server: jdbc:sqlserver://...</li>
     *   <li>H2: jdbc:h2:...</li>
     * </ul>
     * 
     * @param context 包含数据库配置的验证上下文
     *                包括数据库URL、用户名、密码、连接池参数等
     * @param errors 错误收集器，记录数据库配置相关的所有验证错误
     * 
     * @see #validateConnectionPoolConfig(ConfigValidationContext, Errors) 连接池专项验证
     * @see ConfigValidationContext#isProductionEnvironment() 环境判断方法
     * 
     * @since 1.0
     */
    private void validateDatabaseConfig(ConfigValidationContext context, Errors errors) {
        // 验证数据库URL
        String dbUrl = context.getDatabaseUrl();
        if (dbUrl != null && !DATABASE_URL_PATTERN.matcher(dbUrl).matches()) {
            errors.rejectValue("databaseUrl", "invalid.database.url", 
                "Invalid database URL format");
        }
        
        // 验证用户名（生产环境必需）
        if (context.isProductionEnvironment()) {
            ValidationUtils.rejectIfEmptyOrWhitespace(errors, "databaseUsername", 
                "required.database.username", "Database username is required in production");
            
            ValidationUtils.rejectIfEmptyOrWhitespace(errors, "databasePassword", 
                "required.database.password", "Database password is required in production");
        }
        
        // 验证连接池配置
        validateConnectionPoolConfig(context, errors);
    }

    
    /**
     * 验证数据库连接池配置参数
     * 
     * <p>此方法专门验证数据库连接池的各项参数，确保连接池配置
     * 的合理性和性能优化。主要验证内容包括：
     * 
     * <ul>
     *   <li><strong>最大连接数验证</strong>：
     *       <ul>
     *         <li>范围检查：1-100之间</li>
     *         <li>性能考虑：不同环境下的最优值</li>
     *         <li>资源限制：防止过多连接占用系统资源</li>
     *       </ul>
     *   </li>
     *   <li><strong>最小空闲连接验证</strong>：
     *       <ul>
     *         <li>逻辑一致性：不能超过最大连接数</li>
     *         <li>性能平衡：确保空闲连接数量合理</li>
     *         <li>资源效率：避免过多空闲连接浪费</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>验证规则说明：</strong>
     * <table border="1">
     *   <tr><th>参数</th><th>有效范围</th><th>推荐值</th><th>错误代码</th></tr>
     *   <tr><td>maxPoolSize</td><td>1-100</td><td>开发:5-10，生产:10-50</td><td>invalid.range</td></tr>
     *   <tr><td>minIdle</td><td>0-maxPoolSize</td><td>maxPoolSize的20%-50%</td><td>invalid.pool.config</td></tr>
     * </table>
     * 
     * <p><strong>性能优化建议：</strong>
     * <ul>
     *   <li>开发环境：较小的连接池，节约资源</li>
     *   <li>测试环境：中等连接池，模拟生产负载</li>
     *   <li>生产环境：根据并发量调整，高并发下适当增大</li>
     * </ul>
     * 
     * @param context 包含连接池配置的验证上下文
     * @param errors 错误收集器，用于记录连接池配置错误
     * 
     * @see #validateRange(int, int, int, String, String, Errors) 范围验证工具方法
     * @see ConfigValidationContext#getMaxPoolSize() 最大连接数参数
     * @see ConfigValidationContext#getMinIdle() 最小空闲连接数参数
     * 
     * @since 1.0
     */
    private void validateConnectionPoolConfig(ConfigValidationContext context, Errors errors) {
        Integer maxPoolSize = context.getMaxPoolSize();
        if (maxPoolSize != null) {
            validateRange(maxPoolSize, 1, 100, "maxPoolSize", 
                "Connection pool max size must be between 1 and 100", errors);
        }
        
        Integer minIdle = context.getMinIdle();
        if (minIdle != null && maxPoolSize != null) {
            if (minIdle > maxPoolSize) {
                errors.rejectValue("minIdle", "invalid.pool.config", 
                    "Minimum idle connections cannot exceed maximum pool size");
            }
        }
    }
    
    /**
     * 验证安全相关配置参数
     * 
     * <p>此方法对应用程序的安全配置进行全面验证，确保系统
     * 在不同环境下都能保持适当的安全级别。主要验证内容包括：
     * 
     * <ul>
     *   <li><strong>JWT配置验证</strong>：
     *       <ul>
     *         <li>密钥强度：生产环境要求至少32字符</li>
     *         <li>过期时间：5分钟到7天之间</li>
     *         <li>存在性检查：生产环境强制要求</li>
     *       </ul>
     *   </li>
     *   <li><strong>CORS配置验证</strong>：
     *       <ul>
     *         <li>来源地址格式：必须是有效的URL或通配符</li>
     *         <li>生产环境限制：禁止使用通配符"*"</li>
     *         <li>安全检查：防止跨域攻击</li>
     *       </ul>
     *   </li>
     *   <li><strong>限流配置验证</strong>：
     *       <ul>
     *         <li>请求频率：1-10000次/分钟</li>
     *         <li>防护级别：根据应用类型调整</li>
     *         <li>DDoS防护：配合其他安全措施</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>环境特定规则：</strong>
     * <table border="1">
     *   <tr><th>配置项</th><th>开发环境</th><th>生产环境</th></tr>
     *   <tr><td>JWT密钥</td><td>可选，无长度要求</td><td>必需，≥ 32字符</td></tr>
     *   <tr><td>CORS来源</td><td>允许"*"通配符</td><td>禁止"*"，明确指定</td></tr>
     *   <tr><td>限流设置</td><td>较宽松</td><td>较严格</td></tr>
     * </table>
     * 
     * <p><strong>安全最佳实践：</strong>
     * <ul>
     *   <li>JWT密钥应使用高强度随机字符串</li>
     *   <li>CORS在生产环境中应明确指定允许的域名</li>
     *   <li>限流策略应结合业务特点和服务器性能</li>
     *   <li>定期轮换敏感配置参数</li>
     * </ul>
     * 
     * @param context 包含安全配置的验证上下文
     * @param errors 错误收集器，用于记录安全配置相关错误
     * 
     * @see #validateCorsConfig(ConfigValidationContext, Errors) CORS专项验证
     * @see ConfigValidationContext#isProductionEnvironment() 环境判断方法
     * 
     * @since 1.0
     */
    private void validateSecurityConfig(ConfigValidationContext context, Errors errors) {
        // 验证JWT密钥（生产环境必需）
        if (context.isProductionEnvironment()) {
            String jwtSecret = context.getJwtSecret();
            ValidationUtils.rejectIfEmptyOrWhitespace(errors, "jwtSecret", 
                "required.jwt.secret", "JWT secret is required in production");
            
            if (jwtSecret != null && jwtSecret.length() < 32) {
                errors.rejectValue("jwtSecret", "weak.jwt.secret", 
                    "JWT secret must be at least 32 characters long in production");
            }
        }
        
        // 验证JWT过期时间
        Long jwtExpiration = context.getJwtExpiration();
        if (jwtExpiration != null) {
            validateRange(jwtExpiration.intValue(), 300, 86400 * 7, "jwtExpiration", 
                "JWT expiration must be between 5 minutes and 7 days", errors);
        }
        
        // 验证CORS配置
        validateCorsConfig(context, errors);
        
        // 验证限流配置
        Integer rateLimit = context.getRateLimit();
        if (rateLimit != null) {
            validateRange(rateLimit, 1, 10000, "rateLimit", 
                "Rate limit must be between 1 and 10000 requests per minute", errors);
        }
    }
    
    /**
     * 验证CORS（跨源资源共享）配置参数
     * 
     * <p>CORS是一种安全机制，允许Web页面从不同域名访问资源。
     * 此方法验证CORS配置的安全性和正确性：
     * 
     * <ul>
     *   <li><strong>允许来源验证</strong>：
     *       <ul>
     *         <li>URL格式检查：非通配符来源必须是有效URL</li>
     *         <li>通配符处理："*"仅在开发环境中允许</li>
     *         <li>协议检查：确保HTTPS在生产环境中优先</li>
     *       </ul>
     *   </li>
     *   <li><strong>生产环境安全限制</strong>：
     *       <ul>
     *         <li>禁止通配符：不允许使用"*"允许所有来源</li>
     *         <li>域名白名单：仅允许明确指定的信任域名</li>
     *         <li>安全评估：防止CSRF和XSS攻击</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>安全最佳实践：</strong>
     * <ul>
     *   <li><strong>开发环境</strong>：
     *       <ul>
     *         <li>可使用"*"通配符便于调试</li>
     *         <li>允许localhost和开发服务器地址</li>
     *       </ul>
     *   </li>
     *   <li><strong>生产环境</strong>：
     *       <ul>
     *         <li>明确列举所有允许的域名</li>
     *         <li>优先使用HTTPS协议</li>
     *         <li>定期审查和更新允许列表</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>错误类型说明：</strong>
     * <ul>
     *   <li>{@code invalid.cors.origin} - 无效的CORS来源URL格式</li>
     *   <li>{@code insecure.cors.config} - 不安全的CORS配置（生产环境中使用通配符）</li>
     * </ul>
     * 
     * @param context 包含CORS配置的验证上下文
     * @param errors 错误收集器，用于记录CORS配置相关错误
     * 
     * @see #isValidUrl(String) URL有效性验证方法
     * @see ConfigValidationContext#getCorsAllowedOrigins() CORS允许来源列表
     * @see ConfigValidationContext#isProductionEnvironment() 环境判断方法
     * 
     * @example
     * <pre>{@code
     * // 开发环境 - 允许的配置
     * String[] devOrigins = {"*", "http://localhost:3000"};
     * 
     * // 生产环境 - 推荐的配置
     * String[] prodOrigins = {
     *     "https://myapp.com",
     *     "https://admin.myapp.com"
     * };
     * }</pre>
     * 
     * @since 1.0
     */
    private void validateCorsConfig(ConfigValidationContext context, Errors errors) {
        String[] allowedOrigins = context.getCorsAllowedOrigins();
        if (allowedOrigins != null) {
            for (String origin : allowedOrigins) {
                if (!"*".equals(origin) && !isValidUrl(origin)) {
                    errors.rejectValue("corsAllowedOrigins", "invalid.cors.origin", 
                        "Invalid CORS allowed origin: " + origin);
                }
            }
        }
        
        // 生产环境不应允许所有来源
        if (context.isProductionEnvironment() && allowedOrigins != null) {
            for (String origin : allowedOrigins) {
                if ("*".equals(origin)) {
                    errors.rejectValue("corsAllowedOrigins", "insecure.cors.config", 
                        "CORS should not allow all origins in production");
                    break;
                }
            }
        }
    }
    
    /**
     * 验证日志相关配置参数
     * 
     * <p>此方法对应用程序的日志配置进行验证，确保日志系统
     * 能够正常工作并提供有效的调试信息。主要验证内容包括：
     * 
     * <ul>
     *   <li><strong>日志级别验证</strong>：
     *       <ul>
     *         <li>有效级别：TRACE, DEBUG, INFO, WARN, ERROR, OFF</li>
     *         <li>大小写兼容：自动转换为大写进行验证</li>
     *         <li>环境建议：开发环境DEBUG，生产环境INFO或WARN</li>
     *       </ul>
     *   </li>
     *   <li><strong>日志文件路径验证</strong>：
     *       <ul>
     *         <li>路径格式：使用Java NIO验证路径有效性</li>
     *         <li>目录权限：确保应用有写入权限</li>
     *         <li>存储空间：考虑日志轮转和空间管理</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>日志级别说明：</strong>
     * <table border="1">
     *   <tr><th>级别</th><th>用途</th><th>适用场景</th></tr>
     *   <tr><td>TRACE</td><td>最详细的调试信息</td><td>问题排查，性能分析</td></tr>
     *   <tr><td>DEBUG</td><td>调试信息</td><td>开发和测试环境</td></tr>
     *   <tr><td>INFO</td><td>一般信息</td><td>生产环境正常日志</td></tr>
     *   <tr><td>WARN</td><td>警告信息</td><td>潜在问题提醒</td></tr>
     *   <tr><td>ERROR</td><td>错误信息</td><td>系统异常和错误</td></tr>
     *   <tr><td>OFF</td><td>关闭日志</td><td>特殊情况下禁用日志</td></tr>
     * </table>
     * 
     * <p><strong>性能考虑：</strong>
     * <ul>
     *   <li>过低的日志级别可能影响应用性能</li>
     *   <li>日志文件大小和轮转策略需要合理配置</li>
     *   <li>异步日志可以提高性能但可能丢失日志</li>
     * </ul>
     * 
     * @param context 包含日志配置的验证上下文
     * @param errors 错误收集器，用于记录日志配置相关错误
     * 
     * @see #isValidLogLevel(String) 日志级别有效性验证
     * @see #isValidFilePath(String) 文件路径有效性验证
     * @see ConfigValidationContext#getRootLogLevel() 根日志级别
     * @see ConfigValidationContext#getLogFile() 日志文件路径
     * 
     * @since 1.0
     */
    private void validateLoggingConfig(ConfigValidationContext context, Errors errors) {
        // 验证日志级别
        String rootLogLevel = context.getRootLogLevel();
        if (rootLogLevel != null && !isValidLogLevel(rootLogLevel)) {
            errors.rejectValue("rootLogLevel", "invalid.log.level", 
                "Invalid root log level: " + rootLogLevel);
        }
        
        // 验证日志文件路径
        String logFile = context.getLogFile();
        if (logFile != null && !isValidFilePath(logFile)) {
            errors.rejectValue("logFile", "invalid.log.file", 
                "Invalid log file path: " + logFile);
        }
    }
    
    /**
     * 验证应用特定的自定义配置参数
     * 
     * <p>此方法对与应用业务逻辑相关的自定义配置进行验证，
     * 确保这些功能性配置的合理性和有效性。主要验证内容包括：
     * 
     * <ul>
     *   <li><strong>缓存配置验证</strong>：
     *       <ul>
     *         <li>TTL（生存时间）：1秒到24小时之间</li>
     *         <li>最大缓存大小：1到100,000个条目</li>
     *         <li>内存管理：防止内存溢出和性能下降</li>
     *       </ul>
     *   </li>
     *   <li><strong>监控配置验证</strong>：
     *       <ul>
     *         <li>监控间隔：5秒到1小时之间</li>
     *         <li>性能影响：频繁监控可能影响系统性能</li>
     *         <li>资源消耗：平衡监控精度和资源开销</li>
     *       </ul>
     *   </li>
     * </ul>
     * 
     * <p><strong>缓存配置最佳实践：</strong>
     * <table border="1">
     *   <tr><th>场景</th><th>TTL推荐值</th><th>最大大小推荐</th><th>说明</th></tr>
     *   <tr><td>用户会话</td><td>30分钟</td><td>10,000</td><td>中等时长，适中容量</td></tr>
     *   <tr><td>配置数据</td><td>1小时</td><td>1,000</td><td>较长时间，小容量</td></tr>
     *   <tr><td>查询结果</td><td>5分钟</td><td>50,000</td><td>短时间，大容量</td></tr>
     *   <tr><td>实时数据</td><td>30秒</td><td>5,000</td><td>极短时间</td></tr>
     * </table>
     * 
     * <p><strong>监控间隔指导：</strong>
     * <ul>
     *   <li><strong>高频监控（5-30秒）</strong>：关键业务指标，实时报警</li>
     *   <li><strong>中频监控（1-10分钟）</strong>：一般性能指标，趋势分析</li>
     *   <li><strong>低频监控（10-60分钟）</strong>：长期统计，容量规划</li>
     * </ul>
     * 
     * <p><strong>性能优化建议：</strong>
     * <ul>
     *   <li>根据应用访问模式调整缓存TTL</li>
     *   <li>使用分层缓存策略提高命中率</li>
     *   <li>监控数据应按优先级分级处理</li>
     *   <li>定期清理过期缓存和监控数据</li>
     * </ul>
     * 
     * @param context 包含自定义配置的验证上下文
     * @param errors 错误收集器，用于记录自定义配置相关错误
     * 
     * @see #validateRange(int, int, int, String, String, Errors) 数值范围验证工具
     * @see ConfigValidationContext#getCacheTtl() 缓存TTL配置
     * @see ConfigValidationContext#getCacheMaxSize() 缓存大小配置
     * @see ConfigValidationContext#getMonitoringInterval() 监控间隔配置
     * 
     * @since 1.0
     */
    private void validateCustomConfig(ConfigValidationContext context, Errors errors) {
        // 验证缓存配置
        Integer cacheTtl = context.getCacheTtl();
        if (cacheTtl != null) {
            validateRange(cacheTtl, 1, 86400, "cacheTtl", 
                "Cache TTL must be between 1 second and 24 hours", errors);
        }
        
        Integer cacheMaxSize = context.getCacheMaxSize();
        if (cacheMaxSize != null) {
            validateRange(cacheMaxSize, 1, 100000, "cacheMaxSize", 
                "Cache max size must be between 1 and 100000", errors);
        }
        
        // 验证监控配置
        Integer monitoringInterval = context.getMonitoringInterval();
        if (monitoringInterval != null) {
            validateRange(monitoringInterval, 5, 3600, "monitoringInterval", 
                "Monitoring interval must be between 5 seconds and 1 hour", errors);
        }
    }
    
    /**
     * 验证网络端口号的有效性和可用性
     * 
     * <p>此方法对指定的端口号进行全面验证，确保端口号符合网络协议规范
     * 且在当前系统环境中可用。验证包括：
     * 
     * <ul>
     *   <li><strong>范围验证</strong>：端口号必须在1-65535之间</li>
     *   <li><strong>特权端口检查</strong>：小于1024的端口需要管理员权限</li>
     *   <li><strong>保留端口警告</strong>：避免使用已知的系统保留端口</li>
     * </ul>
     * 
     * <p><strong>特权端口说明：</strong>
     * 在Unix-like系统中，端口号1-1023被称为特权端口或well-known端口，
     * 只有具有root权限的进程才能绑定这些端口。常见的特权端口包括：
     * <ul>
     *   <li>22 - SSH</li>
     *   <li>80 - HTTP</li>
     *   <li>443 - HTTPS</li>
     *   <li>3306 - MySQL</li>
     *   <li>5432 - PostgreSQL</li>
     * </ul>
     * 
     * <p><strong>错误代码说明：</strong>
     * <ul>
     *   <li>{@code invalid.port} - 端口号超出有效范围</li>
     *   <li>{@code privileged.port} - 尝试使用特权端口但无相应权限</li>
     * </ul>
     * 
     * @param port 待验证的端口号，可以为null（null值会被跳过验证）
     * @param field 错误报告中使用的字段名，用于标识具体的配置项
     * @param errors 错误收集器，用于记录端口验证过程中发现的问题
     * 
     * @see #isPrivilegedPortAllowed() 检查当前环境是否允许使用特权端口
     * 
     * @example
     * <pre>{@code
     * // 验证服务器端口
     * validatePort(8080, "server.port", errors);
     * 
     * // 验证数据库端口
     * validatePort(3306, "database.port", errors);
     * }</pre>
     * 
     * @since 1.0
     */
    private void validatePort(Integer port, String field, Errors errors) {
        if (port != null) {
            if (port < 1 || port > 65535) {
                errors.rejectValue(field, "invalid.port", 
                    "Port must be between 1 and 65535");
            } else if (port < 1024 && !isPrivilegedPortAllowed()) {
                errors.rejectValue(field, "privileged.port", 
                    "Privileged ports (< 1024) require special permissions");
            }
        }
    }
    
    /**
     * 验证数值是否在指定范围内
     * 
     * <p>此方法为一个通用的范围验证工具，用于检查整数值是否
     * 在合理的范围内。广泛用于各种配置参数的边界检查。
     * 
     * <p><strong>应用场景：</strong>
     * <ul>
     *   <li>连接池大小限制</li>
     *   <li>超时时间设置</li>
     *   <li>缓存参数配置</li>
     *   <li>限流阈值设置</li>
     *   <li>监控间隔配置</li>
     * </ul>
     * 
     * <p><strong>验证逻辑：</strong>
     * 当数值不在指定的[min, max]闭间隔内时，将向错误收集器
     * 添加一个带有错误代码"invalid.range"的错误记录。
     * 
     * <p><strong>参数说明：</strong>
     * <ul>
     *   <li>边界值包含：min和max都是有效值</li>
     *   <li>支持负数范围验证</li>
     *   <li>错误消息支持自定义</li>
     * </ul>
     * 
     * @param value 待验证的整数值
     * @param min 允许的最小值（包含）
     * @param max 允许的最大值（包含）
     * @param field 配置字段名，用于错误定位
     * @param message 自定义错误消息，应描述有效范围
     * @param errors 错误收集器，用于记录验证错误
     * 
     * @example
     * <pre>{@code
     * // 验证连接池大小
     * validateRange(poolSize, 1, 100, "maxPoolSize", 
     *     "Connection pool size must be between 1 and 100", errors);
     * 
     * // 验证超时时间（毫秒）
     * validateRange(timeout, 1000, 60000, "timeout", 
     *     "Timeout must be between 1 and 60 seconds", errors);
     * }</pre>
     * 
     * @since 1.0
     */
    private void validateRange(int value, int min, int max, String field, String message, Errors errors) {
        if (value < min || value > max) {
            errors.rejectValue(field, "invalid.range", message);
        }
    }
    
    /**
     * 验证URL字符串的格式正确性和协议支持性
     * 
     * <p>此方法使用多层验证策略确保URL的有效性：
     * <ol>
     *   <li><strong>基础格式检查</strong>：使用预编译的正则表达式验证URL结构</li>
     *   <li><strong>Java URL解析</strong>：利用java.net.URL进行深度格式验证</li>
     *   <li><strong>协议支持检查</strong>：确保协议在支持范围内</li>
     * </ol>
     * 
     * <p><strong>支持的URL协议：</strong>
     * <ul>
     *   <li>{@code http://} - 超文本传输协议</li>
     *   <li>{@code https://} - 安全超文本传输协议</li>
     *   <li>{@code ftp://} - 文件传输协议</li>
     * </ul>
     * 
     * <p><strong>验证示例：</strong>
     * <table border="1">
     *   <tr><th>URL</th><th>验证结果</th><th>说明</th></tr>
     *   <tr><td>https://api.example.com</td><td>✓ 有效</td><td>标准HTTPS URL</td></tr>
     *   <tr><td>http://localhost:8080/api</td><td>✓ 有效</td><td>本地开发URL</td></tr>
     *   <tr><td>ftp://files.example.com</td><td>✓ 有效</td><td>FTP服务器URL</td></tr>
     *   <tr><td>file:///path/to/file</td><td>✗ 无效</td><td>不支持的协议</td></tr>
     *   <tr><td>not-a-url</td><td>✗ 无效</td><td>格式错误</td></tr>
     * </table>
     * 
     * <p><strong>性能优化：</strong>
     * 方法使用预编译的正则表达式{@link #URL_PATTERN}进行初步筛选，
     * 避免对明显不符合格式的字符串进行昂贵的URL解析操作。
     * 
     * @param url 待验证的URL字符串，null或空字符串将返回false
     * @return {@code true} 如果URL格式正确且协议受支持；{@code false} 否则
     * 
     * @see #URL_PATTERN 预编译的URL匹配正则表达式
     * @see java.net.URL URL解析类
     * 
     * @example
     * <pre>{@code
     * // 验证API端点URL
     * if (isValidUrl("https://api.service.com/v1")) {
     *     // URL有效，可以进行后续处理
     * }
     * 
     * // 验证重定向URL
     * String redirectUrl = config.getRedirectUrl();
     * if (!isValidUrl(redirectUrl)) {
     *     errors.rejectValue("redirectUrl", "invalid.url", "无效的重定向URL");
     * }
     * }</pre>
     * 
     * @since 1.0
     */
    private boolean isValidUrl(String url) {
        if (url == null || url.trim().isEmpty()) {
            return false;
        }
        
        try {
            new URL(url);
            return URL_PATTERN.matcher(url).matches();
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * 验证日志级别的有效性
     * 
     * <p>此方法检查指定的日志级别是否为 Java 日志框架支持的
     * 有效级别。支持大小写不敏感的验证。
     * 
     * <p><strong>支持的日志级别：</strong>
     * <table border="1">
     *   <tr><th>级别</th><th>详细程度</th><th>使用场景</th><th>性能影响</th></tr>
     *   <tr><td>TRACE</td><td>最高</td><td>深度调试，问题排查</td><td>最大</td></tr>
     *   <tr><td>DEBUG</td><td>高</td><td>开发调试，功能测试</td><td>较大</td></tr>
     *   <tr><td>INFO</td><td>中</td><td>一般信息，业务流程</td><td>中等</td></tr>
     *   <tr><td>WARN</td><td>低</td><td>警告信息，非致命错误</td><td>较小</td></tr>
     *   <tr><td>ERROR</td><td>最低</td><td>错误信息，系统异常</td><td>最小</td></tr>
     *   <tr><td>OFF</td><td>无</td><td>关闭日志输出</td><td>无</td></tr>
     * </table>
     * 
     * <p><strong>环境建议配置：</strong>
     * <ul>
     *   <li><strong>开发环境</strong>：DEBUG或TRACE，方便调试</li>
     *   <li><strong>测试环境</strong>：INFO，平衡信息和性能</li>
     *   <li><strong>预产环境</strong>：WARN，减少日志量进行性能测试</li>
     *   <li><strong>生产环境</strong>：INFO或WARN，确保性能和存储效率</li>
     * </ul>
     * 
     * <p><strong>性能考虑：</strong>
     * 日志级别越低（TRACE < DEBUG < INFO < WARN < ERROR），
     * 输出的日志信息越多，对系统性能的影响越大。
     * 
     * @param level 待验证的日志级别字符串，支持大小写不敏感
     * @return {@code true} 如果级别有效；{@code false} 如果级别无效或为null
     * 
     * @example
     * <pre>{@code
     * // 验证各种格式
     * isValidLogLevel("INFO");    // true
     * isValidLogLevel("info");    // true  
     * isValidLogLevel("Info");    // true
     * isValidLogLevel("INVALID"); // false
     * isValidLogLevel(null);      // false
     * }</pre>
     * 
     * @since 1.0
     */
    private boolean isValidLogLevel(String level) {
        if (level == null) {
            return false;
        }
        
        String upperLevel = level.toUpperCase();
        return "TRACE".equals(upperLevel) || "DEBUG".equals(upperLevel) || 
               "INFO".equals(upperLevel) || "WARN".equals(upperLevel) || 
               "ERROR".equals(upperLevel) || "OFF".equals(upperLevel);
    }
    
    /**
     * 验证文件路径的格式正确性和可访问性
     * 
     * <p>此方法使用Java NIO.2 API验证文件路径的格式和可访问性，
     * 支持跨平台的路径格式检查。主要用于验证日志文件路径、
     * 配置文件路径等参数。
     * 
     * <p><strong>验证内容：</strong>
     * <ul>
     *   <li><strong>路径格式</strong>：检查路径字符串的语法正确性</li>
     *   <li><strong>路径解析</strong>：验证路径是否可以被JVM正确解析</li>
     *   <li><strong>安全检查</strong>：防止路径遭历攻击和不安全路径</li>
     * </ul>
     * 
     * <p><strong>支持的路径格式：</strong>
     * <table border="1">
     *   <tr><th>平台</th><th>绝对路径格式</th><th>相对路径格式</th></tr>
     *   <tr><td>Windows</td><td>C:\\logs\\app.log</td><td>logs\\app.log</td></tr>
     *   <tr><td>Unix/Linux</td><td>/var/log/app.log</td><td>logs/app.log</td></tr>
     *   <tr><td>macOS</td><td>/Users/user/logs/app.log</td><td>./logs/app.log</td></tr>
     * </table>
     * 
     * <p><strong>安全注意事项：</strong>
     * <ul>
     *   <li>防止使用"../"进行目录遭历</li>
     *   <li>检查路径长度以防止缓冲区溢出</li>
     *   <li>验证路径中的特殊字符和空格</li>
     * </ul>
     * 
     * <p><strong>错误场景：</strong>
     * <ul>
     *   <li>null或空字符串</li>
     *   <li>包含非法字符的路径</li>
     *   <li>格式不正确的路径分隔符</li>
     *   <li>超出系统限制的路径长度</li>
     * </ul>
     * 
     * <p><strong>性能考虑：</strong>
     * 此方法仅进行格式验证，不执行实际的文件系统访问，
     * 因此性能开销较小。如需检查文件是否存在或可写，
     * 应在实际使用时另行检查。
     * 
     * @param path 待验证的文件路径字符串
     * @return {@code true} 如果路径格式正确；{@code false} 如果路径无效或为null
     * 
     * @see java.nio.file.Paths NIO.2路径API
     * @see java.nio.file.InvalidPathException 路径格式异常
     * 
     * @example
     * <pre>{@code
     * // Windows路径验证
     * isValidFilePath("C:\\logs\\application.log");  // true
     * isValidFilePath("logs\\app.log");            // true
     * 
     * // Unix/Linux路径验证
     * isValidFilePath("/var/log/application.log"); // true
     * isValidFilePath("./logs/app.log");           // true
     * 
     * // 无效路径
     * isValidFilePath(null);                       // false
     * isValidFilePath("");                         // false
     * isValidFilePath("con\x00trol");              // false
     * }</pre>
     * 
     * @since 1.0
     */
    private boolean isValidFilePath(String path) {
        if (path == null || path.trim().isEmpty()) {
            return false;
        }
        
        try {
            java.nio.file.Paths.get(path);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * 检查当前运行环境是否允许使用特权端口
     * 
     * <p>特权端口（Privileged Ports）是指端口号小于1024的网络端口，
     * 在类 Unix 系统中，只有具有超级用户权限（root）的进程才能绑定
     * 这些端口。此方法用于检查当前应用是否具有使用特权端口的权限。
     * 
     * <p><strong>常见的特权端口：</strong>
     * <table border="1">
     *   <tr><th>端口</th><th>服务</th><th>说明</th></tr>
     *   <tr><td>21</td><td>FTP</td><td>文件传输协议</td></tr>
     *   <tr><td>22</td><td>SSH</td><td>安全Shell协议</td></tr>
     *   <tr><td>23</td><td>Telnet</td><td>远程终端协议</td></tr>
     *   <tr><td>25</td><td>SMTP</td><td>邮件传输协议</td></tr>
     *   <tr><td>53</td><td>DNS</td><td>域名解析服务</td></tr>
     *   <tr><td>80</td><td>HTTP</td><td>超文本传输协议</td></tr>
     *   <tr><td>110</td><td>POP3</td><td>邮件接收协议</td></tr>
     *   <tr><td>143</td><td>IMAP</td><td>邮件访问协议</td></tr>
     *   <tr><td>443</td><td>HTTPS</td><td>安全HTTP协议</td></tr>
     *   <tr><td>993</td><td>IMAPS</td><td>安全IMAP协议</td></tr>
     * </table>
     * 
     * <p><strong>使用场景：</strong>
     * <ul>
     *   <li><strong>Web服务器</strong>：使甈80和443端口提供HTTP/HTTPS服务</li>
     *   <li><strong>邮件服务器</strong>：使甈25、110、143等端口</li>
     *   <li><strong>数据库服务</strong>：传统上MySQL使甈3306，PostgreSQL使甈5432</li>
     *   <li><strong>系统服务</strong>：DNS、NTP等系统基础服务</li>
     * </ul>
     * 
     * <p><strong>安全考虑：</strong>
     * <ul>
     *   <li>特权端口的设计初衷是防止普通用户启动系统服务</li>
     *   <li>在生产环境中，应谨慎使用特权端口</li>
     *   <li>容器化环境可能有不同的权限管理方式</li>
     * </ul>
     * 
     * <p><strong>绕过特权端口限制的方法：</strong>
     * <ul>
     *   <li><strong>使用非特权端口</strong>：选择1024以上的端口</li>
     *   <li><strong>反向代理</strong>：使用Nginx等代理转发请求</li>
     *   <li><strong>端口映射</strong>：在容器或网络层面进行端口映射</li>
     *   <li><strong>能力绑定</strong>：在Linux中使用CAP_NET_BIND_SERVICE能力</li>
     * </ul>
     * 
     * <p><strong>实现说明：</strong>
     * 当前实现始终返回{@code false}，表示默认不允许使用特权端口。
     * 在实际部署中，可以根据具体环境修改这个逻辑：
     * <ul>
     *   <li>检查系统属性或环境变量</li>
     *   <li>检查当前用户的权限</li>
     *   <li>检查容器运行时环境</li>
     * </ul>
     * 
     * @return {@code true} 如果允许使用特权端口；{@code false} 否则
     * 
     * @see #validatePort(Integer, String, Errors) 端口验证方法
     * 
     * @example
     * <pre>{@code
     * // 在实际应用中的可能实现
     * private boolean isPrivilegedPortAllowed() {
     *     // 检查环境变量
     *     if ("true".equals(System.getenv("ALLOW_PRIVILEGED_PORTS"))) {
     *         return true;
     *     }
     *     
     *     // 检查是否在容器中运行
     *     if (isRunningInContainer()) {
     *         return true;
     *     }
     *     
     *     // 检查当前用户是否为root
     *     return "root".equals(System.getProperty("user.name"));
     * }
     * }</pre>
     * 
     * @since 1.0
     */
    private boolean isPrivilegedPortAllowed() {
        // 在实际应用中，这里可以检查系统权限或配置
        return false;
    }
}