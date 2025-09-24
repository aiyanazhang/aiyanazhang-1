package com.company.envchecker.diagnostic;

import com.company.envchecker.model.DiagnosticResult;
import com.company.envchecker.model.JavaInstallationInfo;
import com.company.envchecker.model.EnvironmentVariableInfo;
import com.company.envchecker.model.JavaEnvironmentInfo;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 环境诊断引擎
 * 负责诊断Java环境配置问题并提供解决建议
 */
public class EnvironmentDiagnostic {

    /**
     * 执行完整的环境诊断
     * 
     * @param javaEnvironmentInfo Java环境信息
     * @param environmentVariableInfo 环境变量信息
     * @param javaInstallations Java安装列表
     * @return 诊断结果列表
     */
    public List<DiagnosticResult> diagnose(JavaEnvironmentInfo javaEnvironmentInfo,
                                         EnvironmentVariableInfo environmentVariableInfo,
                                         List<JavaInstallationInfo> javaInstallations) {
        List<DiagnosticResult> results = new ArrayList<>();

        // 基础配置诊断
        results.addAll(diagnoseBasicConfiguration(environmentVariableInfo));
        
        // Java版本诊断
        results.addAll(diagnoseJavaVersion(javaEnvironmentInfo));
        
        // 路径配置诊断
        results.addAll(diagnosePathConfiguration(environmentVariableInfo));
        
        // 安装版本诊断
        results.addAll(diagnoseInstallations(javaInstallations));
        
        // 兼容性诊断
        results.addAll(diagnoseCompatibility(javaEnvironmentInfo, javaInstallations));

        return results;
    }

    /**
     * 诊断基础配置
     * 
     * @param envInfo 环境变量信息
     * @return 诊断结果列表
     */
    public List<DiagnosticResult> diagnoseBasicConfiguration(EnvironmentVariableInfo envInfo) {
        List<DiagnosticResult> results = new ArrayList<>();

        // 检查JAVA_HOME配置
        if (envInfo.getJavaHome() == null || envInfo.getJavaHome().trim().isEmpty()) {
            results.add(new DiagnosticResult(
                "Basic Configuration",
                DiagnosticResult.Level.WARN,
                "JAVA_HOME environment variable is not set",
                "Set JAVA_HOME to your Java installation directory (e.g., export JAVA_HOME=/path/to/java)",
                "JAVA_HOME",
                "JAVA_HOME_CHECK"
            ));
        } else {
            File javaHomeDir = new File(envInfo.getJavaHome());
            if (!javaHomeDir.exists()) {
                results.add(new DiagnosticResult(
                    "Basic Configuration",
                    DiagnosticResult.Level.ERROR,
                    "JAVA_HOME points to non-existent directory: " + envInfo.getJavaHome(),
                    "Update JAVA_HOME to point to a valid Java installation directory",
                    "JAVA_HOME",
                    "JAVA_HOME_VALIDITY_CHECK"
                ));
            } else if (!javaHomeDir.isDirectory()) {
                results.add(new DiagnosticResult(
                    "Basic Configuration",
                    DiagnosticResult.Level.ERROR,
                    "JAVA_HOME points to a file, not a directory: " + envInfo.getJavaHome(),
                    "Update JAVA_HOME to point to a directory",
                    "JAVA_HOME",
                    "JAVA_HOME_TYPE_CHECK"
                ));
            } else {
                // 检查JAVA_HOME结构
                File binDir = new File(javaHomeDir, "bin");
                if (!binDir.exists()) {
                    results.add(new DiagnosticResult(
                        "Basic Configuration",
                        DiagnosticResult.Level.ERROR,
                        "JAVA_HOME does not contain a 'bin' directory",
                        "Ensure JAVA_HOME points to the root of a Java installation",
                        "JAVA_HOME",
                        "JAVA_HOME_STRUCTURE_CHECK"
                    ));
                }
            }
        }

        // 检查PATH配置
        if (envInfo.getPathVariable() == null || envInfo.getPathVariable().trim().isEmpty()) {
            results.add(new DiagnosticResult(
                "Basic Configuration",
                DiagnosticResult.Level.ERROR,
                "PATH environment variable is not set",
                "Ensure PATH environment variable is properly set",
                "PATH",
                "PATH_CHECK"
            ));
        } else if (envInfo.getJavaHome() != null) {
            String expectedJavaPath = envInfo.getJavaHome() + File.separator + "bin";
            if (!envInfo.getPathVariable().contains(expectedJavaPath)) {
                results.add(new DiagnosticResult(
                    "Basic Configuration",
                    DiagnosticResult.Level.WARN,
                    "PATH does not contain Java bin directory",
                    "Add " + expectedJavaPath + " to your PATH variable",
                    "PATH",
                    "PATH_JAVA_CHECK"
                ));
            }
        }

        return results;
    }

