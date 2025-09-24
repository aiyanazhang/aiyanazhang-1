package com.company.envchecker.formatter;

import com.company.envchecker.model.*;

import java.util.List;

/**
 * 控制台输出格式化器
 * 负责将检查结果格式化为控制台友好的文本输出
 */
public class ConsoleOutputFormatter {

    private static final String SEPARATOR = "=" + "=".repeat(79);
    private static final String SUB_SEPARATOR = "-" + "-".repeat(39);

    /**
     * 格式化完整的环境报告
     * 
     * @param report 环境报告
     * @return 格式化后的字符串
     */
    public String formatReport(EnvironmentReport report) {
        StringBuilder output = new StringBuilder();

        output.append(SEPARATOR).append("\n");
        output.append("Java Environment Check Report\n");
        output.append("Generated at: ").append(new java.util.Date(report.getCheckTimestamp())).append("\n");
        if (report.getCheckDuration() != null) {
            output.append("Check Duration: ").append(report.getCheckDuration()).append("\n");
        }
        output.append(SEPARATOR).append("\n\n");

        // 系统信息
        if (report.getSystemInfo() != null) {
            output.append(formatSystemInfo(report.getSystemInfo()));
            output.append("\n");
        }

        // Java环境信息
        if (report.getJavaEnvironmentInfo() != null) {
            output.append(formatJavaEnvironmentInfo(report.getJavaEnvironmentInfo()));
            output.append("\n");
        }

        // 环境变量信息
        if (report.getEnvironmentVariableInfo() != null) {
            output.append(formatEnvironmentVariableInfo(report.getEnvironmentVariableInfo()));
            output.append("\n");
        }

        // Java安装信息
        if (report.getJavaInstallations() != null && !report.getJavaInstallations().isEmpty()) {
            output.append(formatJavaInstallations(report.getJavaInstallations()));
            output.append("\n");
        }

        // 诊断结果
        if (report.getDiagnosticResults() != null && !report.getDiagnosticResults().isEmpty()) {
            output.append(formatDiagnosticResults(report.getDiagnosticResults()));
        }

        return output.toString();
    }

    /**
     * 格式化系统信息
     * 
     * @param systemInfo 系统信息
     * @return 格式化后的字符串
     */
    public String formatSystemInfo(SystemInfo systemInfo) {
        StringBuilder output = new StringBuilder();
        
        output.append("SYSTEM INFORMATION\n");
        output.append(SUB_SEPARATOR).append("\n");
        output.append(String.format("%-20s: %s\n", "Operating System", 
                     formatValue(systemInfo.getOperatingSystem())));
        output.append(String.format("%-20s: %s\n", "OS Version", 
                     formatValue(systemInfo.getOsVersion())));
        output.append(String.format("%-20s: %s\n", "Architecture", 
                     formatValue(systemInfo.getArchitecture())));
        output.append(String.format("%-20s: %s\n", "User Name", 
                     formatValue(systemInfo.getUserName())));
        output.append(String.format("%-20s: %s\n", "User Home", 
                     formatValue(systemInfo.getUserHome())));
        output.append(String.format("%-20s: %s\n", "Working Directory", 
                     formatValue(systemInfo.getWorkingDirectory())));
        output.append(String.format("%-20s: %s\n", "Temp Directory", 
                     formatValue(systemInfo.getTempDirectory())));
        output.append(String.format("%-20s: %s\n", "File Encoding", 
                     formatValue(systemInfo.getFileEncoding())));
        output.append(String.format("%-20s: %s\n", "System Encoding", 
                     formatValue(systemInfo.getSystemEncoding())));

        return output.toString();
    }

