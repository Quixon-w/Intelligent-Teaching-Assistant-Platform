package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 教学效率指数VO
 */
@Data
public class TeachingEfficiencyVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 整体教学效率指数
     */
    private Double overallEfficiencyIndex;

    /**
     * 课程通过率统计
     */
    private List<CoursePassRateVO> coursePassRates;

    /**
     * 需要优化的课程
     */
    private List<CourseOptimizationVO> optimizationSuggestions;

    /**
     * 教学效率趋势
     */
    private List<EfficiencyTrendVO> efficiencyTrends;

    /**
     * 学科表现分析
     */
    private List<SubjectPerformanceVO> subjectPerformances;
} 