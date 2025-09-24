package com.company.envchecker.detector;

import com.company.envchecker.model.JavaEnvironmentInfo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Java版本检测器测试类
 */
class JavaVersionDetectorTest {

    private JavaVersionDetector detector;

    @BeforeEach
    void setUp() {
        detector = new JavaVersionDetector();
    }

    @Test
    void detectJavaEnvironment_ShouldReturnValidJavaInfo() {
        // Act
        JavaEnvironmentInfo javaInfo = detector.detectJavaEnvironment();

        // Assert
        assertNotNull(javaInfo);
        assertNotNull(javaInfo.getJavaVersion());
        assertNotNull(javaInfo.getJavaVendor());
        assertNotNull(javaInfo.getJavaHome());
        assertNotNull(javaInfo.getVmName());
        assertNotNull(javaInfo.getVmVersion());
        assertNotNull(javaInfo.getRuntimeName());
        
        // 验证值不为"Unknown"
        assertNotEquals("Unknown", javaInfo.getJavaVersion());
        assertNotEquals("Unknown", javaInfo.getJavaVendor());
        assertNotEquals("Unknown", javaInfo.getJavaHome());
    }

    @Test
    void getJavaMajorVersion_ShouldReturnValidVersion() {
        // Act
        int majorVersion = detector.getJavaMajorVersion();

        // Assert
        assertTrue(majorVersion > 0);
        assertTrue(majorVersion >= 8); // 假设至少是Java 8
    }

    @Test
    void supportsModules_ShouldReturnCorrectResult() {
        // Act
        boolean supportsModules = detector.supportsModules();
        int majorVersion = detector.getJavaMajorVersion();

        // Assert
        assertEquals(majorVersion >= 9, supportsModules);
    }

    @Test
    void isLTSVersion_ShouldReturnCorrectResult() {
        // Act
        boolean isLTS = detector.isLTSVersion();
        int majorVersion = detector.getJavaMajorVersion();

        // Assert
        boolean expectedLTS = majorVersion == 8 || majorVersion == 11 || 
                             majorVersion == 17 || majorVersion == 21;
        assertEquals(expectedLTS, isLTS);
    }

    @Test
    void getDetailedVersionInfo_ShouldReturnFormattedInfo() {
        // Act
        String versionInfo = detector.getDetailedVersionInfo();

        // Assert
        assertNotNull(versionInfo);
        assertFalse(versionInfo.trim().isEmpty());
        assertTrue(versionInfo.contains("Java Version:"));
        assertTrue(versionInfo.contains("JVM:"));
    }

    @Test
    void getJVMArguments_ShouldReturnString() {
        // Act
        String jvmArgs = detector.getJVMArguments();

        // Assert
        assertNotNull(jvmArgs);
        // JVM参数可能为空，但不应该为null
    }

    @Test
    void getJVMStartTime_ShouldReturnValidTime() {
        // Act
        long startTime = detector.getJVMStartTime();

        // Assert
        assertTrue(startTime > 0);
        assertTrue(startTime <= System.currentTimeMillis());
    }

    @Test
    void getJVMUptime_ShouldReturnPositiveValue() {
        // Act
        long uptime = detector.getJVMUptime();

        // Assert
        assertTrue(uptime > 0);
    }

    @Test
    void isOpenJDK_ShouldReturnBooleanResult() {
        // Act
        boolean isOpenJDK = detector.isOpenJDK();

        // Assert - 这只是检查方法能正常执行，不验证具体结果
        assertNotNull(isOpenJDK);
    }

    @Test
    void isOracleJDK_ShouldReturnBooleanResult() {
        // Act
        boolean isOracleJDK = detector.isOracleJDK();

        // Assert - 这只是检查方法能正常执行，不验证具体结果
        assertNotNull(isOracleJDK);
    }

    @Test
    void getCompilerInfo_ShouldReturnString() {
        // Act
        String compilerInfo = detector.getCompilerInfo();

        // Assert
        assertNotNull(compilerInfo);
        assertFalse(compilerInfo.trim().isEmpty());
    }
}