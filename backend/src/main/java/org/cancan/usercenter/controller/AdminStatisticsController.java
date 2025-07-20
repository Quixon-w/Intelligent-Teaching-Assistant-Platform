package org.cancan.usercenter.controller;

import org.cancan.usercenter.common.BaseResponse;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.common.ResultUtils;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.model.dto.AdminStatisticsRequest;
import org.cancan.usercenter.model.vo.*;
import org.cancan.usercenter.service.AdminStatisticsService;
import org.springframework.web.bind.annotation.*;

import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 管理员统计数据控制器
 */
@RestController
@RequestMapping("/api/admin/statistics")
public class AdminStatisticsController {

    @Resource
    private AdminStatisticsService adminStatisticsService;

    /**
     * 获取教师使用统计
     */
    @PostMapping("/teacher-usage")
    public BaseResponse<TeacherUsageStatisticsVO> getTeacherUsageStatistics(
            @RequestBody AdminStatisticsRequest request,
            HttpServletRequest httpServletRequest) {
        if (request == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请求参数不能为空");
        }
        TeacherUsageStatisticsVO result = adminStatisticsService.getTeacherUsageStatistics(request);
        return ResultUtils.success(result);
    }

    /**
     * 获取学生使用统计
     */
    @PostMapping("/student-usage")
    public BaseResponse<StudentUsageStatisticsVO> getStudentUsageStatistics(
            @RequestBody AdminStatisticsRequest request,
            HttpServletRequest httpServletRequest) {
        if (request == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请求参数不能为空");
        }
        StudentUsageStatisticsVO result = adminStatisticsService.getStudentUsageStatistics(request);
        return ResultUtils.success(result);
    }

    /**
     * 获取教学效率指数
     */
    @PostMapping("/teaching-efficiency")
    public BaseResponse<TeachingEfficiencyVO> getTeachingEfficiency(
            @RequestBody AdminStatisticsRequest request,
            HttpServletRequest httpServletRequest) {
        if (request == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请求参数不能为空");
        }
        TeachingEfficiencyVO result = adminStatisticsService.getTeachingEfficiency(request);
        return ResultUtils.success(result);
    }

    /**
     * 获取学生学习效果
     */
    @PostMapping("/learning-effectiveness")
    public BaseResponse<LearningEffectivenessVO> getLearningEffectiveness(
            @RequestBody AdminStatisticsRequest request,
            HttpServletRequest httpServletRequest) {
        if (request == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请求参数不能为空");
        }
        LearningEffectivenessVO result = adminStatisticsService.getLearningEffectiveness(request);
        return ResultUtils.success(result);
    }

    /**
     * 获取系统概览数据
     */
    @GetMapping("/overview")
    public BaseResponse<SystemOverviewVO> getSystemOverview(HttpServletRequest httpServletRequest) {
        SystemOverviewVO result = adminStatisticsService.getSystemOverview();
        return ResultUtils.success(result);
    }
} 