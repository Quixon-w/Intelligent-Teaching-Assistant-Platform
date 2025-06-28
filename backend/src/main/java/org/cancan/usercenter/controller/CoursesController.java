package org.cancan.usercenter.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.cancan.usercenter.common.BaseResponse;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.common.ResultUtils;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.LessonsMapper;
import org.cancan.usercenter.mapper.ScoresMapper;
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.EnrollService;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.ADMIN_ROLE;
import static org.cancan.usercenter.constant.UserConstant.TEACHER_ROLE;

/**
 * 课程接口
 *
 * @author 洪
 */
@RestController
@RequestMapping("/api/course")
@Slf4j
@Tag(name = "body参数")
public class CoursesController {

    @Resource
    private ScoresMapper scoresMapper;
    @Resource
    private LessonsMapper lessonsMapper;

    @Resource
    private CoursesService coursesService;
    @Resource
    private EnrollService enrollService;
    @Resource
    private UserService userService;

    @GetMapping("/findOne")
    @Operation(summary = "查找某个课程")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true)
    })
    public BaseResponse<Courses> findOne(@RequestParam Long courseId) {
        Courses courses = coursesService.getValidCourseById(courseId);
        return ResultUtils.success(courses);
    }

    @GetMapping("/listById")
    @Operation(summary = "获取教师课程列表")
    @Parameters({
            @Parameter(name = "teacherId", description = "老师id", required = true)
    })
    public BaseResponse<List<Courses>> listById(@RequestParam Long teacherId) {
        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("teacher_id", teacherId);
        return ResultUtils.success(coursesService.list(queryWrapper));
    }

    @GetMapping("/listPage")
    @Operation(summary = "按页获取课程列表")
    @Parameters({
            @Parameter(name = "pageNum", description = "当前页码", required = true),
            @Parameter(name = "pageSize", description = "每页条数", required = true),
            @Parameter(name = "courseName", description = "课程名"),
            @Parameter(name = "teacherName", description = "老师名字")
    })
    public BaseResponse<Page<Courses>> listPage(
            @RequestParam Integer pageNum,
            @RequestParam Integer pageSize,
            @RequestParam(required = false) String courseName,
            @RequestParam(required = false) String teacherName
    ) {
        // 校验参数
        if (pageNum == null || pageNum <= 0 || pageSize == null || pageSize <= 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "分页参数非法");
        }
        // 筛选条件
        QueryWrapper<Courses> queryWrapper = coursesService.buildCourseQuery(courseName, teacherName);
        // 分页查询
        Page<Courses> page = new Page<>(pageNum, pageSize);
        Page<Courses> resultPage = coursesService.page(page, queryWrapper);
        return ResultUtils.success(resultPage);
    }

    @PostMapping("/add")
    @Operation(summary = "添加课程")
    @Parameters({
            @Parameter(name = "courseName", description = "课程名", required = true),
            @Parameter(name = "comment", description = "课程描述")
    })
    public BaseResponse<Courses> addCourse(@RequestParam String courseName, @RequestParam(required = false) String comment, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        // 仅老师可开课
        if (currentUser.getUserRole() != TEACHER_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师不可开课");
        }
        return ResultUtils.success(coursesService.addCourse(courseName, comment, currentUser.getId()));
    }

    @PostMapping("/delete")
    @Operation(summary = "删除课程")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true)
    })
    public BaseResponse<Boolean> deleteCourse(@RequestParam Long courseId, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        coursesService.isTeacher(courseId, currentUser.getId());
        return ResultUtils.success(coursesService.removeById(courseId));
    }

    @PostMapping("/edit")
    @Operation(summary = "编辑课程简介")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true),
            @Parameter(name = "comment", description = "课程简介", required = true)
    })
    public BaseResponse<Boolean> editComment(@RequestParam Long courseId, @RequestParam String comment, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        if (!coursesService.isTeacher(courseId, currentUser.getId())) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可删除课程");
        }
        return ResultUtils.success(coursesService.editComment(courseId, comment));
    }

    @PostMapping("/over")
    @Operation(summary = "结束课程")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true)
    })
    public BaseResponse<Boolean> over(@RequestParam Long courseId, HttpServletRequest request) {
        Courses course = coursesService.getValidCourseById(courseId);
        User currentUser = userService.getCurrentUser(request);
        if (!coursesService.isTeacher(courseId, currentUser.getId()) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可结束课程");
        }
        return ResultUtils.success(coursesService.over(course));
    }

    @GetMapping("/score")
    @Operation(summary = "获取该课程下某学生的总成绩")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true),
            @Parameter(name = "studentId", description = "学生id", required = true)
    })
    public BaseResponse<Float> getScore(@RequestParam Long courseId, @RequestParam Long studentId, HttpServletRequest request) {
        // 非老师，非学生，非管理员不可查看成绩
        User currentUser = userService.getCurrentUser(request);
        if (!coursesService.isTeacher(courseId, currentUser.getId())
                && !Objects.equals(currentUser.getId(), studentId)
                && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可获取学生分数");
        }
        // 查询成绩
        QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("courses_id", courseId).eq("student_id", studentId);
        Enroll enroll = enrollService.getOne(queryWrapper);
        return ResultUtils.success(enroll.getFinalScore());
    }

    @GetMapping("/scoreList")
    @Operation(summary = "获取该课程下某学生的所有课时成绩")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true),
            @Parameter(name = "studentId", description = "学生id", required = true)
    })
    public BaseResponse<List<Scores>> getListScores(@RequestParam Long courseId, @RequestParam Long studentId, HttpServletRequest request) {
        // 非老师，非学生，非管理员不可查看成绩
        User currentUser = userService.getCurrentUser(request);
        if (!coursesService.isTeacher(courseId, currentUser.getId())
                && !Objects.equals(currentUser.getId(), studentId)
                && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可获取学生分数");
        }
        // 获得课程下所有课时
        QueryWrapper<Lessons> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("course_id", courseId);
        List<Long> lessonsIds = lessonsMapper.selectList(queryWrapper).stream().map(Lessons::getLessonId).toList();
        if (lessonsIds.isEmpty()) {
            return null;
        }
        // 查询成绩
        QueryWrapper<Scores> queryWrapperS = new QueryWrapper<>();
        queryWrapperS.eq("student_id", studentId);
        queryWrapperS.in("lesson_id", lessonsIds);
        List<Scores> scores = scoresMapper.selectList(queryWrapperS);
        return ResultUtils.success(scores);
    }

}
