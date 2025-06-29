package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.mapper.LessonQuestionMapMapper;
import org.cancan.usercenter.model.domain.LessonQuestionMap;
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.service.LessonQuestionMapService;
import org.cancan.usercenter.service.QuestionsService;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

/**
 * @author 洪
 * {@code @description} 针对表【lesson_question_map】的数据库操作Service实现
 * {@code @createDate} 2025-06-23 09:10:46
 */
@Service
public class LessonQuestionMapServiceImpl extends ServiceImpl<LessonQuestionMapMapper, LessonQuestionMap> implements LessonQuestionMapService {

    @Resource
    private QuestionsService questionsService;

    /**
     * @param lessonId 课时id
     * @return 课时习题表
     */
    @Override
    public List<Questions> getOrderedQuestions(Long lessonId, boolean committed) {
        // 获取课时问题列表
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        if (committed) {
            queryWrapper.eq("committed", 1);
        }
        List<Long> questionIds = this.list(queryWrapper).stream()
                .map(LessonQuestionMap::getQuestionId).toList();
        if (questionIds.isEmpty()) {
            return Collections.emptyList();
        }
        List<Questions> questions = questionsService.listByIds(questionIds);
        // 将结果转为 Map，方便按 ID 查找
        Map<Long, Questions> map = questions.stream()
                .collect(Collectors.toMap(Questions::getQuestionId, q -> q));
        // 按 questionIds 顺序重建 List
        return questionIds.stream()
                .map(map::get) // 保证顺序
                .filter(Objects::nonNull) // 万一某个 ID 没查到，避免 NPE
                .toList();
    }

}




