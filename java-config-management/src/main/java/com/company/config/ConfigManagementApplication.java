package com.company.config;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Java配置管理系统主应用程序类
 * 
 * 该应用程序实现了基于Spring Boot的配置管理功能，包括：
 * - 多环境配置支持
 * - 配置验证机制
 * - 热更新功能
 * - 敏感信息加密存储
 * - 配置监控和审计
 * - 性能优化缓存
 */
@SpringBootApplication
@EnableConfigurationProperties
@EnableAspectJAutoProxy
@EnableAsync
@EnableScheduling
public class ConfigManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConfigManagementApplication.class, args);
    }
}