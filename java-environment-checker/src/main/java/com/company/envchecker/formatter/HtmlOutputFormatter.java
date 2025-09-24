package com.company.envchecker.formatter;

import com.company.envchecker.model.*;

import java.util.List;

/**
 * HTML输出格式化器
 * 负责将检查结果格式化为HTML格式输出
 */
public class HtmlOutputFormatter {

    /**
     * 格式化环境报告为HTML
     * 
     * @param report 环境报告
     * @return HTML格式的字符串
     */
    public String formatReport(EnvironmentReport report) {
        StringBuilder html = new StringBuilder();
        
        html.append(getHtmlHeader());
        html.append(getReportTitle(report));
        
        if (report.getSystemInfo() != null) {
            html.append(formatSystemInfoHtml(report.getSystemInfo()));
        }
        
        if (report.getJavaEnvironmentInfo() != null) {
            html.append(formatJavaEnvironmentInfoHtml(report.getJavaEnvironmentInfo()));
        }
        
        if (report.getEnvironmentVariableInfo() != null) {
            html.append(formatEnvironmentVariableInfoHtml(report.getEnvironmentVariableInfo()));
        }
        
        if (report.getJavaInstallations() != null && !report.getJavaInstallations().isEmpty()) {
            html.append(formatJavaInstallationsHtml(report.getJavaInstallations()));
        }
        
        if (report.getDiagnosticResults() != null && !report.getDiagnosticResults().isEmpty()) {
            html.append(formatDiagnosticResultsHtml(report.getDiagnosticResults()));
        }
        
        html.append(getHtmlFooter());
        
        return html.toString();
    }

    /**
     * 获取HTML头部
     */
    private String getHtmlHeader() {
        return "<!DOCTYPE html>\n" +
               "<html lang=\"en\">\n" +
               "<head>\n" +
               "    <meta charset=\"UTF-8\">\n" +
               "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" +
               "    <title>Java Environment Check Report</title>\n" +
               "    <style>\n" +
               getCSS() +
               "    </style>\n" +
               "</head>\n" +
               "<body>\n" +
               "    <div class=\"container\">\n";
    }

