package org.cancan.usercenter.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.cancan.usercenter.common.BaseResponse;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.common.ResultUtils;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.*;
import org.cancan.usercenter.utils.RedisUtil;
import static org.cancan.usercenter.constant.UserConstant.*;

import java.util.List;
import java.util.Objects;

/**
 * 课程接口
 *
 * @author 洪
 */
@RestController
@RequestMapping("/course")
@CrossOrigin
@Slf4j
@Tag(name = "body参数")
public class CoursesController {

    @Resource
    private CoursesService coursesService;

    @Resource
    private UserService userService;

    @Resource
    private RedisUtil redisUtil;

    @GetMapping("/list")
    @Operation(summary = "获取课程列表")
    @Parameters({
            @Parameter(name = "courseName", description = "课程名", required = true),
    })
    public BaseResponse<List<Courses>> list(@RequestParam String courseName, HttpServletRequest request) {
        QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
        if (StringUtils.isNotBlank(courseName)) {
            queryWrapper.like("course_name", courseName);
        }
        List<Courses> coursesList = coursesService.list(queryWrapper);
        return ResultUtils.success(coursesList);
    }

    @PostMapping("/add")
    @Operation(summary = "添加课程")
    @Parameters({
            @Parameter(name = "courseName", description = "课程名", required = true),
    })
    public BaseResponse<Courses> addCourse(@RequestParam String courseName, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        // 仅老师可开课
        if (currentUser.getUserRole() != TEACHER_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师不可开课");
        }
        return ResultUtils.success(coursesService.addCourse(courseName, currentUser.getId()));
    }

    @PostMapping("/delete")
    @Operation(summary = "删除课程")
    public BaseResponse<Boolean> deleteCourse(@RequestParam Long courseId, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        // 仅老师本人可删除课程
        Courses courses = coursesService.getById(courseId);
        if (!Objects.equals(courses.getTeacherId(), currentUser.getId())) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可删除课程");
        }
        return ResultUtils.success(coursesService.removeById(courseId));
    }
}
