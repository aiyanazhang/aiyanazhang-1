package com.company.config.loader;

import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.PostConstruct;
import java.util.Arrays;
import java.util.List;

/**
 * 环境检测器 - 负责检测当前运行环境并设置相应的Profile
 */
@Component
public class EnvironmentDetector {
    
    private static final Logger logger = LoggerFactory.getLogger(EnvironmentDetector.class);
    
    @Autowired
    private Environment environment;
    
    private String currentEnvironment;
    private EnvironmentType environmentType;
    
    /**
     * 支持的环境类型
     */
    public enum EnvironmentType {
        DEVELOPMENT("dev", "开发环境"),
        TESTING("test", "测试环境"),
        STAGING("staging", "预发布环境"),
        PRODUCTION("prod", "生产环境"),
        UNKNOWN("unknown", "未知环境");
        
        private final String profile;
        private final String description;
        
        EnvironmentType(String profile, String description) {
            this.profile = profile;
            this.description = description;
        }
        
        public String getProfile() {
            return profile;
        }
        
        public String getDescription() {
            return description;
        }
        
        public static EnvironmentType fromProfile(String profile) {
            for (EnvironmentType type : values()) {
                if (type.getProfile().equals(profile)) {
                    return type;
                }
            }
            return UNKNOWN;
        }
    }
    
    /**
     * 初始化环境检测
     */
    @PostConstruct
    public void detectEnvironment() {
        String[] activeProfiles = environment.getActiveProfiles();
        
        if (activeProfiles.length == 0) {
            // 如果没有激活的Profile，尝试从其他源检测
            currentEnvironment = detectEnvironmentFromSources();
            environmentType = EnvironmentType.fromProfile(currentEnvironment);
        } else {
            // 使用第一个激活的Profile作为当前环境
            currentEnvironment = activeProfiles[0];
            environmentType = EnvironmentType.fromProfile(currentEnvironment);
        }
        
        if (environmentType == EnvironmentType.UNKNOWN) {
            // 如果仍然无法确定环境，默认为开发环境
            currentEnvironment = EnvironmentType.DEVELOPMENT.getProfile();
            environmentType = EnvironmentType.DEVELOPMENT;
            logger.warn("Unable to detect environment, defaulting to development environment");
        }
        
        logger.info("Detected environment: {} ({})", 
            environmentType.getDescription(), currentEnvironment);
        
        // 记录所有激活的Profile
        if (activeProfiles.length > 0) {
            logger.info("Active profiles: {}", Arrays.toString(activeProfiles));
        }
        
        // 验证环境配置的有效性
        validateEnvironmentConfiguration();
    }
    
    /**
     * 从多个源检测环境
     */
    private String detectEnvironmentFromSources() {
        // 1. 检查环境变量
        String envFromVar = detectFromEnvironmentVariable();
        if (envFromVar != null) {
            logger.info("Environment detected from environment variable: {}", envFromVar);
            return envFromVar;
        }
        
        // 2. 检查系统属性
        String envFromProperty = detectFromSystemProperty();
        if (envFromProperty != null) {
            logger.info("Environment detected from system property: {}", envFromProperty);
            return envFromProperty;
        }
        
        // 3. 检查主机名模式
        String envFromHostname = detectFromHostname();
        if (envFromHostname != null) {
            logger.info("Environment detected from hostname: {}", envFromHostname);
            return envFromHostname;
        }
        
        // 4. 检查文件系统标识
        String envFromFileSystem = detectFromFileSystem();
        if (envFromFileSystem != null) {
            logger.info("Environment detected from file system: {}", envFromFileSystem);
            return envFromFileSystem;
        }
        
        return null;
    }
    
    /**
     * 从环境变量检测环境
     */
    private String detectFromEnvironmentVariable() {
        // 检查常见的环境变量
        List<String> envVars = Arrays.asList(
            "SPRING_PROFILES_ACTIVE",
            "ENVIRONMENT",
            "ENV",
            "DEPLOYMENT_ENV"
        );
        
        for (String varName : envVars) {
            String value = System.getenv(varName);
            if (value != null && !value.trim().isEmpty()) {
                return normalizeEnvironmentName(value.trim());
            }
        }
        
        return null;
    }
    
