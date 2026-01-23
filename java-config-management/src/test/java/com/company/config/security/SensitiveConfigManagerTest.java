package com.company.config.security;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 敏感配置管理器测试
 */
class SensitiveConfigManagerTest {
    
    private SensitiveConfigManager sensitiveConfigManager;
    
    @BeforeEach
    void setUp() {
        sensitiveConfigManager = new SensitiveConfigManager();
        // 启用加密
        ReflectionTestUtils.setField(sensitiveConfigManager, "encryptionEnabled", true);
    }
    
    @Test
    void testEncryptAndDecryptConfig() {
        String plaintext = "sensitive-password-123";
        String keyId = "test-key";
        
        // 加密
        String encrypted = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        
        assertNotNull(encrypted);
        assertNotEquals(plaintext, encrypted);
        
        // 解密
        String decrypted = sensitiveConfigManager.decryptConfig(encrypted, keyId);
        
        assertEquals(plaintext, decrypted);
    }
    
    @Test
    void testEncryptionDisabled() {
        // 禁用加密
        ReflectionTestUtils.setField(sensitiveConfigManager, "encryptionEnabled", false);
        
        String plaintext = "test-value";
        String keyId = "test-key";
        
        // 加密时应该返回原值
        String encrypted = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        assertEquals(plaintext, encrypted);
        
        // 解密时也应该返回原值
        String decrypted = sensitiveConfigManager.decryptConfig(encrypted, keyId);
        assertEquals(plaintext, decrypted);
    }
    
    @Test
    void testNullValueHandling() {
        String keyId = "test-key";
        
        // 测试null值
        String encrypted = sensitiveConfigManager.encryptConfig(null, keyId);
        assertNull(encrypted);
        
        String decrypted = sensitiveConfigManager.decryptConfig(null, keyId);
        assertNull(decrypted);
    }
    
    @Test
    void testEmptyValueHandling() {
        String keyId = "test-key";
        
        // 测试空字符串
        String encrypted = sensitiveConfigManager.encryptConfig("", keyId);
        assertEquals("", encrypted);
        
        String decrypted = sensitiveConfigManager.decryptConfig("", keyId);
        assertEquals("", decrypted);
    }
    
    @Test
    void testDifferentKeysProduceDifferentResults() {
        String plaintext = "same-value";
        String keyId1 = "key1";
        String keyId2 = "key2";
        
        String encrypted1 = sensitiveConfigManager.encryptConfig(plaintext, keyId1);
        String encrypted2 = sensitiveConfigManager.encryptConfig(plaintext, keyId2);
        
        // 不同的密钥应该产生不同的加密结果
        assertNotEquals(encrypted1, encrypted2);
        
        // 但解密后应该得到相同的原文
        String decrypted1 = sensitiveConfigManager.decryptConfig(encrypted1, keyId1);
        String decrypted2 = sensitiveConfigManager.decryptConfig(encrypted2, keyId2);
        
        assertEquals(plaintext, decrypted1);
        assertEquals(plaintext, decrypted2);
    }
    
    @Test
    void testEncryptionConsistency() {
        String plaintext = "consistent-test";
        String keyId = "consistency-key";
        
        // 多次加密同一个值应该产生不同的结果（因为使用了随机IV）
        String encrypted1 = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        String encrypted2 = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        
        assertNotEquals(encrypted1, encrypted2);
        
        // 但解密应该都得到相同的原文
        String decrypted1 = sensitiveConfigManager.decryptConfig(encrypted1, keyId);
        String decrypted2 = sensitiveConfigManager.decryptConfig(encrypted2, keyId);
        
        assertEquals(plaintext, decrypted1);
        assertEquals(plaintext, decrypted2);
    }
    
    @Test
    void testGenerateMasterKey() {
        String masterKey = sensitiveConfigManager.generateMasterKey();
        
        assertNotNull(masterKey);
        assertFalse(masterKey.isEmpty());
        
        // Base64编码的密钥长度应该合理
        assertTrue(masterKey.length() > 40);
    }
    
    @Test
    void testKeyRotation() {
        String keyId = "rotation-test";
        String plaintext = "test-value";
        
        // 加密一个值
        String encrypted1 = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        
        // 轮换密钥
        sensitiveConfigManager.rotateKey(keyId);
        
        // 再次加密应该使用新密钥
        String encrypted2 = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        
        // 新加密的值应该不同
        assertNotEquals(encrypted1, encrypted2);
    }
    
    @Test
    void testClearKeyCache() {
        String keyId = "cache-test";
        String plaintext = "test-value";
        
        // 加密一个值（这会创建密钥缓存）
        sensitiveConfigManager.encryptConfig(plaintext, keyId);
        
        // 清除密钥缓存
        assertDoesNotThrow(() -> sensitiveConfigManager.clearKeyCache());
    }
    
    @Test
    void testGetKeyStatistics() {
        // 执行一些加密操作
        sensitiveConfigManager.encryptConfig("value1", "key1");
        sensitiveConfigManager.encryptConfig("value2", "key2");
        
        var stats = sensitiveConfigManager.getKeyStatistics();
        
        assertNotNull(stats);
        assertTrue(stats.containsKey("totalKeys"));
        assertTrue(stats.containsKey("encryptionEnabled"));
        assertTrue(stats.containsKey("algorithm"));
        assertTrue(stats.containsKey("transformation"));
        
        assertEquals(true, stats.get("encryptionEnabled"));
        assertEquals("AES", stats.get("algorithm"));
    }
    
    @Test
    void testValidateKeyIntegrity() {
        String keyId = "integrity-test";
        String plaintext = "integrity-value";
        
        // 先加密一个值以创建密钥
        sensitiveConfigManager.encryptConfig(plaintext, keyId);
        
        // 验证密钥完整性
        boolean isValid = sensitiveConfigManager.validateKeyIntegrity(keyId);
        assertTrue(isValid);
        
        // 验证不存在的密钥
        boolean isInvalidValid = sensitiveConfigManager.validateKeyIntegrity("nonexistent-key");
        assertFalse(isInvalidValid);
    }
    
    @Test
    void testLargeValueEncryption() {
        // 测试大文本加密
        StringBuilder largeText = new StringBuilder();
        for (int i = 0; i < 1000; i++) {
            largeText.append("This is a large text for encryption testing. ");
        }
        
        String plaintext = largeText.toString();
        String keyId = "large-text-key";
        
        String encrypted = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        String decrypted = sensitiveConfigManager.decryptConfig(encrypted, keyId);
        
        assertEquals(plaintext, decrypted);
    }
    
    @Test
    void testSpecialCharactersEncryption() {
        // 测试特殊字符加密
        String plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~测试中文字符";
        String keyId = "special-chars-key";
        
        String encrypted = sensitiveConfigManager.encryptConfig(plaintext, keyId);
        String decrypted = sensitiveConfigManager.decryptConfig(encrypted, keyId);
        
        assertEquals(plaintext, decrypted);
    }
}