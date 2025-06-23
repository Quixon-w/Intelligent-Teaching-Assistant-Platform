package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.apache.commons.lang3.StringUtils;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.UserService;
import org.cancan.usercenter.utils.SpecialCode;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.TEACHER_ROLE;

/**
 * @author 洪
 * {@code @description} 针对表【courses】的数据库操作Service实现
 * {@code @createDate} 2025-06-21 09:06:32
 */
@Service
public class CoursesServiceImpl extends ServiceImpl<CoursesMapper, Courses> implements CoursesService {

    @Resource
    private UserService userService;

    /**
     * @param courseName 课程名
     * @param teacherId  老师id
     * @param comment    课程描述
     * @return 课程
     */
    @Override
    public Courses addCourse(String courseName, String comment, Long teacherId) {
        // 参数校验
        if (courseName == null || teacherId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR);
        }
        SpecialCode.validateCode(courseName);
        // 课程名长度限制
        if (courseName.length() > 20) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课程名长度不能超过20");
        }
        // 插入数据
        Courses courses = new Courses();
        courses.setName(courseName);
        courses.setTeacherId(teacherId);
        courses.setComment(Objects.requireNonNullElse(comment, "暂无简介"));
        boolean result = this.save(courses);
        if (!result) {
            return null;
        }
        return courses;
    }

    /**
     * @param coursesId 课程id
     * @param request   请求
     * @return 是否是老师
     */
    @Override
    public Boolean isTeacher(Long coursesId, HttpServletRequest request) {
        Courses courses = this.getValidCourseById(coursesId);
        return courses.getTeacherId().equals(userService.getCurrentUser(request).getId());
    }

    /**
     * @param courseId 课程id
     * @return 有效课程
     */
    @Override
    public Courses getValidCourseById(Long courseId) {
        if (courseId == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课程id不能为空");
        }
        Courses courses = this.getById(courseId);
        if (courses == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "课程不存在");
        }
        return courses;
    }

    /**
     * @param courseId 课程id
     * @param comment  课程简介
     * @return 是否修改成功
     */
    @Override
    public Boolean editComment(Long courseId, String comment) {
        Courses courses = this.getById(courseId);
        courses.setComment(comment);
        return this.updateById(courses);
    }

    /**
     * 构建查询条件
     *
     * @param courseName  课程名
     * @param teacherName 教师名
     * @return 查询条件
     */
    @Override
    public QueryWrapper<Courses> buildCourseQuery(String courseName, String teacherName) {
        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
        if (StringUtils.isNotBlank(courseName)) {
            SpecialCode.validateCode(courseName);
            queryWrapper.like("course_name", courseName);
        }
        if (StringUtils.isNotBlank(teacherName)) {
            QueryWrapper<User> queryWrapperName = new QueryWrapper<>();
            queryWrapperName.like("username", teacherName);
            queryWrapperName.eq("user_role", TEACHER_ROLE);
            List<Long> teacherIds = userService.list(queryWrapperName).stream().map(User::getId).toList();
            if (!teacherIds.isEmpty()) {
                queryWrapper.in("teacher_id", teacherIds);
            } else {
                // 如果没有匹配的老师ID，避免查出所有课程
                queryWrapper.eq("teacher_id", -1L);
            }
        }
        return queryWrapper;
    }

}




