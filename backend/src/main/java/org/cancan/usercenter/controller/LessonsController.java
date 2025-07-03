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
import org.cancan.usercenter.model.domain.response.GetListScoresResponse;
import org.cancan.usercenter.service.*;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.ADMIN_ROLE;

/**
 * 课时接口
 *
 * @author 洪
 */
@RestController
@RequestMapping("/lesson")
@Slf4j
@Tag(name = "课时信息")
public class LessonsController {

    @Resource
    private LessonsService lessonsService;
    @Resource
    private CoursesService coursesService;
    @Resource
    private EnrollService enrollService;
    @Resource
    private UserService userService;
    @Resource
    private ScoresService scoresService;

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
        coursesService.isTeacher(courseId, userService.getCurrentUser(request).getId());
        return ResultUtils.success(lessonsService.addLesson(lessonName, courseId));
    }

    @PostMapping("/delete")
    @Operation(summary = "删除课时")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时id", required = true)
    })
    public BaseResponse<Boolean> deleteLesson(@RequestParam Long lessonId, HttpServletRequest request) {
        // 判断是否是老师本人
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        User currentUser = userService.getCurrentUser(request);
        if (!lessonsService.isTeacher(lessons, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
        }
        // 课程不可已经结束
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        if (courses.getIsOver() == 1) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课程已结束");
        }
        return ResultUtils.success(lessonsService.deleteLesson(lessonId));
    }

    @GetMapping("/list")
    @Operation(summary = "查看某课程的所有课时")
    @Parameters({
            @Parameter(name = "courseId", description = "课程id", required = true)
    })
    public BaseResponse<List<Lessons>> listLessonsByCourse(@RequestParam Long courseId) {
        return ResultUtils.success(lessonsService.listLessons(courseId));
    }

    @GetMapping("/getScore")
    @Operation(summary = "查看某学生某课时的分数")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时id", required = true),
            @Parameter(name = "studentId", description = "学生id", required = true)
    })
    public BaseResponse<Float> getScore(@RequestParam Long lessonId, @RequestParam Long studentId, HttpServletRequest request) {
        // 校验参数，课程和课时都有效
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        // 学生已选该课
        if (!enrollService.isEnrolled(courses.getId(), studentId)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "学生未选该课");
        }
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
        // 确认该 lesson 存在习题
        if (lessons.getHasQuestion() == 0) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时不存在习题");
        }
        // 查询返回
        return ResultUtils.success(scoresService.getScore(lessonId, studentId));
    }

    @GetMapping("/getListScores")
    @Operation(summary = "查看某课时所有学生的分数")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时id", required = true),
    })
    public BaseResponse<List<GetListScoresResponse>> listAllScores(@RequestParam Long lessonId, HttpServletRequest request) {
        // 校验参数，课程和课时都有效
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        // 验证权限
        User currentUser = userService.getCurrentUser(request);
        if (
                !(currentUser.getUserRole() == ADMIN_ROLE)
                        && !Objects.equals(currentUser.getId(), courses.getTeacherId())
        ) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有老师能查看自己课程课时的分数");
        }
        // 确认该 lesson 存在习题
        if (lessons.getHasQuestion() == 0) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时不存在习题");
        }
        // 查询返回
        List<User> students = enrollService.getStudentsByCourseId(courses.getId());
        List<GetListScoresResponse> list = new ArrayList<>();
        if (students != null && !students.isEmpty()) {
            for (User student : students) {
                GetListScoresResponse response = new GetListScoresResponse();
                response.setStudent(userService.getSafetyUser(student));
                response.setScore(scoresService.getScore(lessonId, student.getId()));
                list.add(response);
            }
            return ResultUtils.success(list);
        } else {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "该课程无选课学生");
        }
    }

    @GetMapping("/getQuestionedLessonNum")
    @Operation(summary = "查看某老师发布过习题的课时数量")
    @Parameters({
            @Parameter(name = "teacherId", description = "老师id", required = true),
    })
    public BaseResponse<Long> getQuestionedLessonNum(@RequestParam Long teacherId) {
        List<Courses> courses = coursesService.getCoursesByTeacherId(teacherId);
        if (courses.isEmpty()) {
            return ResultUtils.success(0L);
        }
        List<Long> courseIds = courses.stream().map(Courses::getId).toList();
        QueryWrapper<Lessons> queryWrapperL = new QueryWrapper<>();
        queryWrapperL.in("course_id", courseIds);
        queryWrapperL.eq("has_question", 1);
        return ResultUtils.success(lessonsService.count(queryWrapperL));
    }

    @PostMapping("/commit")
    @Operation(summary = "发布习题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionIds", description = "习题ID列表", required = true)
    })
    public BaseResponse<Boolean> commit(@RequestParam Long lessonId, HttpServletRequest request) {
        // 校验参数与权限
        User currentUser = userService.getCurrentUser(request);
        Lessons lesson = lessonsService.getValidLessonById(lessonId);
        if (!lessonsService.isTeacher(lesson, currentUser)) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有该课程老师可发布习题");
        }
        if (lesson.getHasQuestion() == 1) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时已发布过习题");
        }
        // 设置该课时已有习题
        lesson.setHasQuestion(1);
        lessonsService.updateById(lesson);
        return ResultUtils.success(true);
    }

}
