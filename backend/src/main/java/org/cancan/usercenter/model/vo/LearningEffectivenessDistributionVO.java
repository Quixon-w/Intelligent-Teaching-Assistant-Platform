package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 学习效果分布VO
 */
@Data
public class LearningEffectivenessDistributionVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 等级
     */
    private String level;

    /**
     * 学生数量
     */
    private Long studentCount;

    /**
     * 占比
     */
    private Double percentage;

    /**
     * 分数范围
     */
    private String scoreRange;
} 