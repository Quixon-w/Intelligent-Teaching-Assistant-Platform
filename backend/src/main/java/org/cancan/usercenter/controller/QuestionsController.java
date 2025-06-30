package org.cancan.usercenter.controller;

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
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.QuestionsService;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.ADMIN_ROLE;

/**
 * 习题接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/question")
@Slf4j
@Tag(name = "习题信息")
public class QuestionsController {

    @Resource
    private QuestionsService questionsService;
    @Resource
    private UserService userService;

    @PostMapping("/addOne")
    @Operation(summary = "添加教师个人习题集", description = "id不需要传入")
    public BaseResponse<Questions> addOne(@RequestBody Questions question, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        if (!Objects.equals(question.getTeacherId(), currentUser.getId()) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "老师只能添加自己的习题集");
        }
        // 清空习题 id
        question.setQuestionId(null);
        if (StringUtils.isAnyBlank(question.getKnowledge(), question.getQuestion(), question.getAnswer(), question.getExplanation()) || question.getOptions() == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "存在参数为空");
        }
        boolean result = questionsService.addQuestion(question);
        if (!result) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加失败");
        }
        return ResultUtils.success(question);
    }

    @GetMapping("/selectById")
    @Operation(summary = "查找某题")
    @Parameters({
            @Parameter(name = "questionId", description = "题id", required = true)
    })
    public BaseResponse<Questions> getQuestion(@RequestParam Long questionId) {
        return ResultUtils.success(questionsService.getById(questionId));
    }

    @GetMapping("/selectByFather")
    @Operation(summary = "教师根据knowledge父标签获得问题集")
    @Parameters({
            @Parameter(name = "father", description = "知识点", required = true)
    })
    public BaseResponse<List<Questions>> selectByFather(@RequestParam String father, @RequestParam Long teacherId, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        if (!Objects.equals(currentUser.getId(), teacherId) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可查看");
        }
        return ResultUtils.success(questionsService.selectByFather(father, teacherId));
    }

    @GetMapping("/listByTeacherId")
    @Operation(summary = "获取某老师所有题目")
    public BaseResponse<List<Questions>> listByTeacherId(@RequestParam Long teacherId, HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        if (!Objects.equals(teacherId, currentUser.getId()) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "不是老师本人不可查看");
        }
        return ResultUtils.success(questionsService.listByTeacherId(teacherId));
    }

}
