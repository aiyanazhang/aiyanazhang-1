package com.company.envchecker.scanner;

import com.company.envchecker.model.JavaInstallationInfo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * JDK/JRE扫描器
 * 负责扫描系统中已安装的所有JDK和JRE版本
 */
public class JdkJreScanner {

    /**
     * 扫描系统中所有Java安装
     * 
     * @return Java安装信息列表
     */
    public List<JavaInstallationInfo> scanJavaInstallations() {
        List<JavaInstallationInfo> installations = new ArrayList<>();
        Set<String> scannedPaths = new HashSet<>();

        // 获取当前活动的Java安装
        String currentJavaHome = System.getProperty("java.home");
        if (currentJavaHome != null) {
            JavaInstallationInfo currentInstall = analyzeJavaInstallation(currentJavaHome, true);
            if (currentInstall != null) {
                installations.add(currentInstall);
                scannedPaths.add(currentJavaHome);
            }
        }

        // 扫描常见安装路径
        List<String> scanPaths = getCommonJavaInstallationPaths();
        for (String scanPath : scanPaths) {
            scanJavaInstallationsInPath(scanPath, installations, scannedPaths);
        }

        // 从环境变量扫描
        scanFromEnvironmentVariables(installations, scannedPaths);

        return installations;
    }

    /**
     * 分析单个Java安装
     * 
     * @param javaPath Java安装路径
     * @param isActive 是否为当前活动版本
     * @return Java安装信息
     */
    public JavaInstallationInfo analyzeJavaInstallation(String javaPath, boolean isActive) {
        if (javaPath == null || javaPath.trim().isEmpty()) {
            return null;
        }

        File javaDir = new File(javaPath);
        if (!javaDir.exists() || !javaDir.isDirectory()) {
            return null;
        }

        JavaInstallationInfo installation = new JavaInstallationInfo();
        installation.setInstallPath(javaPath);
        installation.setActive(isActive);

        // 检测Java类型 (JDK vs JRE)
        installation.setType(detectJavaType(javaDir));

        // 获取版本信息
        String version = getJavaVersion(javaDir);
        installation.setVersion(version);
        installation.setSpecificationVersion(extractSpecificationVersion(version));

        // 获取供应商信息
        installation.setVendor(getJavaVendor(javaDir));

        // 获取架构信息
        installation.setArchitecture(getJavaArchitecture(javaDir));

        // 获取构建信息
        installation.setBuildInfo(getJavaBuildInfo(javaDir));

        return installation;
    }

    /**
     * 获取常见的Java安装路径
     * 
     * @return 常见安装路径列表
     */
    private List<String> getCommonJavaInstallationPaths() {
        List<String> paths = new ArrayList<>();

        if (isWindows()) {
            paths.add("C:\\Program Files\\Java");
            paths.add("C:\\Program Files (x86)\\Java");
            paths.add("C:\\Program Files\\AdoptOpenJDK");
            paths.add("C:\\Program Files\\Eclipse Foundation");
            paths.add("C:\\Program Files\\Amazon Corretto");
        } else if (isMacOS()) {
            paths.add("/System/Library/Java/JavaVirtualMachines");
            paths.add("/Library/Java/JavaVirtualMachines");
            paths.add("/System/Library/Frameworks/JavaVM.framework/Versions");
        } else {
            // Linux/Unix
            paths.add("/usr/lib/jvm");
            paths.add("/usr/java");
            paths.add("/opt/java");
            paths.add("/opt/jdk");
            paths.add("/usr/local/java");
            paths.add("/usr/local/jdk");
        }

        return paths;
    }

    /**
     * 在指定路径中扫描Java安装
     * 
     * @param basePath 基础路径
     * @param installations 安装列表
     * @param scannedPaths 已扫描路径集合
     */
    private void scanJavaInstallationsInPath(String basePath, List<JavaInstallationInfo> installations, Set<String> scannedPaths) {
        File baseDir = new File(basePath);
        if (!baseDir.exists() || !baseDir.isDirectory()) {
            return;
        }

        File[] subdirs = baseDir.listFiles(File::isDirectory);
        if (subdirs == null) {
            return;
        }

        for (File subdir : subdirs) {
            String subdirPath = subdir.getAbsolutePath();
            if (scannedPaths.contains(subdirPath)) {
                continue;
            }

            if (isJavaInstallation(subdir)) {
                JavaInstallationInfo installation = analyzeJavaInstallation(subdirPath, false);
                if (installation != null) {
                    installations.add(installation);
                    scannedPaths.add(subdirPath);
                }
            } else {
                // 递归扫描子目录 (限制深度避免无限递归)
                scanJavaInstallationsInPath(subdirPath, installations, scannedPaths);
            }
        }
    }

    /**
     * 从环境变量扫描Java安装
     * 
     * @param installations 安装列表
     * @param scannedPaths 已扫描路径集合
     */
    private void scanFromEnvironmentVariables(List<JavaInstallationInfo> installations, Set<String> scannedPaths) {
        String[] envVars = {"JAVA_HOME", "JRE_HOME", "JDK_HOME"};
        
        for (String envVar : envVars) {
            String path = System.getenv(envVar);
            if (path != null && !scannedPaths.contains(path)) {
                JavaInstallationInfo installation = analyzeJavaInstallation(path, false);
                if (installation != null) {
                    installations.add(installation);
                    scannedPaths.add(path);
                }
            }
        }
    }

