package com.company.config.hotreload;

import org.springframework.context.ApplicationEvent;

/**
 * 配置变化事件
 */
public class ConfigChangeEvent extends ApplicationEvent {
    
    private final String filePath;
    private final ConfigChangeType changeType;
    private final String oldValue;
    private final String newValue;
    private final long timestamp;
    
    public ConfigChangeEvent(Object source, String filePath, ConfigChangeType changeType, 
                           String oldValue, String newValue) {
        super(source);
        this.filePath = filePath;
        this.changeType = changeType;
        this.oldValue = oldValue;
        this.newValue = newValue;
        this.timestamp = System.currentTimeMillis();
    }
    
    public String getFilePath() {
        return filePath;
    }
    
    public ConfigChangeType getChangeType() {
        return changeType;
    }
    
    public String getOldValue() {
        return oldValue;
    }
    
    public String getNewValue() {
        return newValue;
    }
    
    public long getTimestamp() {
        return timestamp;
    }
    
    @Override
    public String toString() {
        return String.format("ConfigChangeEvent{filePath='%s', changeType=%s, timestamp=%d}", 
            filePath, changeType, timestamp);
    }
}