    /**
     * 诊断Java版本
     * 
     * @param javaInfo Java环境信息
     * @return 诊断结果列表
     */
    public List<DiagnosticResult> diagnoseJavaVersion(JavaEnvironmentInfo javaInfo) {
        List<DiagnosticResult> results = new ArrayList<>();

        String version = javaInfo.getJavaSpecVersion();
        if (version == null || "Unknown".equals(version)) {
            results.add(new DiagnosticResult(
                "Java Version",
                DiagnosticResult.Level.ERROR,
                "Unable to determine Java version",
                "Verify Java installation and try running 'java -version'",
                "Java Runtime",
                "VERSION_DETECTION"
            ));
            return results;
        }

        try {
            int majorVersion = getMajorVersion(version);
            
            // 检查是否为过旧版本
            if (majorVersion < 8) {
                results.add(new DiagnosticResult(
                    "Java Version",
                    DiagnosticResult.Level.ERROR,
                    "Java version " + version + " is no longer supported",
                    "Upgrade to Java 8 or later for security and feature updates",
                    "Java Runtime",
                    "OBSOLETE_VERSION"
                ));
            } else if (majorVersion == 8) {
                results.add(new DiagnosticResult(
                    "Java Version",
                    DiagnosticResult.Level.INFO,
                    "Using Java 8 (LTS version)",
                    "Consider upgrading to Java 11, 17, or 21 for improved performance and features",
                    "Java Runtime",
                    "LTS_VERSION_INFO"
                ));
            } else if (isLTSVersion(majorVersion)) {
                results.add(new DiagnosticResult(
                    "Java Version",
                    DiagnosticResult.Level.INFO,
                    "Using Java " + majorVersion + " (LTS version)",
                    "You are using a Long Term Support version - excellent choice!",
                    "Java Runtime",
                    "LTS_VERSION_INFO"
                ));
            } else {
                results.add(new DiagnosticResult(
                    "Java Version",
                    DiagnosticResult.Level.WARN,
                    "Using Java " + majorVersion + " (non-LTS version)",
                    "Consider using an LTS version (8, 11, 17, 21) for production environments",
                    "Java Runtime",
                    "NON_LTS_VERSION"
                ));
            }

        } catch (NumberFormatException e) {
            results.add(new DiagnosticResult(
                "Java Version",
                DiagnosticResult.Level.WARN,
                "Unable to parse Java version: " + version,
                "Verify Java installation integrity",
                "Java Runtime",
                "VERSION_PARSE_ERROR"
            ));
        }

        return results;
    }

    /**
     * 诊断路径配置
     * 
     * @param envInfo 环境变量信息
     * @return 诊断结果列表
     */
    public List<DiagnosticResult> diagnosePathConfiguration(EnvironmentVariableInfo envInfo) {
        List<DiagnosticResult> results = new ArrayList<>();

        // 检查CLASSPATH配置
        if (envInfo.getClassPath() != null && !envInfo.getClassPath().trim().isEmpty()) {
            String[] classpathEntries = envInfo.getClassPath().split(File.pathSeparator);
            int invalidEntries = 0;
            
            for (String entry : classpathEntries) {
                if (entry.trim().isEmpty()) continue;
                File file = new File(entry);
                if (!file.exists()) {
                    invalidEntries++;
                }
            }
            
            if (invalidEntries > 0) {
                results.add(new DiagnosticResult(
                    "Path Configuration",
                    DiagnosticResult.Level.WARN,
                    "CLASSPATH contains " + invalidEntries + " invalid entries",
                    "Remove non-existent paths from CLASSPATH or ensure all paths are accessible",
                    "CLASSPATH",
                    "CLASSPATH_VALIDITY"
                ));
            }
        }

        // 检查冲突的环境变量
        if (envInfo.getJavaHome() != null && envInfo.getJreHome() != null) {
            if (!envInfo.getJavaHome().equals(envInfo.getJreHome())) {
                results.add(new DiagnosticResult(
                    "Path Configuration",
                    DiagnosticResult.Level.WARN,
                    "JAVA_HOME and JRE_HOME point to different locations",
                    "Ensure JAVA_HOME and JRE_HOME are consistent or remove JRE_HOME",
                    "Environment Variables",
                    "HOME_CONFLICT"
                ));
            }
        }

        return results;
    }

