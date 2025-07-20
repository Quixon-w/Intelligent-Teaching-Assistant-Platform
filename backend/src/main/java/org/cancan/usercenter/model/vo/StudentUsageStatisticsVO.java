package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 学生使用统计VO
 */
@Data
public class StudentUsageStatisticsVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 总使用次数
     */
    private Long totalUsageCount;

    /**
     * 活跃学生数量
     */
    private Long activeStudentCount;

    /**
     * 平均使用次数
     */
    private Double averageUsageCount;

    /**
     * 最活跃板块
     */
    private List<ActiveModuleVO> activeModules;

    /**
     * 使用趋势数据
     */
    private List<UsageTrendVO> usageTrends;

    /**
     * 学生使用排名
     */
    private List<StudentRankingVO> studentRankings;
} 