    /**
     * 获取CSS样式
     */
    private String getCSS() {
        return "        body {\n" +
               "            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;\n" +
               "            line-height: 1.6;\n" +
               "            margin: 0;\n" +
               "            padding: 20px;\n" +
               "            background-color: #f5f5f5;\n" +
               "        }\n" +
               "        .container {\n" +
               "            max-width: 1200px;\n" +
               "            margin: 0 auto;\n" +
               "            background-color: white;\n" +
               "            padding: 30px;\n" +
               "            border-radius: 10px;\n" +
               "            box-shadow: 0 0 20px rgba(0,0,0,0.1);\n" +
               "        }\n" +
               "        h1 {\n" +
               "            color: #2c3e50;\n" +
               "            text-align: center;\n" +
               "            border-bottom: 3px solid #3498db;\n" +
               "            padding-bottom: 10px;\n" +
               "        }\n" +
               "        h2 {\n" +
               "            color: #34495e;\n" +
               "            border-left: 4px solid #3498db;\n" +
               "            padding-left: 15px;\n" +
               "            margin-top: 30px;\n" +
               "        }\n" +
               "        .info-table {\n" +
               "            width: 100%;\n" +
               "            border-collapse: collapse;\n" +
               "            margin: 15px 0;\n" +
               "        }\n" +
               "        .info-table th, .info-table td {\n" +
               "            padding: 12px;\n" +
               "            text-align: left;\n" +
               "            border-bottom: 1px solid #ddd;\n" +
               "        }\n" +
               "        .info-table th {\n" +
               "            background-color: #f8f9fa;\n" +
               "            font-weight: 600;\n" +
               "            width: 200px;\n" +
               "        }\n" +
               "        .info-table tr:hover {\n" +
               "            background-color: #f8f9fa;\n" +
               "        }\n" +
               "        .installation-card {\n" +
               "            border: 1px solid #ddd;\n" +
               "            border-radius: 5px;\n" +
               "            padding: 15px;\n" +
               "            margin: 10px 0;\n" +
               "            background-color: #fafafa;\n" +
               "        }\n" +
               "        .installation-card.active {\n" +
               "            border-color: #27ae60;\n" +
               "            background-color: #e8f8f0;\n" +
               "        }\n" +
               "        .installation-title {\n" +
               "            font-weight: bold;\n" +
               "            color: #2c3e50;\n" +
               "            font-size: 1.1em;\n" +
               "        }\n" +
               "        .active-badge {\n" +
               "            background-color: #27ae60;\n" +
               "            color: white;\n" +
               "            padding: 2px 8px;\n" +
               "            border-radius: 12px;\n" +
               "            font-size: 0.8em;\n" +
               "            margin-left: 10px;\n" +
               "        }\n" +
               "        .diagnostic-item {\n" +
               "            margin: 15px 0;\n" +
               "            padding: 15px;\n" +
               "            border-radius: 5px;\n" +
               "            border-left: 4px solid;\n" +
               "        }\n" +
               "        .diagnostic-error {\n" +
               "            background-color: #fdf2f2;\n" +
               "            border-left-color: #e74c3c;\n" +
               "        }\n" +
               "        .diagnostic-warn {\n" +
               "            background-color: #fefbf3;\n" +
               "            border-left-color: #f39c12;\n" +
               "        }\n" +
               "        .diagnostic-info {\n" +
               "            background-color: #f0f8ff;\n" +
               "            border-left-color: #3498db;\n" +
               "        }\n" +
               "        .diagnostic-level {\n" +
               "            font-weight: bold;\n" +
               "            font-size: 0.9em;\n" +
               "        }\n" +
               "        .error { color: #e74c3c; }\n" +
               "        .warn { color: #f39c12; }\n" +
               "        .info { color: #3498db; }\n" +
               "        .code {\n" +
               "            background-color: #f4f4f4;\n" +
               "            padding: 2px 6px;\n" +
               "            border-radius: 3px;\n" +
               "            font-family: 'Courier New', monospace;\n" +
               "            font-size: 0.9em;\n" +
               "        }\n" +
               "        .suggestion {\n" +
               "            margin-top: 10px;\n" +
               "            padding: 10px;\n" +
               "            background-color: rgba(52, 152, 219, 0.1);\n" +
               "            border-radius: 3px;\n" +
               "        }\n" +
               "        .timestamp {\n" +
               "            text-align: center;\n" +
               "            color: #7f8c8d;\n" +
               "            font-style: italic;\n" +
               "            margin-bottom: 20px;\n" +
               "        }\n";
    }

    /**
     * 获取报告标题
     */
    private String getReportTitle(EnvironmentReport report) {
        StringBuilder html = new StringBuilder();
        html.append("        <h1>Java Environment Check Report</h1>\n");
        html.append("        <div class=\"timestamp\">\n");
        html.append("            Generated at: ").append(new java.util.Date(report.getCheckTimestamp()));
        if (report.getCheckDuration() != null) {
            html.append(" | Duration: ").append(report.getCheckDuration());
        }
        html.append("\n        </div>\n");
        return html.toString();
    }

    /**
     * 格式化系统信息为HTML
     */
    private String formatSystemInfoHtml(SystemInfo systemInfo) {
        StringBuilder html = new StringBuilder();
        html.append("        <h2>System Information</h2>\n");
        html.append("        <table class=\"info-table\">\n");
        html.append(formatTableRow("Operating System", systemInfo.getOperatingSystem()));
        html.append(formatTableRow("OS Version", systemInfo.getOsVersion()));
        html.append(formatTableRow("Architecture", systemInfo.getArchitecture()));
        html.append(formatTableRow("User Name", systemInfo.getUserName()));
        html.append(formatTableRow("User Home", systemInfo.getUserHome()));
        html.append(formatTableRow("Working Directory", systemInfo.getWorkingDirectory()));
        html.append(formatTableRow("Temp Directory", systemInfo.getTempDirectory()));
        html.append(formatTableRow("File Encoding", systemInfo.getFileEncoding()));
        html.append(formatTableRow("System Encoding", systemInfo.getSystemEncoding()));
        html.append("        </table>\n");
        return html.toString();
    }

