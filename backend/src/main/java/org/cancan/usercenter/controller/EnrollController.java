package org.cancan.usercenter.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
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
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.EnrollService;
import org.cancan.usercenter.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;
import java.util.Queue;

import static org.cancan.usercenter.constant.UserConstant.*;

/**
 * 课程接口
 *
 * @author 洪
 */
@RestController
@RequestMapping("/enroll")
@CrossOrigin
@Slf4j
@Tag(name = "body参数")
public class EnrollController {

    @Resource
    private CoursesService coursesService;

    @Resource
    private UserService userService;

    @Resource
    private EnrollService enrollService;
    @Autowired
    private CoursesMapper coursesMapper;

    @PostMapping("/")
    @Operation(summary = "学生选课")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true),
    })
    public BaseResponse<Boolean> enrollCourse(@RequestParam Long courseId, HttpServletRequest request) {
        if (courseId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "课程ID不能为空");
        }
        User currentUser = userService.getCurrentUser(request);
        if (currentUser.getUserRole() == TEACHER_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有学生可以选课");
        }
        return ResultUtils.success(enrollService.enroll(courseId, currentUser.getId()));
    }

    @PostMapping("/dismiss")
    @Operation(summary = "退课")
    @Parameters({
            @Parameter(name = "studentId", description = "学生ID", required = true),
            @Parameter(name = "courseId", description = "课程ID", required = true),
    })
    public BaseResponse<Boolean> disCourse(@RequestParam Long studentId, @RequestParam Long courseId, HttpServletRequest request) {
        if (studentId == null || courseId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "学生ID和课程ID不能为空");
        }
        // 获取当前用户
        User currentUser = userService.getCurrentUser(request);
        // 获取课程信息
        Courses courses = coursesService.getById(courseId);
        if (courses == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课程不存在");
        }
        // 判断退课权限
        if (
                !Objects.equals(currentUser.getId(), studentId) &&
                !Objects.equals(currentUser.getId(), courses.getTeacherId()) &&
                currentUser.getUserRole() != ADMIN_ROLE
        ) {
            throw new BusinessException(ErrorCode.NO_AUTH, "没有权限");
        }
        return ResultUtils.success(enrollService.dismiss(courseId, studentId));
    }

    @PostMapping("/list/student")
    @Operation(summary = "查看某学生的所有选课")
    public BaseResponse<List<Courses>> listCourses(@RequestParam Long studentId, HttpServletRequest request) {
        if (studentId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "学生ID不能为空");
        }
        User currentUser = userService.getCurrentUser(request);
        if (currentUser.getUserRole() != STUDENT_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有学生可以选课");
        }
        if (!Objects.equals(currentUser.getId(), studentId)) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只能查看自己的选课");
        }
        List<Courses> coursesList = enrollService.getCoursesByStudentId(studentId);
        if (coursesList == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "学生无选课记录");
        }
        return ResultUtils.success(coursesList);
    }

    @PostMapping("/list/course")
    @Operation(summary = "查看某课程的所有选课学生")
    public BaseResponse<List<User>> listStudents(@RequestParam Long courseId, HttpServletRequest request) {
        if (courseId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "课程ID不能为空");
        }
        User currentUser = userService.getCurrentUser(request);
        if (currentUser.getUserRole() != TEACHER_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有老师可以查看");
        }
        Courses course = coursesService.getById(courseId);
        if (!Objects.equals(currentUser.getId(), course.getTeacherId())) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只能查看自己的选课");
        }
        List<User> studentsList = enrollService.getStudentsByCourseId(courseId);
        if (studentsList == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课无选课学生");
        }
        return ResultUtils.success(studentsList);
    }
}
