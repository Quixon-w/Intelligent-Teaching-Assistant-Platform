package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
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
    private Long courseId;

    /**
     * 课时名称
     */
    private String lessonName;

    /**
     * 课时生成时间
     */
    private Date createTime;

}