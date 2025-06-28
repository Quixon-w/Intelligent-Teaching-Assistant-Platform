package org.cancan.usercenter.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
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
import org.cancan.usercenter.model.domain.LessonQuestionMap;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.LessonQuestionMapService;
import org.cancan.usercenter.service.LessonsService;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

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

    @PostMapping("/add")
    @Operation(summary = "批量添加某课时的预发布习题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionIds", description = "习题ID列表", required = true)
    })
    public BaseResponse<List<LessonQuestionMap>> add(@RequestParam Long lessonId, @RequestParam List<Long> questionIds) {
        // 确认课时有效性
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        // 问题列表不为空
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        if (questionIds != null && !questionIds.isEmpty()) {
            queryWrapper.in("question_id", questionIds);
        } else {
            throw new BusinessException(ErrorCode.NULL_ERROR, "问题ID列表不能为空");
        }
        // 只允许添加一次习题
        if (lessons.getHasQuestion() != 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课时已添加过的问题");
        }
        // 插入 lesson-question 记录
        List<LessonQuestionMap> records = questionIds.stream()
                .map(qid -> {
                    LessonQuestionMap lq = new LessonQuestionMap();
                    lq.setLessonId(lessonId);
                    lq.setQuestionId(qid);
                    return lq;
                }).toList();
        if (!lessonQuestionMapService.saveBatch(records)) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加课时问题失败");
        }
        lessons.setHasQuestion(1);
        lessonsService.updateById(lessons);
        return ResultUtils.success(records);
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
        if (!lessonsService.isTeacher(lessonId, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有老师可删除未发布习题");
        }
        // 删除 lesson-question 记录
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        queryWrapper.eq("question_id", questionId);
        queryWrapper.eq("committed", 0);
        boolean removed = lessonQuestionMapService.remove(queryWrapper);
        if (!removed) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "未找到该未发布习题");
        }
        return ResultUtils.success(true);
    }

    @GetMapping("/list")
    @Operation(summary = "获取某课时的所有顺序习题列表")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true)
    })
    public BaseResponse<List<Questions>> list(@RequestParam Long lessonId, HttpServletRequest request) {
        // 校验权限
        User currentUser = userService.getCurrentUser(request);
        if (!lessonsService.isTeacher(lessonId, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有老师可查看所有已发布和未发布习题");
        }
        // 确认课时有效性
        Lessons lesson = lessonsService.getValidLessonById(lessonId);
        // 确认是否有问题
        if (lesson.getHasQuestion() == 0) {
            return ResultUtils.success(null);
        }
        // 获取顺序课时习题列表
        return ResultUtils.success(lessonQuestionMapService.getOrderedQuestions(lessonId, false));
    }

    @GetMapping("/listCommitted")
    @Operation(summary = "获取某课时的已发布顺序习题列表")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true)
    })
    public BaseResponse<List<Questions>> listCommitted(@RequestParam Long lessonId) {
        // 确认课时有效性
        Lessons lesson = lessonsService.getValidLessonById(lessonId);
        // 确认是否有问题
        if (lesson.getHasQuestion() == 0) {
            return ResultUtils.success(null);
        }
        // 获取顺序已发布课时习题列表
        List<Questions> committedQuestions = lessonQuestionMapService.getOrderedQuestions(lessonId, true);
        return ResultUtils.success(committedQuestions);
    }

    @PostMapping("/commit")
    @Operation(summary = "发布习题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionIds", description = "习题ID列表", required = true)
    })
    public BaseResponse<Boolean> commit(@RequestParam Long lessonId, @RequestParam List<Long> questionIds, HttpServletRequest request) {
        // 校验参数与权限
        if (questionIds == null || questionIds.isEmpty()) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "发布习题列表为空");
        }
        User currentUser = userService.getCurrentUser(request);
        if (!lessonsService.isTeacher(lessonId, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有该课程老师可发布习题");
        }
        // 查询发布
        UpdateWrapper<LessonQuestionMap> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("lesson_id", lessonId);
        updateWrapper.in("question_id", questionIds);
        updateWrapper.set("committed", 1);
        return ResultUtils.success(lessonQuestionMapService.update(updateWrapper));
    }

}
