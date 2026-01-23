package com.company.config.security;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

/**
 * 敏感信息加密管理器
 * 负责敏感配置信息的加密存储和解密访问
 */
@Component
public class SensitiveConfigManager {
    
    private static final Logger logger = LoggerFactory.getLogger(SensitiveConfigManager.class);
    
    // 加密算法配置
    private static final String ALGORITHM = "AES";
    private static final String TRANSFORMATION = "AES/GCM/NoPadding";
    private static final int GCM_IV_LENGTH = 12;
    private static final int GCM_TAG_LENGTH = 16;
    
    // 密钥缓存
    private final Map<String, SecretKey> keyCache = new ConcurrentHashMap<>();
    
    // 加密配置缓存
    private final Map<String, String> encryptedConfigCache = new ConcurrentHashMap<>();
    
    @Value("${app.config.encryption.master-key:}")
    private String masterKeyBase64;
    
    @Value("${app.config.encryption.enabled:true}")
    private boolean encryptionEnabled;
    
    /**
     * 加密敏感配置值
     * @param plaintext 明文配置值
     * @param keyId 密钥标识
     * @return 加密后的Base64编码字符串
     */
    public String encryptConfig(String plaintext, String keyId) {
        if (!encryptionEnabled) {
            logger.warn("Encryption is disabled, returning plaintext");
            return plaintext;
        }
        
        if (plaintext == null || plaintext.isEmpty()) {
            return plaintext;
        }
        
        try {
            SecretKey secretKey = getOrCreateKey(keyId);
            
            Cipher cipher = Cipher.getInstance(TRANSFORMATION);
            
            // 生成随机IV
            byte[] iv = new byte[GCM_IV_LENGTH];
            SecureRandom.getInstanceStrong().nextBytes(iv);
            
            GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, parameterSpec);
            
            byte[] encryptedData = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));
            
            // 组合IV和加密数据
            byte[] encryptedWithIv = new byte[iv.length + encryptedData.length];
            System.arraycopy(iv, 0, encryptedWithIv, 0, iv.length);
            System.arraycopy(encryptedData, 0, encryptedWithIv, iv.length, encryptedData.length);
            
            String encrypted = Base64.getEncoder().encodeToString(encryptedWithIv);
            
            logger.debug("Successfully encrypted config value for key: {}", keyId);
            return encrypted;
            
        } catch (Exception e) {
            logger.error("Failed to encrypt config value for key: {}", keyId, e);
            throw new SecurityException("Encryption failed", e);
        }
    }
    
    /**
     * 解密敏感配置值
     * @param encryptedValue 加密的Base64编码字符串
     * @param keyId 密钥标识
     * @return 解密后的明文字符串
     */
    public String decryptConfig(String encryptedValue, String keyId) {
        if (!encryptionEnabled) {
            return encryptedValue;
        }
        
        if (encryptedValue == null || encryptedValue.isEmpty()) {
            return encryptedValue;
        }
        
        // 检查是否为加密格式
        if (!isEncryptedValue(encryptedValue)) {
            logger.debug("Value is not encrypted, returning as-is");
            return encryptedValue;
        }
        
        try {
            SecretKey secretKey = getOrCreateKey(keyId);
            
            byte[] encryptedWithIv = Base64.getDecoder().decode(encryptedValue);
            
            // 分离IV和加密数据
            byte[] iv = new byte[GCM_IV_LENGTH];
            byte[] encryptedData = new byte[encryptedWithIv.length - GCM_IV_LENGTH];
            
            System.arraycopy(encryptedWithIv, 0, iv, 0, iv.length);
            System.arraycopy(encryptedWithIv, iv.length, encryptedData, 0, encryptedData.length);
            
            Cipher cipher = Cipher.getInstance(TRANSFORMATION);
            GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv);
            cipher.init(Cipher.DECRYPT_MODE, secretKey, parameterSpec);
            
            byte[] decryptedData = cipher.doFinal(encryptedData);
            String decrypted = new String(decryptedData, StandardCharsets.UTF_8);
            
            logger.debug("Successfully decrypted config value for key: {}", keyId);
            return decrypted;
            
        } catch (Exception e) {
            logger.error("Failed to decrypt config value for key: {}", keyId, e);
            throw new SecurityException("Decryption failed", e);
        }
    }
    
    /**
     * 获取或创建密钥
     */
    private SecretKey getOrCreateKey(String keyId) {
        return keyCache.computeIfAbsent(keyId, id -> {
            try {
                if (masterKeyBase64 != null && !masterKeyBase64.isEmpty()) {
                    // 使用主密钥派生特定密钥
                    return deriveKeyFromMaster(id);
                } else {
                    // 生成新密钥
                    return generateNewKey();
                }
            } catch (Exception e) {
                logger.error("Failed to create key for id: {}", id, e);
                throw new SecurityException("Key creation failed", e);
            }
        });
    }
    
    /**
     * 从主密钥派生特定密钥
     */
    private SecretKey deriveKeyFromMaster(String keyId) {
        try {
            byte[] masterKey = Base64.getDecoder().decode(masterKeyBase64);
            
            // 使用HMAC-SHA256进行密钥派生
            javax.crypto.Mac mac = javax.crypto.Mac.getInstance("HmacSHA256");
            SecretKeySpec keySpec = new SecretKeySpec(masterKey, "HmacSHA256");
            mac.init(keySpec);
            
            byte[] derivedKey = mac.doFinal(keyId.getBytes(StandardCharsets.UTF_8));
            
            // 截取前32字节作为AES-256密钥
            byte[] aesKey = new byte[32];
            System.arraycopy(derivedKey, 0, aesKey, 0, Math.min(derivedKey.length, 32));
            
            return new SecretKeySpec(aesKey, ALGORITHM);
            
        } catch (Exception e) {
            logger.error("Failed to derive key from master for id: {}", keyId, e);
            throw new SecurityException("Key derivation failed", e);
        }
    }
    
    /**
     * 生成新的AES密钥
     */
    private SecretKey generateNewKey() throws NoSuchAlgorithmException {
        KeyGenerator keyGenerator = KeyGenerator.getInstance(ALGORITHM);
        keyGenerator.init(256); // AES-256
        return keyGenerator.generateKey();
    }
    
    /**
     * 检查值是否为加密格式
     */
    private boolean isEncryptedValue(String value) {
        try {
            // 尝试Base64解码，如果成功且长度合理，认为是加密值
            byte[] decoded = Base64.getDecoder().decode(value);
            return decoded.length > GCM_IV_LENGTH + GCM_TAG_LENGTH;
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * 生成新的主密钥
     */
    public String generateMasterKey() {
        try {
            KeyGenerator keyGenerator = KeyGenerator.getInstance(ALGORITHM);
            keyGenerator.init(256);
            SecretKey masterKey = keyGenerator.generateKey();
            
            String masterKeyBase64 = Base64.getEncoder().encodeToString(masterKey.getEncoded());
            logger.info("Generated new master key");
            
            return masterKeyBase64;
            
        } catch (NoSuchAlgorithmException e) {
            logger.error("Failed to generate master key", e);
            throw new SecurityException("Master key generation failed", e);
        }
    }
    
    /**
     * 轮换密钥
     */
    public void rotateKey(String keyId) {
        keyCache.remove(keyId);
        logger.info("Rotated key for id: {}", keyId);
    }
    
    /**
     * 清除所有密钥缓存
     */
    public void clearKeyCache() {
        keyCache.clear();
        logger.info("Cleared all key cache");
    }
    
    /**
     * 获取密钥统计信息
     */
    public Map<String, Object> getKeyStatistics() {
        Map<String, Object> stats = new ConcurrentHashMap<>();
        stats.put("totalKeys", keyCache.size());
        stats.put("encryptionEnabled", encryptionEnabled);
        stats.put("algorithm", ALGORITHM);
        stats.put("transformation", TRANSFORMATION);
        return stats;
    }
    
    /**
     * 验证密钥完整性
     */
    public boolean validateKeyIntegrity(String keyId) {
        try {
            SecretKey key = keyCache.get(keyId);
            if (key == null) {
                return false;
            }
            
            // 测试加密解密
            String testData = "test-data-" + System.currentTimeMillis();
            String encrypted = encryptConfig(testData, keyId);
            String decrypted = decryptConfig(encrypted, keyId);
            
            return testData.equals(decrypted);
            
        } catch (Exception e) {
            logger.error("Key integrity validation failed for id: {}", keyId, e);
            return false;
        }
    }
}