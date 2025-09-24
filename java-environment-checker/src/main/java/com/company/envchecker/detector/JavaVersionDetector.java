package com.company.envchecker.detector;

import com.company.envchecker.model.JavaEnvironmentInfo;

/**
 * Java版本检测器
 * 负责检测当前运行的Java版本和JVM相关信息
 */
public class JavaVersionDetector {

    /**
     * 检测Java环境信息
     * 
     * @return JavaEnvironmentInfo 包含Java环境详细信息的对象
     */
    public JavaEnvironmentInfo detectJavaEnvironment() {
        JavaEnvironmentInfo javaInfo = new JavaEnvironmentInfo();

        try {
            // 收集Java版本信息
            javaInfo.setJavaVersion(getSystemProperty("java.version", "Unknown"));
            javaInfo.setJavaSpecVersion(getSystemProperty("java.specification.version", "Unknown"));
            javaInfo.setJavaVendor(getSystemProperty("java.vendor", "Unknown"));
            javaInfo.setJavaHome(getSystemProperty("java.home", "Unknown"));

            // 收集JVM信息
            javaInfo.setVmName(getSystemProperty("java.vm.name", "Unknown"));
            javaInfo.setVmVersion(getSystemProperty("java.vm.version", "Unknown"));
            javaInfo.setVmVendor(getSystemProperty("java.vm.vendor", "Unknown"));

            // 收集运行时信息
            javaInfo.setRuntimeName(getSystemProperty("java.runtime.name", "Unknown"));
            javaInfo.setRuntimeVersion(getSystemProperty("java.runtime.version", "Unknown"));

            // 收集路径信息
            javaInfo.setClassPath(getSystemProperty("java.class.path", ""));
            javaInfo.setLibraryPath(getSystemProperty("java.library.path", ""));
            javaInfo.setBootClassPath(getSystemProperty("sun.boot.class.path", ""));

        } catch (Exception e) {
            System.err.println("Error detecting Java environment: " + e.getMessage());
        }

        return javaInfo;
    }

    /**
     * 安全地获取系统属性
     * 
     * @param propertyName 属性名称
     * @param defaultValue 默认值
     * @return 属性值或默认值
     */
    private String getSystemProperty(String propertyName, String defaultValue) {
        try {
            String value = System.getProperty(propertyName);
            return value != null ? value : defaultValue;
        } catch (SecurityException e) {
            System.err.println("Security exception accessing property: " + propertyName);
            return defaultValue;
        }
    }

    /**
     * 获取Java主版本号
     * 
     * @return Java主版本号
     */
    public int getJavaMajorVersion() {
        String version = getSystemProperty("java.specification.version", "0");
        try {
            // Java 9+ 使用单一版本号 (9, 10, 11, ...)
            // Java 8及以下使用 1.x 格式 (1.8, 1.7, ...)
            if (version.startsWith("1.")) {
                return Integer.parseInt(version.substring(2, 3));
            } else {
                return Integer.parseInt(version.split("\\.")[0]);
            }
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    /**
     * 检查当前Java版本是否支持模块系统 (Java 9+)
     * 
     * @return true 如果支持模块系统
     */
    public boolean supportsModules() {
        return getJavaMajorVersion() >= 9;
    }

    /**
     * 检查当前Java版本是否为LTS版本
     * 
     * @return true 如果是LTS版本
     */
    public boolean isLTSVersion() {
        int majorVersion = getJavaMajorVersion();
        // LTS版本: 8, 11, 17, 21, ...
        return majorVersion == 8 || majorVersion == 11 || majorVersion == 17 || majorVersion == 21;
    }

    /**
     * 获取详细的Java版本描述
     * 
     * @return 格式化的Java版本信息
     */
    public String getDetailedVersionInfo() {
        StringBuilder versionInfo = new StringBuilder();
        
        String version = getSystemProperty("java.version", "Unknown");
        String vendor = getSystemProperty("java.vendor", "Unknown");
        String vmName = getSystemProperty("java.vm.name", "Unknown");
        
        versionInfo.append("Java Version: ").append(version);
        if (!"Unknown".equals(vendor)) {
            versionInfo.append(" (").append(vendor).append(")");
        }
        versionInfo.append("\nJVM: ").append(vmName);
        
        if (isLTSVersion()) {
            versionInfo.append(" [LTS]");
        }
        
        return versionInfo.toString();
    }

    /**
     * 获取JVM启动参数
     * 
     * @return JVM启动参数列表
     */
    public String getJVMArguments() {
        try {
            java.lang.management.RuntimeMXBean runtimeMxBean = 
                java.lang.management.ManagementFactory.getRuntimeMXBean();
            java.util.List<String> arguments = runtimeMxBean.getInputArguments();
            return String.join(" ", arguments);
        } catch (Exception e) {
            return "Unable to retrieve JVM arguments: " + e.getMessage();
        }
    }

    /**
     * 获取JVM启动时间
     * 
     * @return JVM启动时间（毫秒）
     */
    public long getJVMStartTime() {
        try {
            java.lang.management.RuntimeMXBean runtimeMxBean = 
                java.lang.management.ManagementFactory.getRuntimeMXBean();
            return runtimeMxBean.getStartTime();
        } catch (Exception e) {
            return 0;
        }
    }

    /**
     * 获取JVM运行时长
     * 
     * @return JVM运行时长（毫秒）
     */
    public long getJVMUptime() {
        try {
            java.lang.management.RuntimeMXBean runtimeMxBean = 
                java.lang.management.ManagementFactory.getRuntimeMXBean();
            return runtimeMxBean.getUptime();
        } catch (Exception e) {
            return 0;
        }
    }

    /**
     * 检查是否为OpenJDK
     * 
     * @return true 如果是OpenJDK
     */
    public boolean isOpenJDK() {
        String vmName = getSystemProperty("java.vm.name", "").toLowerCase();
        String vendor = getSystemProperty("java.vendor", "").toLowerCase();
        return vmName.contains("openjdk") || vendor.contains("openjdk");
    }

    /**
     * 检查是否为Oracle JDK
     * 
     * @return true 如果是Oracle JDK
     */
    public boolean isOracleJDK() {
        String vendor = getSystemProperty("java.vendor", "").toLowerCase();
        return vendor.contains("oracle");
    }

    /**
     * 获取Java编译器信息
     * 
     * @return 编译器信息，如果不可用则返回空字符串
     */
    public String getCompilerInfo() {
        try {
            javax.tools.JavaCompiler compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
            if (compiler != null) {
                return "Java Compiler available: " + compiler.getClass().getName();
            } else {
                return "Java Compiler not available (JRE only)";
            }
        } catch (Exception e) {
            return "Unable to check compiler availability: " + e.getMessage();
        }
    }
}