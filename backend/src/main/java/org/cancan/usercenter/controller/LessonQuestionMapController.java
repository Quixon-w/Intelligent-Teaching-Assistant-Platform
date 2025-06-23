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
import org.cancan.usercenter.model.domain.LessonQuestionMap;
import org.cancan.usercenter.service.LessonQuestionMapService;
import org.cancan.usercenter.service.LessonsService;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 课时问题关联接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/map")
@Slf4j
@Tag(name = "body参数")
public class LessonQuestionMapController {

    @Resource
    private LessonQuestionMapService lessonQuestionMapService;

    @Resource
    private LessonsService lessonsService;

    @Resource
    private UserService userService;

    @PostMapping("/add")
    @Operation(summary = "批量添加课时问题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionIds", description = "问题ID列表", required = true)
    })
    public BaseResponse<List<LessonQuestionMap>> add(Long lessonId, List<Long> questionIds) {
        // 确认课时有效性
        lessonsService.getValidLessonById(lessonId);
        // 插入 lesson-question 记录
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        if (questionIds != null && !questionIds.isEmpty()) {
            queryWrapper.in("question_id", questionIds);
        } else {
            throw new BusinessException(ErrorCode.NULL_ERROR, "问题ID列表不能为空");
        }
        if (lessonQuestionMapService.exists(queryWrapper)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "存在课时已添加过的问题");
        }
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
        return ResultUtils.success(records);
    }

    @PostMapping("/delete")
    @Operation(summary = "删除某个课时的某个问题")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "questionId", description = "问题ID", required = true)
    })
    public BaseResponse<Boolean> delete(Long lessonId, Long questionId, HttpServletRequest request) {
        // 检查有效性与权限
        lessonsService.isTeacher(lessonId, userService.getCurrentUser(request));
        // 删除 lesson-question 记录
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        queryWrapper.eq("question_id", questionId);
        return ResultUtils.success(lessonQuestionMapService.remove(queryWrapper));
    }

    @GetMapping("/list")
    @Operation(summary = "获取课时问题列表")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true)
    })
    public BaseResponse<List<LessonQuestionMap>> list(Long lessonId) {
        // 确认课时有效性
        lessonsService.getValidLessonById(lessonId);
        // 获取课时问题列表
        QueryWrapper<LessonQuestionMap> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        return ResultUtils.success(lessonQuestionMapService.list(queryWrapper));
    }

}
