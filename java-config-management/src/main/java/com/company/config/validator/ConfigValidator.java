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
 * 配置验证器 - 负责验证配置项的有效性
 */
@Component
public class ConfigValidator implements Validator {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigValidator.class);
    
    // 常用的正则表达式模式
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
    
    private static final Pattern URL_PATTERN = Pattern.compile(
        "^(https?|ftp)://[\\w\\-._~:/?#\\[\\]@!$&'()*+,;=]+$");
    
    private static final Pattern DATABASE_URL_PATTERN = Pattern.compile(
        "^jdbc:[\\w]+://[\\w\\-._~:/?#\\[\\]@!$&'()*+,;=]+$");
    
    private static final Pattern HOST_PORT_PATTERN = Pattern.compile(
        "^[\\w\\-._~]+:\\d{1,5}$");

    @Override
    public boolean supports(Class<?> clazz) {
        return ConfigValidationContext.class.equals(clazz);
    }

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
     * 验证服务器配置
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
     * 验证数据库配置
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
     * 验证连接池配置
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
     * 验证安全配置
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
     * 验证CORS配置
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
     * 验证日志配置
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
     * 验证自定义配置
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
     * 验证端口号
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
     * 验证数值范围
     */
    private void validateRange(int value, int min, int max, String field, String message, Errors errors) {
        if (value < min || value > max) {
            errors.rejectValue(field, "invalid.range", message);
        }
    }
    
    /**
     * 验证URL格式
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
     * 验证日志级别
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
     * 验证文件路径
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
     * 检查是否允许使用特权端口
     */
    private boolean isPrivilegedPortAllowed() {
        // 在实际应用中，这里可以检查系统权限或配置
        return false;
    }
}