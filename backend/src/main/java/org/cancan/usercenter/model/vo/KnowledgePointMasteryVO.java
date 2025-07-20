package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 知识点掌握情况VO
 */
@Data
public class KnowledgePointMasteryVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 知识点
     */
    private String knowledgePoint;

    /**
     * 掌握率
     */
    private Double masteryRate;

    /**
     * 总题目数
     */
    private Long totalQuestions;

    /**
     * 正确题目数
     */
    private Long correctCount;
} 