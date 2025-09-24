package com.company.envchecker.analyzer;

import com.company.envchecker.model.EnvironmentVariableInfo;
import java.util.Map;

/**
 * 环境变量分析器
 * 负责分析Java相关的环境变量配置
 */
public class EnvironmentVariableAnalyzer {

    /**
     * 分析环境变量信息
     * 
     * @return EnvironmentVariableInfo 包含环境变量详细信息的对象
     */
    public EnvironmentVariableInfo analyzeEnvironmentVariables() {
        EnvironmentVariableInfo envInfo = new EnvironmentVariableInfo();

        try {
            Map<String, String> envMap = System.getenv();

            // 分析关键Java环境变量
            envInfo.setJavaHome(getEnvironmentVariable("JAVA_HOME"));
            envInfo.setPathVariable(getEnvironmentVariable("PATH"));
            envInfo.setClassPath(getEnvironmentVariable("CLASSPATH"));
            envInfo.setJreHome(getEnvironmentVariable("JRE_HOME"));
            envInfo.setJavaOpts(getEnvironmentVariable("JAVA_OPTS"));

            // 分析构建工具环境变量
            envInfo.setMavenHome(getEnvironmentVariable("MAVEN_HOME"));
            envInfo.setGradleHome(getEnvironmentVariable("GRADLE_HOME"));
            envInfo.setM2Home(getEnvironmentVariable("M2_HOME"));
            envInfo.setAntHome(getEnvironmentVariable("ANT_HOME"));

        } catch (Exception e) {
            System.err.println("Error analyzing environment variables: " + e.getMessage());
        }

        return envInfo;
    }

    /**
     * 安全地获取环境变量
     * 
     * @param variableName 环境变量名称
     * @return 环境变量值，如果不存在则返回null
     */
    private String getEnvironmentVariable(String variableName) {
        try {
            return System.getenv(variableName);
        } catch (SecurityException e) {
            System.err.println("Security exception accessing environment variable: " + variableName);
            return null;
        }
    }

    /**
     * 检查JAVA_HOME是否设置且有效
     * 
     * @return true 如果JAVA_HOME设置且指向有效目录
     */
    public boolean isJavaHomeValid() {
        String javaHome = getEnvironmentVariable("JAVA_HOME");
        if (javaHome == null || javaHome.trim().isEmpty()) {
            return false;
        }

        java.io.File javaHomeDir = new java.io.File(javaHome);
        if (!javaHomeDir.exists() || !javaHomeDir.isDirectory()) {
            return false;
        }

        // 检查是否包含bin目录
        java.io.File binDir = new java.io.File(javaHomeDir, "bin");
        return binDir.exists() && binDir.isDirectory();
    }

    /**
     * 检查PATH是否包含Java可执行文件路径
     * 
     * @return true 如果PATH包含Java路径
     */
    public boolean isJavaInPath() {
        String path = getEnvironmentVariable("PATH");
        if (path == null) {
            return false;
        }

        String javaHome = getEnvironmentVariable("JAVA_HOME");
        if (javaHome != null) {
            String javaBinPath = javaHome + java.io.File.separator + "bin";
            return path.contains(javaBinPath);
        }

        // 检查PATH中是否有其他Java路径
        String pathSeparator = System.getProperty("path.separator", ":");
        String[] pathEntries = path.split(pathSeparator);
        
        for (String pathEntry : pathEntries) {
            java.io.File javaExe = new java.io.File(pathEntry, "java");
            java.io.File javaExeWindows = new java.io.File(pathEntry, "java.exe");
            if (javaExe.exists() || javaExeWindows.exists()) {
                return true;
            }
        }

        return false;
    }

    /**
     * 获取PATH中的所有Java可执行文件路径
     * 
     * @return Java可执行文件路径列表
     */
    public java.util.List<String> getJavaExecutablePaths() {
        java.util.List<String> javaPaths = new java.util.ArrayList<>();
        String path = getEnvironmentVariable("PATH");
        
        if (path == null) {
            return javaPaths;
        }

        String pathSeparator = System.getProperty("path.separator", ":");
        String[] pathEntries = path.split(pathSeparator);
        
        for (String pathEntry : pathEntries) {
            java.io.File javaExe = new java.io.File(pathEntry, "java");
            java.io.File javaExeWindows = new java.io.File(pathEntry, "java.exe");
            
            if (javaExe.exists()) {
                javaPaths.add(javaExe.getAbsolutePath());
            } else if (javaExeWindows.exists()) {
                javaPaths.add(javaExeWindows.getAbsolutePath());
            }
        }

        return javaPaths;
    }

