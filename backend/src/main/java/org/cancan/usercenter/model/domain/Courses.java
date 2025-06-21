package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * 
 * @TableName courses
 */
@TableName(value ="courses")
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
     * 创建时间
     */
    private Date createTime;
}