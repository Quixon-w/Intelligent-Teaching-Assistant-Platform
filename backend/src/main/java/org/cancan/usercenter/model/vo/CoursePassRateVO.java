package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 课程通过率VO
 */
@Data
public class CoursePassRateVO implements Serializable {

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
     * 通过率
     */
    private Double passRate;

    /**
     * 总测试人数
     */
    private Long totalStudents;

    /**
     * 通过人数
     */
    private Long passedStudents;

    /**
     * 平均分数
     */
    private Double averageScore;
} 