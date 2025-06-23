package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * {@code @TableName} questions
 */
@TableName(value = "questions")
@Data
public class Questions {
    /**
     * 习题ID
     */
    @TableId(type = IdType.AUTO)
    private Long questionId;

    /**
     * 知识点
     */
    private String knowledge;

    /**
     * 题目
     */
    private String question;

    /**
     * 选项
     */
    private Object options;

    /**
     * 答案
     */
    private String answer;

    /**
     * 解析
     */
    private String explanation;
}