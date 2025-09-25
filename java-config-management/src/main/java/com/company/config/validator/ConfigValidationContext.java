package com.company.config.validator;

/**
 * 配置验证上下文类
 * 
 * <p>此类作为配置验证的数据载体，包含了所有需要验证的配置项。
 * 通过将相关的配置参数封装在一个对象中，提供了统一的验证入口
 * 和清晰的配置结构。
 * 
 * <p><strong>功能特性：</strong>
 * <ul>
 *   <li><strong>统一验证入口</strong>：所有配置项集中管理，便于统一验证</li>
 *   <li><strong>环境敏感配置</strong>：支持根据不同环境应用不同的验证规则</li>
 *   <li><strong>类型安全</strong>：使用强类型定义，编译时可检查类型错误</li>
 *   <li><strong>可扩展性</strong>：新增配置项时只需添加字段和Getter/Setter</li>
 * </ul>
 * 
 * <p><strong>配置分类：</strong>
 * <table border="1">
 *   <tr><th>配置类别</th><th>主要参数</th><th>验证重点</th></tr>
 *   <tr><td>服务器配置</td><td>端口号、上下文路径</td><td>端口范围、路径格式</td></tr>
 *   <tr><td>数据库配置</td><td>URL、用户名、密码、连接池</td><td>URL格式、认证信息、池参数</td></tr>
 *   <tr><td>安全配置</td><td>JWT、CORS、限流</td><td>密钥强度、跨域策略、频率限制</td></tr>
 *   <tr><td>日志配置</td><td>日志级别、文件路径</td><td>级别有效性、路径正确性</td></tr>
 *   <tr><td>自定义配置</td><td>缓存、监控</td><td>TTL范围、容量限制、间隔合理性</td></tr>
 * </table>
 * 
 * <p><strong>环境支持：</strong>
 * 通过{@link #isProductionEnvironment()}方法区分不同环境，
 * 在生产环境中应用更严格的验证规则：
 * <ul>
 *   <li>强制要求敏感配置（数据库密码、JWT密钥）</li>
 *   <li>禁止不安全的配置（CORS通配符）</li>
 *   <li>更严格的参数范围限制</li>
 * </ul>
 * 
 * <p><strong>使用示例：</strong>
 * <pre>{@code
 * // 创建配置上下文
 * ConfigValidationContext context = new ConfigValidationContext();
 * 
 * // 设置服务器配置
 * context.setServerPort(8080);
 * context.setServerContextPath("/api");
 * 
 * // 设置数据库配置
 * context.setDatabaseUrl("jdbc:mysql://localhost:3306/mydb");
 * context.setDatabaseUsername("user");
 * context.setDatabasePassword("password");
 * 
 * // 设置环境标识
 * context.setProductionEnvironment(false);
 * 
 * // 进行验证
 * Errors errors = new BeanPropertyBindingResult(context, "config");
 * validator.validate(context, errors);
 * }</pre>
 * 
 * <p><strong>设计原则：</strong>
 * <ul>
 *   <li><strong>单一职责</strong>：仅作为数据载体，不包含验证逻辑</li>
 *   <li><strong>不可变性</strong>：验证过程中不修改对象状态</li>
 *   <li><strong>可读性</strong>：清晰的字段命名和分组结构</li>
 *   <li><strong>扩展性</strong>：方便添加新的配置类别和参数</li>
 * </ul>
 * 
 * @author 配置管理团队
 * @version 1.0
 * @since 2024-01-01
 * @see ConfigValidator 配置验证器类
 */
public class ConfigValidationContext {
    
    /**
     * 服务器配置参数组
     * 
     * <p>包含了Web服务器的基本配置参数，用于定义应用的
     * 网络访问特性和路由配置。
     */
    
    /**
     * 服务器监听端口号
     * 
     * <p>定义应用服务器监听的TCP端口号。在Spring Boot中对应
     * {@code server.port}配置属性。
     * 
     * <p><strong>取值范围：</strong>1-65535
     * <p><strong>默认值：</strong>8080（Spring Boot默认）
     * <p><strong>特殊考虑：</strong>小于1024的端口需要特殊权限
     */
    private Integer serverPort;
    