    /**
     * 诊断Java安装
     * 
     * @param installations Java安装列表
     * @return 诊断结果列表
     */
    public List<DiagnosticResult> diagnoseInstallations(List<JavaInstallationInfo> installations) {
        List<DiagnosticResult> results = new ArrayList<>();

        if (installations.isEmpty()) {
            results.add(new DiagnosticResult(
                "Java Installations",
                DiagnosticResult.Level.ERROR,
                "No Java installations found",
                "Install Java from Oracle, OpenJDK, or other vendors",
                "Java Installation",
                "NO_INSTALLATIONS"
            ));
            return results;
        }

        // 检查是否有活动安装
        boolean hasActiveInstallation = installations.stream().anyMatch(JavaInstallationInfo::isActive);
        if (!hasActiveInstallation) {
            results.add(new DiagnosticResult(
                "Java Installations",
                DiagnosticResult.Level.WARN,
                "No active Java installation detected",
                "Set JAVA_HOME to point to your preferred Java installation",
                "Java Installation",
                "NO_ACTIVE_INSTALLATION"
            ));
        }

        // 检查多版本安装
        if (installations.size() > 1) {
            results.add(new DiagnosticResult(
                "Java Installations",
                DiagnosticResult.Level.INFO,
                "Multiple Java installations found (" + installations.size() + " installations)",
                "Use JAVA_HOME to specify which installation to use",
                "Java Installation",
                "MULTIPLE_INSTALLATIONS"
            ));
        }

        // 检查JRE vs JDK
        long jreCount = installations.stream()
            .filter(install -> "JRE".equals(install.getType()))
            .count();
        long jdkCount = installations.stream()
            .filter(install -> "JDK".equals(install.getType()))
            .count();

        if (jdkCount == 0 && jreCount > 0) {
            results.add(new DiagnosticResult(
                "Java Installations",
                DiagnosticResult.Level.WARN,
                "Only JRE installations found, no JDK",
                "Install a JDK if you need to compile Java code",
                "Java Installation",
                "NO_JDK_FOUND"
            ));
        }

        return results;
    }

    /**
     * 诊断兼容性问题
     * 
     * @param javaInfo Java环境信息
     * @param installations Java安装列表
     * @return 诊断结果列表
     */
    public List<DiagnosticResult> diagnoseCompatibility(JavaEnvironmentInfo javaInfo, 
                                                       List<JavaInstallationInfo> installations) {
        List<DiagnosticResult> results = new ArrayList<>();

        // 检查JAVA_HOME和当前运行Java版本是否匹配
        String runtimeJavaHome = javaInfo.getJavaHome();
        String envJavaHome = System.getenv("JAVA_HOME");

        if (envJavaHome != null && runtimeJavaHome != null && !runtimeJavaHome.equals(envJavaHome)) {
            results.add(new DiagnosticResult(
                "Compatibility",
                DiagnosticResult.Level.WARN,
                "JAVA_HOME and current runtime Java installation don't match",
                "Ensure JAVA_HOME points to the Java installation you want to use",
                "Environment Configuration",
                "JAVA_HOME_MISMATCH"
            ));
        }

        // 检查架构兼容性
        String osArch = System.getProperty("os.arch", "unknown");
        for (JavaInstallationInfo installation : installations) {
            if (installation.isActive() && installation.getArchitecture() != null) {
                if (!installation.getArchitecture().equals(osArch) && 
                    !areArchitecturesCompatible(osArch, installation.getArchitecture())) {
                    results.add(new DiagnosticResult(
                        "Compatibility",
                        DiagnosticResult.Level.WARN,
                        "Java architecture (" + installation.getArchitecture() + 
                        ") may not be optimal for system architecture (" + osArch + ")",
                        "Consider using a Java installation that matches your system architecture",
                        "Architecture",
                        "ARCHITECTURE_MISMATCH"
                    ));
                }
            }
        }

        return results;
    }

    /**
     * 获取主版本号
     */
    private int getMajorVersion(String version) {
        if (version.startsWith("1.")) {
            return Integer.parseInt(version.substring(2, 3));
        } else {
            return Integer.parseInt(version.split("\\.")[0]);
        }
    }

    /**
     * 检查是否为LTS版本
     */
    private boolean isLTSVersion(int majorVersion) {
        return majorVersion == 8 || majorVersion == 11 || majorVersion == 17 || majorVersion == 21;
    }

    /**
     * 检查架构兼容性
     */
    private boolean areArchitecturesCompatible(String osArch, String javaArch) {
        // 简化的架构兼容性检查
        if (osArch.equals(javaArch)) {
            return true;
        }
        
        // x86_64 和 amd64 是兼容的
        if ((osArch.equals("x86_64") && javaArch.equals("amd64")) ||
            (osArch.equals("amd64") && javaArch.equals("x86_64"))) {
            return true;
        }
        
        return false;
    }
}