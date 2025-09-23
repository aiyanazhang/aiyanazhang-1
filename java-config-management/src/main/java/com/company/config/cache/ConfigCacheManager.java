package com.company.config.cache;

import com.company.config.hotreload.ConfigChangeEvent;
import com.company.config.monitor.ConfigurationMonitor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.scheduling.annotation.Scheduled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.Map;
import java.util.Set;
import java.util.LinkedHashSet;

/**
 * 配置缓存管理器
 * 提供多层次配置缓存，提升配置访问性能
 */
@Component
public class ConfigCacheManager {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigCacheManager.class);
    
    @Autowired(required = false)
    private ConfigurationMonitor configurationMonitor;
    
    @Value("${app.config.cache.enabled:true}")
    private boolean cacheEnabled;
    
    @Value("${app.config.cache.ttl:300}")
    private long cacheTtlSeconds;
    
    @Value("${app.config.cache.max-size:1000}")
    private int maxCacheSize;
    
    @Value("${app.config.cache.lazy-loading:true}")
    private boolean lazyLoadingEnabled;
    
    @Value("${app.config.cache.preload-keys:}")
    private String[] preloadKeys;
    
    // L1缓存：频繁访问的配置
    private final Map<String, CacheEntry> l1Cache = new ConcurrentHashMap<>();
    
    // L2缓存：一般配置
    private final Map<String, CacheEntry> l2Cache = new ConcurrentHashMap<>();
    
    // 访问频率统计
    private final Map<String, AtomicLong> accessCounts = new ConcurrentHashMap<>();
    
    // 缓存统计
    private final AtomicLong cacheHits = new AtomicLong(0);
    private final AtomicLong cacheMisses = new AtomicLong(0);
    private final AtomicLong evictions = new AtomicLong(0);
    
    // 读写锁
    private final ReadWriteLock cacheLock = new ReentrantReadWriteLock();
    
    // 缓存清理任务
    private ScheduledExecutorService cleanupExecutor;
    
    // L1缓存访问阈值
    private static final long L1_ACCESS_THRESHOLD = 10;
    
    // 缓存分层大小比例
    private static final double L1_SIZE_RATIO = 0.2; // L1缓存占总缓存大小的20%
    
    @PostConstruct
    public void initialize() {
        if (!cacheEnabled) {
            logger.info("Configuration cache is disabled");
            return;
        }
        
        logger.info("Initializing configuration cache manager");
        
        // 启动缓存清理任务
        startCleanupTask();
        
        // 预加载配置
        preloadConfigurations();
        
        logger.info("Configuration cache manager initialized - TTL: {}s, MaxSize: {}", 
            cacheTtlSeconds, maxCacheSize);
    }
    
    /**
     * 启动缓存清理任务
     */
    private void startCleanupTask() {
        cleanupExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread thread = new Thread(r, "config-cache-cleanup");
            thread.setDaemon(true);
            return thread;
        });
        
        // 每分钟执行一次清理任务
        cleanupExecutor.scheduleWithFixedDelay(this::cleanupExpiredEntries, 
            60, 60, TimeUnit.SECONDS);
    }
    
    /**
     * 预加载配置
     */
    private void preloadConfigurations() {
        if (preloadKeys != null && preloadKeys.length > 0) {
            for (String key : preloadKeys) {
                if (key != null && !key.trim().isEmpty()) {
                    // 预加载时不记录为缓存未命中
                    try {
                        String value = loadConfigValue(key);
                        if (value != null) {
                            putInCache(key, value, CacheLevel.L2);
                            logger.debug("Preloaded configuration: {}", key);
                        }
                    } catch (Exception e) {
                        logger.warn("Failed to preload configuration: {}", key, e);
                    }
                }
            }
            
            logger.info("Preloaded {} configuration keys", preloadKeys.length);
        }
    }
    
    /**
     * 获取配置值（带缓存）
     * @param key 配置键
     * @param loader 配置加载器函数
     * @return 配置值
     */
    public String getCachedConfig(String key, java.util.function.Supplier<String> loader) {
        if (!cacheEnabled) {
            return loader.get();
        }
        
        // 记录访问
        recordAccess(key);
        
        cacheLock.readLock().lock();
        try {
            // 先检查L1缓存
            CacheEntry entry = l1Cache.get(key);
            if (entry != null && !entry.isExpired()) {
                cacheHits.incrementAndGet();
                recordAccess(key);
                return entry.getValue();
            }
            
            // 再检查L2缓存
            entry = l2Cache.get(key);
            if (entry != null && !entry.isExpired()) {
                cacheHits.incrementAndGet();
                recordAccess(key);
                
                // 如果访问频率高，提升到L1缓存
                if (shouldPromoteToL1(key)) {
                    promoteToL1Cache(key, entry.getValue());
                }
                
                return entry.getValue();
            }
        } finally {
            cacheLock.readLock().unlock();
        }
        
        // 缓存未命中，加载数据
        cacheMisses.incrementAndGet();
        
        long startTime = System.currentTimeMillis();
        String value = loader.get();
        long loadTime = System.currentTimeMillis() - startTime;
        
        // 记录加载时间
        if (configurationMonitor != null) {
            configurationMonitor.recordConfigLoadTime(loadTime);
        }
        
        // 放入缓存
        if (value != null) {
            CacheLevel level = determineInitialCacheLevel(key);
            putInCache(key, value, level);
        }
        
        return value;
    }
    
    /**
     * 记录配置访问
     */
    private void recordAccess(String key) {
        accessCounts.computeIfAbsent(key, k -> new AtomicLong(0)).incrementAndGet();
        
        if (configurationMonitor != null) {
            configurationMonitor.recordConfigAccess(key);
        }
    }
    
    /**
     * 判断是否应该提升到L1缓存
     */
    private boolean shouldPromoteToL1(String key) {
        AtomicLong count = accessCounts.get(key);
        return count != null && count.get() >= L1_ACCESS_THRESHOLD;
    }
    
    /**
     * 提升到L1缓存
     */
    private void promoteToL1Cache(String key, String value) {
        cacheLock.writeLock().lock();
        try {
            // 从L2缓存移除
            l2Cache.remove(key);
            
            // 添加到L1缓存
            putInL1Cache(key, value);
            
            logger.debug("Promoted config to L1 cache: {}", key);
        } finally {
            cacheLock.writeLock().unlock();
        }
    }
    
    /**
     * 确定初始缓存级别
     */
    private CacheLevel determineInitialCacheLevel(String key) {
        // 敏感配置或系统配置优先放入L1缓存
        if (isCriticalConfig(key)) {
            return CacheLevel.L1;
        }
        return CacheLevel.L2;
    }
    
    /**
     * 判断是否为关键配置
     */
    private boolean isCriticalConfig(String key) {
        return key.startsWith("server.") || 
               key.startsWith("spring.datasource.") ||
               key.startsWith("security.") ||
               key.contains("password") ||
               key.contains("secret") ||
               key.contains("key");
    }
    
    /**
     * 放入缓存
     */
    private void putInCache(String key, String value, CacheLevel level) {
        cacheLock.writeLock().lock();
        try {
            if (level == CacheLevel.L1) {
                putInL1Cache(key, value);
            } else {
                putInL2Cache(key, value);
            }
        } finally {
            cacheLock.writeLock().unlock();
        }
    }
    
    /**
     * 放入L1缓存
     */
    private void putInL1Cache(String key, String value) {
        int l1MaxSize = (int) (maxCacheSize * L1_SIZE_RATIO);
        
        // 如果L1缓存已满，移除最少访问的项
        if (l1Cache.size() >= l1MaxSize) {
            evictLeastAccessedFromL1();
        }
        
        l1Cache.put(key, new CacheEntry(value, System.currentTimeMillis() + cacheTtlSeconds * 1000));
    }
    
    /**
     * 放入L2缓存
     */
    private void putInL2Cache(String key, String value) {
        int l2MaxSize = maxCacheSize - l1Cache.size();
        
        // 如果L2缓存已满，移除最少访问的项
        if (l2Cache.size() >= l2MaxSize) {
            evictLeastAccessedFromL2();
        }
        
        l2Cache.put(key, new CacheEntry(value, System.currentTimeMillis() + cacheTtlSeconds * 1000));
    }
    
    /**
     * 从L1缓存移除最少访问的项
     */
    private void evictLeastAccessedFromL1() {
        String leastAccessedKey = findLeastAccessedKey(l1Cache.keySet());
        if (leastAccessedKey != null) {
            l1Cache.remove(leastAccessedKey);
            evictions.incrementAndGet();
            logger.debug("Evicted from L1 cache: {}", leastAccessedKey);
        }
    }
    
    /**
     * 从L2缓存移除最少访问的项
     */
    private void evictLeastAccessedFromL2() {
        String leastAccessedKey = findLeastAccessedKey(l2Cache.keySet());
        if (leastAccessedKey != null) {
            l2Cache.remove(leastAccessedKey);
            evictions.incrementAndGet();
            logger.debug("Evicted from L2 cache: {}", leastAccessedKey);
        }
    }
    
    /**
     * 查找最少访问的键
     */
    private String findLeastAccessedKey(Set<String> keys) {
        return keys.stream()
            .min((k1, k2) -> {
                long count1 = accessCounts.getOrDefault(k1, new AtomicLong(0)).get();
                long count2 = accessCounts.getOrDefault(k2, new AtomicLong(0)).get();
                return Long.compare(count1, count2);
            })
            .orElse(null);
    }
    
    /**
     * 失效缓存项
     * @param key 配置键
     */
    public void invalidate(String key) {
        if (!cacheEnabled) {
            return;
        }
        
        cacheLock.writeLock().lock();
        try {
            boolean removed = false;
            
            if (l1Cache.remove(key) != null) {
                removed = true;
            }
            
            if (l2Cache.remove(key) != null) {
                removed = true;
            }
            
            if (removed) {
                logger.debug("Invalidated cache for key: {}", key);
            }
        } finally {
            cacheLock.writeLock().unlock();
        }
    }
    
    /**
     * 监听配置变更事件
     */
    @EventListener
    public void handleConfigChange(ConfigChangeEvent event) {
        if (!cacheEnabled) {
            return;
        }
        
        // 配置变更时清空相关缓存
        clearRelatedCache(event.getFilePath());
        
        logger.info("Cleared cache due to config change: {}", event.getChangeType());
    }
    
    /**
     * 清除相关缓存
     */
    private void clearRelatedCache(String filePath) {
        if (filePath.contains("application")) {
            // 如果是主配置文件变更，清空所有缓存
            clearAllCache();
        } else {
            // 否则只清除部分缓存
            clearCacheByPattern(extractKeyPattern(filePath));
        }
    }
    
    /**
     * 提取键模式
     */
    private String extractKeyPattern(String filePath) {
        // 从文件路径提取可能的配置键前缀
        if (filePath.contains("database")) {
            return "spring.datasource";
        } else if (filePath.contains("security")) {
            return "security";
        } else if (filePath.contains("server")) {
            return "server";
        }
        return null;
    }
    
    /**
     * 按模式清除缓存
     */
    private void clearCacheByPattern(String pattern) {
        if (pattern == null) {
            return;
        }
        
        cacheLock.writeLock().lock();
        try {
            l1Cache.entrySet().removeIf(entry -> entry.getKey().startsWith(pattern));
            l2Cache.entrySet().removeIf(entry -> entry.getKey().startsWith(pattern));
            
            logger.debug("Cleared cache entries matching pattern: {}", pattern);
        } finally {
            cacheLock.writeLock().unlock();
        }
    }
    
    /**
     * 清空所有缓存
     */
    public void clearAllCache() {
        if (!cacheEnabled) {
            return;
        }
        
        cacheLock.writeLock().lock();
        try {
            l1Cache.clear();
            l2Cache.clear();
            accessCounts.clear();
            
            logger.info("Cleared all configuration cache");
        } finally {
            cacheLock.writeLock().unlock();
        }
    }
    
    /**
     * 定期清理过期缓存项
     */
    @Scheduled(fixedRate = 300000) // 每5分钟执行一次
    public void cleanupExpiredEntries() {
        if (!cacheEnabled) {
            return;
        }
        
        long currentTime = System.currentTimeMillis();
        int removedCount = 0;
        
        cacheLock.writeLock().lock();
        try {
            // 清理L1缓存过期项
            removedCount += l1Cache.entrySet().removeIf(entry -> 
                entry.getValue().getExpiryTime() < currentTime);
            
            // 清理L2缓存过期项
            removedCount += l2Cache.entrySet().removeIf(entry -> 
                entry.getValue().getExpiryTime() < currentTime);
            
            if (removedCount > 0) {
                logger.debug("Cleaned up {} expired cache entries", removedCount);
            }
        } finally {
            cacheLock.writeLock().unlock();
        }
    }
    
    /**
     * 预热缓存
     * @param keys 要预热的配置键列表
     */
    public void warmupCache(String[] keys) {
        if (!cacheEnabled || keys == null) {
            return;
        }
        
        logger.info("Starting cache warmup for {} keys", keys.length);
        
        for (String key : keys) {
            try {
                String value = loadConfigValue(key);
                if (value != null) {
                    putInCache(key, value, determineInitialCacheLevel(key));
                }
            } catch (Exception e) {
                logger.warn("Failed to warmup cache for key: {}", key, e);
            }
        }
        
        logger.info("Cache warmup completed");
    }
    
    /**
     * 加载配置值（模拟实现）
     */
    private String loadConfigValue(String key) {
        // 这里应该调用实际的配置加载逻辑
        // 为了演示，返回一个模拟值
        return "loaded-value-for-" + key;
    }
    
    /**
     * 获取缓存统计信息
     */
    public Map<String, Object> getCacheStatistics() {
        Map<String, Object> stats = new ConcurrentHashMap<>();
        
        cacheLock.readLock().lock();
        try {
            stats.put("cacheEnabled", cacheEnabled);
            stats.put("l1CacheSize", l1Cache.size());
            stats.put("l2CacheSize", l2Cache.size());
            stats.put("totalCacheSize", l1Cache.size() + l2Cache.size());
            stats.put("maxCacheSize", maxCacheSize);
            stats.put("cacheTtlSeconds", cacheTtlSeconds);
            stats.put("cacheHits", cacheHits.get());
            stats.put("cacheMisses", cacheMisses.get());
            stats.put("evictions", evictions.get());
            
            // 计算命中率
            long totalAccess = cacheHits.get() + cacheMisses.get();
            double hitRate = totalAccess > 0 ? (double) cacheHits.get() / totalAccess : 0.0;
            stats.put("hitRate", String.format("%.2f%%", hitRate * 100));
            
            // 最频繁访问的配置
            stats.put("topAccessedConfigs", getTopAccessedConfigs(10));
            
        } finally {
            cacheLock.readLock().unlock();
        }
        
        return stats;
    }
    
    /**
     * 获取最频繁访问的配置
     */
    private java.util.List<Map<String, Object>> getTopAccessedConfigs(int limit) {
        return accessCounts.entrySet().stream()
            .sorted(Map.Entry.<String, AtomicLong>comparingByValue(
                (a, b) -> Long.compare(b.get(), a.get())))
            .limit(limit)
            .map(entry -> {
                Map<String, Object> item = new ConcurrentHashMap<>();
                item.put("key", entry.getKey());
                item.put("accessCount", entry.getValue().get());
                return item;
            })
            .collect(java.util.stream.Collectors.toList());
    }
    
    @PreDestroy
    public void shutdown() {
        if (cleanupExecutor != null) {
            cleanupExecutor.shutdown();
            try {
                if (!cleanupExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    cleanupExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                cleanupExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        logger.info("Configuration cache manager shutdown completed");
    }
    
    /**
     * 缓存级别枚举
     */
    public enum CacheLevel {
        L1, L2
    }
    
    /**
     * 缓存项
     */
    private static class CacheEntry {
        private final String value;
        private final long expiryTime;
        
        public CacheEntry(String value, long expiryTime) {
            this.value = value;
            this.expiryTime = expiryTime;
        }
        
        public String getValue() {
            return value;
        }
        
        public long getExpiryTime() {
            return expiryTime;
        }
        
        public boolean isExpired() {
            return System.currentTimeMillis() > expiryTime;
        }
    }
}