    /**
     * 应用上下文路径
     * 
     * <p>定义应用的根路径前缀，所有的HTTP请求都将以此路径开头。
     * 在Spring Boot中对应{@code server.servlet.context-path}配置属性。
     * 
     * <p><strong>格式要求：</strong>必须以"/"开头，例如"/api"、"/app"
     * <p><strong>默认值：</strong>null（表示根路径"/"）
     * <p><strong>示例：</strong>"/api/v1"、"/myapp"
     */
    private String serverContextPath;
    
    /**
     * 数据库配置参数组
     * 
     * <p>包含了数据库连接和连接池的所有相关配置，
     * 用于建立和管理数据库连接。
     */
    
    /**
     * 数据库连接URL
     * 
     * <p>JDBC数据库连接字符串，包含数据库类型、主机地址、端口、
     * 数据库名和连接参数。
     * 
     * <p><strong>支持的格式：</strong>
     * <ul>
     *   <li>MySQL: {@code jdbc:mysql://localhost:3306/mydb?useSSL=false}</li>
     *   <li>PostgreSQL: {@code jdbc:postgresql://localhost:5432/mydb}</li>
     *   <li>H2: {@code jdbc:h2:mem:testdb} 或 {@code jdbc:h2:file:./data/mydb}</li>
     * </ul>
     */
    private String databaseUrl;
    
    /**
     * 数据库连接用户名
     * 
     * <p>用于数据库身份验证的用户名。在生产环境中为必需参数。
     * 
     * <p><strong>安全建议：</strong>
     * <ul>
     *   <li>使用专用的数据库用户，避免使用root或sa</li>
     *   <li>根据最小权限原则分配数据库权限</li>
     * </ul>
     */
    private String databaseUsername;
    
    /**
     * 数据库连接密码
     * 
     * <p>用于数据库身份验证的密码。在生产环境中为必需参数。
     * 
     * <p><strong>安全要求：</strong>
     * <ul>
     *   <li>生产环境中不能为空</li>
     *   <li>建议使用强密码政策</li>
     *   <li>定期更换密码</li>
     *   <li>使用密码管理工具统一管理</li>
     * </ul>
     */
    private String databasePassword;
    
    /**
     * 数据库连接池最大连接数
     * 
     * <p>定义连接池中允许的最大连接数量。超出此数量的请求
     * 将被阻塞或拒绝。
     * 
     * <p><strong>取值范围：</strong>1-100
     * <p><strong>推荐配置：</strong>
     * <ul>
     *   <li>开发环境: 5-10个连接</li>
     *   <li>测试环境: 10-20个连接</li>
     *   <li>生产环境: 20-50个连接（根据并发量调整）</li>
     * </ul>
     */
    private Integer maxPoolSize;
    
    /**
     * 数据库连接池最小空闲连接数
     * 
     * <p>在连接池中保持的最小空闲连接数量。这些连接在空闲时
     * 不会被释放，以便快速响应新的数据库请求。
     * 
     * <p><strong>约束条件：</strong>必须小于或等于{@link #maxPoolSize}
     * <p><strong>性能考虑：</strong>较高的数值能提高响应速度，但会占用更多资源
     */
    private Integer minIdle;
    
    /**
     * 安全配置参数组
     * 
     * <p>包含了应用安全相关的所有配置参数，用于保障系统
     * 在不同环境下的安全性。
     */
    
    /**
     * JWT签名密钥
     * 
     * <p>用于JWT令牌签名和验证的密钥字符串。在生产环境中
     * 必须提供且必须具有足够的安全强度。
     * 
     * <p><strong>安全要求：</strong>
     * <ul>
     *   <li>生产环境中必须至少32个字符</li>
     *   <li>建议使用随机生成的强密钥</li>
     *   <li>不应在代码中硬编码，使用环境变量或外部配置</li>
     * </ul>
     */
    private String jwtSecret;
    
    /**
     * JWT令牌过期时间
     * 
     * <p>定义JWT令牌的有效期，单位为秒。过期后令牌将无效，
     * 需要重新登录或刷新令牌。
     * 
     * <p><strong>取值范围：</strong>300秒（5分钟）到604800秒（7天）
     * <p><strong>推荐设置：</strong>
     * <ul>
     *   <li>短期令牌: 15-60分钟（高安全场景）</li>
     *   <li>中期令牌: 2-8小时（一般应用）</li>
     *   <li>长期令牌: 1-7天（便民应用）</li>
     * </ul>
     */
    private Long jwtExpiration;
    
