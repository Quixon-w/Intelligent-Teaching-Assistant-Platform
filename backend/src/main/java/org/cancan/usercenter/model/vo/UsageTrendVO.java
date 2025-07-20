package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 使用趋势VO
 */
@Data
public class UsageTrendVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 时间点
     */
    private LocalDateTime timePoint;

    /**
     * 使用次数
     */
    private Long usageCount;

    /**
     * 用户类型：teacher, student
     */
    private String userType;
} 