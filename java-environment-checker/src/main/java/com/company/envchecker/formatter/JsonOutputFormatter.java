package com.company.envchecker.formatter;

import com.company.envchecker.model.EnvironmentReport;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

/**
 * JSON输出格式化器
 * 负责将检查结果格式化为JSON格式输出
 */
public class JsonOutputFormatter {

    private final Gson gson;

    public JsonOutputFormatter() {
        this.gson = new GsonBuilder()
            .setPrettyPrinting()
            .setDateFormat("yyyy-MM-dd HH:mm:ss")
            .create();
    }

    /**
     * 格式化环境报告为JSON
     * 
     * @param report 环境报告
     * @return JSON格式的字符串
     */
    public String formatReport(EnvironmentReport report) {
        return gson.toJson(report);
    }

    /**
     * 格式化为紧凑的JSON（无格式化）
     * 
     * @param report 环境报告
     * @return 紧凑的JSON字符串
     */
    public String formatReportCompact(EnvironmentReport report) {
        Gson compactGson = new Gson();
        return compactGson.toJson(report);
    }
}