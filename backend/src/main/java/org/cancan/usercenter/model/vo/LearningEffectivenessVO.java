package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 学生学习效果VO
 */
@Data
public class LearningEffectivenessVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 平均正确率
     */
    private Double averageCorrectRate;

    /**
     * 正确率趋势
     */
    private List<CorrectRateTrendVO> correctRateTrends;

    /**
     * 知识点掌握情况
     */
    private List<KnowledgePointMasteryVO> knowledgePointMastery;

    /**
     * 高频错误知识点
     */
    private List<HighFrequencyErrorVO> highFrequencyErrors;

    /**
     * 学习效果分布
     */
    private List<LearningEffectivenessDistributionVO> effectivenessDistribution;
} 