    /**
     * 格式化Java环境信息为HTML
     */
    private String formatJavaEnvironmentInfoHtml(JavaEnvironmentInfo javaInfo) {
        StringBuilder html = new StringBuilder();
        html.append("        <h2>Java Environment</h2>\n");
        html.append("        <table class=\"info-table\">\n");
        html.append(formatTableRow("Java Version", javaInfo.getJavaVersion()));
        html.append(formatTableRow("Specification Version", javaInfo.getJavaSpecVersion()));
        html.append(formatTableRow("Vendor", javaInfo.getJavaVendor()));
        html.append(formatTableRow("Java Home", javaInfo.getJavaHome()));
        html.append(formatTableRow("VM Name", javaInfo.getVmName()));
        html.append(formatTableRow("VM Version", javaInfo.getVmVersion()));
        html.append(formatTableRow("VM Vendor", javaInfo.getVmVendor()));
        html.append(formatTableRow("Runtime Name", javaInfo.getRuntimeName()));
        html.append(formatTableRow("Runtime Version", javaInfo.getRuntimeVersion()));
        html.append(formatTableRow("Class Path", formatPathForHtml(javaInfo.getClassPath())));
        html.append(formatTableRow("Library Path", formatPathForHtml(javaInfo.getLibraryPath())));
        if (javaInfo.getBootClassPath() != null && !javaInfo.getBootClassPath().isEmpty()) {
            html.append(formatTableRow("Boot Class Path", formatPathForHtml(javaInfo.getBootClassPath())));
        }
        html.append("        </table>\n");
        return html.toString();
    }

    /**
     * 格式化环境变量信息为HTML
     */
    private String formatEnvironmentVariableInfoHtml(EnvironmentVariableInfo envInfo) {
        StringBuilder html = new StringBuilder();
        html.append("        <h2>Environment Variables</h2>\n");
        html.append("        <table class=\"info-table\">\n");
        html.append(formatTableRow("JAVA_HOME", envInfo.getJavaHome()));
        html.append(formatTableRow("JRE_HOME", envInfo.getJreHome()));
        html.append(formatTableRow("JAVA_OPTS", envInfo.getJavaOpts()));
        html.append(formatTableRow("CLASSPATH", formatPathForHtml(envInfo.getClassPath())));
        html.append(formatTableRow("PATH", formatPathForHtml(envInfo.getPathVariable())));
        
        // 构建工具
        if (hasAnyBuildToolEnvVars(envInfo)) {
            html.append(formatTableRow("MAVEN_HOME", envInfo.getMavenHome()));
            html.append(formatTableRow("M2_HOME", envInfo.getM2Home()));
            html.append(formatTableRow("GRADLE_HOME", envInfo.getGradleHome()));
            html.append(formatTableRow("ANT_HOME", envInfo.getAntHome()));
        }
        
        html.append("        </table>\n");
        return html.toString();
    }

    /**
     * 格式化Java安装信息为HTML
     */
    private String formatJavaInstallationsHtml(List<JavaInstallationInfo> installations) {
        StringBuilder html = new StringBuilder();
        html.append("        <h2>Java Installations</h2>\n");
        
        for (JavaInstallationInfo installation : installations) {
            String cardClass = installation.isActive() ? "installation-card active" : "installation-card";
            html.append("        <div class=\"").append(cardClass).append("\">\n");
            html.append("            <div class=\"installation-title\">\n");
            html.append("                ").append(htmlEscape(formatValue(installation.getType())))
                .append(" ").append(htmlEscape(formatValue(installation.getVersion())))
                .append(" - ").append(htmlEscape(formatValue(installation.getVendor())));
            if (installation.isActive()) {
                html.append("                <span class=\"active-badge\">ACTIVE</span>\n");
            }
            html.append("            </div>\n");
            html.append("            <div><strong>Path:</strong> <span class=\"code\">")
                .append(htmlEscape(formatValue(installation.getInstallPath()))).append("</span></div>\n");
            if (installation.getArchitecture() != null && !"Unknown".equals(installation.getArchitecture())) {
                html.append("            <div><strong>Architecture:</strong> ")
                    .append(htmlEscape(installation.getArchitecture())).append("</div>\n");
            }
            if (installation.getBuildInfo() != null && !"Unknown".equals(installation.getBuildInfo())) {
                html.append("            <div><strong>Build Info:</strong> ")
                    .append(htmlEscape(installation.getBuildInfo())).append("</div>\n");
            }
            html.append("        </div>\n");
        }
        
        return html.toString();
    }

