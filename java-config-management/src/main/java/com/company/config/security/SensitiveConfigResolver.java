package com.company.config.security;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.PostConstruct;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 敏感配置属性解析器
 * 负责识别和处理敏感配置属性
 */
@Component
public class SensitiveConfigResolver {
    
    private static final Logger logger = LoggerFactory.getLogger(SensitiveConfigResolver.class);
    
    @Autowired
    private Environment environment;
    
    @Autowired
    private SensitiveConfigManager sensitiveConfigManager;
    
    // 敏感配置键的模式
    private static final List<String> SENSITIVE_PATTERNS = Arrays.asList(
        "password", "secret", "key", "token", "credential", 
        "auth", "private", "secure", "encrypted"
    );
    
    // 敏感配置缓存
    private final Map<String, String> sensitiveConfigCache = new ConcurrentHashMap<>();
    
    // 加密前缀标识
    private static final String ENCRYPTED_PREFIX = "{encrypted}";
    
    @PostConstruct
    public void initializeSensitiveConfigs() {
        logger.info("Initializing sensitive configuration resolver");
        
        // 扫描并处理敏感配置
        scanAndProcessSensitiveConfigs();
    }
    
    /**
     * 获取敏感配置值（自动解密）
     * @param key 配置键
     * @return 解密后的配置值
     */
    public String getSensitiveConfig(String key) {
        // 先检查缓存
        String cachedValue = sensitiveConfigCache.get(key);
        if (cachedValue != null) {
            return cachedValue;
        }
        
        String rawValue = environment.getProperty(key);
        if (rawValue == null) {
            return null;
        }
        
        String resolvedValue;
        if (isEncryptedValue(rawValue)) {
            // 解密加密值
            String encryptedValue = rawValue.substring(ENCRYPTED_PREFIX.length());
            resolvedValue = sensitiveConfigManager.decryptConfig(encryptedValue, key);
        } else {
            // 非加密值直接返回
            resolvedValue = rawValue;
        }
        
        // 缓存解密后的值
        if (isSensitiveKey(key)) {
            sensitiveConfigCache.put(key, resolvedValue);
        }
        
        return resolvedValue;
    }
    
    /**
     * 设置敏感配置值（自动加密）
     * @param key 配置键
     * @param value 配置值
     * @return 加密后的配置值
     */
    public String setSensitiveConfig(String key, String value) {
        if (value == null || value.isEmpty()) {
            return value;
        }
        
        String encryptedValue = sensitiveConfigManager.encryptConfig(value, key);
        String storedValue = ENCRYPTED_PREFIX + encryptedValue;
        
        // 更新缓存
        sensitiveConfigCache.put(key, value);
        
        logger.info("Set sensitive config for key: {}", key);
        return storedValue;
    }
    
    /**
     * 判断配置键是否为敏感信息
     * @param key 配置键
     * @return 是否敏感
     */
    public boolean isSensitiveKey(String key) {
        if (key == null) {
            return false;
        }
        
        String lowerKey = key.toLowerCase();
        return SENSITIVE_PATTERNS.stream()
            .anyMatch(pattern -> lowerKey.contains(pattern));
    }
    
    /**
     * 判断配置值是否为加密格式
     * @param value 配置值
     * @return 是否加密
     */
    public boolean isEncryptedValue(String value) {
        return value != null && value.startsWith(ENCRYPTED_PREFIX);
    }
    
    /**
     * 扫描并处理敏感配置
     */
    private void scanAndProcessSensitiveConfigs() {
        try {
            // 获取所有配置属性
            org.springframework.core.env.MutablePropertySources propertySources = 
                ((org.springframework.core.env.AbstractEnvironment) environment).getPropertySources();
            
            int sensitiveCount = 0;
            int encryptedCount = 0;
            
            for (org.springframework.core.env.PropertySource<?> propertySource : propertySources) {
                if (propertySource.getSource() instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> source = (Map<String, Object>) propertySource.getSource();
                    
                    for (Map.Entry<String, Object> entry : source.entrySet()) {
                        String key = entry.getKey();
                        String value = String.valueOf(entry.getValue());
                        
                        if (isSensitiveKey(key)) {
                            sensitiveCount++;
                            
                            if (isEncryptedValue(value)) {
                                encryptedCount++;
                                logger.debug("Found encrypted sensitive config: {}", key);
                            } else {
                                logger.debug("Found unencrypted sensitive config: {}", key);
                            }
                        }
                    }
                }
            }
            
            logger.info("Scanned sensitive configs - Total: {}, Encrypted: {}", 
                sensitiveCount, encryptedCount);
            
        } catch (Exception e) {
            logger.error("Failed to scan sensitive configurations", e);
        }
    }
    
