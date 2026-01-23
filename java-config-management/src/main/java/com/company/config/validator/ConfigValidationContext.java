package com.company.config.validator;

/**
 * 配置验证上下文 - 包含需要验证的所有配置项
 */
public class ConfigValidationContext {
    
    // 服务器配置
    private Integer serverPort;
    private String serverContextPath;
    
    // 数据库配置
    private String databaseUrl;
    private String databaseUsername;
    private String databasePassword;
    private Integer maxPoolSize;
    private Integer minIdle;
    
    // 安全配置
    private String jwtSecret;
    private Long jwtExpiration;
    private String[] corsAllowedOrigins;
    private Integer rateLimit;
    
    // 日志配置
    private String rootLogLevel;
    private String logFile;
    
    // 自定义配置
    private Integer cacheTtl;
    private Integer cacheMaxSize;
    private Integer monitoringInterval;
    
    // 环境信息
    private boolean productionEnvironment;
    
    // 构造函数
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