    /**
     * 检查目录是否为Java安装
     * 
     * @param dir 目录
     * @return true 如果是Java安装目录
     */
    private boolean isJavaInstallation(File dir) {
        // 检查bin目录是否存在
        File binDir = new File(dir, "bin");
        if (!binDir.exists()) {
            return false;
        }

        // 检查java可执行文件是否存在
        String javaExe = isWindows() ? "java.exe" : "java";
        File javaExecutable = new File(binDir, javaExe);
        return javaExecutable.exists();
    }

    /**
     * 检测Java类型 (JDK vs JRE)
     * 
     * @param javaDir Java目录
     * @return Java类型
     */
    private String detectJavaType(File javaDir) {
        // 检查是否有javac编译器
        File binDir = new File(javaDir, "bin");
        String javacExe = isWindows() ? "javac.exe" : "javac";
        File javacExecutable = new File(binDir, javacExe);
        
        if (javacExecutable.exists()) {
            return "JDK";
        }

        // 检查lib目录中是否有tools.jar
        File libDir = new File(javaDir, "lib");
        File toolsJar = new File(libDir, "tools.jar");
        if (toolsJar.exists()) {
            return "JDK";
        }

        return "JRE";
    }

    /**
     * 获取Java版本信息
     * 
     * @param javaDir Java目录
     * @return 版本信息
     */
    private String getJavaVersion(File javaDir) {
        try {
            File binDir = new File(javaDir, "bin");
            String javaExe = isWindows() ? "java.exe" : "java";
            File javaExecutable = new File(binDir, javaExe);

            if (!javaExecutable.exists()) {
                return "Unknown";
            }

            ProcessBuilder pb = new ProcessBuilder(javaExecutable.getAbsolutePath(), "-version");
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            String line = reader.readLine();
            reader.close();
            process.waitFor();

            if (line != null && line.contains("version")) {
                // 提取版本号
                int start = line.indexOf("\"") + 1;
                int end = line.lastIndexOf("\"");
                if (start > 0 && end > start) {
                    return line.substring(start, end);
                }
            }
        } catch (Exception e) {
            // 如果执行失败，尝试从release文件读取
            return getVersionFromReleaseFile(javaDir);
        }

        return "Unknown";
    }

    /**
     * 从release文件获取版本信息
     * 
     * @param javaDir Java目录
     * @return 版本信息
     */
    private String getVersionFromReleaseFile(File javaDir) {
        File releaseFile = new File(javaDir, "release");
        if (!releaseFile.exists()) {
            return "Unknown";
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(releaseFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("JAVA_VERSION=")) {
                    String version = line.substring("JAVA_VERSION=".length());
                    return version.replaceAll("\"", "");
                }
            }
        } catch (IOException e) {
            // Ignore
        }

        return "Unknown";
    }

    /**
     * 获取Java供应商信息
     * 
     * @param javaDir Java目录
     * @return 供应商信息
     */
    private String getJavaVendor(File javaDir) {
        File releaseFile = new File(javaDir, "release");
        if (!releaseFile.exists()) {
            return "Unknown";
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(releaseFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("IMPLEMENTOR=")) {
                    String vendor = line.substring("IMPLEMENTOR=".length());
                    return vendor.replaceAll("\"", "");
                }
            }
        } catch (IOException e) {
            // Ignore
        }

        return "Unknown";
    }

    /**
     * 获取Java架构信息
     * 
     * @param javaDir Java目录
     * @return 架构信息
     */
    private String getJavaArchitecture(File javaDir) {
        File releaseFile = new File(javaDir, "release");
        if (!releaseFile.exists()) {
            return "Unknown";
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(releaseFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("OS_ARCH=")) {
                    String arch = line.substring("OS_ARCH=".length());
                    return arch.replaceAll("\"", "");
                }
            }
        } catch (IOException e) {
            // Ignore
        }

        return "Unknown";
    }

    /**
     * 获取Java构建信息
     * 
     * @param javaDir Java目录
     * @return 构建信息
     */
    private String getJavaBuildInfo(File javaDir) {
        File releaseFile = new File(javaDir, "release");
        if (!releaseFile.exists()) {
            return "Unknown";
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(releaseFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("BUILD_INFO=")) {
                    String buildInfo = line.substring("BUILD_INFO=".length());
                    return buildInfo.replaceAll("\"", "");
                }
            }
        } catch (IOException e) {
            // Ignore
        }

        return "Unknown";
    }

    /**
     * 提取规范版本号
     * 
     * @param fullVersion 完整版本号
     * @return 规范版本号
     */
    private String extractSpecificationVersion(String fullVersion) {
        if (fullVersion == null || "Unknown".equals(fullVersion)) {
            return "Unknown";
        }

        // Java 9+ 版本格式: 11.0.1, 17.0.2
        // Java 8及以下: 1.8.0_291, 1.7.0_80
        if (fullVersion.startsWith("1.")) {
            int dotIndex = fullVersion.indexOf('.', 2);
            if (dotIndex > 0) {
                return fullVersion.substring(0, dotIndex);
            }
        } else {
            int dotIndex = fullVersion.indexOf('.');
            if (dotIndex > 0) {
                return fullVersion.substring(0, dotIndex);
            }
        }

        return fullVersion;
    }

    /**
     * 检查是否为Windows系统
     */
    private boolean isWindows() {
        String osName = System.getProperty("os.name", "").toLowerCase();
        return osName.contains("windows");
    }

    /**
     * 检查是否为macOS系统
     */
    private boolean isMacOS() {
        String osName = System.getProperty("os.name", "").toLowerCase();
        return osName.contains("mac") || osName.contains("darwin");
    }
}