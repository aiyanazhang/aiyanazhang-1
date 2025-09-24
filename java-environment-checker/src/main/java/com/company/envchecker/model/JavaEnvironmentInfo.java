package com.company.envchecker.model;

import java.util.Objects;

/**
 * Java环境信息模型类
 * 用于封装Java版本和JVM相关信息
 */
public class JavaEnvironmentInfo {
    private String javaVersion;
    private String javaSpecVersion;
    private String javaVendor;
    private String javaHome;
    private String vmName;
    private String vmVersion;
    private String vmVendor;
    private String runtimeName;
    private String runtimeVersion;
    private String classPath;
    private String libraryPath;
    private String bootClassPath;

    public JavaEnvironmentInfo() {}

    public JavaEnvironmentInfo(String javaVersion, String javaSpecVersion, String javaVendor,
                              String javaHome, String vmName, String vmVersion, String vmVendor,
                              String runtimeName, String runtimeVersion, String classPath,
                              String libraryPath, String bootClassPath) {
        this.javaVersion = javaVersion;
        this.javaSpecVersion = javaSpecVersion;
        this.javaVendor = javaVendor;
        this.javaHome = javaHome;
        this.vmName = vmName;
        this.vmVersion = vmVersion;
        this.vmVendor = vmVendor;
        this.runtimeName = runtimeName;
        this.runtimeVersion = runtimeVersion;
        this.classPath = classPath;
        this.libraryPath = libraryPath;
        this.bootClassPath = bootClassPath;
    }

    // Getters and Setters
    public String getJavaVersion() {
        return javaVersion;
    }

    public void setJavaVersion(String javaVersion) {
        this.javaVersion = javaVersion;
    }

    public String getJavaSpecVersion() {
        return javaSpecVersion;
    }

    public void setJavaSpecVersion(String javaSpecVersion) {
        this.javaSpecVersion = javaSpecVersion;
    }

    public String getJavaVendor() {
        return javaVendor;
    }

    public void setJavaVendor(String javaVendor) {
        this.javaVendor = javaVendor;
    }

    public String getJavaHome() {
        return javaHome;
    }

    public void setJavaHome(String javaHome) {
        this.javaHome = javaHome;
    }

    public String getVmName() {
        return vmName;
    }

    public void setVmName(String vmName) {
        this.vmName = vmName;
    }

    public String getVmVersion() {
        return vmVersion;
    }

    public void setVmVersion(String vmVersion) {
        this.vmVersion = vmVersion;
    }

    public String getVmVendor() {
        return vmVendor;
    }

    public void setVmVendor(String vmVendor) {
        this.vmVendor = vmVendor;
    }

    public String getRuntimeName() {
        return runtimeName;
    }

    public void setRuntimeName(String runtimeName) {
        this.runtimeName = runtimeName;
    }

    public String getRuntimeVersion() {
        return runtimeVersion;
    }

    public void setRuntimeVersion(String runtimeVersion) {
        this.runtimeVersion = runtimeVersion;
    }

    public String getClassPath() {
        return classPath;
    }

    public void setClassPath(String classPath) {
        this.classPath = classPath;
    }

    public String getLibraryPath() {
        return libraryPath;
    }

    public void setLibraryPath(String libraryPath) {
        this.libraryPath = libraryPath;
    }

    public String getBootClassPath() {
        return bootClassPath;
    }

    public void setBootClassPath(String bootClassPath) {
        this.bootClassPath = bootClassPath;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        JavaEnvironmentInfo that = (JavaEnvironmentInfo) o;
        return Objects.equals(javaVersion, that.javaVersion) &&
               Objects.equals(javaSpecVersion, that.javaSpecVersion) &&
               Objects.equals(javaVendor, that.javaVendor) &&
               Objects.equals(javaHome, that.javaHome) &&
               Objects.equals(vmName, that.vmName) &&
               Objects.equals(vmVersion, that.vmVersion) &&
               Objects.equals(vmVendor, that.vmVendor) &&
               Objects.equals(runtimeName, that.runtimeName) &&
               Objects.equals(runtimeVersion, that.runtimeVersion) &&
               Objects.equals(classPath, that.classPath) &&
               Objects.equals(libraryPath, that.libraryPath) &&
               Objects.equals(bootClassPath, that.bootClassPath);
    }

    @Override
    public int hashCode() {
        return Objects.hash(javaVersion, javaSpecVersion, javaVendor, javaHome,
                          vmName, vmVersion, vmVendor, runtimeName, runtimeVersion,
                          classPath, libraryPath, bootClassPath);
    }

    @Override
    public String toString() {
        return "JavaEnvironmentInfo{" +
               "javaVersion='" + javaVersion + '\'' +
               ", javaSpecVersion='" + javaSpecVersion + '\'' +
               ", javaVendor='" + javaVendor + '\'' +
               ", javaHome='" + javaHome + '\'' +
               ", vmName='" + vmName + '\'' +
               ", vmVersion='" + vmVersion + '\'' +
               ", vmVendor='" + vmVendor + '\'' +
               ", runtimeName='" + runtimeName + '\'' +
               ", runtimeVersion='" + runtimeVersion + '\'' +
               ", classPath='" + classPath + '\'' +
               ", libraryPath='" + libraryPath + '\'' +
               ", bootClassPath='" + bootClassPath + '\'' +
               '}';
    }
}