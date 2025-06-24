package org.cancan.usercenter.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.cancan.usercenter.common.BaseResponse;
import org.cancan.usercenter.common.ResultUtils;
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.service.QuestionsService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 习题接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/api/question")
@Slf4j
@Tag(name = "body参数")
public class QuestionsController {

    @Resource
    private QuestionsService questionsService;

    @GetMapping
    @Operation(summary = "查看某题")
    @Parameters({
            @Parameter(name = "questionId", description = "题id", required = true)
    })
    public BaseResponse<Questions> getQuestion(@RequestParam Long questionId) {
        return ResultUtils.success(questionsService.getById(questionId));
    }

}
