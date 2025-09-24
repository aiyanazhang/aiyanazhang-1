package com.company.envchecker.checker;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 路径配置检查器
 * 负责检查Java相关的路径配置和文件存在性
 */
public class PathConfigurationChecker {

    /**
     * 检查JAVA_HOME路径配置
     * 
     * @return 检查结果映射
     */
    public Map<String, Boolean> checkJavaHomePaths() {
        Map<String, Boolean> results = new HashMap<>();
        String javaHome = System.getenv("JAVA_HOME");

        if (javaHome == null || javaHome.trim().isEmpty()) {
            results.put("JAVA_HOME_SET", false);
            return results;
        }

        results.put("JAVA_HOME_SET", true);

        File javaHomeDir = new File(javaHome);
        results.put("JAVA_HOME_EXISTS", javaHomeDir.exists());
        results.put("JAVA_HOME_IS_DIRECTORY", javaHomeDir.isDirectory());

        if (javaHomeDir.exists() && javaHomeDir.isDirectory()) {
            // 检查关键目录
            results.put("BIN_DIR_EXISTS", new File(javaHomeDir, "bin").exists());
            results.put("LIB_DIR_EXISTS", new File(javaHomeDir, "lib").exists());
            
            // 检查配置目录 (Java 9+)
            File confDir = new File(javaHomeDir, "conf");
            results.put("CONF_DIR_EXISTS", confDir.exists());
            
            // 如果没有conf目录，检查jre目录 (Java 8及以下)
            if (!confDir.exists()) {
                results.put("JRE_DIR_EXISTS", new File(javaHomeDir, "jre").exists());
            }
        }

        return results;
    }

    /**
     * 检查Java可执行文件
     * 
     * @return 可执行文件检查结果
     */
    public Map<String, Boolean> checkJavaExecutables() {
        Map<String, Boolean> results = new HashMap<>();
        String javaHome = System.getenv("JAVA_HOME");

        if (javaHome == null) {
            return results;
        }

        File binDir = new File(javaHome, "bin");
        if (!binDir.exists()) {
            return results;
        }

        // 检查关键可执行文件
        String[] executables = {"java", "javac", "jar", "javadoc", "javap", "jconsole"};
        String execSuffix = isWindows() ? ".exe" : "";

        for (String executable : executables) {
            File execFile = new File(binDir, executable + execSuffix);
            results.put(executable.toUpperCase() + "_EXISTS", execFile.exists());
            if (execFile.exists()) {
                results.put(executable.toUpperCase() + "_EXECUTABLE", execFile.canExecute());
            }
        }

        return results;
    }

    /**
     * 检查Java库文件
     * 
     * @return 库文件检查结果
     */
    public Map<String, Boolean> checkJavaLibraries() {
        Map<String, Boolean> results = new HashMap<>();
        String javaHome = System.getenv("JAVA_HOME");

        if (javaHome == null) {
            return results;
        }

        File libDir = new File(javaHome, "lib");
        if (!libDir.exists()) {
            results.put("LIB_DIR_EXISTS", false);
            return results;
        }

        results.put("LIB_DIR_EXISTS", true);

        // 检查关键库文件 (根据Java版本不同可能位置不同)
        String[] libraries = {"tools.jar", "rt.jar", "jsse.jar"};
        
        for (String library : libraries) {
            File libFile = new File(libDir, library);
            results.put(library.replace(".", "_").toUpperCase() + "_EXISTS", libFile.exists());
        }

        // Java 9+ 模块系统检查
        File modulesDir = new File(libDir, "modules");
        results.put("MODULES_DIR_EXISTS", modulesDir.exists());

        return results;
    }

    /**
     * 检查扩展目录
     * 
     * @return 扩展目录检查结果
     */
    public Map<String, Boolean> checkExtensionDirectories() {
        Map<String, Boolean> results = new HashMap<>();
        String javaHome = System.getenv("JAVA_HOME");

        if (javaHome == null) {
            return results;
        }

        // 检查扩展目录 (Java 8及以下)
        File extDir = new File(javaHome, "jre" + File.separator + "lib" + File.separator + "ext");
        results.put("EXT_DIR_EXISTS", extDir.exists());

        // 检查endorsed目录
        File endorsedDir = new File(javaHome, "jre" + File.separator + "lib" + File.separator + "endorsed");
        results.put("ENDORSED_DIR_EXISTS", endorsedDir.exists());

        return results;
    }