    /**
     * 加密现有的敏感配置
     * @param key 配置键
     * @return 是否成功加密
     */
    public boolean encryptExistingConfig(String key) {
        try {
            String currentValue = environment.getProperty(key);
            if (currentValue == null || isEncryptedValue(currentValue)) {
                return false;
            }
            
            if (isSensitiveKey(key)) {
                String encryptedValue = setSensitiveConfig(key, currentValue);
                logger.info("Encrypted existing config for key: {}", key);
                return true;
            }
            
            return false;
        } catch (Exception e) {
            logger.error("Failed to encrypt existing config for key: {}", key, e);
            return false;
        }
    }
    
    /**
     * 批量加密敏感配置
     * @return 加密成功的配置数量
     */
    public int encryptAllSensitiveConfigs() {
        int encryptedCount = 0;
        
        try {
            org.springframework.core.env.MutablePropertySources propertySources = 
                ((org.springframework.core.env.AbstractEnvironment) environment).getPropertySources();
            
            for (org.springframework.core.env.PropertySource<?> propertySource : propertySources) {
                if (propertySource.getSource() instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> source = (Map<String, Object>) propertySource.getSource();
                    
                    for (String key : source.keySet()) {
                        if (encryptExistingConfig(key)) {
                            encryptedCount++;
                        }
                    }
                }
            }
            
            logger.info("Batch encryption completed, encrypted {} configs", encryptedCount);
            
        } catch (Exception e) {
            logger.error("Failed to batch encrypt sensitive configurations", e);
        }
        
        return encryptedCount;
    }
    
    /**
     * 验证敏感配置的完整性
     * @return 验证结果
     */
    public Map<String, Object> validateSensitiveConfigs() {
        Map<String, Object> result = new ConcurrentHashMap<>();
        int totalChecked = 0;
        int validCount = 0;
        int invalidCount = 0;
        
        try {
            for (String key : sensitiveConfigCache.keySet()) {
                totalChecked++;
                
                if (sensitiveConfigManager.validateKeyIntegrity(key)) {
                    validCount++;
                } else {
                    invalidCount++;
                    logger.warn("Integrity validation failed for sensitive config: {}", key);
                }
            }
            
            result.put("totalChecked", totalChecked);
            result.put("validCount", validCount);
            result.put("invalidCount", invalidCount);
            result.put("success", invalidCount == 0);
            
            logger.info("Sensitive config validation completed - Valid: {}, Invalid: {}", 
                validCount, invalidCount);
            
        } catch (Exception e) {
            logger.error("Failed to validate sensitive configurations", e);
            result.put("error", e.getMessage());
            result.put("success", false);
        }
        
        return result;
    }
    
    /**
     * 清除敏感配置缓存
     */
    public void clearSensitiveConfigCache() {
        sensitiveConfigCache.clear();
        logger.info("Cleared sensitive configuration cache");
    }
    
    /**
     * 获取敏感配置统计信息
     */
    public Map<String, Object> getSensitiveConfigStatistics() {
        Map<String, Object> stats = new ConcurrentHashMap<>();
        stats.put("cachedConfigs", sensitiveConfigCache.size());
        stats.put("sensitivePatterns", SENSITIVE_PATTERNS);
        stats.put("encryptedPrefix", ENCRYPTED_PREFIX);
        
        // 统计敏感配置类型
        Map<String, Integer> typeStats = new ConcurrentHashMap<>();
        for (String key : sensitiveConfigCache.keySet()) {
            for (String pattern : SENSITIVE_PATTERNS) {
                if (key.toLowerCase().contains(pattern)) {
                    typeStats.merge(pattern, 1, Integer::sum);
                }
            }
        }
        stats.put("typeStatistics", typeStats);
        
        return stats;
    }
    
    /**
     * 轮换敏感配置的加密密钥
     * @param key 配置键
     * @return 是否成功轮换
     */
    public boolean rotateSensitiveConfigKey(String key) {
        try {
            if (!isSensitiveKey(key) || !sensitiveConfigCache.containsKey(key)) {
                return false;
            }
            
            // 获取原始值
            String originalValue = sensitiveConfigCache.get(key);
            
            // 轮换密钥
            sensitiveConfigManager.rotateKey(key);
            
            // 重新加密
            String newEncryptedValue = setSensitiveConfig(key, originalValue);
            
            logger.info("Rotated encryption key for sensitive config: {}", key);
            return true;
            
        } catch (Exception e) {
            logger.error("Failed to rotate key for sensitive config: {}", key, e);
            return false;
        }
    }
}