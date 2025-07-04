package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.User;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【courses】的数据库操作Service
 * {@code @createDate} 2025-06-21 09:06:32
 */
public interface CoursesService extends IService<Courses> {

    /**
     * 添加课程
     *
     * @param courseName 课程名
     * @param teacher    老师
     * @return 课程
     */
    Courses addCourse(String courseName, String comment, User teacher);

    /**
     * 判断是否是本老师在操作
     *
     * @param coursesId 课程id
     * @param userId    用户id
     * @return 是否是老师
     */
    Boolean isTeacher(Long coursesId, Long userId);

    /**
     * 获取有效课程
     *
     * @param courseId 课程id
     * @return 课程
     */
    Courses getValidCourseById(Long courseId);

    /**
     * 修改课程简介
     *
     * @param courseId 课程id
     * @param comment  课程简介
     * @return 是否成功
     */
    Boolean editComment(Long courseId, String comment);

    /**
     * 构建课程查询条件
     *
     * @param courseName  课程名
     * @param teacherName 老师名字
     * @return 查询条件
     */
    QueryWrapper<Courses> buildCourseQuery(String courseName, String teacherName);

    /**
     * 课程结束
     *
     * @param course 课程
     * @return 是否成功
     */
    Boolean over(Courses course);

    /**
     * 获取该学生的所有课程
     *
     * @param studentId 学生 id
     * @return 课程列表
     */
    List<Courses> getCoursesByStudentId(Long studentId);

    /**
     * 删除课程
     *
     * @param courseId 课程id
     * @return 是否成功
     */
    Boolean deleteCourse(Long courseId);

    /**
     * 获取该老师所有课程
     *
     * @param teacherId 老师 id
     * @return 课程列表
     */
    List<Courses> getCoursesByTeacherId(Long teacherId);

}
