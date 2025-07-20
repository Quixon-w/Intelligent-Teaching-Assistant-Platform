package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.mapper.QuestionRecordsMapper;
import org.cancan.usercenter.model.domain.QuestionRecords;
import org.cancan.usercenter.service.QuestionRecordsService;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * @author 洪
 * {@code @description} 针对表【question_records】的数据库操作Service实现
 * {@code @createDate} 2025-06-23 13:47:55
 */
@Service
public class QuestionRecordsServiceImpl extends ServiceImpl<QuestionRecordsMapper, QuestionRecords> implements QuestionRecordsService {

    @Resource
    private QuestionRecordsMapper questionRecordsMapper;

    /**
     * @param lessonId 课时ID
     * @return 做题记录
     */
    @Override
    public List<QuestionRecords> getStudentLessonRecords(Long lessonId, Long studentId) {
        // 搜索答题记录
        QueryWrapper<QuestionRecords> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("student_id", studentId);
        queryWrapper.eq("lesson_id", lessonId);
        queryWrapper.orderByAsc("question_id");
        return questionRecordsMapper.selectList(queryWrapper);
    }

    /**
     * 获取学生在某课时的错题知识点统计
     *
     * @param lessonId 课时ID
     * @param studentId 学生ID
     * @return 知识点-错误次数的映射
     */
    @Override
    public List<Map<String, Object>> getWrongKnowledgeStatsByLesson(Long lessonId, Long studentId) {
        return questionRecordsMapper.getWrongKnowledgeStatsByLesson(lessonId, studentId);
    }

    /**
     * 获取学生在某课程的错题知识点统计
     *
     * @param courseId 课程ID
     * @param studentId 学生ID
     * @return 知识点-错误次数的映射
     */
    @Override
    public List<Map<String, Object>> getWrongKnowledgeStatsByCourse(Long courseId, Long studentId) {
        return questionRecordsMapper.getWrongKnowledgeStatsByCourse(courseId, studentId);
    }

    /**
     * 获取学生在某课时的所有错题记录（包含知识点信息）
     *
     * @param lessonId 课时ID
     * @param studentId 学生ID
     * @return 错题记录列表
     */
    @Override
    public List<Map<String, Object>> getWrongQuestionsByLesson(Long lessonId, Long studentId) {
        return questionRecordsMapper.getWrongQuestionsByLesson(lessonId, studentId);
    }
}




