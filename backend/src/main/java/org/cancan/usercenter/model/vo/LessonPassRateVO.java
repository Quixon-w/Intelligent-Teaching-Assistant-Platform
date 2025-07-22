package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 课时通过率VO
 */
@Data
public class LessonPassRateVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 课时ID
     */
    private Long lessonId;

    /**
     * 课时名称
     */
    private String lessonName;

    /**
     * 所属课程名称
     */
    private String courseName;

    /**
     * 通过率
     */
    private Double passRate;

    /**
     * 平均分数
     */
    private Double averageScore;

    /**
     * 总记录数
     */
    private Long totalRecords;

    /**
     * 正确记录数
     */
    private Long correctRecords;
} 