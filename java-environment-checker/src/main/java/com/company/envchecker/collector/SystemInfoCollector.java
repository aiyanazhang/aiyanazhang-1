package com.company.envchecker.collector;

import com.company.envchecker.model.SystemInfo;

/**
 * 系统信息收集器
 * 负责收集操作系统和硬件相关信息
 */
public class SystemInfoCollector {

    /**
     * 收集系统信息
     * 
     * @return SystemInfo 包含系统详细信息的对象
     */
    public SystemInfo collectSystemInfo() {
        SystemInfo systemInfo = new SystemInfo();

        try {
            // 收集操作系统信息
            systemInfo.setOperatingSystem(getSystemProperty("os.name", "Unknown"));
            systemInfo.setOsVersion(getSystemProperty("os.version", "Unknown"));
            systemInfo.setArchitecture(getSystemProperty("os.arch", "Unknown"));

            // 收集用户信息
            systemInfo.setUserName(getSystemProperty("user.name", "Unknown"));
            systemInfo.setUserHome(getSystemProperty("user.home", "Unknown"));
            systemInfo.setWorkingDirectory(getSystemProperty("user.dir", "Unknown"));

            // 收集系统目录信息
            systemInfo.setTempDirectory(getSystemProperty("java.io.tmpdir", "Unknown"));

            // 收集编码信息
            systemInfo.setFileEncoding(getSystemProperty("file.encoding", "Unknown"));
            systemInfo.setSystemEncoding(getSystemProperty("sun.jnu.encoding", "Unknown"));

        } catch (Exception e) {
            System.err.println("Error collecting system information: " + e.getMessage());
        }

        return systemInfo;
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
     * 获取详细的操作系统信息
     * 
     * @return 格式化的操作系统描述
     */
    public String getDetailedOSInfo() {
        StringBuilder osInfo = new StringBuilder();
        
        String osName = getSystemProperty("os.name", "Unknown");
        String osVersion = getSystemProperty("os.version", "Unknown");
        String osArch = getSystemProperty("os.arch", "Unknown");
        
        osInfo.append(osName);
        if (!"Unknown".equals(osVersion)) {
            osInfo.append(" ").append(osVersion);
        }
        if (!"Unknown".equals(osArch)) {
            osInfo.append(" (").append(osArch).append(")");
        }
        
        return osInfo.toString();
    }

    /**
     * 获取系统内存信息
     * 
     * @return 格式化的内存信息字符串
     */
    public String getMemoryInfo() {
        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        long maxMemory = runtime.maxMemory();
        long usedMemory = totalMemory - freeMemory;

        return String.format("Total: %d MB, Used: %d MB, Free: %d MB, Max: %d MB",
                           totalMemory / (1024 * 1024),
                           usedMemory / (1024 * 1024),
                           freeMemory / (1024 * 1024),
                           maxMemory / (1024 * 1024));
    }

    /**
     * 检查系统是否为Windows
     * 
     * @return true 如果是Windows系统
     */
    public boolean isWindows() {
        String osName = getSystemProperty("os.name", "").toLowerCase();
        return osName.contains("windows");
    }

    /**
     * 检查系统是否为macOS
     * 
     * @return true 如果是macOS系统
     */
    public boolean isMacOS() {
        String osName = getSystemProperty("os.name", "").toLowerCase();
        return osName.contains("mac") || osName.contains("darwin");
    }

    /**
     * 检查系统是否为Linux
     * 
     * @return true 如果是Linux系统
     */
    public boolean isLinux() {
        String osName = getSystemProperty("os.name", "").toLowerCase();
        return osName.contains("linux");
    }

    /**
     * 检查系统是否为Unix类系统
     * 
     * @return true 如果是Unix类系统
     */
    public boolean isUnix() {
        String osName = getSystemProperty("os.name", "").toLowerCase();
        return osName.contains("unix") || osName.contains("aix") || osName.contains("sunos");
    }

    /**
     * 获取系统路径分隔符
     * 
     * @return 系统路径分隔符
     */
    public String getPathSeparator() {
        return getSystemProperty("path.separator", ":");
    }

    /**
     * 获取文件分隔符
     * 
     * @return 文件分隔符
     */
    public String getFileSeparator() {
        return getSystemProperty("file.separator", "/");
    }

    /**
     * 获取行分隔符
     * 
     * @return 行分隔符
     */
    public String getLineSeparator() {
        return getSystemProperty("line.separator", "\n");
    }
}