    /**
     * 获取类路径中的无效条目
     * 
     * @return 无效的类路径条目列表
     */
    public List<String> getInvalidClasspathEntries() {
        List<String> invalidEntries = new ArrayList<>();
        String classpath = System.getProperty("java.class.path", "");

        if (classpath.isEmpty()) {
            return invalidEntries;
        }

        String pathSeparator = System.getProperty("path.separator", ":");
        String[] entries = classpath.split(pathSeparator);

        for (String entry : entries) {
            if (entry.trim().isEmpty()) {
                continue;
            }

            File file = new File(entry);
            if (!file.exists()) {
                invalidEntries.add(entry + " (does not exist)");
            } else if (entry.endsWith(".jar") && !file.isFile()) {
                invalidEntries.add(entry + " (not a file)");
            } else if (!entry.endsWith(".jar") && !file.isDirectory()) {
                invalidEntries.add(entry + " (not a directory)");
            }
        }

        return invalidEntries;
    }

    /**
     * 获取库路径中的无效条目
     * 
     * @return 无效的库路径条目列表
     */
    public List<String> getInvalidLibraryPathEntries() {
        List<String> invalidEntries = new ArrayList<>();
        String libraryPath = System.getProperty("java.library.path", "");

        if (libraryPath.isEmpty()) {
            return invalidEntries;
        }

        String pathSeparator = System.getProperty("path.separator", ":");
        String[] entries = libraryPath.split(pathSeparator);

        for (String entry : entries) {
            if (entry.trim().isEmpty()) {
                continue;
            }

            File dir = new File(entry);
            if (!dir.exists()) {
                invalidEntries.add(entry + " (does not exist)");
            } else if (!dir.isDirectory()) {
                invalidEntries.add(entry + " (not a directory)");
            }
        }

        return invalidEntries;
    }

    /**
     * 检查文件权限
     * 
     * @param filePath 文件路径
     * @return 权限检查结果
     */
    public Map<String, Boolean> checkFilePermissions(String filePath) {
        Map<String, Boolean> permissions = new HashMap<>();
        File file = new File(filePath);

        permissions.put("EXISTS", file.exists());
        if (file.exists()) {
            permissions.put("READABLE", file.canRead());
            permissions.put("WRITABLE", file.canWrite());
            permissions.put("EXECUTABLE", file.canExecute());
            permissions.put("IS_FILE", file.isFile());
            permissions.put("IS_DIRECTORY", file.isDirectory());
        }

        return permissions;
    }

    /**
     * 验证Java安装完整性
     * 
     * @param javaHomePath Java安装路径
     * @return 验证结果描述
     */
    public String validateJavaInstallation(String javaHomePath) {
        if (javaHomePath == null || javaHomePath.trim().isEmpty()) {
            return "Java home path is empty";
        }

        File javaHome = new File(javaHomePath);
        if (!javaHome.exists()) {
            return "Java home directory does not exist: " + javaHomePath;
        }

        if (!javaHome.isDirectory()) {
            return "Java home path is not a directory: " + javaHomePath;
        }

        // 检查关键目录
        File binDir = new File(javaHome, "bin");
        if (!binDir.exists()) {
            return "Missing bin directory in Java installation";
        }

        File libDir = new File(javaHome, "lib");
        if (!libDir.exists()) {
            return "Missing lib directory in Java installation";
        }

        // 检查Java可执行文件
        String javaExe = isWindows() ? "java.exe" : "java";
        File javaExecutable = new File(binDir, javaExe);
        if (!javaExecutable.exists()) {
            return "Java executable not found: " + javaExecutable.getAbsolutePath();
        }

        if (!javaExecutable.canExecute()) {
            return "Java executable is not executable: " + javaExecutable.getAbsolutePath();
        }

        return "Java installation is valid";
    }

    /**
     * 获取可能的Java安装路径
     * 
     * @return 可能的Java安装路径列表
     */
    public List<String> getPossibleJavaInstallationPaths() {
        List<String> paths = new ArrayList<>();

        // 从环境变量获取
        String javaHome = System.getenv("JAVA_HOME");
        if (javaHome != null && !javaHome.trim().isEmpty()) {
            paths.add(javaHome);
        }

        // 从系统属性获取
        String javaHomeProperty = System.getProperty("java.home");
        if (javaHomeProperty != null && !paths.contains(javaHomeProperty)) {
            paths.add(javaHomeProperty);
        }

        // 添加常见的安装路径
        if (isWindows()) {
            addIfExists(paths, "C:\\Program Files\\Java");
            addIfExists(paths, "C:\\Program Files (x86)\\Java");
        } else if (isMacOS()) {
            addIfExists(paths, "/System/Library/Java/JavaVirtualMachines");
            addIfExists(paths, "/Library/Java/JavaVirtualMachines");
        } else {
            // Linux/Unix
            addIfExists(paths, "/usr/lib/jvm");
            addIfExists(paths, "/usr/java");
            addIfExists(paths, "/opt/java");
        }

        return paths;
    }

    /**
     * 如果目录存在则添加到列表中
     */
    private void addIfExists(List<String> paths, String path) {
        File dir = new File(path);
        if (dir.exists() && dir.isDirectory() && !paths.contains(path)) {
            paths.add(path);
        }
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