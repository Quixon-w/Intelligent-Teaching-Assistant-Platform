package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * {@code @TableName} lesson_question_map
 */
@TableName(value = "lesson_question_map")
@Data
public class LessonQuestionMap {
    /**
     * 课时ID
     */
    private Long lessonId;

    /**
     * 习题ID
     */
    private Long questionId;

    /**
     * 习题在测试中的时间顺序
     */
    private Date timeOrder;
}