    /**
     * 格式化诊断结果为HTML
     */
    private String formatDiagnosticResultsHtml(List<DiagnosticResult> diagnosticResults) {
        StringBuilder html = new StringBuilder();
        html.append("        <h2>Diagnostic Results</h2>\n");
        
        // 统计信息
        long errorCount = diagnosticResults.stream()
            .filter(r -> r.getLevel() == DiagnosticResult.Level.ERROR).count();
        long warnCount = diagnosticResults.stream()
            .filter(r -> r.getLevel() == DiagnosticResult.Level.WARN).count();
        long infoCount = diagnosticResults.stream()
            .filter(r -> r.getLevel() == DiagnosticResult.Level.INFO).count();
        
        html.append("        <div style=\"margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;\">\n");
        html.append("            <strong>Summary:</strong> ");
        html.append("            <span class=\"error\">").append(errorCount).append(" Error(s)</span>, ");
        html.append("            <span class=\"warn\">").append(warnCount).append(" Warning(s)</span>, ");
        html.append("            <span class=\"info\">").append(infoCount).append(" Info</span>\n");
        html.append("        </div>\n");
        
        // 详细结果
        for (DiagnosticResult result : diagnosticResults) {
            String levelClass = "diagnostic-" + result.getLevel().getValue().toLowerCase();
            html.append("        <div class=\"diagnostic-item ").append(levelClass).append("\">\n");
            html.append("            <div class=\"diagnostic-level ").append(result.getLevel().getValue().toLowerCase()).append("\">");
            html.append(result.getLevel().getValue()).append("</div>\n");
            html.append("            <div><strong>").append(htmlEscape(result.getMessage())).append("</strong></div>\n");
            if (result.getSuggestion() != null && !result.getSuggestion().isEmpty()) {
                html.append("            <div class=\"suggestion\">\n");
                html.append("                <strong>Suggestion:</strong> ").append(htmlEscape(result.getSuggestion())).append("\n");
                html.append("            </div>\n");
            }
            html.append("        </div>\n");
        }
        
        return html.toString();
    }

    /**
     * 格式化表格行
     */
    private String formatTableRow(String key, String value) {
        return "            <tr><th>" + htmlEscape(key) + "</th><td>" + 
               htmlEscape(formatValue(value)) + "</td></tr>\n";
    }

    /**
     * 格式化路径为HTML（处理长路径）
     */
    private String formatPathForHtml(String path) {
        if (path == null || path.trim().isEmpty()) {
            return "[Not Set]";
        }
        
        // 对于很长的路径，添加换行
        if (path.length() > 100) {
            String pathSeparator = System.getProperty("path.separator", ":");
            String[] parts = path.split(pathSeparator);
            if (parts.length > 1) {
                return "<span class=\"code\">" + String.join("<br/>" + pathSeparator, parts) + "</span>";
            }
        }
        
        return "<span class=\"code\">" + htmlEscape(path) + "</span>";
    }

    /**
     * HTML转义
     */
    private String htmlEscape(String text) {
        if (text == null) return "";
        return text.replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace("\"", "&quot;")
                  .replace("'", "&#x27;");
    }

    /**
     * 格式化值
     */
    private String formatValue(String value) {
        return (value == null || value.trim().isEmpty()) ? "[Not Set]" : value;
    }

    /**
     * 检查是否有构建工具环境变量
     */
    private boolean hasAnyBuildToolEnvVars(EnvironmentVariableInfo envInfo) {
        return envInfo.getMavenHome() != null || 
               envInfo.getM2Home() != null || 
               envInfo.getGradleHome() != null || 
               envInfo.getAntHome() != null;
    }

    /**
     * 获取HTML尾部
     */
    private String getHtmlFooter() {
        return "    </div>\n" +
               "</body>\n" +
               "</html>";
    }
}