    /**
     * 格式化Java环境信息
     * 
     * @param javaInfo Java环境信息
     * @return 格式化后的字符串
     */
    public String formatJavaEnvironmentInfo(JavaEnvironmentInfo javaInfo) {
        StringBuilder output = new StringBuilder();
        
        output.append("JAVA ENVIRONMENT\n");
        output.append(SUB_SEPARATOR).append("\n");
        output.append(String.format("%-20s: %s\n", "Java Version", 
                     formatValue(javaInfo.getJavaVersion())));
        output.append(String.format("%-20s: %s\n", "Spec Version", 
                     formatValue(javaInfo.getJavaSpecVersion())));
        output.append(String.format("%-20s: %s\n", "Vendor", 
                     formatValue(javaInfo.getJavaVendor())));
        output.append(String.format("%-20s: %s\n", "Java Home", 
                     formatValue(javaInfo.getJavaHome())));
        output.append(String.format("%-20s: %s\n", "VM Name", 
                     formatValue(javaInfo.getVmName())));
        output.append(String.format("%-20s: %s\n", "VM Version", 
                     formatValue(javaInfo.getVmVersion())));
        output.append(String.format("%-20s: %s\n", "VM Vendor", 
                     formatValue(javaInfo.getVmVendor())));
        output.append(String.format("%-20s: %s\n", "Runtime Name", 
                     formatValue(javaInfo.getRuntimeName())));
        output.append(String.format("%-20s: %s\n", "Runtime Version", 
                     formatValue(javaInfo.getRuntimeVersion())));

        // 显示路径信息（截断过长的路径）
        output.append(String.format("%-20s: %s\n", "Class Path", 
                     formatPath(javaInfo.getClassPath())));
        output.append(String.format("%-20s: %s\n", "Library Path", 
                     formatPath(javaInfo.getLibraryPath())));
        if (javaInfo.getBootClassPath() != null && !javaInfo.getBootClassPath().isEmpty()) {
            output.append(String.format("%-20s: %s\n", "Boot Class Path", 
                         formatPath(javaInfo.getBootClassPath())));
        }

        return output.toString();
    }

    /**
     * 格式化环境变量信息
     * 
     * @param envInfo 环境变量信息
     * @return 格式化后的字符串
     */
    public String formatEnvironmentVariableInfo(EnvironmentVariableInfo envInfo) {
        StringBuilder output = new StringBuilder();
        
        output.append("ENVIRONMENT VARIABLES\n");
        output.append(SUB_SEPARATOR).append("\n");
        output.append(String.format("%-15s: %s\n", "JAVA_HOME", 
                     formatValue(envInfo.getJavaHome())));
        output.append(String.format("%-15s: %s\n", "JRE_HOME", 
                     formatValue(envInfo.getJreHome())));
        output.append(String.format("%-15s: %s\n", "JAVA_OPTS", 
                     formatValue(envInfo.getJavaOpts())));
        output.append(String.format("%-15s: %s\n", "CLASSPATH", 
                     formatPath(envInfo.getClassPath())));
        output.append(String.format("%-15s: %s\n", "PATH", 
                     formatPath(envInfo.getPathVariable())));
        
        // 构建工具环境变量
        if (hasAnyBuildToolEnvVars(envInfo)) {
            output.append("\nBuild Tools:\n");
            if (envInfo.getMavenHome() != null) {
                output.append(String.format("%-15s: %s\n", "MAVEN_HOME", envInfo.getMavenHome()));
            }
            if (envInfo.getM2Home() != null) {
                output.append(String.format("%-15s: %s\n", "M2_HOME", envInfo.getM2Home()));
            }
            if (envInfo.getGradleHome() != null) {
                output.append(String.format("%-15s: %s\n", "GRADLE_HOME", envInfo.getGradleHome()));
            }
            if (envInfo.getAntHome() != null) {
                output.append(String.format("%-15s: %s\n", "ANT_HOME", envInfo.getAntHome()));
            }
        }

        return output.toString();
    }

