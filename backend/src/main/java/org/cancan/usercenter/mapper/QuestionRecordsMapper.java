package org.cancan.usercenter.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.cancan.usercenter.model.domain.QuestionRecords;

import java.util.List;
import java.util.Map;

/**
 * @author 洪
 * {@code @description} 针对表【question_records】的数据库操作Mapper
 * {@code @createDate} 2025-06-23 13:47:55
 * {@code @Entity} generator.domain.QuestionRecords
 */
public interface QuestionRecordsMapper extends BaseMapper<QuestionRecords> {

    /**
     * 获取学生在某课时的错题知识点统计
     *
     * @param lessonId 课时ID
     * @param studentId 学生ID
     * @return 知识点-错误次数的映射
     */
    @Select("SELECT q.knowledge, COUNT(*) as wrongCount " +
            "FROM question_records qr " +
            "JOIN questions q ON qr.question_id = q.question_id " +
            "WHERE qr.lesson_id = #{lessonId} " +
            "AND qr.student_id = #{studentId} " +
            "AND qr.is_correct = 0 " +
            "AND q.knowledge IS NOT NULL " +
            "GROUP BY q.knowledge " +
            "ORDER BY wrongCount DESC")
    List<Map<String, Object>> getWrongKnowledgeStatsByLesson(@Param("lessonId") Long lessonId, @Param("studentId") Long studentId);

    /**
     * 获取学生在某课程的错题知识点统计
     *
     * @param courseId 课程ID
     * @param studentId 学生ID
     * @return 知识点-错误次数的映射
     */
    @Select("SELECT q.knowledge, COUNT(*) as wrongCount " +
            "FROM question_records qr " +
            "JOIN questions q ON qr.question_id = q.question_id " +
            "JOIN lessons l ON qr.lesson_id = l.lesson_id " +
            "WHERE l.course_id = #{courseId} " +
            "AND qr.student_id = #{studentId} " +
            "AND qr.is_correct = 0 " +
            "AND q.knowledge IS NOT NULL " +
            "GROUP BY q.knowledge " +
            "ORDER BY wrongCount DESC")
    List<Map<String, Object>> getWrongKnowledgeStatsByCourse(@Param("courseId") Long courseId, @Param("studentId") Long studentId);

    /**
     * 获取学生在某课时的所有错题记录（包含知识点信息）
     *
     * @param lessonId 课时ID
     * @param studentId 学生ID
     * @return 错题记录列表
     */
    @Select("SELECT qr.*, q.knowledge, q.question, q.explanation " +
            "FROM question_records qr " +
            "JOIN questions q ON qr.question_id = q.question_id " +
            "WHERE qr.lesson_id = #{lessonId} " +
            "AND qr.student_id = #{studentId} " +
            "AND qr.is_correct = 0 " +
            "ORDER BY qr.submit_time DESC")
    List<Map<String, Object>> getWrongQuestionsByLesson(@Param("lessonId") Long lessonId, @Param("studentId") Long studentId);

}




