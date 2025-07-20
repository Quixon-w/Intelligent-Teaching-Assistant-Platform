package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 学科表现VO
 */
@Data
public class SubjectPerformanceVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 学科名称
     */
    private String subjectName;

    /**
     * 平均通过率
     */
    private Double averagePassRate;

    /**
     * 学生数量
     */
    private Long studentCount;

    /**
     * 课程数量
     */
    private Long courseCount;
} 