    /**
     * 从系统属性检测环境
     */
    private String detectFromSystemProperty() {
        String value = System.getProperty("spring.profiles.active");
        if (value != null && !value.trim().isEmpty()) {
            return normalizeEnvironmentName(value.trim());
        }
        return null;
    }
    
    /**
     * 从主机名检测环境
     */
    private String detectFromHostname() {
        try {
            String hostname = java.net.InetAddress.getLocalHost().getHostName().toLowerCase();
            
            if (hostname.contains("dev") || hostname.contains("development")) {
                return EnvironmentType.DEVELOPMENT.getProfile();
            } else if (hostname.contains("test") || hostname.contains("testing")) {
                return EnvironmentType.TESTING.getProfile();
            } else if (hostname.contains("staging") || hostname.contains("stage")) {
                return EnvironmentType.STAGING.getProfile();
            } else if (hostname.contains("prod") || hostname.contains("production")) {
                return EnvironmentType.PRODUCTION.getProfile();
            }
        } catch (Exception e) {
            logger.debug("Failed to get hostname for environment detection", e);
        }
        
        return null;
    }
    
    /**
     * 从文件系统检测环境
     */
    private String detectFromFileSystem() {
        // 检查特定的环境标识文件
        java.io.File[] envFiles = {
            new java.io.File("/etc/environment-dev"),
            new java.io.File("/etc/environment-test"),
            new java.io.File("/etc/environment-staging"),
            new java.io.File("/etc/environment-prod")
        };
        
        for (java.io.File file : envFiles) {
            if (file.exists()) {
                String fileName = file.getName();
                return fileName.substring(fileName.lastIndexOf('-') + 1);
            }
        }
        
        return null;
    }
    
    /**
     * 规范化环境名称
     */
    private String normalizeEnvironmentName(String envName) {
        String normalized = envName.toLowerCase();
        
        switch (normalized) {
            case "development":
            case "dev":
            case "local":
                return EnvironmentType.DEVELOPMENT.getProfile();
            case "testing":
            case "test":
                return EnvironmentType.TESTING.getProfile();
            case "staging":
            case "stage":
            case "pre":
            case "preprod":
                return EnvironmentType.STAGING.getProfile();
            case "production":
            case "prod":
            case "live":
                return EnvironmentType.PRODUCTION.getProfile();
            default:
                return normalized;
        }
    }
    
    /**
     * 验证环境配置的有效性
     */
    private void validateEnvironmentConfiguration() {
        if (environmentType == EnvironmentType.PRODUCTION) {
            validateProductionEnvironment();
        } else if (environmentType == EnvironmentType.DEVELOPMENT) {
            validateDevelopmentEnvironment();
        }
    }
    
    /**
     * 验证生产环境配置
     */
    private void validateProductionEnvironment() {
        // 检查生产环境必需的配置
        List<String> requiredConfigs = Arrays.asList(
            "spring.datasource.url",
            "spring.datasource.username",
            "security.jwt.secret"
        );
        
        for (String config : requiredConfigs) {
            String value = environment.getProperty(config);
            if (value == null || value.trim().isEmpty()) {
                logger.error("Missing required production configuration: {}", config);
                throw new IllegalStateException("Missing required production configuration: " + config);
            }
        }
        
        logger.info("Production environment configuration validation passed");
    }
    
    /**
     * 验证开发环境配置
     */
    private void validateDevelopmentEnvironment() {
        // 开发环境的验证相对宽松
        logger.debug("Development environment configuration validation passed");
    }
    
    /**
     * 获取当前环境
     */
    public String getCurrentEnvironment() {
        return currentEnvironment;
    }
    
    /**
     * 获取当前环境类型
     */
    public EnvironmentType getEnvironmentType() {
        return environmentType;
    }
    
    /**
     * 判断是否为开发环境
     */
    public boolean isDevelopment() {
        return environmentType == EnvironmentType.DEVELOPMENT;
    }
    
    /**
     * 判断是否为测试环境
     */
    public boolean isTesting() {
        return environmentType == EnvironmentType.TESTING;
    }
    
    /**
     * 判断是否为生产环境
     */
    public boolean isProduction() {
        return environmentType == EnvironmentType.PRODUCTION;
    }
    
    /**
     * 判断是否为预发布环境
     */
    public boolean isStaging() {
        return environmentType == EnvironmentType.STAGING;
    }
}