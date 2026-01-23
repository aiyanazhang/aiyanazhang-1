package com.company.config.hotreload;

/**
 * 配置变化类型枚举
 */
public enum ConfigChangeType {
    
    FILE_CREATED("文件创建"),
    FILE_MODIFIED("文件修改"),
    FILE_DELETED("文件删除"),
    CONFIG_UPDATED("配置更新"),
    MANUAL_RELOAD("手动重载"),
    RELOAD_FAILED("重载失败"),
    KEY_ADDED("配置键添加"),
    KEY_REMOVED("配置键删除"),
    KEY_MODIFIED("配置键修改");
    
    private final String description;
    
    ConfigChangeType(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
    
    @Override
    public String toString() {
        return description;
    }
}