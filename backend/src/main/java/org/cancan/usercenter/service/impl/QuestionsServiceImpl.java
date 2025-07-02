package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.CollectionUtils;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.mapper.LessonQuestionMapMapper;
import org.cancan.usercenter.mapper.LessonsMapper;
import org.cancan.usercenter.mapper.QuestionsMapper;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.LessonQuestionMap;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.service.QuestionsService;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【questions】的数据库操作Service实现
 * {@code @createDate} 2025-06-22 10:55:25
 */
@Service
public class QuestionsServiceImpl extends ServiceImpl<QuestionsMapper, Questions> implements QuestionsService {

    @Resource
    private CoursesMapper coursesMapper;
    @Resource
    private QuestionsMapper questionsMapper;
    @Resource
    private LessonQuestionMapMapper lessonQuestionMapMapper;
    @Resource
    private LessonsMapper lessonsMapper;

    /**
     * @param father 父级知识点
     * @return 问题集
     */
    @Override
    public List<Questions> selectByFather(String father, Long teacherId) {
        if (father == null || teacherId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "父级知识点为空或教师ID为空");
        }
        return questionsMapper.selectMatchedQuestions(father, teacherId);
    }

    /**
     * @param question 习题
     * @return 添加的习题
     */
    @Override
    public Boolean addQuestion(Questions question) {
        // 校验参数
        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("teacher_id", question.getTeacherId());
        if (!coursesMapper.exists(queryWrapper)) {
            throw new BusinessException(ErrorCode.NO_AUTH, "无开设课程");
        }
        if (StringUtils.isAnyBlank(
                question.getKnowledge(), question.getQuestion(), question.getAnswer(), question.getExplanation()
        ) || question.getOptions() == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "存在参数为空");
        }
        int result = questionsMapper.insert(question);
        if (result <= 0) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加失败");
        } else {
            return true;
        }
    }

//    /**
//     * @param questions 问题
//     * @return 修改成功
//     */
//    @Override
//    public Boolean addQuestionList(List<Questions> questions) {
//        if (CollectionUtils.isEmpty(questions)) {
//            throw new BusinessException(ErrorCode.PARAMS_ERROR, "问题列表不能为空");
//        }
//        // 校验老师是否有课程
//        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
//        queryWrapper.eq("teacher_id", questions.get(0).getTeacherId());
//        if (!coursesMapper.exists(queryWrapper)) {
//            throw new BusinessException(ErrorCode.NO_AUTH, "无开设课程");
//        }
//        // 校验参数
//        for (Questions question : questions) {
//            if (StringUtils.isAnyBlank(
//                    question.getKnowledge(), question.getQuestion(), question.getAnswer(), question.getExplanation()
//            ) || question.getOptions() == null) {
//                throw new BusinessException(ErrorCode.NULL_ERROR, "存在参数为空");
//            }
//        }
//        // 批量保存
//        List<BatchResult> saved = questionsMapper.insert(questions);
//        if (CollectionUtils.isEmpty(Collections.singleton(saved))) {
//            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "批量添加失败");
//        }
//        return true;
//    }

    /**
     * @param teacherId 教师id
     * @return 习题集
     */
    @Override
    public List<Questions> listByTeacherId(Long teacherId) {
        if (teacherId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "教师ID为空");
        }
        QueryWrapper<Questions> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("teacher_id", teacherId);
        return questionsMapper.selectList(queryWrapper);
    }

    /**
     * @param questionId 问题id
     * @return 查询结果
     */
    @Override
    public List<Lessons> isCommitted(Long questionId) {
        // 查询所有使用到该题的课时 Ids
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("question_id", questionId);
        queryWrapper.select("DISTINCT lesson_id"); // 去重
        List<Object> rawIds = lessonQuestionMapMapper.selectObjs(queryWrapper);
        List<Long> lessonQuestionMapIds = rawIds.stream()
                .map(id -> Long.valueOf(id.toString()))
                .toList();
        // 批量查所有课时
        if (CollectionUtils.isEmpty(lessonQuestionMapIds)) {
            return Collections.emptyList();
        }
        return lessonsMapper.selectByIds(lessonQuestionMapIds);
    }
}




