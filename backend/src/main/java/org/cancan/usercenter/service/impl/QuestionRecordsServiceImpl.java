package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.mapper.QuestionRecordsMapper;
import org.cancan.usercenter.model.domain.QuestionRecords;
import org.cancan.usercenter.service.QuestionRecordsService;
import org.springframework.stereotype.Service;

import java.util.List;

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
}




