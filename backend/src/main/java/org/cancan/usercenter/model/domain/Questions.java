package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.fasterxml.jackson.annotation.JsonProperty;
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
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private Long questionId;

    /**
     * 教师ID
     */
    private Long teacherId;

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
    @TableField(typeHandler = JacksonTypeHandler.class)
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