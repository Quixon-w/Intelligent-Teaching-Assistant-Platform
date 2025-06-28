package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.User;

/**
 * @author 洪
 * {@code @description} 针对表【lessons】的数据库操作Service
 * {@code @createDate} 2025-06-22 11:12:14
 */
public interface LessonsService extends IService<Lessons> {

    /**
     * 添加课时
     *
     * @param lessonName 课时名
     * @param courseId   课程ID
     * @return 课时对象
     */
    Lessons addLesson(String lessonName, Long courseId);

    /**
     * 判断用户是否是课时的教师
     *
     * @param lessonId    课时ID
     * @param currentUser 当前用户
     */
    void isTeacher(Long lessonId, User currentUser);

    /**
     * 获取有效的课时对象
     *
     * @param lessonId 课时ID
     * @return 课时对象
     */
    Lessons getValidLessonById(Long lessonId);

}
