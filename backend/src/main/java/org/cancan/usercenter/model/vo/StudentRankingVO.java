package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 学生排名VO
 */
@Data
public class StudentRankingVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 学生ID
     */
    private Long studentId;

    /**
     * 学生姓名
     */
    private String studentName;

    /**
     * 使用次数
     */
    private Long usageCount;

    /**
     * 排名
     */
    private Integer ranking;
} 