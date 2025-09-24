package com.company.envchecker.model;

import java.util.Objects;

/**
 * 系统信息模型类
 * 用于封装操作系统和硬件相关信息
 */
public class SystemInfo {
    private String operatingSystem;
    private String osVersion;
    private String architecture;
    private String userName;
    private String userHome;
    private String workingDirectory;
    private String tempDirectory;
    private String fileEncoding;
    private String systemEncoding;

    public SystemInfo() {}

    public SystemInfo(String operatingSystem, String osVersion, String architecture,
                     String userName, String userHome, String workingDirectory,
                     String tempDirectory, String fileEncoding, String systemEncoding) {
        this.operatingSystem = operatingSystem;
        this.osVersion = osVersion;
        this.architecture = architecture;
        this.userName = userName;
        this.userHome = userHome;
        this.workingDirectory = workingDirectory;
        this.tempDirectory = tempDirectory;
        this.fileEncoding = fileEncoding;
        this.systemEncoding = systemEncoding;
    }

    // Getters and Setters
    public String getOperatingSystem() {
        return operatingSystem;
    }

    public void setOperatingSystem(String operatingSystem) {
        this.operatingSystem = operatingSystem;
    }

    public String getOsVersion() {
        return osVersion;
    }

    public void setOsVersion(String osVersion) {
        this.osVersion = osVersion;
    }

    public String getArchitecture() {
        return architecture;
    }

    public void setArchitecture(String architecture) {
        this.architecture = architecture;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getUserHome() {
        return userHome;
    }

    public void setUserHome(String userHome) {
        this.userHome = userHome;
    }

    public String getWorkingDirectory() {
        return workingDirectory;
    }

    public void setWorkingDirectory(String workingDirectory) {
        this.workingDirectory = workingDirectory;
    }

    public String getTempDirectory() {
        return tempDirectory;
    }

    public void setTempDirectory(String tempDirectory) {
        this.tempDirectory = tempDirectory;
    }

    public String getFileEncoding() {
        return fileEncoding;
    }

    public void setFileEncoding(String fileEncoding) {
        this.fileEncoding = fileEncoding;
    }

    public String getSystemEncoding() {
        return systemEncoding;
    }

    public void setSystemEncoding(String systemEncoding) {
        this.systemEncoding = systemEncoding;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SystemInfo that = (SystemInfo) o;
        return Objects.equals(operatingSystem, that.operatingSystem) &&
               Objects.equals(osVersion, that.osVersion) &&
               Objects.equals(architecture, that.architecture) &&
               Objects.equals(userName, that.userName) &&
               Objects.equals(userHome, that.userHome) &&
               Objects.equals(workingDirectory, that.workingDirectory) &&
               Objects.equals(tempDirectory, that.tempDirectory) &&
               Objects.equals(fileEncoding, that.fileEncoding) &&
               Objects.equals(systemEncoding, that.systemEncoding);
    }

    @Override
    public int hashCode() {
        return Objects.hash(operatingSystem, osVersion, architecture, userName,
                          userHome, workingDirectory, tempDirectory, fileEncoding, systemEncoding);
    }

    @Override
    public String toString() {
        return "SystemInfo{" +
               "operatingSystem='" + operatingSystem + '\'' +
               ", osVersion='" + osVersion + '\'' +
               ", architecture='" + architecture + '\'' +
               ", userName='" + userName + '\'' +
               ", userHome='" + userHome + '\'' +
               ", workingDirectory='" + workingDirectory + '\'' +
               ", tempDirectory='" + tempDirectory + '\'' +
               ", fileEncoding='" + fileEncoding + '\'' +
               ", systemEncoding='" + systemEncoding + '\'' +
               '}';
    }
}