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
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.service.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.ADMIN_ROLE;

/**
 * 课时问题关联接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/map")
@Slf4j
@Tag(name = "课时与习题对应关系")
public class LessonQuestionMapController {

    @Resource
    private LessonQuestionMapService lessonQuestionMapService;
    @Resource
    private LessonsService lessonsService;
    @Resource
    private UserService userService;
    @Resource
    private QuestionsService questionsService;
    @Resource
    private CoursesService coursesService;

    @PostMapping("/addByEntity")
    @Operation(summary = "添加某课时的一个预发布习题", description = "创建新习题，习题id不需要传入")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "question", description = "习题", required = true)
    })
    public BaseResponse<Boolean> addByEntity(@RequestParam Long lessonId, @RequestBody Questions question, HttpServletRequest request) {
        // 校验权限
        User currentUser = userService.getCurrentUser(request);
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        if (!lessonsService.isTeacher(lessons, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
        }
        if (lessons.getHasQuestion() == 1) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时已发布过习题");
        }
        // 添加习题集
        boolean result = questionsService.addQuestion(question);
        if (!result) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加失败");
        }
        // 插入 lesson-question 记录
        LessonQuestionMap lessonQuestionMap = new LessonQuestionMap();
        lessonQuestionMap.setLessonId(lessonId);
        lessonQuestionMap.setQuestionId(question.getQuestionId());
        return ResultUtils.success(lessonQuestionMapService.save(lessonQuestionMap));
    }

    @PostMapping("/addByIds")
    @Operation(summary = "批量添加某课时的预发布习题", description = "传入教师个人习题集中的习题，只需要习题id")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionIds", description = "习题ID列表", required = true)
    })
    public BaseResponse<Boolean> addByIds(@RequestParam Long lessonId, @RequestParam List<Long> questionIds, HttpServletRequest request) {
        // 校验有效性与权限
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        if (!lessonsService.isTeacher(lessons, userService.getCurrentUser(request))) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
        }
        if (lessons.getHasQuestion() == 1) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时已发布过习题");
        }
        // 确认习题存在
        if (questionIds == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请传入习题id集");
        }
        questionIds.forEach(questionId -> {
            if (questionsService.getById(questionId) == null) {
                throw new BusinessException(ErrorCode.PARAMS_ERROR, "传入的习题id有误");
            }
        });
        // 无重复添加的习题
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        queryWrapper.in("question_id", questionIds);
        if (lessonQuestionMapService.exists(queryWrapper)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "习题重复传入");
        }
        // 添加课时习题映射
        List<LessonQuestionMap> records = questionIds.stream()
                .map(q -> {
                    LessonQuestionMap lq = new LessonQuestionMap();
                    lq.setLessonId(lessonId);
                    lq.setQuestionId(q);
                    return lq;
                }).toList();
        if (!lessonQuestionMapService.saveBatch(records)) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加课时习题映射关系失败");
        }
        return ResultUtils.success(true);
    }

    @PostMapping("/delete")
    @Operation(summary = "删除某个课时未发布的习题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionId", description = "习题ID", required = true)
    })
    public BaseResponse<Boolean> delete(@RequestParam Long lessonId, @RequestParam Long questionId, HttpServletRequest request) {
        // 检查有效性与权限
        User currentUser = userService.getCurrentUser(request);
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        if (!lessonsService.isTeacher(lessons, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有老师可删除未发布习题");
        }
        if (lessons.getHasQuestion() == 1) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时习题已发布过");
        }
        // 删除 lesson-question 记录
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        queryWrapper.eq("question_id", questionId);
        return ResultUtils.success(lessonQuestionMapService.remove(queryWrapper));
    }

    @GetMapping("/list")
    @Operation(summary = "获取某课时的所有顺序习题列表", description = "非老师本人只能查看已发布的习题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true)
    })
    public BaseResponse<List<Questions>> list(@RequestParam Long lessonId, HttpServletRequest request) {
        // 确认课时有效性
        User currentUser = userService.getCurrentUser(request);
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        // 习题未发布，访问者不是该课程老师也不是管理员
        if (lessons.getHasQuestion() == 0 && !Objects.equals(currentUser.getId(), courses.getTeacherId()) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人不可查看未发布习题");
        }
        // 获取顺序课时习题列表
        return ResultUtils.success(lessonQuestionMapService.getOrderedQuestions(lessonId));
    }

}
