package com.company.config.monitor;

import com.company.config.hotreload.ConfigChangeEvent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.EventListener;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.springframework.scheduling.annotation.Scheduled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

import javax.annotation.PostConstruct;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

/**
 * 配置监控器
 * 负责监控配置的访问、变更和性能指标
 */
@Component
public class ConfigurationMonitor {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigurationMonitor.class);
    
    @Autowired
    private Environment environment;
    
    @Autowired(required = false)
    private MeterRegistry meterRegistry;
    
    @Value("${app.config.monitoring.enabled:true}")
    private boolean monitoringEnabled;
    
    @Value("${app.config.monitoring.interval:60}")
    private int monitoringIntervalSeconds;
    
    // 性能指标
    private Counter configAccessCounter;
    private Counter configChangeCounter;
    private Timer configLoadTimer;
    private AtomicInteger activeConfigSources;
    private AtomicLong lastMonitoringTime;
    
    // 配置访问统计
    private final Map<String, AtomicInteger> configAccessStats = new ConcurrentHashMap<>();
    private final Map<String, AtomicLong> configAccessTimes = new ConcurrentHashMap<>();
    
    // 配置变更历史
    private final List<ConfigChangeRecord> changeHistory = new ArrayList<>();
    private static final int MAX_HISTORY_SIZE = 1000;
    
    // 监控指标
    private final Map<String, Object> monitoringMetrics = new ConcurrentHashMap<>();
    
    @PostConstruct
    public void initialize() {
        if (!monitoringEnabled) {
            logger.info("Configuration monitoring is disabled");
            return;
        }
        
        logger.info("Initializing configuration monitor");
        
        // 初始化指标
        initializeMetrics();
        
        // 开始监控
        startMonitoring();
        
        logger.info("Configuration monitor initialized successfully");
    }
    
    /**
     * 初始化监控指标
     */
    private void initializeMetrics() {
        activeConfigSources = new AtomicInteger(0);
        lastMonitoringTime = new AtomicLong(System.currentTimeMillis());
        
        if (meterRegistry != null) {
            // 配置访问计数器
            configAccessCounter = Counter.builder("config.access.total")
                .description("Total number of configuration access")
                .register(meterRegistry);
            
            // 配置变更计数器
            configChangeCounter = Counter.builder("config.change.total")
                .description("Total number of configuration changes")
                .register(meterRegistry);
            
            // 配置加载时间计时器
            configLoadTimer = Timer.builder("config.load.duration")
                .description("Configuration loading duration")
                .register(meterRegistry);
            
            // 活动配置源数量
            Gauge.builder("config.sources.active")
                .description("Number of active configuration sources")
                .register(meterRegistry, activeConfigSources, AtomicInteger::get);
            
            // 配置缓存大小
            Gauge.builder("config.cache.size")
                .description("Configuration cache size")
                .register(meterRegistry, this, ConfigurationMonitor::getCacheSize);
        }
    }
    
    /**
     * 开始监控
     */
    private void startMonitoring() {
        // 统计初始配置源数量
        countActiveConfigSources();
        
        logger.info("Configuration monitoring started with interval: {} seconds", 
            monitoringIntervalSeconds);
    }
    
    /**
     * 记录配置访问
     * @param key 配置键
     */
    public void recordConfigAccess(String key) {
        if (!monitoringEnabled) {
            return;
        }
        
        // 增加总访问计数
        if (configAccessCounter != null) {
            configAccessCounter.increment();
        }
        
        // 记录具体配置项的访问次数
        configAccessStats.computeIfAbsent(key, k -> new AtomicInteger(0)).incrementAndGet();
        configAccessTimes.put(key, System.currentTimeMillis());
        
        logger.debug("Recorded config access for key: {}", key);
    }
    
    /**
     * 记录配置加载时间
     * @param durationMs 加载耗时（毫秒）
     */
    public void recordConfigLoadTime(long durationMs) {
        if (!monitoringEnabled) {
            return;
        }
        
        if (configLoadTimer != null) {
            configLoadTimer.record(durationMs, java.util.concurrent.TimeUnit.MILLISECONDS);
        }
        
        logger.debug("Recorded config load time: {} ms", durationMs);
    }
    
    /**
     * 监听配置变更事件
     */
    @EventListener
    public void handleConfigChange(ConfigChangeEvent event) {
        if (!monitoringEnabled) {
            return;
        }
        
        // 增加变更计数
        if (configChangeCounter != null) {
            configChangeCounter.increment();
        }
        
        // 记录变更历史
        recordConfigChange(event);
        
        logger.info("Monitored config change: {} - {}", 
            event.getChangeType(), event.getFilePath());
    }
    
    /**
     * 记录配置变更
     */
    private void recordConfigChange(ConfigChangeEvent event) {
        ConfigChangeRecord record = new ConfigChangeRecord(
            event.getFilePath(),
            event.getChangeType().toString(),
            event.getOldValue(),
            event.getNewValue(),
            LocalDateTime.now()
        );
        
        synchronized (changeHistory) {
            changeHistory.add(record);
            
            // 保持历史记录在限定大小内
            if (changeHistory.size() > MAX_HISTORY_SIZE) {
                changeHistory.remove(0);
            }
        }
    }
    
    /**
     * 定期监控任务
     */
    @Scheduled(fixedDelayString = "${app.config.monitoring.interval:60}000")
    public void performPeriodicMonitoring() {
        if (!monitoringEnabled) {
            return;
        }
        
        logger.debug("Performing periodic configuration monitoring");
        
        try {
            // 更新监控指标
            updateMonitoringMetrics();
            
            // 检查配置健康状态
            checkConfigurationHealth();
            
            // 清理过期访问记录
            cleanupOldAccessRecords();
            
            lastMonitoringTime.set(System.currentTimeMillis());
            
        } catch (Exception e) {
            logger.error("Error during periodic monitoring", e);
        }
    }
    
    /**
     * 更新监控指标
     */
    private void updateMonitoringMetrics() {
        monitoringMetrics.put("totalConfigAccess", getTotalConfigAccess());
        monitoringMetrics.put("totalConfigChanges", changeHistory.size());
        monitoringMetrics.put("activeConfigSources", activeConfigSources.get());
        monitoringMetrics.put("lastMonitoringTime", lastMonitoringTime.get());
        monitoringMetrics.put("monitoringEnabled", monitoringEnabled);
        monitoringMetrics.put("mostAccessedConfigs", getMostAccessedConfigs(10));
        monitoringMetrics.put("recentChanges", getRecentChanges(10));
    }
    
    /**
     * 检查配置健康状态
     */
    private void checkConfigurationHealth() {
        int healthScore = 100;
        List<String> healthIssues = new ArrayList<>();
        
        // 检查配置源状态
        countActiveConfigSources();
        if (activeConfigSources.get() == 0) {
            healthScore -= 50;
            healthIssues.add("No active configuration sources");
        }
        
        // 检查最近是否有加载失败
        long recentFailures = changeHistory.stream()
            .filter(record -> record.getTimestamp().isAfter(LocalDateTime.now().minusMinutes(10)))
            .filter(record -> record.getChangeType().contains("FAILED"))
            .count();
        
        if (recentFailures > 0) {
            healthScore -= (int) (recentFailures * 10);
            healthIssues.add("Recent configuration load failures: " + recentFailures);
        }
        
        monitoringMetrics.put("healthScore", healthScore);
        monitoringMetrics.put("healthIssues", healthIssues);
        
        if (healthScore < 80) {
            logger.warn("Configuration health score is low: {}, issues: {}", 
                healthScore, healthIssues);
        }
    }
    
    /**
     * 清理过期的访问记录
     */
    private void cleanupOldAccessRecords() {
        long cutoffTime = System.currentTimeMillis() - (24 * 60 * 60 * 1000); // 24小时前
        
        configAccessTimes.entrySet().removeIf(entry -> entry.getValue() < cutoffTime);
    }
    
    /**
     * 统计活动配置源数量
     */
    private void countActiveConfigSources() {
        int count = 0;
        
        try {
            org.springframework.core.env.MutablePropertySources propertySources = 
                ((org.springframework.core.env.AbstractEnvironment) environment).getPropertySources();
            
            for (org.springframework.core.env.PropertySource<?> propertySource : propertySources) {
                if (propertySource.getSource() != null) {
                    count++;
                }
            }
        } catch (Exception e) {
            logger.error("Failed to count active config sources", e);
        }
        
        activeConfigSources.set(count);
    }
    
    /**
     * 获取总配置访问次数
     */
    private long getTotalConfigAccess() {
        return configAccessStats.values().stream()
            .mapToLong(AtomicInteger::get)
            .sum();
    }
    
    /**
     * 获取最常访问的配置项
     */
    private List<Map<String, Object>> getMostAccessedConfigs(int limit) {
        return configAccessStats.entrySet().stream()
            .sorted(Map.Entry.<String, AtomicInteger>comparingByValue(
                (a, b) -> Integer.compare(b.get(), a.get())))
            .limit(limit)
            .map(entry -> {
                Map<String, Object> item = new ConcurrentHashMap<>();
                item.put("key", entry.getKey());
                item.put("accessCount", entry.getValue().get());
                item.put("lastAccess", configAccessTimes.get(entry.getKey()));
                return item;
            })
            .collect(java.util.stream.Collectors.toList());
    }
    
    /**
     * 获取最近的配置变更
     */
    private List<ConfigChangeRecord> getRecentChanges(int limit) {
        synchronized (changeHistory) {
            return changeHistory.stream()
                .sorted((a, b) -> b.getTimestamp().compareTo(a.getTimestamp()))
                .limit(limit)
                .collect(java.util.stream.Collectors.toList());
        }
    }
    
    /**
     * 获取缓存大小（用于Gauge指标）
     */
    private double getCacheSize() {
        return configAccessStats.size();
    }
    
    /**
     * 获取监控统计信息
     */
    public Map<String, Object> getMonitoringStatistics() {
        Map<String, Object> stats = new ConcurrentHashMap<>(monitoringMetrics);
        stats.put("monitoringInterval", monitoringIntervalSeconds);
        stats.put("maxHistorySize", MAX_HISTORY_SIZE);
        return stats;
    }
    
    /**
     * 重置监控统计
     */
    public void resetStatistics() {
        configAccessStats.clear();
        configAccessTimes.clear();
        
        synchronized (changeHistory) {
            changeHistory.clear();
        }
        
        monitoringMetrics.clear();
        lastMonitoringTime.set(System.currentTimeMillis());
        
        logger.info("Configuration monitoring statistics reset");
    }
    
    /**
     * 启用监控
     */
    public void enableMonitoring() {
        if (!monitoringEnabled) {
            monitoringEnabled = true;
            initialize();
            logger.info("Configuration monitoring enabled");
        }
    }
    
    /**
     * 禁用监控
     */
    public void disableMonitoring() {
        if (monitoringEnabled) {
            monitoringEnabled = false;
            logger.info("Configuration monitoring disabled");
        }
    }
    
    /**
     * 配置变更记录
     */
    public static class ConfigChangeRecord {
        private final String filePath;
        private final String changeType;
        private final String oldValue;
        private final String newValue;
        private final LocalDateTime timestamp;
        
        public ConfigChangeRecord(String filePath, String changeType, String oldValue, 
                                String newValue, LocalDateTime timestamp) {
            this.filePath = filePath;
            this.changeType = changeType;
            this.oldValue = oldValue;
            this.newValue = newValue;
            this.timestamp = timestamp;
        }
        
        // Getters
        public String getFilePath() { return filePath; }
        public String getChangeType() { return changeType; }
        public String getOldValue() { return oldValue; }
        public String getNewValue() { return newValue; }
        public LocalDateTime getTimestamp() { return timestamp; }
        
        @Override
        public String toString() {
            return String.format("ConfigChangeRecord{filePath='%s', changeType='%s', timestamp=%s}", 
                filePath, changeType, timestamp.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        }
    }
}