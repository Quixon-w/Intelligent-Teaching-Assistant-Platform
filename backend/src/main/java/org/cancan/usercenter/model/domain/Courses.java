package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * {@code @TableName} courses
 */
@TableName(value = "courses")
@Data
public class Courses {
    /**
     * 课程ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 课程名称
     */
    private String name;

    /**
     * 教师ID
     */
    private Long teacherId;

    /**
     * 教师名字
     */
    private String teacherName;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 课程简介
     */
    private String comment;

    /**
     * 课程是否结束
     */
    private Integer isOver;
}