    /**
     * CORS允许的来源列表
     * 
     * <p>定义允许跨域访问的来源域名列表。用于解决浏览器的
     * 同源策略限制，允许指定的域名访问应用的API。
     * 
     * <p><strong>配置示例：</strong>
     * <ul>
     *   <li>开发环境: {@code ["*"]} 或 {@code ["http://localhost:3000"]}</li>
     *   <li>生产环境: {@code ["https://myapp.com", "https://admin.myapp.com"]}</li>
     * </ul>
     * 
     * <p><strong>安全注意：</strong>生产环境中禁止使用通配符"*"
     */
    private String[] corsAllowedOrigins;
    
    /**
     * API请求限流设置
     * 
     * <p>定义单个客户端在每分钟内允许的最大请求数量。
     * 用于防止恶意攻击和保护系统资源。
     * 
     * <p><strong>取值范围：</strong>1-10000次/分钟
     * <p><strong>参考配置：</strong>
     * <ul>
     *   <li>严格限制: 60-300次/分钟</li>
     *   <li>中等限制: 300-1000次/分钟</li>
     *   <li>宽松限制: 1000-5000次/分钟</li>
     * </ul>
     */
    private Integer rateLimit;
    
    // 日志配置
    private String rootLogLevel;
    private String logFile;
    
    /**
     * 自定义配置参数组
     * 
     * <p>包含了与应用业务逻辑相关的自定义配置参数，
     * 如缓存、监控等功能性配置。
     */
    
    /**
     * 缓存数据生存时间（TTL）
     * 
     * <p>定义缓存条目的默认生存时间，单位为秒。超过此时间
     * 的缓存条目将被自动清理。
     * 
     * <p><strong>取值范围：</strong>1秒到86400秒，即1大第2天
     * <p><strong>使用建议：</strong>
     * <ul>
     *   <li>短期数据（用户状态）: 300-1800秒（5-30分钟）</li>
     *   <li>中期数据（查询结果）: 1800-7200秒（30分钟-2小时）</li>
     *   <li>稳定数据（配置信息）: 7200-86400秒（2-24小时）</li>
     * </ul>
     */
    private Integer cacheTtl;
    
    /**
     * 缓存最大容量
     * 
     * <p>定义缓存中允许存储的最大条目数量。当超过此数量时，
     * 将根据缓存策略（如LRU）清理最久未使用的条目。
     * 
     * <p><strong>取值范围：</strong>1-100000个条目
     * <p><strong>容量规划：</strong>
     * <ul>
     *   <li>小型应用: 100-1000个条目</li>
     *   <li>中型应用: 1000-10000个条目</li>
     *   <li>大型应用: 10000-100000个条目</li>
     * </ul>
     * 
     * <p><strong>内存评估：</strong>需考虑单个缓存条目的平均大小
     */
    private Integer cacheMaxSize;
    
    /**
     * 系统监控数据采集间隔
     * 
     * <p>定义系统性能监控数据的采集频率，单位为秒。
     * 包括CPU使用率、内存使用率、请求量等指标。
     * 
     * <p><strong>取值范围：</strong>5秒到3600秒（1小时）
     * <p><strong>监控类型建议：</strong>
     * <ul>
     *   <li>实时监控: 5-30秒（关键指标）</li>
     *   <li>常规监控: 60-300秒（一般指标）</li>
     *   <li>趋势分析: 300-1800秒（长期统计）</li>
     * </ul>
     * 
     * <p><strong>性能影响：</strong>过低的间隔可能影响系统性能
     */
    private Integer monitoringInterval;
    
    /**
     * 环境信息配置
     * 
     * <p>用于标识当前运行环境的配置参数，影响验证规则的严格程度。
     */
    
