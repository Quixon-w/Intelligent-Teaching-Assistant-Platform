package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 教师使用统计VO
 */
@Data
public class TeacherUsageStatisticsVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 总使用次数
     */
    private Long totalUsageCount;

    /**
     * 活跃教师数量
     */
    private Long activeTeacherCount;

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
     * 教师使用排名
     */
    private List<TeacherRankingVO> teacherRankings;
} 