    /**
     * 检查环境变量是否存在冲突
     * 
     * @return 冲突描述列表
     */
    public java.util.List<String> checkEnvironmentConflicts() {
        java.util.List<String> conflicts = new java.util.ArrayList<>();

        String javaHome = getEnvironmentVariable("JAVA_HOME");
        String jreHome = getEnvironmentVariable("JRE_HOME");

        // 检查JAVA_HOME和JRE_HOME冲突
        if (javaHome != null && jreHome != null) {
            if (!javaHome.equals(jreHome) && !jreHome.startsWith(javaHome)) {
                conflicts.add("JAVA_HOME and JRE_HOME point to different locations");
            }
        }

        // 检查MAVEN_HOME和M2_HOME冲突
        String mavenHome = getEnvironmentVariable("MAVEN_HOME");
        String m2Home = getEnvironmentVariable("M2_HOME");
        if (mavenHome != null && m2Home != null && !mavenHome.equals(m2Home)) {
            conflicts.add("MAVEN_HOME and M2_HOME have different values");
        }

        return conflicts;
    }

    /**
     * 获取所有Java相关的环境变量
     * 
     * @return Java相关环境变量的映射
     */
    public Map<String, String> getAllJavaRelatedEnvironmentVariables() {
        Map<String, String> javaEnvVars = new java.util.HashMap<>();
        Map<String, String> allEnvVars = System.getenv();

        // 预定义的Java相关环境变量
        String[] javaRelatedVars = {
            "JAVA_HOME", "JRE_HOME", "JAVA_OPTS", "JAVA_TOOL_OPTIONS",
            "CLASSPATH", "MAVEN_HOME", "M2_HOME", "GRADLE_HOME", 
            "ANT_HOME", "SCALA_HOME", "KOTLIN_HOME"
        };

        for (String varName : javaRelatedVars) {
            String value = allEnvVars.get(varName);
            if (value != null) {
                javaEnvVars.put(varName, value);
            }
        }

        // 查找其他可能的Java相关变量
        for (Map.Entry<String, String> entry : allEnvVars.entrySet()) {
            String key = entry.getKey().toLowerCase();
            if ((key.contains("java") || key.contains("jdk") || key.contains("jre")) 
                && !javaEnvVars.containsKey(entry.getKey())) {
                javaEnvVars.put(entry.getKey(), entry.getValue());
            }
        }

        return javaEnvVars;
    }

    /**
     * 验证构建工具环境变量
     * 
     * @param toolName 工具名称 (maven, gradle, ant)
     * @return 验证结果描述
     */
    public String validateBuildToolEnvironment(String toolName) {
        String homeVar = null;
        String executableName = null;

        switch (toolName.toLowerCase()) {
            case "maven":
                homeVar = getEnvironmentVariable("MAVEN_HOME");
                if (homeVar == null) {
                    homeVar = getEnvironmentVariable("M2_HOME");
                }
                executableName = isWindows() ? "mvn.cmd" : "mvn";
                break;
            case "gradle":
                homeVar = getEnvironmentVariable("GRADLE_HOME");
                executableName = isWindows() ? "gradle.bat" : "gradle";
                break;
            case "ant":
                homeVar = getEnvironmentVariable("ANT_HOME");
                executableName = isWindows() ? "ant.bat" : "ant";
                break;
            default:
                return "Unknown build tool: " + toolName;
        }

        if (homeVar == null) {
            return toolName + " home directory not set in environment variables";
        }

        java.io.File homeDir = new java.io.File(homeVar);
        if (!homeDir.exists() || !homeDir.isDirectory()) {
            return toolName + " home directory does not exist: " + homeVar;
        }

        java.io.File executable = new java.io.File(homeDir, "bin" + java.io.File.separator + executableName);
        if (!executable.exists()) {
            return toolName + " executable not found: " + executable.getAbsolutePath();
        }

        return toolName + " environment is valid";
    }

    /**
     * 检查是否为Windows系统
     * 
     * @return true 如果是Windows系统
     */
    private boolean isWindows() {
        String osName = System.getProperty("os.name", "").toLowerCase();
        return osName.contains("windows");
    }
}