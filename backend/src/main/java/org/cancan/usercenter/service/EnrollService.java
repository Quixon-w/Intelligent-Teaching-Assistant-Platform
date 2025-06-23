package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.Enroll;
import org.cancan.usercenter.model.domain.User;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【enrollments】的数据库操作Service
 * {@code @createDate} 2025-06-21 11:21:31
 */
public interface EnrollService extends IService<Enroll> {

    /**
     * 退课
     *
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 退课结果
     */
    Boolean dismiss(Long courseId, Long studentId);

    /**
     * 选课
     *
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 选课结果
     */
    Boolean enroll(Long courseId, Long studentId);

    /**
     * 获取某学生的所有选课
     *
     * @param studentId 学生id
     * @return 选课列表
     */
    List<Courses> getCoursesByStudentId(Long studentId);

    /**
     * 获取某课程的所有选课学生
     *
     * @param courseId 课程id
     * @return 选课学生列表
     */
    List<User> getStudentsByCourseId(Long courseId);

    /**
     * 判断某学生是否选了某课程
     *
     * @param courseId  课程id
     * @param studentId 学生id
     */
    void isEnrolled(Long courseId, Long studentId);
}
