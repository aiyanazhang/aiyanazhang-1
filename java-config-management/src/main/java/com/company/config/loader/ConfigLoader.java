package com.company.config.loader;

import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 配置加载器 - 负责从多个源加载配置
 * 实现配置优先级策略：命令行参数 > 环境变量 > 外部配置文件 > 内部配置文件 > 默认值
 */
@Component
public class ConfigLoader {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigLoader.class);
    
    @Autowired
    private Environment environment;
    
    @Autowired
    private ApplicationContext applicationContext;
    
    @Autowired
    private ResourceLoader resourceLoader;
    
    // 配置缓存
    private final Map<String, Object> configCache = new ConcurrentHashMap<>();
    
    // 配置源优先级定义
    private final List<ConfigSource> configSources = Arrays.asList(
        ConfigSource.COMMAND_LINE,
        ConfigSource.SYSTEM_ENV,
        ConfigSource.EXTERNAL_FILE,
        ConfigSource.INTERNAL_FILE,
        ConfigSource.DEFAULT_VALUE
    );
    
    /**
     * 根据键获取配置值，按优先级顺序查找
     * @param key 配置键
     * @return 配置值
     */
    public String getProperty(String key) {
        return getProperty(key, null);
    }
    
    /**
     * 根据键获取配置值，提供默认值
     * @param key 配置键
     * @param defaultValue 默认值
     * @return 配置值
     */
    public String getProperty(String key, String defaultValue) {
        // 首先检查缓存
        Object cachedValue = configCache.get(key);
        if (cachedValue != null) {
            return cachedValue.toString();
        }
        
        // 按优先级顺序查找配置
        for (ConfigSource source : configSources) {
            String value = getPropertyFromSource(key, source);
            if (StringUtils.hasText(value)) {
                // 缓存配置值
                configCache.put(key, value);
                logger.debug("Found property '{}' from source '{}' with value '{}'", 
                    key, source, value);
                return value;
            }
        }
        
        // 如果没有找到，返回默认值
        if (defaultValue != null) {
            configCache.put(key, defaultValue);
        }
        
        return defaultValue;
    }
    
    /**
     * 从指定配置源获取配置值
     * @param key 配置键
     * @param source 配置源
     * @return 配置值
     */
    private String getPropertyFromSource(String key, ConfigSource source) {
        switch (source) {
            case COMMAND_LINE:
                return getCommandLineProperty(key);
            case SYSTEM_ENV:
                return getEnvironmentVariable(key);
            case EXTERNAL_FILE:
                return getExternalFileProperty(key);
            case INTERNAL_FILE:
                return getInternalFileProperty(key);
            case DEFAULT_VALUE:
                return getDefaultProperty(key);
            default:
                return null;
        }
    }
    
    /**
     * 获取命令行参数
     */
    private String getCommandLineProperty(String key) {
        // Spring Boot会自动处理命令行参数，通过Environment获取
        return environment.getProperty(key);
    }
    
    /**
     * 获取环境变量，支持多种命名格式
     */
    private String getEnvironmentVariable(String key) {
        // 尝试原始键名
        String value = System.getenv(key);
        if (value != null) {
            return value;
        }
        
        // 尝试大写格式
        String upperKey = key.toUpperCase().replace('.', '_').replace('-', '_');
        value = System.getenv(upperKey);
        if (value != null) {
            return value;
        }
        
        // 通过Spring Environment获取（支持relaxed binding）
        return environment.getProperty(key);
    }
    
    /**
     * 从外部配置文件获取属性
     */
    private String getExternalFileProperty(String key) {
        try {
            Resource resource = resourceLoader.getResource("file:config/application.yml");
            if (resource.exists()) {
                // 这里可以集成YAML解析器，简化示例只返回environment的值
                return environment.getProperty(key);
            }
        } catch (Exception e) {
            logger.debug("Failed to load external configuration file", e);
        }
        return null;
    }
    
    /**
     * 从内部配置文件获取属性
     */
    private String getInternalFileProperty(String key) {
        // Spring Boot会自动加载classpath中的application.yml等文件
        return environment.getProperty(key);
    }
    
    /**
     * 获取默认配置值
     */
    private String getDefaultProperty(String key) {
        // 在实际实现中，这里可以从配置元数据或默认配置映射中获取
        Map<String, String> defaults = getDefaultConfiguration();
        return defaults.get(key);
    }
    
    /**
     * 获取默认配置映射
     */
    private Map<String, String> getDefaultConfiguration() {
        Map<String, String> defaults = new HashMap<>();
        defaults.put("server.port", "8080");
        defaults.put("server.servlet.context-path", "/");
        defaults.put("server.compression.enabled", "true");
        defaults.put("logging.level.root", "INFO");
        defaults.put("logging.level.com.company", "DEBUG");
        defaults.put("spring.jpa.hibernate.ddl-auto", "create-drop");
        defaults.put("security.jwt.expiration", "86400");
        defaults.put("security.rate-limit.requests-per-minute", "100");
        return defaults;
    }
    
    /**
     * 清除配置缓存
     */
    public void clearCache() {
        configCache.clear();
        logger.info("Configuration cache cleared");
    }
    
    /**
     * 重新加载配置
     */
    public void reloadConfiguration() {
        clearCache();
        logger.info("Configuration reloaded");
    }
    
    /**
     * 获取所有配置键
     */
    public Set<String> getAllPropertyNames() {
        Set<String> allKeys = new HashSet<>();
        
        // 从Environment获取所有属性源的键
        environment.getPropertySources().forEach(propertySource -> {
            if (propertySource.getSource() instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> source = (Map<String, Object>) propertySource.getSource();
                allKeys.addAll(source.keySet());
            }
        });
        
        return allKeys;
    }
    
    /**
     * 配置源枚举
     */
    public enum ConfigSource {
        COMMAND_LINE("命令行参数"),
        SYSTEM_ENV("系统环境变量"),
        EXTERNAL_FILE("外部配置文件"),
        INTERNAL_FILE("内部配置文件"),
        DEFAULT_VALUE("默认值");
        
        private final String description;
        
        ConfigSource(String description) {
            this.description = description;
        }
        
        public String getDescription() {
            return description;
        }
    }
}