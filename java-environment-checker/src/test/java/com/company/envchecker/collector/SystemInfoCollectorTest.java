package com.company.envchecker.collector;

import com.company.envchecker.model.SystemInfo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 系统信息收集器测试类
 */
class SystemInfoCollectorTest {

    private SystemInfoCollector collector;

    @BeforeEach
    void setUp() {
        collector = new SystemInfoCollector();
    }

    @Test
    void collectSystemInfo_ShouldReturnValidSystemInfo() {
        // Act
        SystemInfo systemInfo = collector.collectSystemInfo();

        // Assert
        assertNotNull(systemInfo);
        assertNotNull(systemInfo.getOperatingSystem());
        assertNotNull(systemInfo.getArchitecture());
        assertNotNull(systemInfo.getUserName());
        assertNotNull(systemInfo.getUserHome());
        assertNotNull(systemInfo.getWorkingDirectory());
        assertNotNull(systemInfo.getTempDirectory());
        assertNotNull(systemInfo.getFileEncoding());
        
        // 验证值不为空字符串
        assertFalse(systemInfo.getOperatingSystem().trim().isEmpty());
        assertFalse(systemInfo.getArchitecture().trim().isEmpty());
        assertFalse(systemInfo.getUserName().trim().isEmpty());
    }

    @Test
    void getDetailedOSInfo_ShouldReturnFormattedOSInfo() {
        // Act
        String osInfo = collector.getDetailedOSInfo();

        // Assert
        assertNotNull(osInfo);
        assertFalse(osInfo.trim().isEmpty());
        assertTrue(osInfo.contains(System.getProperty("os.name")));
    }

    @Test
    void getMemoryInfo_ShouldReturnFormattedMemoryInfo() {
        // Act
        String memoryInfo = collector.getMemoryInfo();

        // Assert
        assertNotNull(memoryInfo);
        assertFalse(memoryInfo.trim().isEmpty());
        assertTrue(memoryInfo.contains("Total:"));
        assertTrue(memoryInfo.contains("MB"));
    }

    @Test
    void isWindows_ShouldReturnCorrectResult() {
        // Act
        boolean result = collector.isWindows();
        
        // Assert
        String osName = System.getProperty("os.name", "").toLowerCase();
        assertEquals(osName.contains("windows"), result);
    }

    @Test
    void isMacOS_ShouldReturnCorrectResult() {
        // Act
        boolean result = collector.isMacOS();
        
        // Assert
        String osName = System.getProperty("os.name", "").toLowerCase();
        boolean expected = osName.contains("mac") || osName.contains("darwin");
        assertEquals(expected, result);
    }

    @Test
    void isLinux_ShouldReturnCorrectResult() {
        // Act
        boolean result = collector.isLinux();
        
        // Assert
        String osName = System.getProperty("os.name", "").toLowerCase();
        assertEquals(osName.contains("linux"), result);
    }

    @Test
    void getPathSeparator_ShouldReturnValidSeparator() {
        // Act
        String pathSeparator = collector.getPathSeparator();

        // Assert
        assertNotNull(pathSeparator);
        assertFalse(pathSeparator.isEmpty());
        assertEquals(System.getProperty("path.separator"), pathSeparator);
    }

    @Test
    void getFileSeparator_ShouldReturnValidSeparator() {
        // Act
        String fileSeparator = collector.getFileSeparator();

        // Assert
        assertNotNull(fileSeparator);
        assertFalse(fileSeparator.isEmpty());
        assertEquals(System.getProperty("file.separator"), fileSeparator);
    }

    @Test
    void getLineSeparator_ShouldReturnValidSeparator() {
        // Act
        String lineSeparator = collector.getLineSeparator();

        // Assert
        assertNotNull(lineSeparator);
        assertFalse(lineSeparator.isEmpty());
        assertEquals(System.getProperty("line.separator"), lineSeparator);
    }
}