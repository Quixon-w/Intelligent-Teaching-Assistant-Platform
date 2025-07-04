package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.*;
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.EnrollService;
import org.cancan.usercenter.utils.SpecialCode;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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
    private UserMapper userMapper;
    @Resource
    private CoursesMapper coursesMapper;
    @Resource
    private LessonsMapper lessonsMapper;
    @Resource
    private QuestionRecordsMapper questionRecordsMapper;
    @Resource
    private LessonQuestionMapMapper lessonQuestionMapMapper;
    @Resource
    private ScoresMapper scoresMapper;

    @Resource
    private EnrollService enrollService;

    /**
     * @param courseName 课程名
     * @param teacher    老师
     * @param comment    课程描述
     * @return 课程
     */
    @Override
    public Courses addCourse(String courseName, String comment, User teacher) {
        // 参数校验
        if (courseName == null) {
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
        courses.setTeacherId(teacher.getId());
        courses.setTeacherName(teacher.getUsername());
        courses.setComment(Objects.requireNonNullElse(comment, "暂无简介"));
        boolean result = this.save(courses);
        if (!result) {
            return null;
        }
        return courses;
    }

    /**
     * @param coursesId 课程id
     * @param userId    老师id
     * @return 是否是老师
     */
    @Override
    public Boolean isTeacher(Long coursesId, Long userId) {
        Courses courses = this.getValidCourseById(coursesId);
        return courses.getTeacherId().equals(userId);
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
    @Transactional
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
            queryWrapper.like("name", courseName);
        }
        if (StringUtils.isNotBlank(teacherName)) {
            QueryWrapper<User> queryWrapperN = new QueryWrapper<>();
            queryWrapperN.like("username", teacherName);
            queryWrapperN.eq("user_role", TEACHER_ROLE);
            List<Long> teacherIds = userMapper.selectList(queryWrapperN).stream().map(User::getId).toList();
            if (!teacherIds.isEmpty()) {
                queryWrapper.in("teacher_id", teacherIds);
            } else {
                // 如果没有匹配的老师ID，避免查出所有课程
                queryWrapper.eq("teacher_id", -1L);
            }
        }
        return queryWrapper;
    }

    /**
     * @param course 课程
     * @return 是否成功
     */
    @Override
    @Transactional
    public Boolean over(Courses course) {
        if (course.getIsOver() == 1) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课程已结束");
        }
        enrollService.calculateStudentsScores(course.getId());
        course.setIsOver(1);
        return this.updateById(course);
    }

    /**
     * @param studentId 学生id
     * @return 课程列表
     */
    @Override
    public List<Courses> getCoursesByStudentId(Long studentId) {
        List<Long> courseIds = enrollService.getCoursesByStudentId(studentId);
        if (courseIds.isEmpty()) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该学生无选课记录");
        }
        return coursesMapper.selectByIds(courseIds);
    }

    /**
     * @param courseId 课程id
     * @return 是否成功
     */
    @Override
    @Transactional
    public Boolean deleteCourse(Long courseId) {
        QueryWrapper<Lessons> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("course_id", courseId);
        List<Long> lessonIds = lessonsMapper.selectList(queryWrapper).stream().map(Lessons::getLessonId).toList();
        if (!lessonIds.isEmpty()) {
            // 删除答题记录
            QueryWrapper<QuestionRecords> queryWrapperQ = new QueryWrapper<>();
            queryWrapperQ.in("lesson_id", lessonIds);
            questionRecordsMapper.delete(queryWrapperQ);
            // 删除课时习题映射关系
            QueryWrapper<LessonQuestionMap> queryWrapperM = new QueryWrapper<>();
            queryWrapperM.in("lesson_id", lessonIds);
            lessonQuestionMapMapper.delete(queryWrapperM);
            // 删除课时成绩表
            QueryWrapper<Scores> queryWrapperS = new QueryWrapper<>();
            queryWrapperS.in("lesson_id", lessonIds);
            scoresMapper.delete(queryWrapperS);
            // 删除课时
            lessonsMapper.delete(queryWrapper);
        }
        // 删除选课
        QueryWrapper<Enroll> queryWrapperE = new QueryWrapper<>();
        queryWrapperE.eq("courses_id", courseId);
        enrollService.remove(queryWrapperE);
        // 删除课程
        return this.removeById(courseId);
    }

    /**
     * @param teacherId 老师 id
     * @return 课程列表
     */
    @Override
    public List<Courses> getCoursesByTeacherId(Long teacherId) {
        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("teacher_id", teacherId);
        return coursesMapper.selectList(queryWrapper);
    }

}