    /**
     * 是否为生产环境
     * 
     * <p>标识当前应用是否运行在生产环境中。此标识影响配置
     * 验证的严格程度和安全要求。
     * 
     * <p><strong>环境差异：</strong>
     * <table border="1">
     *   <tr><th>验证项</th><th>开发环境（false）</th><th>生产环境（true）</th></tr>
     *   <tr><td>数据库密码</td><td>可为空</td><td>必须提供</td></tr>
     *   <tr><td>JWT密钥</td><td>可为空</td><td>必须提供且≥ 32字符</td></tr>
     *   <tr><td>CORS设置</td><td>允许"*"通配符</td><td>禁止"*"，必须明确指定</td></tr>
     *   <tr><td>日志级别</td><td>建议DEBUG</td><td>建议INFO或WARN</td></tr>
     * </table>
     * 
     * <p><strong>设置方式：</strong>
     * <ul>
     *   <li>通过Spring Profile自动检测</li>
     *   <li>通过环境变量手动设置</li>
     *   <li>通过配置文件显式指定</li>
     * </ul>
     * 
     * <p><strong>默认值：</strong>{@code false}（非生产环境）
     */
    private boolean productionEnvironment;
    
    /**
     * 默认构造函数
     * 
     * <p>初始化一个空的配置验证上下文对象。所有配置参数
     * 都将使用默认值（大多数为null，环境标识为false）。
     * 
     * <p>使甡}应在构造后通过setter方法设置具体的配置值。
     * 
     * @since 1.0
     */
    public ConfigValidationContext() {
    }
    
    // Getter和Setter方法
    public Integer getServerPort() {
        return serverPort;
    }
    
    public void setServerPort(Integer serverPort) {
        this.serverPort = serverPort;
    }
    
    public String getServerContextPath() {
        return serverContextPath;
    }
    
    public void setServerContextPath(String serverContextPath) {
        this.serverContextPath = serverContextPath;
    }
    
    public String getDatabaseUrl() {
        return databaseUrl;
    }
    
    public void setDatabaseUrl(String databaseUrl) {
        this.databaseUrl = databaseUrl;
    }
    
    public String getDatabaseUsername() {
        return databaseUsername;
    }
    
    public void setDatabaseUsername(String databaseUsername) {
        this.databaseUsername = databaseUsername;
    }
    
    public String getDatabasePassword() {
        return databasePassword;
    }
    
    public void setDatabasePassword(String databasePassword) {
        this.databasePassword = databasePassword;
    }
    
    public Integer getMaxPoolSize() {
        return maxPoolSize;
    }
    
    public void setMaxPoolSize(Integer maxPoolSize) {
        this.maxPoolSize = maxPoolSize;
    }
    
    public Integer getMinIdle() {
        return minIdle;
    }
    
    public void setMinIdle(Integer minIdle) {
        this.minIdle = minIdle;
    }
    
    public String getJwtSecret() {
        return jwtSecret;
    }
    
    public void setJwtSecret(String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }
    
    public Long getJwtExpiration() {
        return jwtExpiration;
    }
    
    public void setJwtExpiration(Long jwtExpiration) {
        this.jwtExpiration = jwtExpiration;
    }
    
    public String[] getCorsAllowedOrigins() {
        return corsAllowedOrigins;
    }
    
    public void setCorsAllowedOrigins(String[] corsAllowedOrigins) {
        this.corsAllowedOrigins = corsAllowedOrigins;
    }
    
    public Integer getRateLimit() {
        return rateLimit;
    }
    
    public void setRateLimit(Integer rateLimit) {
        this.rateLimit = rateLimit;
    }
    
    public String getRootLogLevel() {
        return rootLogLevel;
    }
    
    public void setRootLogLevel(String rootLogLevel) {
        this.rootLogLevel = rootLogLevel;
    }
    
    public String getLogFile() {
        return logFile;
    }
    
    public void setLogFile(String logFile) {
        this.logFile = logFile;
    }
    
    public Integer getCacheTtl() {
        return cacheTtl;
    }
    
    public void setCacheTtl(Integer cacheTtl) {
        this.cacheTtl = cacheTtl;
    }
    
    public Integer getCacheMaxSize() {
        return cacheMaxSize;
    }
    
    public void setCacheMaxSize(Integer cacheMaxSize) {
        this.cacheMaxSize = cacheMaxSize;
    }
    
    public Integer getMonitoringInterval() {
        return monitoringInterval;
    }
    
    public void setMonitoringInterval(Integer monitoringInterval) {
        this.monitoringInterval = monitoringInterval;
    }
    
    public boolean isProductionEnvironment() {
        return productionEnvironment;
    }
    
    public void setProductionEnvironment(boolean productionEnvironment) {
        this.productionEnvironment = productionEnvironment;
    }
}