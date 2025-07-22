package org.cancan.usercenter.service;

import org.cancan.usercenter.model.dto.AdminStatisticsRequest;
import org.cancan.usercenter.model.vo.*;

/**
 * 管理员统计服务接口
 */
public interface AdminStatisticsService {

    /**
     * 获取教师使用统计
     */
    TeacherUsageStatisticsVO getTeacherUsageStatistics(AdminStatisticsRequest request);

    /**
     * 获取学生使用统计
     */
    StudentUsageStatisticsVO getStudentUsageStatistics(AdminStatisticsRequest request);

    /**
     * 获取教学效率指数
     */
    TeachingEfficiencyVO getTeachingEfficiency(AdminStatisticsRequest request);

    /**
     * 获取学生学习效果
     */
    LearningEffectivenessVO getLearningEffectiveness(AdminStatisticsRequest request);

    /**
     * 获取系统概览数据
     */
    SystemOverviewVO getSystemOverview();

    /**
     * 获取活跃用户数量
     * @param period 统计周期：today-今日，month-本月
     * @return 活跃用户数量
     */
    Long getActiveUsersCount(String period);
} 