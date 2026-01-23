package com.company.config.validator;

import com.company.config.loader.EnvironmentDetector;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.BindingResult;
import org.springframework.validation.ObjectError;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

/**
 * 启动时配置验证器 - 在应用程序启动时验证配置
 */
@Component
public class StartupConfigValidator implements ApplicationListener<ApplicationReadyEvent> {
    
    private static final Logger logger = LoggerFactory.getLogger(StartupConfigValidator.class);
    
    @Autowired
    private Environment environment;
    
    @Autowired
    private EnvironmentDetector environmentDetector;
    
    @Autowired
    private ConfigValidator configValidator;
    
    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        logger.info("Starting configuration validation on application startup");
        
        try {
            // 创建配置验证上下文
            ConfigValidationContext context = createValidationContext();
            
            // 执行验证
            BindingResult bindingResult = new BeanPropertyBindingResult(context, "config");
            configValidator.validate(context, bindingResult);
            
            // 处理验证结果
            handleValidationResult(bindingResult);
            
        } catch (Exception e) {
            logger.error("Configuration validation failed with exception", e);
            throw new ConfigurationValidationException("Configuration validation failed", e);
        }
    }
    
    /**
     * 创建配置验证上下文
     */
    private ConfigValidationContext createValidationContext() {
        ConfigValidationContext context = new ConfigValidationContext();
        
        // 设置环境信息
        context.setProductionEnvironment(environmentDetector.isProduction());
        
        // 设置服务器配置
        context.setServerPort(getIntegerProperty("server.port"));
        context.setServerContextPath(environment.getProperty("server.servlet.context-path"));
        
        // 设置数据库配置
        context.setDatabaseUrl(environment.getProperty("spring.datasource.url"));
        context.setDatabaseUsername(environment.getProperty("spring.datasource.username"));
        context.setDatabasePassword(environment.getProperty("spring.datasource.password"));
        context.setMaxPoolSize(getIntegerProperty("spring.datasource.hikari.maximum-pool-size"));
        context.setMinIdle(getIntegerProperty("spring.datasource.hikari.minimum-idle"));
        
        // 设置安全配置
        context.setJwtSecret(environment.getProperty("security.jwt.secret"));
        context.setJwtExpiration(getLongProperty("security.jwt.expiration"));
        context.setCorsAllowedOrigins(getCorsAllowedOrigins());
        context.setRateLimit(getIntegerProperty("security.rate-limit.requests-per-minute"));
        
        // 设置日志配置
        context.setRootLogLevel(environment.getProperty("logging.level.root"));
        context.setLogFile(environment.getProperty("logging.file.name"));
        
        // 设置自定义配置
        context.setCacheTtl(getIntegerProperty("app.config.cache.ttl"));
        context.setCacheMaxSize(getIntegerProperty("app.config.cache.max-size"));
        context.setMonitoringInterval(getIntegerProperty("app.config.monitoring.interval"));
        
        return context;
    }
    
    /**
     * 获取整型配置属性
     */
    private Integer getIntegerProperty(String key) {
        String value = environment.getProperty(key);
        if (value != null && !value.trim().isEmpty()) {
            try {
                return Integer.parseInt(value.trim());
            } catch (NumberFormatException e) {
                logger.warn("Invalid integer value for property '{}': {}", key, value);
            }
        }
        return null;
    }
    
    /**
     * 获取长整型配置属性
     */
    private Long getLongProperty(String key) {
        String value = environment.getProperty(key);
        if (value != null && !value.trim().isEmpty()) {
            try {
                return Long.parseLong(value.trim());
            } catch (NumberFormatException e) {
                logger.warn("Invalid long value for property '{}': {}", key, value);
            }
        }
        return null;
    }
    
    /**
     * 获取CORS允许的来源
     */
    private String[] getCorsAllowedOrigins() {
        String origins = environment.getProperty("security.cors.allowed-origins");
        if (origins != null && !origins.trim().isEmpty()) {
            return origins.split(",");
        }
        return null;
    }
    
    /**
     * 处理验证结果
     */
    private void handleValidationResult(BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            List<ObjectError> errors = bindingResult.getAllErrors();
            
            logger.error("Configuration validation failed with {} errors:", errors.size());
            
            for (ObjectError error : errors) {
                String errorMessage = String.format("Field: %s, Error: %s", 
                    error.getObjectName(), error.getDefaultMessage());
                logger.error("  - {}", errorMessage);
            }
            
            // 根据环境决定是否抛出异常
            if (environmentDetector.isProduction()) {
                // 生产环境验证失败必须停止应用
                throw new ConfigurationValidationException(
                    "Configuration validation failed in production environment");
            } else if (environmentDetector.isDevelopment()) {
                // 开发环境只记录警告，允许继续运行
                logger.warn("Configuration validation failed, but continuing in development mode");
            } else {
                // 测试和其他环境抛出异常
                throw new ConfigurationValidationException("Configuration validation failed");
            }
        } else {
            logger.info("Configuration validation completed successfully");
            logConfigurationSummary();
        }
    }
    
    /**
     * 记录配置摘要
     */
    private void logConfigurationSummary() {
        logger.info("=== Configuration Summary ===");
        logger.info("Environment: {}", environmentDetector.getCurrentEnvironment());
        logger.info("Server Port: {}", environment.getProperty("server.port"));
        logger.info("Database URL: {}", maskSensitiveInfo(environment.getProperty("spring.datasource.url")));
        logger.info("Database Username: {}", environment.getProperty("spring.datasource.username"));
        logger.info("Log Level: {}", environment.getProperty("logging.level.root"));
        logger.info("Cache TTL: {}", environment.getProperty("app.config.cache.ttl"));
        logger.info("Monitoring Enabled: {}", environment.getProperty("app.config.monitoring.enabled"));
        logger.info("Hot Reload Enabled: {}", environment.getProperty("app.config.hotreload.enabled"));
        logger.info("=============================");
    }
    
    /**
     * 掩盖敏感信息
     */
    private String maskSensitiveInfo(String info) {
        if (info == null || info.length() <= 8) {
            return "***";
        }
        
        int maskLength = info.length() - 8;
        StringBuilder masked = new StringBuilder();
        masked.append(info.substring(0, 4));
        
        for (int i = 0; i < maskLength; i++) {
            masked.append('*');
        }
        
        masked.append(info.substring(info.length() - 4));
        return masked.toString();
    }
    
    /**
     * 配置验证异常
     */
    public static class ConfigurationValidationException extends RuntimeException {
        public ConfigurationValidationException(String message) {
            super(message);
        }
        
        public ConfigurationValidationException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}