    /**
     * 格式化Java安装信息
     * 
     * @param installations Java安装列表
     * @return 格式化后的字符串
     */
    public String formatJavaInstallations(List<JavaInstallationInfo> installations) {
        StringBuilder output = new StringBuilder();
        
        output.append("JAVA INSTALLATIONS\n");
        output.append(SUB_SEPARATOR).append("\n");
        
        for (int i = 0; i < installations.size(); i++) {
            JavaInstallationInfo installation = installations.get(i);
            output.append(String.format("%d. %s %s %s%s\n", 
                         i + 1,
                         formatValue(installation.getType()),
                         formatValue(installation.getVersion()),
                         formatValue(installation.getVendor()),
                         installation.isActive() ? " [ACTIVE]" : ""));
            output.append(String.format("   Path: %s\n", formatValue(installation.getInstallPath())));
            if (installation.getArchitecture() != null && !"Unknown".equals(installation.getArchitecture())) {
                output.append(String.format("   Architecture: %s\n", installation.getArchitecture()));
            }
            if (i < installations.size() - 1) {
                output.append("\n");
            }
        }

        return output.toString();
    }

    /**
     * 格式化诊断结果
     * 
     * @param diagnosticResults 诊断结果列表
     * @return 格式化后的字符串
     */
    public String formatDiagnosticResults(List<DiagnosticResult> diagnosticResults) {
        StringBuilder output = new StringBuilder();
        
        output.append("DIAGNOSTIC RESULTS\n");
        output.append(SUB_SEPARATOR).append("\n");

        // 按级别分组统计
        long errorCount = diagnosticResults.stream()
            .filter(r -> r.getLevel() == DiagnosticResult.Level.ERROR).count();
        long warnCount = diagnosticResults.stream()
            .filter(r -> r.getLevel() == DiagnosticResult.Level.WARN).count();
        long infoCount = diagnosticResults.stream()
            .filter(r -> r.getLevel() == DiagnosticResult.Level.INFO).count();

        output.append(String.format("Summary: %d Error(s), %d Warning(s), %d Info\n\n", 
                     errorCount, warnCount, infoCount));

        // 显示各级别的结果
        if (errorCount > 0) {
            output.append("ERRORS:\n");
            formatDiagnosticsByLevel(output, diagnosticResults, DiagnosticResult.Level.ERROR);
            output.append("\n");
        }

        if (warnCount > 0) {
            output.append("WARNINGS:\n");
            formatDiagnosticsByLevel(output, diagnosticResults, DiagnosticResult.Level.WARN);
            output.append("\n");
        }

        if (infoCount > 0) {
            output.append("INFORMATION:\n");
            formatDiagnosticsByLevel(output, diagnosticResults, DiagnosticResult.Level.INFO);
        }

        return output.toString();
    }

    /**
     * 按级别格式化诊断结果
     */
    private void formatDiagnosticsByLevel(StringBuilder output, List<DiagnosticResult> results, 
                                         DiagnosticResult.Level level) {
        results.stream()
            .filter(r -> r.getLevel() == level)
            .forEach(result -> {
                output.append(String.format("  • %s\n", result.getMessage()));
                if (result.getSuggestion() != null && !result.getSuggestion().isEmpty()) {
                    output.append(String.format("    Solution: %s\n", result.getSuggestion()));
                }
                output.append("\n");
            });
    }

    /**
     * 格式化值，处理null和空值
     */
    private String formatValue(String value) {
        return (value == null || value.trim().isEmpty()) ? "[Not Set]" : value;
    }

    /**
     * 格式化路径，截断过长的路径
     */
    private String formatPath(String path) {
        if (path == null || path.trim().isEmpty()) {
            return "[Not Set]";
        }
        
        // 如果路径太长，截断中间部分
        if (path.length() > 100) {
            return path.substring(0, 40) + "..." + path.substring(path.length() - 40);
        }
        
        return path;
    }

    /**
     * 检查是否有任何构建工具环境变量
     */
    private boolean hasAnyBuildToolEnvVars(EnvironmentVariableInfo envInfo) {
        return envInfo.getMavenHome() != null || 
               envInfo.getM2Home() != null || 
               envInfo.getGradleHome() != null || 
               envInfo.getAntHome() != null;
    }
}