package com.company.envchecker;

import com.company.envchecker.analyzer.EnvironmentVariableAnalyzer;
import com.company.envchecker.collector.SystemInfoCollector;
import com.company.envchecker.detector.JavaVersionDetector;
import com.company.envchecker.diagnostic.EnvironmentDiagnostic;
import com.company.envchecker.formatter.ConsoleOutputFormatter;
import com.company.envchecker.formatter.HtmlOutputFormatter;
import com.company.envchecker.formatter.JsonOutputFormatter;
import com.company.envchecker.model.*;
import com.company.envchecker.scanner.JdkJreScanner;

import org.apache.commons.cli.*;

import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

/**
 * Java环境检查工具主应用程序
 * 提供命令行界面，支持多种检查模式和输出格式
 */
public class JavaEnvironmentChecker {

    private static final String VERSION = "1.0.0";

    public static void main(String[] args) {
        JavaEnvironmentChecker checker = new JavaEnvironmentChecker();
        try {
            checker.run(args);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }

    /**
     * 运行应用程序
     * 
     * @param args 命令行参数
     */
    public void run(String[] args) throws Exception {
        Options options = createOptions();
        CommandLineParser parser = new DefaultParser();
        
        try {
            CommandLine cmd = parser.parse(options, args);
            
            if (cmd.hasOption("help")) {
                printHelp(options);
                return;
            }
            
            if (cmd.hasOption("version")) {
                printVersion();
                return;
            }
            
            // 执行环境检查
            EnvironmentReport report = performEnvironmentCheck(cmd);
            
            // 输出结果
            outputReport(report, cmd);
            
        } catch (ParseException e) {
            System.err.println("Error parsing command line: " + e.getMessage());
            printHelp(options);
            System.exit(1);
        }
    }

    /**
     * 创建命令行选项
     * 
     * @return 命令行选项
     */
    private Options createOptions() {
        Options options = new Options();

        options.addOption("h", "help", false, "Show help message");
        options.addOption("v", "version", false, "Show version information");
        
        options.addOption(Option.builder("m")
            .longOpt("mode")
            .hasArg()
            .argName("MODE")
            .desc("Check mode: quick, detailed, diagnostic, scan (default: detailed)")
            .build());
        
        options.addOption(Option.builder("o")
            .longOpt("output")
            .hasArg()
            .argName("FILE")
            .desc("Output file path")
            .build());
        
        options.addOption(Option.builder("f")
            .longOpt("format")
            .hasArg()
            .argName("FORMAT")
            .desc("Output format: console, json, html (default: console)")
            .build());
        
        options.addOption("q", "quiet", false, "Quiet mode - minimal output");
        options.addOption("d", "debug", false, "Enable debug output");
        
        return options;
    }

    /**
     * 执行环境检查
     * 
     * @param cmd 命令行参数
     * @return 环境报告
     */
    private EnvironmentReport performEnvironmentCheck(CommandLine cmd) {
        long startTime = System.currentTimeMillis();
        
        String mode = cmd.getOptionValue("mode", "detailed");
        boolean quiet = cmd.hasOption("quiet");
        boolean debug = cmd.hasOption("debug");
        
        if (!quiet) {
            System.out.println("Java Environment Checker v" + VERSION);
            System.out.println("Starting environment check (" + mode + " mode)...");
            System.out.println();
        }

        EnvironmentReport report = new EnvironmentReport();

        try {
            // 收集系统信息
            if (!quiet) System.out.print("Collecting system information... ");
            SystemInfoCollector systemCollector = new SystemInfoCollector();
            SystemInfo systemInfo = systemCollector.collectSystemInfo();
            report.setSystemInfo(systemInfo);
            if (!quiet) System.out.println("Done");

            // 检测Java环境
            if (!quiet) System.out.print("Detecting Java environment... ");
            JavaVersionDetector javaDetector = new JavaVersionDetector();
            JavaEnvironmentInfo javaInfo = javaDetector.detectJavaEnvironment();
            report.setJavaEnvironmentInfo(javaInfo);
            if (!quiet) System.out.println("Done");

            // 分析环境变量
            if (!quiet) System.out.print("Analyzing environment variables... ");
            EnvironmentVariableAnalyzer envAnalyzer = new EnvironmentVariableAnalyzer();
            EnvironmentVariableInfo envInfo = envAnalyzer.analyzeEnvironmentVariables();
            report.setEnvironmentVariableInfo(envInfo);
            if (!quiet) System.out.println("Done");

            // 扫描Java安装 (除了quick模式)
            if (!"quick".equals(mode)) {
                if (!quiet) System.out.print("Scanning Java installations... ");
                JdkJreScanner scanner = new JdkJreScanner();
                List<JavaInstallationInfo> installations = scanner.scanJavaInstallations();
                report.setJavaInstallations(installations);
                if (!quiet) System.out.println("Done");
            }

            // 执行诊断 (diagnostic或detailed模式)
            if ("diagnostic".equals(mode) || "detailed".equals(mode)) {
                if (!quiet) System.out.print("Running diagnostics... ");
                EnvironmentDiagnostic diagnostic = new EnvironmentDiagnostic();
                List<DiagnosticResult> diagnosticResults = diagnostic.diagnose(
                    javaInfo, envInfo, report.getJavaInstallations());
                report.setDiagnosticResults(diagnosticResults);
                if (!quiet) System.out.println("Done");
            }

        } catch (Exception e) {
            if (debug) {
                e.printStackTrace();
            }
            throw new RuntimeException("Error during environment check: " + e.getMessage(), e);
        }

        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        report.setCheckDuration(formatDuration(duration));

        if (!quiet) {
            System.out.println("\nEnvironment check completed in " + formatDuration(duration));
            System.out.println();
        }

        return report;
    }

    /**
     * 输出报告
     * 
     * @param report 环境报告
     * @param cmd 命令行参数
     */
    private void outputReport(EnvironmentReport report, CommandLine cmd) throws IOException {
        String format = cmd.getOptionValue("format", "console");
        String outputFile = cmd.getOptionValue("output");
        boolean quiet = cmd.hasOption("quiet");

        String output;
        
        switch (format.toLowerCase()) {
            case "json":
                JsonOutputFormatter jsonFormatter = new JsonOutputFormatter();
                output = jsonFormatter.formatReport(report);
                break;
            case "html":
                HtmlOutputFormatter htmlFormatter = new HtmlOutputFormatter();
                output = htmlFormatter.formatReport(report);
                break;
            case "console":
            default:
                ConsoleOutputFormatter consoleFormatter = new ConsoleOutputFormatter();
                output = consoleFormatter.formatReport(report);
                break;
        }

        if (outputFile != null) {
            // 输出到文件
            try (FileWriter writer = new FileWriter(outputFile)) {
                writer.write(output);
                if (!quiet) {
                    System.out.println("Report saved to: " + outputFile);
                }
            }
        } else {
            // 输出到控制台
            System.out.println(output);
        }
    }

    /**
     * 打印帮助信息
     * 
     * @param options 命令行选项
     */
    private void printHelp(Options options) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.setWidth(100);
        
        System.out.println("Java Environment Checker v" + VERSION);
        System.out.println("A comprehensive tool for checking local Java environment configuration\n");
        
        formatter.printHelp("java-env-checker", options);
        
        System.out.println("\nCheck Modes:");
        System.out.println("  quick      - Basic Java environment information");
        System.out.println("  detailed   - Complete environment check with diagnostics (default)");
        System.out.println("  diagnostic - Focus on environment diagnostics and issues");
        System.out.println("  scan       - Scan for all Java installations");
        
        System.out.println("\nOutput Formats:");
        System.out.println("  console    - Human-readable console output (default)");
        System.out.println("  json       - JSON format for programmatic processing");
        System.out.println("  html       - HTML report with styling");
        
        System.out.println("\nExamples:");
        System.out.println("  java-env-checker");
        System.out.println("  java-env-checker --mode quick");
        System.out.println("  java-env-checker --mode diagnostic --format json --output report.json");
        System.out.println("  java-env-checker --format html --output report.html");
        
        System.out.println("\nFor more information, visit: https://github.com/company/java-environment-checker");
    }

    /**
     * 打印版本信息
     */
    private void printVersion() {
        System.out.println("Java Environment Checker");
        System.out.println("Version: " + VERSION);
        System.out.println("Java Runtime: " + System.getProperty("java.version") + 
                         " (" + System.getProperty("java.vendor") + ")");
        System.out.println("Operating System: " + System.getProperty("os.name") + 
                         " " + System.getProperty("os.version") + 
                         " (" + System.getProperty("os.arch") + ")");
    }

    /**
     * 格式化持续时间
     * 
     * @param durationMs 持续时间（毫秒）
     * @return 格式化的持续时间字符串
     */
    private String formatDuration(long durationMs) {
        if (durationMs < 1000) {
            return durationMs + "ms";
        } else if (durationMs < 60000) {
            return String.format("%.2fs", durationMs / 1000.0);
        } else {
            long minutes = durationMs / 60000;
            long seconds = (durationMs % 60000) / 1000;
            return String.format("%dm %ds", minutes, seconds);
        }
    }
}