package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.QuestionRecords;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【question_records】的数据库操作Service
 * {@code @createDate} 2025-06-23 13:47:55
 */
public interface QuestionRecordsService extends IService<QuestionRecords> {

    /**
     * 获取某学生某课时做题记录
     *
     * @param lessonId 课时ID
     * @return 课时做题记录
     */
    List<QuestionRecords> getStudentLessonRecords(Long lessonId, Long studentId);

}
