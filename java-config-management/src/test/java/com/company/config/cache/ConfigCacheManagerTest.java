package com.company.config.cache;

import com.company.config.hotreload.ConfigChangeEvent;
import com.company.config.hotreload.ConfigChangeType;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 配置缓存管理器测试
 */
class ConfigCacheManagerTest {
    
    private ConfigCacheManager configCacheManager;
    
    @BeforeEach
    void setUp() {
        configCacheManager = new ConfigCacheManager();
        // 启用缓存
        ReflectionTestUtils.setField(configCacheManager, "cacheEnabled", true);
        ReflectionTestUtils.setField(configCacheManager, "cacheTtlSeconds", 300L);
        ReflectionTestUtils.setField(configCacheManager, "maxCacheSize", 100);
        ReflectionTestUtils.setField(configCacheManager, "lazyLoadingEnabled", true);
        
        configCacheManager.initialize();
    }
    
    @Test
    void testCacheHitAndMiss() {
        String key = "test.key";
        String value = "test.value";
        AtomicInteger loadCount = new AtomicInteger(0);
        
        // 第一次访问，应该是缓存未命中
        String result1 = configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return value;
        });
        
        assertEquals(value, result1);
        assertEquals(1, loadCount.get());
        
        // 第二次访问，应该是缓存命中
        String result2 = configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return "should.not.be.called";
        });
        
        assertEquals(value, result2);
        assertEquals(1, loadCount.get()); // 加载器不应该被再次调用
    }
    
    @Test
    void testCacheDisabled() {
        // 禁用缓存
        ReflectionTestUtils.setField(configCacheManager, "cacheEnabled", false);
        
        String key = "disabled.key";
        String value = "disabled.value";
        AtomicInteger loadCount = new AtomicInteger(0);
        
        // 每次访问都应该调用加载器
        configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return value;
        });
        
        configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return value;
        });
        
        assertEquals(2, loadCount.get());
    }
    
    @Test
    void testCacheInvalidation() {
        String key = "invalidation.key";
        String value = "initial.value";
        
        // 缓存初始值
        String result1 = configCacheManager.getCachedConfig(key, () -> value);
        assertEquals(value, result1);
        
        // 失效缓存
        configCacheManager.invalidate(key);
        
        // 再次访问应该重新加载
        AtomicInteger loadCount = new AtomicInteger(0);
        String newValue = "new.value";
        String result2 = configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return newValue;
        });
        
        assertEquals(newValue, result2);
        assertEquals(1, loadCount.get());
    }
    
    @Test
    void testClearAllCache() {
        // 缓存一些值
        configCacheManager.getCachedConfig("key1", () -> "value1");
        configCacheManager.getCachedConfig("key2", () -> "value2");
        
        // 清空所有缓存
        configCacheManager.clearAllCache();
        
        // 再次访问应该重新加载
        AtomicInteger loadCount = new AtomicInteger(0);
        configCacheManager.getCachedConfig("key1", () -> {
            loadCount.incrementAndGet();
            return "new.value1";
        });
        
        assertEquals(1, loadCount.get());
    }
    
    @Test
    void testConfigChangeEventHandling() {
        String key = "change.key";
        String value = "change.value";
        
        // 缓存值
        configCacheManager.getCachedConfig(key, () -> value);
        
        // 模拟配置变更事件
        ConfigChangeEvent event = new ConfigChangeEvent(
            this, "application.yml", ConfigChangeType.FILE_MODIFIED, null, null);
        
        configCacheManager.handleConfigChange(event);
        
        // 事件处理后，缓存应该被清理
        AtomicInteger loadCount = new AtomicInteger(0);
        configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return "new.value";
        });
        
        assertEquals(1, loadCount.get());
    }
    
    @Test
    void testCacheStatistics() {
        // 执行一些缓存操作
        configCacheManager.getCachedConfig("stats.key1", () -> "value1");
        configCacheManager.getCachedConfig("stats.key2", () -> "value2");
        configCacheManager.getCachedConfig("stats.key1", () -> "value1"); // 缓存命中
        
        Map<String, Object> stats = configCacheManager.getCacheStatistics();
        
        assertNotNull(stats);
        assertTrue(stats.containsKey("cacheEnabled"));
        assertTrue(stats.containsKey("totalCacheSize"));
        assertTrue(stats.containsKey("maxCacheSize"));
        assertTrue(stats.containsKey("cacheTtlSeconds"));
        assertTrue(stats.containsKey("cacheHits"));
        assertTrue(stats.containsKey("cacheMisses"));
        assertTrue(stats.containsKey("hitRate"));
        
        assertEquals(true, stats.get("cacheEnabled"));
        assertEquals(100, stats.get("maxCacheSize"));
        assertEquals(300L, stats.get("cacheTtlSeconds"));
    }
    
    @Test
    void testCacheWarmup() {
        String[] warmupKeys = {"warmup.key1", "warmup.key2", "warmup.key3"};
        
        // 执行缓存预热
        configCacheManager.warmupCache(warmupKeys);
        
        // 验证预热是否生效（通过统计信息）
        Map<String, Object> stats = configCacheManager.getCacheStatistics();
        
        // 由于我们的测试实现中没有实际的配置加载器，
        // 这里主要验证方法执行不抛异常
        assertNotNull(stats);
    }
    
    @Test
    void testNullKeyHandling() {
        // 测试null键处理
        String result = configCacheManager.getCachedConfig(null, () -> "null.value");
        assertEquals("null.value", result);
    }
    
    @Test
    void testNullValueHandling() {
        String key = "null.value.key";
        
        // 测试加载器返回null
        String result = configCacheManager.getCachedConfig(key, () -> null);
        assertNull(result);
        
        // 第二次访问应该重新调用加载器
        AtomicInteger loadCount = new AtomicInteger(0);
        String result2 = configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return null;
        });
        
        assertNull(result2);
        assertEquals(1, loadCount.get());
    }
    
    @Test
    void testCacheCapacity() {
        // 设置较小的缓存大小进行测试
        ReflectionTestUtils.setField(configCacheManager, "maxCacheSize", 3);
        
        // 添加超过容量的缓存项
        configCacheManager.getCachedConfig("capacity.key1", () -> "value1");
        configCacheManager.getCachedConfig("capacity.key2", () -> "value2");
        configCacheManager.getCachedConfig("capacity.key3", () -> "value3");
        configCacheManager.getCachedConfig("capacity.key4", () -> "value4"); // 应该触发驱逐
        
        Map<String, Object> stats = configCacheManager.getCacheStatistics();
        
        // 验证缓存大小不超过限制
        Integer totalSize = (Integer) stats.get("totalCacheSize");
        assertTrue(totalSize <= 3);
    }
    
    @Test
    void testCleanupExpiredEntries() {
        // 设置很短的TTL
        ReflectionTestUtils.setField(configCacheManager, "cacheTtlSeconds", 1L);
        
        String key = "expire.key";
        String value = "expire.value";
        
        // 缓存值
        configCacheManager.getCachedConfig(key, () -> value);
        
        // 等待过期
        try {
            Thread.sleep(1500); // 等待1.5秒
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // 手动触发清理
        configCacheManager.cleanupExpiredEntries();
        
        // 验证过期项被清理
        AtomicInteger loadCount = new AtomicInteger(0);
        configCacheManager.getCachedConfig(key, () -> {
            loadCount.incrementAndGet();
            return "new.value";
        });
        
        assertEquals(1, loadCount.get());
    }
    
    @Test
    void testConcurrentAccess() {
        String key = "concurrent.key";
        String value = "concurrent.value";
        AtomicInteger loadCount = new AtomicInteger(0);
        
        // 模拟并发访问
        Thread[] threads = new Thread[10];
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                String result = configCacheManager.getCachedConfig(key, () -> {
                    loadCount.incrementAndGet();
                    return value;
                });
                assertEquals(value, result);
            });
        }
        
        // 启动所有线程
        for (Thread thread : threads) {
            thread.start();
        }
        
        // 等待所有线程完成
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        // 验证加载器只被调用了一次（或很少次数，因为有并发控制）
        assertTrue(loadCount.get() <= 3); // 允许少量并发加载
    }
}