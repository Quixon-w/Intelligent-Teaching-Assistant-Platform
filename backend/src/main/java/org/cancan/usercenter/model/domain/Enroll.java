package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * 
 * {@code @TableName} enroll
 */
@TableName(value ="enroll")
@Data
public class Enroll {
    /**
     * id
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 课程ID
     */
    private Long coursesId;

    /**
     * 学生ID
     */
    private Long studentId;

    /**
     * 最终成绩
     */
    private Double finalScore;

    /**
     * 选课时间
     */
    private Date startTime;
}