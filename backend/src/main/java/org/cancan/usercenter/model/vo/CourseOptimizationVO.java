package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 课程优化建议VO
 */
@Data
public class CourseOptimizationVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 课程ID
     */
    private Long courseId;

    /**
     * 课程名称
     */
    private String courseName;

    /**
     * 问题类型：low_pass_rate, high_error_rate, poor_engagement等
     */
    private String issueType;

    /**
     * 问题描述
     */
    private String issueDescription;

    /**
     * 建议措施
     */
    private String suggestion;

    /**
     * 优先级：high, medium, low
     */
    private String priority;

    /**
     * 相关数据
     */
    private Double relatedData;
} 