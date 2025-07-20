package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 高频错误知识点VO
 */
@Data
public class HighFrequencyErrorVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 知识点
     */
    private String knowledgePoint;

    /**
     * 错误次数
     */
    private Long errorCount;

    /**
     * 错误率
     */
    private Double errorRate;

    /**
     * 涉及课程数量
     */
    private Long courseCount;

    /**
     * 涉及学生数量
     */
    private Long studentCount;
} 