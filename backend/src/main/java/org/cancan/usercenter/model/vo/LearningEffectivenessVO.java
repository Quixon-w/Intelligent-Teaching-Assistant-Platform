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
     * 整体学习效果指数
     */
    private Double overallEffectiveness;

    /**
     * 课时通过率统计
     */
    private List<LessonPassRateVO> lessonPassRates;

    /**
     * 学生排名
     */
    private List<StudentRankingVO> studentRankings;
} 