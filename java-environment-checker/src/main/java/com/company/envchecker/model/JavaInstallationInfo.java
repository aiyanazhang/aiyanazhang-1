package com.company.envchecker.model;

import java.util.Objects;

/**
 * Java安装信息模型类
 * 用于封装系统中已安装的JDK/JRE版本信息
 */
public class JavaInstallationInfo {
    private String installPath;
    private String version;
    private String vendor;
    private String type; // JDK or JRE
    private String architecture;
    private boolean isActive;
    private String buildInfo;
    private String specificationVersion;

    public JavaInstallationInfo() {}

    public JavaInstallationInfo(String installPath, String version, String vendor,
                               String type, String architecture, boolean isActive,
                               String buildInfo, String specificationVersion) {
        this.installPath = installPath;
        this.version = version;
        this.vendor = vendor;
        this.type = type;
        this.architecture = architecture;
        this.isActive = isActive;
        this.buildInfo = buildInfo;
        this.specificationVersion = specificationVersion;
    }

    // Getters and Setters
    public String getInstallPath() {
        return installPath;
    }

    public void setInstallPath(String installPath) {
        this.installPath = installPath;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getVendor() {
        return vendor;
    }

    public void setVendor(String vendor) {
        this.vendor = vendor;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getArchitecture() {
        return architecture;
    }

    public void setArchitecture(String architecture) {
        this.architecture = architecture;
    }

    public boolean isActive() {
        return isActive;
    }

    public void setActive(boolean active) {
        isActive = active;
    }

    public String getBuildInfo() {
        return buildInfo;
    }

    public void setBuildInfo(String buildInfo) {
        this.buildInfo = buildInfo;
    }

    public String getSpecificationVersion() {
        return specificationVersion;
    }

    public void setSpecificationVersion(String specificationVersion) {
        this.specificationVersion = specificationVersion;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        JavaInstallationInfo that = (JavaInstallationInfo) o;
        return isActive == that.isActive &&
               Objects.equals(installPath, that.installPath) &&
               Objects.equals(version, that.version) &&
               Objects.equals(vendor, that.vendor) &&
               Objects.equals(type, that.type) &&
               Objects.equals(architecture, that.architecture) &&
               Objects.equals(buildInfo, that.buildInfo) &&
               Objects.equals(specificationVersion, that.specificationVersion);
    }

    @Override
    public int hashCode() {
        return Objects.hash(installPath, version, vendor, type, architecture,
                          isActive, buildInfo, specificationVersion);
    }

    @Override
    public String toString() {
        return "JavaInstallationInfo{" +
               "installPath='" + installPath + '\'' +
               ", version='" + version + '\'' +
               ", vendor='" + vendor + '\'' +
               ", type='" + type + '\'' +
               ", architecture='" + architecture + '\'' +
               ", isActive=" + isActive +
               ", buildInfo='" + buildInfo + '\'' +
               ", specificationVersion='" + specificationVersion + '\'' +
               '}';
    }
}