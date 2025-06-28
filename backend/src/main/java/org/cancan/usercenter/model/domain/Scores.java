package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * {@code @TableName} scores
 */
@TableName(value = "scores")
@Data
public class Scores {
    /**
     * 学生ID
     */
    @TableId
    private Long studentId;

    /**
     * 测试ID
     */
    private Long lessonId;

    /**
     * 测试得分
     */
    private Float score;

    /**
     * 高频错误知识点
     */
    private Object commenErrors;

    /**
     * 更新时间
     */
    private String updateTime;
}