package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.mapper.LessonsMapper;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.LessonsService;
import org.cancan.usercenter.utils.SpecialCode;
import org.springframework.stereotype.Service;

/**
 * @author 洪
 * {@code @description} 针对表【lessons】的数据库操作Service实现
 * {@code @createDate} 2025-06-22 11:12:14
 */
@Service
public class LessonsServiceImpl extends ServiceImpl<LessonsMapper, Lessons> implements LessonsService {

    @Resource
    private CoursesMapper coursesMapper;

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
     * @param lessonId    课时ID
     * @param currentUser 当前用户
     */
    @Override
    public Boolean isTeacher(Long lessonId, User currentUser) {
        // 确认有效性
        Lessons lessons = this.getValidLessonById(lessonId);
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

}




