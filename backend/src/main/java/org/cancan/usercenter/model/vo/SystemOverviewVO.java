package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 系统概览VO
 */
@Data
public class SystemOverviewVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 总课程数
     */
    private Long totalCourses;

    /**
     * 总教师数
     */
    private Long totalTeachers;

    /**
     * 总学生数
     */
    private Long totalStudents;

    /**
     * 今日活跃用户数
     */
    private Long todayActiveUsers;

    /**
     * 本周活跃用户数
     */
    private Long weekActiveUsers;

    /**
     * 总测试次数
     */
    private Long totalTests;

    /**
     * 平均通过率
     */
    private Double averagePassRate;
} 