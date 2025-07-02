package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.User;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【lessons】的数据库操作Service
 * {@code @createDate} 2025-06-22 11:12:14
 */
public interface LessonsService extends IService<Lessons> {

    /**
     * 查看某课程的所有课时
     *
     * @param courseId 课程id
     * @return 课时列表
     */
    List<Lessons> listLessons(Long courseId);

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
     * @param lessons     课时
     * @param currentUser 当前用户
     */
    Boolean isTeacher(Lessons lessons, User currentUser);

    /**
     * 获取有效的课时对象
     *
     * @param lessonId 课时ID
     * @return 课时对象
     */
    Lessons getValidLessonById(Long lessonId);

    /**
     * 删除课时
     *
     * @param lessonId 课时ID
     * @return 是否删除成功
     */
    Boolean deleteLesson(Long lessonId);

}
