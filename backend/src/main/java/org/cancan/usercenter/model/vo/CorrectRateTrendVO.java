package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDate;

/**
 * 正确率趋势VO
 */
@Data
public class CorrectRateTrendVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 日期
     */
    private LocalDate date;

    /**
     * 正确率
     */
    private Double correctRate;

    /**
     * 题目数量
     */
    private Long questionCount;
} 