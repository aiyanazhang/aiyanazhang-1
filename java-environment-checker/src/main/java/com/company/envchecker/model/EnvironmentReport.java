package com.company.envchecker.model;

import java.util.List;
import java.util.Objects;

/**
 * 完整环境检查报告模型类
 * 用于封装所有检查结果信息
 */
public class EnvironmentReport {
    private SystemInfo systemInfo;
    private JavaEnvironmentInfo javaEnvironmentInfo;
    private EnvironmentVariableInfo environmentVariableInfo;
    private List<JavaInstallationInfo> javaInstallations;
    private List<DiagnosticResult> diagnosticResults;
    private long checkTimestamp;
    private String checkDuration;

    public EnvironmentReport() {
        this.checkTimestamp = System.currentTimeMillis();
    }

    public EnvironmentReport(SystemInfo systemInfo, JavaEnvironmentInfo javaEnvironmentInfo,
                            EnvironmentVariableInfo environmentVariableInfo,
                            List<JavaInstallationInfo> javaInstallations,
                            List<DiagnosticResult> diagnosticResults) {
        this.systemInfo = systemInfo;
        this.javaEnvironmentInfo = javaEnvironmentInfo;
        this.environmentVariableInfo = environmentVariableInfo;
        this.javaInstallations = javaInstallations;
        this.diagnosticResults = diagnosticResults;
        this.checkTimestamp = System.currentTimeMillis();
    }

    // Getters and Setters
    public SystemInfo getSystemInfo() {
        return systemInfo;
    }

    public void setSystemInfo(SystemInfo systemInfo) {
        this.systemInfo = systemInfo;
    }

    public JavaEnvironmentInfo getJavaEnvironmentInfo() {
        return javaEnvironmentInfo;
    }

    public void setJavaEnvironmentInfo(JavaEnvironmentInfo javaEnvironmentInfo) {
        this.javaEnvironmentInfo = javaEnvironmentInfo;
    }

    public EnvironmentVariableInfo getEnvironmentVariableInfo() {
        return environmentVariableInfo;
    }

    public void setEnvironmentVariableInfo(EnvironmentVariableInfo environmentVariableInfo) {
        this.environmentVariableInfo = environmentVariableInfo;
    }

    public List<JavaInstallationInfo> getJavaInstallations() {
        return javaInstallations;
    }

    public void setJavaInstallations(List<JavaInstallationInfo> javaInstallations) {
        this.javaInstallations = javaInstallations;
    }

    public List<DiagnosticResult> getDiagnosticResults() {
        return diagnosticResults;
    }

    public void setDiagnosticResults(List<DiagnosticResult> diagnosticResults) {
        this.diagnosticResults = diagnosticResults;
    }

    public long getCheckTimestamp() {
        return checkTimestamp;
    }

    public void setCheckTimestamp(long checkTimestamp) {
        this.checkTimestamp = checkTimestamp;
    }

    public String getCheckDuration() {
        return checkDuration;
    }

    public void setCheckDuration(String checkDuration) {
        this.checkDuration = checkDuration;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        EnvironmentReport that = (EnvironmentReport) o;
        return checkTimestamp == that.checkTimestamp &&
               Objects.equals(systemInfo, that.systemInfo) &&
               Objects.equals(javaEnvironmentInfo, that.javaEnvironmentInfo) &&
               Objects.equals(environmentVariableInfo, that.environmentVariableInfo) &&
               Objects.equals(javaInstallations, that.javaInstallations) &&
               Objects.equals(diagnosticResults, that.diagnosticResults) &&
               Objects.equals(checkDuration, that.checkDuration);
    }

    @Override
    public int hashCode() {
        return Objects.hash(systemInfo, javaEnvironmentInfo, environmentVariableInfo,
                          javaInstallations, diagnosticResults, checkTimestamp, checkDuration);
    }

    @Override
    public String toString() {
        return "EnvironmentReport{" +
               "systemInfo=" + systemInfo +
               ", javaEnvironmentInfo=" + javaEnvironmentInfo +
               ", environmentVariableInfo=" + environmentVariableInfo +
               ", javaInstallations=" + javaInstallations +
               ", diagnosticResults=" + diagnosticResults +
               ", checkTimestamp=" + checkTimestamp +
               ", checkDuration='" + checkDuration + '\'' +
               '}';
    }
}