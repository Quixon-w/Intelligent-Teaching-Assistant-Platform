package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;

/**
 * 活跃板块VO
 */
@Data
public class ActiveModuleVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 板块名称
     */
    private String moduleName;

    /**
     * 使用次数
     */
    private Long usageCount;

    /**
     * 占比
     */
    private Double percentage;

    /**
     * 板块类型：course_management, question_generation, student_analysis等
     */
    private String moduleType;
} 