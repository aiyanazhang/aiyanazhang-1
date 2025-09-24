package com.company.envchecker.model;

import java.util.Objects;

/**
 * 诊断结果模型类
 * 用于封装环境诊断的结果信息
 */
public class DiagnosticResult {
    /**
     * 诊断级别枚举
     */
    public enum Level {
        INFO("INFO"),
        WARN("WARN"),
        ERROR("ERROR");

        private final String value;

        Level(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }

        @Override
        public String toString() {
            return value;
        }
    }

    private String category;
    private Level level;
    private String message;
    private String suggestion;
    private String affectedComponent;
    private String checkName;

    public DiagnosticResult() {}

    public DiagnosticResult(String category, Level level, String message,
                           String suggestion, String affectedComponent, String checkName) {
        this.category = category;
        this.level = level;
        this.message = message;
        this.suggestion = suggestion;
        this.affectedComponent = affectedComponent;
        this.checkName = checkName;
    }

    // Getters and Setters
    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public Level getLevel() {
        return level;
    }

    public void setLevel(Level level) {
        this.level = level;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSuggestion() {
        return suggestion;
    }

    public void setSuggestion(String suggestion) {
        this.suggestion = suggestion;
    }

    public String getAffectedComponent() {
        return affectedComponent;
    }

    public void setAffectedComponent(String affectedComponent) {
        this.affectedComponent = affectedComponent;
    }

    public String getCheckName() {
        return checkName;
    }

    public void setCheckName(String checkName) {
        this.checkName = checkName;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DiagnosticResult that = (DiagnosticResult) o;
        return Objects.equals(category, that.category) &&
               level == that.level &&
               Objects.equals(message, that.message) &&
               Objects.equals(suggestion, that.suggestion) &&
               Objects.equals(affectedComponent, that.affectedComponent) &&
               Objects.equals(checkName, that.checkName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(category, level, message, suggestion, affectedComponent, checkName);
    }

    @Override
    public String toString() {
        return "DiagnosticResult{" +
               "category='" + category + '\'' +
               ", level=" + level +
               ", message='" + message + '\'' +
               ", suggestion='" + suggestion + '\'' +
               ", affectedComponent='" + affectedComponent + '\'' +
               ", checkName='" + checkName + '\'' +
               '}';
    }
}