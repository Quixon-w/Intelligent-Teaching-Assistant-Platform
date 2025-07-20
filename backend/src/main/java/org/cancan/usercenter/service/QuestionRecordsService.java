package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.QuestionRecords;

import java.util.List;
import java.util.Map;

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

    /**
     * 获取学生在某课时的错题知识点统计
     *
     * @param lessonId 课时ID
     * @param studentId 学生ID
     * @return 知识点-错误次数的映射
     */
    List<Map<String, Object>> getWrongKnowledgeStatsByLesson(Long lessonId, Long studentId);

    /**
     * 获取学生在某课程的错题知识点统计
     *
     * @param courseId 课程ID
     * @param studentId 学生ID
     * @return 知识点-错误次数的映射
     */
    List<Map<String, Object>> getWrongKnowledgeStatsByCourse(Long courseId, Long studentId);

    /**
     * 获取学生在某课时的所有错题记录（包含知识点信息）
     *
     * @param lessonId 课时ID
     * @param studentId 学生ID
     * @return 错题记录列表
     */
    List<Map<String, Object>> getWrongQuestionsByLesson(Long lessonId, Long studentId);

}
