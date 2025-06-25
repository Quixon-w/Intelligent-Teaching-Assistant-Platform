package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.LessonQuestionMap;
import org.cancan.usercenter.model.domain.Questions;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【lesson_question_map】的数据库操作Service
 * {@code @createDate} 2025-06-23 09:10:46
 */
public interface LessonQuestionMapService extends IService<LessonQuestionMap> {

//    /**
//     * 判断课时中是否有此题
//     *
//     * @param lessonId 课时id
//     * @return 是否有题
//     */
//    Boolean hasQuestion(Long lessonId);

    /**
     * 获取课时中的所有题
     *
     * @param lessonId 课时id
     * @return 课时中的所有题
     */
    List<Questions> getOrderedQuestions(Long lessonId);

}
