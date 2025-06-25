package org.cancan.usercenter.controller;

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
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.service.*;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

/**
 * 做题接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/api/records")
@Slf4j
@Tag(name = "body参数")
public class QuestionRecordsController {

    @Resource
    private CoursesMapper coursesMapper;

    @Resource
    private QuestionRecordsService questionRecordsService;
    @Resource
    private LessonQuestionMapService lessonQuestionMapService;
    @Resource
    private LessonsService lessonsService;
    @Resource
    private UserService userService;
    @Resource
    private CoursesService coursesService;

    @PostMapping("/add")
    @Operation(summary = "添加做题记录")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
    })
    public BaseResponse<List<QuestionRecords>> add(Long lessonId, List<String> answers, HttpServletRequest request) {
        // 校验课时
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        Courses courses = coursesMapper.selectById(lessons.getCourseId());
        if (lessons.getHasQuestion() == 0) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时没有习题");
        }
        // 校验选课
        User currentUser = userService.getCurrentUser(request);
        List<Courses> coursesList = coursesService.getCoursesByStudentId(currentUser.getId());
        if (coursesList == null || !coursesList.contains(courses)) {
            throw new BusinessException(ErrorCode.NO_AUTH, "未选该课");
        }
        // 获取习题列表
        List<Questions> questionsList = lessonQuestionMapService.getOrderedQuestions(lessonId);
        // 校验答案数量
        if (answers == null || answers.size() != questionsList.size()) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "答案数量与题目数量不一致");
        }
        // 逐题构造做题记录
        List<QuestionRecords> records = new ArrayList<>();
        for (int i = 0; i < questionsList.size(); i++) {
            Questions q = questionsList.get(i);
            String userAnswer = answers.get(i);
            QuestionRecords record = new QuestionRecords();
            record.setStudentId(currentUser.getId());
            record.setQuestionId(q.getQuestionId());
            record.setSelectedOption(userAnswer);
            record.setIsCorrect(userAnswer.equals(q.getAnswer()) ? 1 : 0); // 判断是否正确
            record.setLessonId(lessonId);
            records.add(record);
        }
        // 批量插入
        boolean success = questionRecordsService.saveBatch(records);
        if (!success) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "记录保存失败");
        }
        return ResultUtils.success(records);
    }

}
