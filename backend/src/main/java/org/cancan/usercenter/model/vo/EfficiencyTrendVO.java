package org.cancan.usercenter.model.vo;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDate;

/**
 * 效率趋势VO
 */
@Data
public class EfficiencyTrendVO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 日期
     */
    private LocalDate date;

    /**
     * 效率指数
     */
    private Double efficiencyIndex;

    /**
     * 通过率
     */
    private Double passRate;
} 