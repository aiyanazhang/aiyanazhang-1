package com.company.config.monitor;

import com.company.config.hotreload.ConfigChangeEvent;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;

import javax.annotation.PostConstruct;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 配置审计器
 * 负责记录和管理配置变更的审计日志
 */
@Component
public class ConfigurationAuditor {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigurationAuditor.class);
    
    @Value("${app.config.audit.enabled:true}")
    private boolean auditEnabled;
    
    @Value("${app.config.audit.file-path:logs/config-audit.log}")
    private String auditFilePath;
    
    @Value("${app.config.audit.retention-days:30}")
    private int retentionDays;
    
    @Value("${app.config.audit.max-memory-records:10000}")
    private int maxMemoryRecords;
    
    // 内存审计记录队列
    private final Queue<AuditRecord> auditRecords = new ConcurrentLinkedQueue<>();
    
    // 审计统计
    private final AtomicLong totalAuditRecords = new AtomicLong(0);
    private final Map<String, AtomicLong> auditCounts = new ConcurrentHashMap<>();
    
    // 审计文件路径
    private Path auditFilePathObj;
    
    @PostConstruct
    public void initialize() {
        if (!auditEnabled) {
            logger.info("Configuration auditing is disabled");
            return;
        }
        
        logger.info("Initializing configuration auditor");
        
        try {
            // 初始化审计文件路径
            auditFilePathObj = Paths.get(auditFilePath);
            createAuditFileIfNotExists();
            
            // 记录审计器启动
            recordAuditEvent("SYSTEM", "AUDITOR_STARTED", null, 
                "Configuration auditor initialized", "SYSTEM");
            
            logger.info("Configuration auditor initialized successfully");
        } catch (Exception e) {
            logger.error("Failed to initialize configuration auditor", e);
            auditEnabled = false;
        }
    }
    
    /**
     * 创建审计文件（如果不存在）
     */
    private void createAuditFileIfNotExists() throws IOException {
        if (auditFilePathObj.getParent() != null) {
            Files.createDirectories(auditFilePathObj.getParent());
        }
        
        if (!Files.exists(auditFilePathObj)) {
            Files.createFile(auditFilePathObj);
            logger.info("Created audit file: {}", auditFilePathObj.toAbsolutePath());
        }
    }
    
    /**
     * 监听配置变更事件并记录审计日志
     */
    @EventListener
    public void handleConfigChange(ConfigChangeEvent event) {
        if (!auditEnabled) {
            return;
        }
        
        String action = "CONFIG_" + event.getChangeType().toString();
        String resource = event.getFilePath();
        String details = String.format("File: %s, Type: %s", 
            event.getFilePath(), event.getChangeType());
        
        recordAuditEvent(action, resource, event.getOldValue(), 
            event.getNewValue(), "SYSTEM");
        
        logger.debug("Recorded audit for config change: {}", event.getChangeType());
    }
    
    /**
     * 记录审计事件
     * @param action 操作类型
     * @param resource 资源标识
     * @param oldValue 原值
     * @param newValue 新值
     * @param user 用户标识
     */
    public void recordAuditEvent(String action, String resource, String oldValue, 
                                String newValue, String user) {
        if (!auditEnabled) {
            return;
        }
        
        try {
            AuditRecord record = new AuditRecord(
                generateAuditId(),
                action,
                resource,
                oldValue,
                newValue,
                user,
                LocalDateTime.now(),
                getClientInfo()
            );
            
            // 添加到内存队列
            addToMemoryQueue(record);
            
            // 写入审计文件
            writeToAuditFile(record);
            
            // 更新统计
            updateAuditStatistics(action);
            
            logger.debug("Recorded audit event: {} - {}", action, resource);
            
        } catch (Exception e) {
            logger.error("Failed to record audit event", e);
        }
    }
    
    /**
     * 添加记录到内存队列
     */
    private void addToMemoryQueue(AuditRecord record) {
        auditRecords.offer(record);
        
        // 保持队列大小在限制内
        while (auditRecords.size() > maxMemoryRecords) {
            auditRecords.poll();
        }
        
        totalAuditRecords.incrementAndGet();
    }
    
    /**
     * 写入审计文件
     */
    private void writeToAuditFile(AuditRecord record) {
        try (FileWriter writer = new FileWriter(auditFilePathObj.toFile(), true)) {
            writer.write(record.toLogString() + System.lineSeparator());
            writer.flush();
        } catch (IOException e) {
            logger.error("Failed to write audit record to file", e);
        }
    }
    
    /**
     * 更新审计统计
     */
    private void updateAuditStatistics(String action) {
        auditCounts.computeIfAbsent(action, k -> new AtomicLong(0)).incrementAndGet();
    }
    
    /**
     * 生成审计ID
     */
    private String generateAuditId() {
        return "AUDIT-" + System.currentTimeMillis() + "-" + 
               Integer.toHexString((int)(Math.random() * 0xFFFF));
    }
    
    /**
     * 获取客户端信息
     */
    private String getClientInfo() {
        try {
            String hostName = java.net.InetAddress.getLocalHost().getHostName();
            String hostAddress = java.net.InetAddress.getLocalHost().getHostAddress();
            return String.format("%s (%s)", hostName, hostAddress);
        } catch (Exception e) {
            return "Unknown";
        }
    }
    
    /**
     * 定期清理过期审计记录
     */
    @Scheduled(cron = "0 0 2 * * ?") // 每天凌晨2点执行
    public void cleanupExpiredRecords() {
        if (!auditEnabled) {
            return;
        }
        
        logger.info("Starting cleanup of expired audit records");
        
        try {
            LocalDateTime cutoffTime = LocalDateTime.now().minusDays(retentionDays);
            
            // 清理内存记录
            cleanupMemoryRecords(cutoffTime);
            
            // 清理文件记录（简化实现，实际可能需要更复杂的文件处理）
            rotateAuditFile();
            
            logger.info("Completed cleanup of expired audit records");
            
        } catch (Exception e) {
            logger.error("Failed to cleanup expired audit records", e);
        }
    }
    
    /**
     * 清理内存中的过期记录
     */
    private void cleanupMemoryRecords(LocalDateTime cutoffTime) {
        int removedCount = 0;
        AuditRecord record;
        
        while ((record = auditRecords.peek()) != null) {
            if (record.getTimestamp().isBefore(cutoffTime)) {
                auditRecords.poll();
                removedCount++;
            } else {
                break;
            }
        }
        
        logger.info("Removed {} expired records from memory", removedCount);
    }
    
    /**
     * 轮换审计文件
     */
    private void rotateAuditFile() {
        try {
            if (Files.exists(auditFilePathObj) && Files.size(auditFilePathObj) > 10 * 1024 * 1024) { // 10MB
                String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss"));
                Path rotatedFile = Paths.get(auditFilePath + "." + timestamp);
                
                Files.move(auditFilePathObj, rotatedFile);
                createAuditFileIfNotExists();
                
                logger.info("Rotated audit file to: {}", rotatedFile);
            }
        } catch (IOException e) {
            logger.error("Failed to rotate audit file", e);
        }
    }
    
    /**
     * 查询审计记录
     * @param action 操作类型过滤
     * @param resource 资源过滤
     * @param limit 返回记录数限制
     * @return 审计记录列表
     */
    public List<AuditRecord> queryAuditRecords(String action, String resource, int limit) {
        return auditRecords.stream()
            .filter(record -> action == null || record.getAction().contains(action))
            .filter(record -> resource == null || record.getResource().contains(resource))
            .sorted((a, b) -> b.getTimestamp().compareTo(a.getTimestamp()))
            .limit(limit)
            .collect(java.util.stream.Collectors.toList());
    }
    
    /**
     * 获取审计统计信息
     */
    public Map<String, Object> getAuditStatistics() {
        Map<String, Object> stats = new ConcurrentHashMap<>();
        stats.put("auditEnabled", auditEnabled);
        stats.put("totalRecords", totalAuditRecords.get());
        stats.put("memoryRecords", auditRecords.size());
        stats.put("retentionDays", retentionDays);
        stats.put("auditFilePath", auditFilePath);
        stats.put("actionCounts", auditCounts);
        
        // 最近的记录时间
        AuditRecord lastRecord = auditRecords.stream()
            .max((a, b) -> a.getTimestamp().compareTo(b.getTimestamp()))
            .orElse(null);
        
        if (lastRecord != null) {
            stats.put("lastRecordTime", lastRecord.getTimestamp());
        }
        
        return stats;
    }
    
    /**
     * 导出审计记录
     * @param outputPath 输出文件路径
     * @param format 导出格式（JSON、CSV等）
     * @return 是否成功导出
     */
    public boolean exportAuditRecords(String outputPath, String format) {
        try {
            Path outputFile = Paths.get(outputPath);
            
            if (outputFile.getParent() != null) {
                Files.createDirectories(outputFile.getParent());
            }
            
            try (FileWriter writer = new FileWriter(outputFile.toFile())) {
                if ("JSON".equalsIgnoreCase(format)) {
                    exportAsJson(writer);
                } else if ("CSV".equalsIgnoreCase(format)) {
                    exportAsCsv(writer);
                } else {
                    exportAsText(writer);
                }
            }
            
            logger.info("Exported audit records to: {}", outputFile.toAbsolutePath());
            return true;
            
        } catch (Exception e) {
            logger.error("Failed to export audit records", e);
            return false;
        }
    }
    
    /**
     * 导出为JSON格式
     */
    private void exportAsJson(FileWriter writer) throws IOException {
        writer.write("[\n");
        boolean first = true;
        
        for (AuditRecord record : auditRecords) {
            if (!first) {
                writer.write(",\n");
            }
            writer.write(record.toJsonString());
            first = false;
        }
        
        writer.write("\n]");
    }
    
    /**
     * 导出为CSV格式
     */
    private void exportAsCsv(FileWriter writer) throws IOException {
        writer.write("ID,Action,Resource,OldValue,NewValue,User,Timestamp,ClientInfo\n");
        
        for (AuditRecord record : auditRecords) {
            writer.write(record.toCsvString() + "\n");
        }
    }
    
    /**
     * 导出为文本格式
     */
    private void exportAsText(FileWriter writer) throws IOException {
        for (AuditRecord record : auditRecords) {
            writer.write(record.toLogString() + "\n");
        }
    }
    
    /**
     * 启用审计
     */
    public void enableAudit() {
        if (!auditEnabled) {
            auditEnabled = true;
            initialize();
            logger.info("Configuration audit enabled");
        }
    }
    
    /**
     * 禁用审计
     */
    public void disableAudit() {
        if (auditEnabled) {
            auditEnabled = false;
            recordAuditEvent("SYSTEM", "AUDITOR_STOPPED", null, 
                "Configuration auditor disabled", "SYSTEM");
            logger.info("Configuration audit disabled");
        }
    }
    
    /**
     * 审计记录类
     */
    public static class AuditRecord {
        private final String id;
        private final String action;
        private final String resource;
        private final String oldValue;
        private final String newValue;
        private final String user;
        private final LocalDateTime timestamp;
        private final String clientInfo;
        
        public AuditRecord(String id, String action, String resource, String oldValue, 
                          String newValue, String user, LocalDateTime timestamp, String clientInfo) {
            this.id = id;
            this.action = action;
            this.resource = resource;
            this.oldValue = oldValue;
            this.newValue = newValue;
            this.user = user;
            this.timestamp = timestamp;
            this.clientInfo = clientInfo;
        }
        
        // Getters
        public String getId() { return id; }
        public String getAction() { return action; }
        public String getResource() { return resource; }
        public String getOldValue() { return oldValue; }
        public String getNewValue() { return newValue; }
        public String getUser() { return user; }
        public LocalDateTime getTimestamp() { return timestamp; }
        public String getClientInfo() { return clientInfo; }
        
        public String toLogString() {
            return String.format("[%s] %s | Action: %s | Resource: %s | User: %s | Client: %s | Old: %s | New: %s",
                timestamp.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
                id, action, resource, user, clientInfo,
                oldValue != null ? oldValue : "N/A",
                newValue != null ? newValue : "N/A");
        }
        
        public String toJsonString() {
            return String.format("{\"id\":\"%s\",\"action\":\"%s\",\"resource\":\"%s\",\"oldValue\":\"%s\",\"newValue\":\"%s\",\"user\":\"%s\",\"timestamp\":\"%s\",\"clientInfo\":\"%s\"}",
                id, action, resource,
                oldValue != null ? oldValue.replace("\"", "\\\"") : "",
                newValue != null ? newValue.replace("\"", "\\\"") : "",
                user, timestamp.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME), clientInfo);
        }
        
        public String toCsvString() {
            return String.format("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"",
                id, action, resource,
                oldValue != null ? oldValue.replace("\"", "\"\"") : "",
                newValue != null ? newValue.replace("\"", "\"\"") : "",
                user, timestamp.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME), clientInfo);
        }
    }
}