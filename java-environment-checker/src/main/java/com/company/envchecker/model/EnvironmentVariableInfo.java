package com.company.envchecker.model;

import java.util.Objects;

/**
 * 环境变量信息模型类
 * 用于封装Java相关的环境变量配置
 */
public class EnvironmentVariableInfo {
    private String javaHome;
    private String pathVariable;
    private String classPath;
    private String jreHome;
    private String javaOpts;
    private String mavenHome;
    private String gradleHome;
    private String m2Home;
    private String antHome;

    public EnvironmentVariableInfo() {}

    public EnvironmentVariableInfo(String javaHome, String pathVariable, String classPath,
                                  String jreHome, String javaOpts, String mavenHome,
                                  String gradleHome, String m2Home, String antHome) {
        this.javaHome = javaHome;
        this.pathVariable = pathVariable;
        this.classPath = classPath;
        this.jreHome = jreHome;
        this.javaOpts = javaOpts;
        this.mavenHome = mavenHome;
        this.gradleHome = gradleHome;
        this.m2Home = m2Home;
        this.antHome = antHome;
    }

    // Getters and Setters
    public String getJavaHome() {
        return javaHome;
    }

    public void setJavaHome(String javaHome) {
        this.javaHome = javaHome;
    }

    public String getPathVariable() {
        return pathVariable;
    }

    public void setPathVariable(String pathVariable) {
        this.pathVariable = pathVariable;
    }

    public String getClassPath() {
        return classPath;
    }

    public void setClassPath(String classPath) {
        this.classPath = classPath;
    }

    public String getJreHome() {
        return jreHome;
    }

    public void setJreHome(String jreHome) {
        this.jreHome = jreHome;
    }

    public String getJavaOpts() {
        return javaOpts;
    }

    public void setJavaOpts(String javaOpts) {
        this.javaOpts = javaOpts;
    }

    public String getMavenHome() {
        return mavenHome;
    }

    public void setMavenHome(String mavenHome) {
        this.mavenHome = mavenHome;
    }

    public String getGradleHome() {
        return gradleHome;
    }

    public void setGradleHome(String gradleHome) {
        this.gradleHome = gradleHome;
    }

    public String getM2Home() {
        return m2Home;
    }

    public void setM2Home(String m2Home) {
        this.m2Home = m2Home;
    }

    public String getAntHome() {
        return antHome;
    }

    public void setAntHome(String antHome) {
        this.antHome = antHome;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        EnvironmentVariableInfo that = (EnvironmentVariableInfo) o;
        return Objects.equals(javaHome, that.javaHome) &&
               Objects.equals(pathVariable, that.pathVariable) &&
               Objects.equals(classPath, that.classPath) &&
               Objects.equals(jreHome, that.jreHome) &&
               Objects.equals(javaOpts, that.javaOpts) &&
               Objects.equals(mavenHome, that.mavenHome) &&
               Objects.equals(gradleHome, that.gradleHome) &&
               Objects.equals(m2Home, that.m2Home) &&
               Objects.equals(antHome, that.antHome);
    }

    @Override
    public int hashCode() {
        return Objects.hash(javaHome, pathVariable, classPath, jreHome,
                          javaOpts, mavenHome, gradleHome, m2Home, antHome);
    }

    @Override
    public String toString() {
        return "EnvironmentVariableInfo{" +
               "javaHome='" + javaHome + '\'' +
               ", pathVariable='" + pathVariable + '\'' +
               ", classPath='" + classPath + '\'' +
               ", jreHome='" + jreHome + '\'' +
               ", javaOpts='" + javaOpts + '\'' +
               ", mavenHome='" + mavenHome + '\'' +
               ", gradleHome='" + gradleHome + '\'' +
               ", m2Home='" + m2Home + '\'' +
               ", antHome='" + antHome + '\'' +
               '}';
    }
}