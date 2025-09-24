package com.company.config.hotreload;

import com.company.config.loader.ConfigLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;
import org.springframework.scheduling.annotation.Scheduled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.IOException;
import java.nio.file.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;

/**
 * 配置热更新管理器
 * 监控配置文件变化并触发配置重新加载
 */
@Component
public class ConfigHotReloadManager {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigHotReloadManager.class);
    
    @Autowired
    private ConfigLoader configLoader;
    
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    @Value("${app.config.hotreload.enabled:false}")
    private boolean hotReloadEnabled;
    
    @Value("${app.config.hotreload.check-interval:30}")
    private int checkIntervalSeconds;
    
    @Value("${app.config.hotreload.watched-paths:config/}")
    private String[] watchedPaths;
    
    // 文件监控服务
    private WatchService watchService;
    private ScheduledExecutorService executorService;
    
    // 配置文件时间戳缓存
    private final Map<String, Long> fileTimestamps = new ConcurrentHashMap<>();
    
    // 支持的配置文件扩展名
    private static final Set<String> SUPPORTED_EXTENSIONS = Set.of(
        ".yml", ".yaml", ".properties", ".json", ".xml"
    );
    
    // 热更新支持的配置键
    private static final Set<String> HOT_RELOAD_SUPPORTED_KEYS = Set.of(
        "logging.level.root",
        "logging.level.com.company",
        "app.config.cache.ttl",
        "app.config.monitoring.interval",
        "security.rate-limit.requests-per-minute",
        "management.endpoints.web.exposure.include"
    );
    
    @PostConstruct
    public void initialize() {
        if (!hotReloadEnabled) {
            logger.info("Configuration hot reload is disabled");
            return;
        }
        
        logger.info("Initializing configuration hot reload manager");
        
        try {
            initializeWatchService();
            startFileWatcher();
            schedulePeriodicCheck();
            
            logger.info("Configuration hot reload manager initialized successfully");
        } catch (Exception e) {
            logger.error("Failed to initialize hot reload manager", e);
            hotReloadEnabled = false;
        }
    }
    
    /**
     * 初始化文件监控服务
     */
    private void initializeWatchService() throws IOException {
        watchService = FileSystems.getDefault().newWatchService();
        
        // 注册监控路径
        for (String pathStr : watchedPaths) {
            try {
                Path path = Paths.get(pathStr);
                if (Files.exists(path) && Files.isDirectory(path)) {
                    path.register(watchService, 
                        StandardWatchEventKinds.ENTRY_CREATE,
                        StandardWatchEventKinds.ENTRY_MODIFY,
                        StandardWatchEventKinds.ENTRY_DELETE);
                    
                    logger.info("Registered watch path: {}", path.toAbsolutePath());
                    
                    // 初始化文件时间戳
                    initializeFileTimestamps(path);
                } else {
                    logger.warn("Watch path does not exist or is not a directory: {}", pathStr);
                }
            } catch (Exception e) {
                logger.error("Failed to register watch path: {}", pathStr, e);
            }
        }
    }
    
    /**
     * 初始化文件时间戳
     */
    private void initializeFileTimestamps(Path directory) {
        try {
            Files.walk(directory)
                .filter(Files::isRegularFile)
                .filter(this::isSupportedConfigFile)
                .forEach(file -> {
                    try {
                        long lastModified = Files.getLastModifiedTime(file).toMillis();
                        fileTimestamps.put(file.toString(), lastModified);
                        logger.debug("Initialized timestamp for file: {}", file);
                    } catch (IOException e) {
                        logger.warn("Failed to get timestamp for file: {}", file, e);
                    }
                });
        } catch (IOException e) {
            logger.error("Failed to initialize file timestamps for directory: {}", directory, e);
        }
    }
    
    /**
     * 启动文件监控器
     */
    private void startFileWatcher() {
        executorService = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread thread = new Thread(r, "config-file-watcher");
            thread.setDaemon(true);
            return thread;
        });
        
        executorService.submit(this::watchFiles);
    }
    
    /**
     * 文件监控主循环
     */
    private void watchFiles() {
        logger.info("File watcher started");
        
        while (!Thread.currentThread().isInterrupted()) {
            try {
                WatchKey key = watchService.take();
                
                for (WatchEvent<?> event : key.pollEvents()) {
                    WatchEvent.Kind<?> kind = event.kind();
                    
                    if (kind == StandardWatchEventKinds.OVERFLOW) {
                        continue;
                    }
                    
                    @SuppressWarnings("unchecked")
                    WatchEvent<Path> pathEvent = (WatchEvent<Path>) event;
                    Path fileName = pathEvent.context();
                    Path fullPath = ((Path) key.watchable()).resolve(fileName);
                    
                    if (isSupportedConfigFile(fullPath)) {
                        handleFileChange(fullPath, kind);
                    }
                }
                
                boolean valid = key.reset();
                if (!valid) {
                    logger.warn("Watch key is no longer valid");
                    break;
                }
                
            } catch (InterruptedException e) {
                logger.info("File watcher interrupted");
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                logger.error("Error in file watcher", e);
            }
        }
        
        logger.info("File watcher stopped");
    }
    
    /**
     * 处理文件变化
     */
    private void handleFileChange(Path file, WatchEvent.Kind<?> kind) {
        logger.info("Detected file change: {} - {}", kind.name(), file);
        
        try {
            if (kind == StandardWatchEventKinds.ENTRY_DELETE) {
                fileTimestamps.remove(file.toString());
                publishConfigChangeEvent(file.toString(), ConfigChangeType.FILE_DELETED, null, null);
            } else {
                // 检查文件是否真的变化了（避免重复事件）
                if (hasFileActuallyChanged(file)) {
                    reloadConfigurationFile(file);
                }
            }
        } catch (Exception e) {
            logger.error("Failed to handle file change: {}", file, e);
        }
    }
    
    /**
     * 检查文件是否真的变化了
     */
    private boolean hasFileActuallyChanged(Path file) {
        try {
            if (!Files.exists(file)) {
                return false;
            }
            
            long currentModified = Files.getLastModifiedTime(file).toMillis();
            String fileKey = file.toString();
            Long lastModified = fileTimestamps.get(fileKey);
            
            if (lastModified == null || currentModified > lastModified) {
                fileTimestamps.put(fileKey, currentModified);
                return true;
            }
            
            return false;
        } catch (IOException e) {
            logger.warn("Failed to check file modification time: {}", file, e);
            return false;
        }
    }
    
    /**
     * 重新加载配置文件
     */
    private void reloadConfigurationFile(Path file) {
        logger.info("Reloading configuration file: {}", file);
        
        try {
            // 清除配置缓存
            configLoader.clearCache();
            
            // 发布配置重新加载事件
            publishConfigChangeEvent(file.toString(), ConfigChangeType.FILE_MODIFIED, null, null);
            
            logger.info("Successfully reloaded configuration file: {}", file);
        } catch (Exception e) {
            logger.error("Failed to reload configuration file: {}", file, e);
            publishConfigChangeEvent(file.toString(), ConfigChangeType.RELOAD_FAILED, null, e.getMessage());
        }
    }
    
    /**
     * 定期检查配置变化
     */
    @Scheduled(fixedDelayString = "${app.config.hotreload.check-interval:30}000")
    public void periodicConfigCheck() {
        if (!hotReloadEnabled) {
            return;
        }
        
        logger.debug("Performing periodic configuration check");
        
        try {
            checkForConfigChanges();
        } catch (Exception e) {
            logger.error("Error during periodic config check", e);
        }
    }
    
    /**
     * 检查配置变化
     */
    private void checkForConfigChanges() {
        for (String pathStr : watchedPaths) {
            Path path = Paths.get(pathStr);
            if (Files.exists(path) && Files.isDirectory(path)) {
                try {
                    Files.walk(path)
                        .filter(Files::isRegularFile)
                        .filter(this::isSupportedConfigFile)
                        .forEach(file -> {
                            if (hasFileActuallyChanged(file)) {
                                handleFileChange(file, StandardWatchEventKinds.ENTRY_MODIFY);
                            }
                        });
                } catch (IOException e) {
                    logger.error("Failed to check directory for changes: {}", path, e);
                }
            }
        }
    }
    
    /**
     * 检查是否为支持的配置文件
     */
    private boolean isSupportedConfigFile(Path file) {
        String fileName = file.getFileName().toString().toLowerCase();
        return SUPPORTED_EXTENSIONS.stream().anyMatch(fileName::endsWith);
    }
    
    /**
     * 发布配置变化事件
     */
    private void publishConfigChangeEvent(String filePath, ConfigChangeType changeType, 
                                        String oldValue, String newValue) {
        ConfigChangeEvent event = new ConfigChangeEvent(this, filePath, changeType, oldValue, newValue);
        eventPublisher.publishEvent(event);
        
        logger.info("Published config change event: {} - {}", changeType, filePath);
    }
    
    /**
     * 手动触发配置重新加载
     */
    public void manualReload() {
        if (!hotReloadEnabled) {
            logger.warn("Hot reload is disabled, cannot perform manual reload");
            return;
        }
        
        logger.info("Manual configuration reload triggered");
        
        try {
            configLoader.reloadConfiguration();
            publishConfigChangeEvent("manual", ConfigChangeType.MANUAL_RELOAD, null, null);
            
            logger.info("Manual configuration reload completed");
        } catch (Exception e) {
            logger.error("Manual configuration reload failed", e);
            publishConfigChangeEvent("manual", ConfigChangeType.RELOAD_FAILED, null, e.getMessage());
        }
    }
    
    /**
     * 获取热更新统计信息
     */
    public Map<String, Object> getHotReloadStatistics() {
        Map<String, Object> stats = new ConcurrentHashMap<>();
        stats.put("enabled", hotReloadEnabled);
        stats.put("checkIntervalSeconds", checkIntervalSeconds);
        stats.put("watchedPaths", watchedPaths);
        stats.put("monitoredFiles", fileTimestamps.size());
        stats.put("supportedExtensions", SUPPORTED_EXTENSIONS);
        stats.put("supportedKeys", HOT_RELOAD_SUPPORTED_KEYS);
        return stats;
    }
    
    /**
     * 启用热更新
     */
    public void enableHotReload() {
        if (!hotReloadEnabled) {
            hotReloadEnabled = true;
            initialize();
            logger.info("Hot reload enabled");
        }
    }
    
    /**
     * 禁用热更新
     */
    public void disableHotReload() {
        if (hotReloadEnabled) {
            hotReloadEnabled = false;
            shutdown();
            logger.info("Hot reload disabled");
        }
    }
    
    @PreDestroy
    public void shutdown() {
        logger.info("Shutting down configuration hot reload manager");
        
        if (executorService != null) {
            executorService.shutdown();
            try {
                if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                    executorService.shutdownNow();
                }
            } catch (InterruptedException e) {
                executorService.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        if (watchService != null) {
            try {
                watchService.close();
            } catch (IOException e) {
                logger.error("Failed to close watch service", e);
            }
        }
        
        logger.info("Configuration hot reload manager shutdown completed");
    }
}