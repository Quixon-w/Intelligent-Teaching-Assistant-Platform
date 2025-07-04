package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.*;
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.service.LessonsService;
import org.cancan.usercenter.utils.SpecialCode;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【lessons】的数据库操作Service实现
 * {@code @createDate} 2025-06-22 11:12:14
 */
@Service
public class LessonsServiceImpl extends ServiceImpl<LessonsMapper, Lessons> implements LessonsService {

    @Resource
    private LessonsMapper lessonsMapper;
    @Resource
    private CoursesMapper coursesMapper;
    @Resource
    private QuestionRecordsMapper questionRecordsMapper;
    @Resource
    private LessonQuestionMapMapper lessonQuestionMapMapper;
    @Resource
    private ScoresMapper scoresMapper;

    /**
     * @param courseId 课程id
     * @return 课时列表
     */
    @Override
    public List<Lessons> listLessons(Long courseId) {
        // 查询
        QueryWrapper<Lessons> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("course_id", courseId);
        return lessonsMapper.selectList(queryWrapper);
    }

    /**
     * 创建课时
     *
     * @param lessonName 课时名
     * @param courseId   课程ID
     * @return 课时信息
     */
    @Override
    public Lessons addLesson(String lessonName, Long courseId) {
        if (lessonName.length() > 20) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课时名过长");
        }
        SpecialCode.validateCode(lessonName);
        Lessons lessons = new Lessons();
        lessons.setCourseId(courseId);
        lessons.setLessonName(lessonName);
        this.save(lessons);
        return lessons;
    }

    /**
     * @param lessons     课时
     * @param currentUser 当前用户
     */
    @Override
    public Boolean isTeacher(Lessons lessons, User currentUser) {
        // 判断是否是老师本人
        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("id", lessons.getCourseId());
        queryWrapper.eq("teacher_id", currentUser.getId());
        return coursesMapper.exists(queryWrapper);
    }

    /**
     * 获取有效课时
     *
     * @param lessonId 课程ID
     * @return 课时信息
     */
    public Lessons getValidLessonById(Long lessonId) {
        if (lessonId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "课时ID不能为空");
        }
        Lessons lessons = this.getById(lessonId);
        if (lessons == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课时不存在");
        }
        return lessons;
    }

    /**
     * @param lessonId 课时ID
     * @return 删除结果
     */
    @Override
    @Transactional
    public Boolean deleteLesson(Long lessonId) {
        // 删除课时答题记录
        QueryWrapper<QuestionRecords> queryWrapperR = new QueryWrapper<>();
        queryWrapperR.eq("lesson_id", lessonId);
        questionRecordsMapper.delete(queryWrapperR);
        // 删除课时习题映射关系
        QueryWrapper<LessonQuestionMap> queryWrapperM = new QueryWrapper<>();
        queryWrapperM.eq("lesson_id", lessonId);
        lessonQuestionMapMapper.delete(queryWrapperM);
        // 删除课时成绩表
        QueryWrapper<Scores> queryWrapperS = new QueryWrapper<>();
        queryWrapperS.eq("lesson_id", lessonId);
        scoresMapper.delete(queryWrapperS);
        // 移除课时
        return this.removeById(lessonId);
    }

}




