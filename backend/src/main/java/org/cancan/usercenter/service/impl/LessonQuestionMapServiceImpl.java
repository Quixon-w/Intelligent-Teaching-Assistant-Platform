package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.cancan.usercenter.mapper.LessonQuestionMapMapper;
import org.cancan.usercenter.model.domain.LessonQuestionMap;
import org.cancan.usercenter.service.LessonQuestionMapService;
import org.springframework.stereotype.Service;

/**
 * @author 洪
 * {@code @description} 针对表【lesson_question_map】的数据库操作Service实现
 * {@code @createDate} 2025-06-23 09:10:46
 */
@Service
public class LessonQuestionMapServiceImpl extends ServiceImpl<LessonQuestionMapMapper, LessonQuestionMap> implements LessonQuestionMapService {

    /**
     * @param lessonId 课时id
     * @return 课时下是否有题目
     */
    @Override
    public Boolean hasQuestion(Long lessonId) {
        QueryWrapper<LessonQuestionMap> queryWrapperL = new QueryWrapper<>();
        queryWrapperL.eq("lesson_id", lessonId);
        return !this.exists(queryWrapperL);
    }
}




