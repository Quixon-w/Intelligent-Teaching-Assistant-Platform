package org.cancan.usercenter.model.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * 管理员统计请求
 */
@Data
public class AdminStatisticsRequest implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 统计类型：today(当日), week(本周), month(本月)
     */
    private String period = "today";

    /**
     * 课程ID（可选，用于特定课程统计）
     */
    private Long courseId;

    /**
     * 教师ID（可选，用于特定教师统计）
     */
    private Long teacherId;

    /**
     * 学生ID（可选，用于特定学生统计）
     */
    private Long studentId;
} 