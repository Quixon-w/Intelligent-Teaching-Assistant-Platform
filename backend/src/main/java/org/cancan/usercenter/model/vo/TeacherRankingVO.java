package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 教师排名VO
 */
@Data
public class TeacherRankingVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 教师ID
     */
    private Long teacherId;

    /**
     * 教师姓名
     */
    private String teacherName;

    /**
     * 使用次数
     */
    private Long usageCount;

    /**
     * 排名
     */
    private Integer ranking;
} 