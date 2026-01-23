package com.company.config.loader;

import com.company.config.loader.EnvironmentDetector.EnvironmentType;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.core.env.Environment;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * 环境检测器测试
 */
@ExtendWith(MockitoExtension.class)
class EnvironmentDetectorTest {
    
    @Mock
    private Environment environment;
    
    private EnvironmentDetector environmentDetector;
    
    @BeforeEach
    void setUp() {
        environmentDetector = new EnvironmentDetector();
        ReflectionTestUtils.setField(environmentDetector, "environment", environment);
    }
    
    @Test
    void testDetectDevelopmentEnvironment() {
        // 模拟开发环境
        when(environment.getActiveProfiles()).thenReturn(new String[]{"dev"});
        
        environmentDetector.detectEnvironment();
        
        assertEquals("dev", environmentDetector.getCurrentEnvironment());
        assertEquals(EnvironmentType.DEVELOPMENT, environmentDetector.getEnvironmentType());
        assertTrue(environmentDetector.isDevelopment());
        assertFalse(environmentDetector.isProduction());
    }
    
    @Test
    void testDetectProductionEnvironment() {
        // 模拟生产环境
        when(environment.getActiveProfiles()).thenReturn(new String[]{"prod"});
        
        environmentDetector.detectEnvironment();
        
        assertEquals("prod", environmentDetector.getCurrentEnvironment());
        assertEquals(EnvironmentType.PRODUCTION, environmentDetector.getEnvironmentType());
        assertTrue(environmentDetector.isProduction());
        assertFalse(environmentDetector.isDevelopment());
    }
    
    @Test
    void testDetectTestEnvironment() {
        // 模拟测试环境
        when(environment.getActiveProfiles()).thenReturn(new String[]{"test"});
        
        environmentDetector.detectEnvironment();
        
        assertEquals("test", environmentDetector.getCurrentEnvironment());
        assertEquals(EnvironmentType.TESTING, environmentDetector.getEnvironmentType());
        assertTrue(environmentDetector.isTesting());
        assertFalse(environmentDetector.isProduction());
    }
    
    @Test
    void testDetectStagingEnvironment() {
        // 模拟预发布环境
        when(environment.getActiveProfiles()).thenReturn(new String[]{"staging"});
        
        environmentDetector.detectEnvironment();
        
        assertEquals("staging", environmentDetector.getCurrentEnvironment());
        assertEquals(EnvironmentType.STAGING, environmentDetector.getEnvironmentType());
        assertTrue(environmentDetector.isStaging());
        assertFalse(environmentDetector.isProduction());
    }
    
    @Test
    void testDefaultToDevelopmentWhenNoProfileActive() {
        // 模拟没有激活的Profile
        when(environment.getActiveProfiles()).thenReturn(new String[]{});
        
        environmentDetector.detectEnvironment();
        
        assertEquals("dev", environmentDetector.getCurrentEnvironment());
        assertEquals(EnvironmentType.DEVELOPMENT, environmentDetector.getEnvironmentType());
        assertTrue(environmentDetector.isDevelopment());
    }
    
    @Test
    void testEnvironmentTypeFromProfile() {
        assertEquals(EnvironmentType.DEVELOPMENT, EnvironmentType.fromProfile("dev"));
        assertEquals(EnvironmentType.TESTING, EnvironmentType.fromProfile("test"));
        assertEquals(EnvironmentType.STAGING, EnvironmentType.fromProfile("staging"));
        assertEquals(EnvironmentType.PRODUCTION, EnvironmentType.fromProfile("prod"));
        assertEquals(EnvironmentType.UNKNOWN, EnvironmentType.fromProfile("invalid"));
    }
    
    @Test
    void testMultipleActiveProfiles() {
        // 模拟多个激活的Profile，应该使用第一个
        when(environment.getActiveProfiles()).thenReturn(new String[]{"prod", "monitoring"});
        
        environmentDetector.detectEnvironment();
        
        assertEquals("prod", environmentDetector.getCurrentEnvironment());
        assertEquals(EnvironmentType.PRODUCTION, environmentDetector.getEnvironmentType());
    }
}