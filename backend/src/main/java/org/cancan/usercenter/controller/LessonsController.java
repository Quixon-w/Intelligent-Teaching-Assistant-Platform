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
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.EnrollService;
import org.cancan.usercenter.service.LessonsService;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.ADMIN_ROLE;

/**
 * 课程接口
 *
 * @author 洪
 */
@RestController
@RequestMapping("/lesson")
@Slf4j
@Tag(name = "body参数")
public class LessonsController {

    @Resource
    private LessonsService lessonsService;

    @Resource
    private CoursesService coursesService;

    @Resource
    private EnrollService enrollService;

    @Resource
    private UserService userService;

    @PostMapping("/add")
    @Operation(summary = "添加课时")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true),
            @Parameter(name = "lessonName", description = "课时名", required = true)
    })
    public BaseResponse<Lessons> addLesson(@RequestParam Long courseId, @RequestParam String lessonName, HttpServletRequest request) {
        if (courseId == null || lessonName == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "课程ID和课时名不能为空");
        }
        coursesService.isTeacher(courseId, request);
        return ResultUtils.success(lessonsService.addLesson(lessonName, courseId));
    }

    @PostMapping("/delete")
    @Operation(summary = "删除课时")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时id", required = true)
    })
    public BaseResponse<Boolean> deleteLesson(@RequestParam Long lessonId, HttpServletRequest request) {
        // 参数校验
        lessonsService.getValidLessonById(lessonId);
        // 判断是否是老师本人
        User currentUser = userService.getCurrentUser(request);
        lessonsService.isTeacher(lessonId, currentUser);
        return ResultUtils.success(lessonsService.removeById(lessonId));
    }

    @GetMapping("/list")
    @Operation(summary = "查看某课程的课时")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true)
    })
    public BaseResponse<List<Lessons>> listLessons(@RequestParam Long courseId) {
        coursesService.getValidCourseById(courseId);
        QueryWrapper<Lessons> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("course_id", courseId);
        return ResultUtils.success(lessonsService.list(queryWrapper));
    }

    @GetMapping("/getScore")
    @Operation(summary = "查看某学生某课时的分数")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时id", required = true),
            @Parameter(name = "studentId", description = "学生id", required = true)
    })
    public BaseResponse<Integer> getScore(@RequestParam Long lessonId, @RequestParam Long studentId, HttpServletRequest request) {
        // 校验参数，课程和课时都有效
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        // 学生已选该课
        enrollService.isEnrolled(courses.getId(), studentId);
        // 验证权限
        User currentUser = userService.getCurrentUser(request);
        User student = userService.getById(studentId);
        if (
                !Objects.equals(student.getId(), currentUser.getId())
                        && !(currentUser.getUserRole() == ADMIN_ROLE)
                        && !Objects.equals(currentUser.getId(), courses.getTeacherId())
        ) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只能查看自己的分数");
        }
        // 查询返回
        return ResultUtils.success(lessonsService.getLessonScore(lessonId, studentId));
    }

}
