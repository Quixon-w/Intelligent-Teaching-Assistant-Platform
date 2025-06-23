package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * {@code @TableName} question_records
 */
@TableName(value = "question_records")
@Data
public class QuestionRecords {
    /**
     * 记录ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 学生ID
     */
    private Long studentId;

    /**
     * 习题ID
     */
    private Long questionId;

    /**
     * 选择的选项
     */
    private String selectedOption;

    /**
     * 是否正确
     */
    private Integer isCorrect;

    /**
     * 提交时间
     */
    private Date submitTime;

    /**
     * 课时id
     */
    private Long lessonId;
}