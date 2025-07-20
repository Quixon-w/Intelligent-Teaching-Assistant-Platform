package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import lombok.Data;

import java.util.Date;

/**
 * {@code @TableName} lessons
 */
@TableName(value = "lessons")
@Data
public class Lessons {
    /**
     * 课时ID
     */
    @TableId(type = IdType.AUTO)
    private Long lessonId;

    /**
     * 所属课程ID
     */
    @TableField("course_id")
    private Long courseId;

    /**
     * 课时名称
     */
    private String lessonName;

    /**
     * 课时生成时间
     */
    @TableField("create_time")
    private Date createTime;

    /**
     * 是否有习题
     */
    private Integer hasQuestion;

}