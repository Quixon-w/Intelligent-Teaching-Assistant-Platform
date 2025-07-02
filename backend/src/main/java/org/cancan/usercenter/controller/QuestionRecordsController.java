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
import org.cancan.usercenter.mapper.QuestionsMapper;
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.model.domain.response.GetQuestionRecordsResponse;
import org.cancan.usercenter.service.*;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.ADMIN_ROLE;

/**
 * 做题接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/records")
@Slf4j
@Tag(name = "做题记录")
public class QuestionRecordsController {

    @Resource
    private CoursesMapper coursesMapper;
    @Resource
    private QuestionsMapper questionsMapper;

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
    @Resource
    private ScoresService scoresService;

    @PostMapping("/add")
    @Operation(summary = "添加做题记录")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "answers", description = "答案列表", required = true)
    })
    public BaseResponse<List<QuestionRecords>> add(@RequestParam Long lessonId, @RequestParam List<String> answers, HttpServletRequest request) {
        // 确认课时含有已发布习题
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        if (lessons.getHasQuestion() == 0) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时没有习题");
        }
        // 校验选课
        Courses courses = coursesMapper.selectById(lessons.getCourseId());
        User currentUser = userService.getCurrentUser(request);
        List<Courses> coursesList = coursesService.getCoursesByStudentId(currentUser.getId());
        if (coursesList == null || coursesList.isEmpty()) {
            throw new BusinessException(ErrorCode.NO_AUTH, "选课列表为空");
        }
        if (!coursesList.contains(courses)) {
            throw new BusinessException(ErrorCode.NO_AUTH, "未选该课");
        }
        // 校验答题
        if (scoresService.getScore(lessonId, currentUser.getId()) != null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "已提交过该课时的习题");
        }
        // 获取习题列表
        List<Questions> questionsList = lessonQuestionMapService.getOrderedQuestions(lessonId);
        // 校验答案数量
        if (answers == null || answers.size() != questionsList.size()) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "答案数量与题目数量不一致");
        }
        // 逐题构造做题记录
        List<QuestionRecords> records = new ArrayList<>();
        int rightNum = 0;
        for (int i = 0; i < questionsList.size(); i++) {
            Questions q = questionsList.get(i);
            String userAnswer = answers.get(i);
            boolean isCorrect = userAnswer.equals(q.getAnswer());
            QuestionRecords record = new QuestionRecords();
            record.setStudentId(currentUser.getId());
            record.setQuestionId(q.getQuestionId());
            record.setSelectedOption(userAnswer);
            record.setIsCorrect(userAnswer.equals(q.getAnswer()) ? 1 : 0); // 判断是否正确
            record.setLessonId(lessonId);
            records.add(record);
            if (isCorrect) {
                rightNum++;
            }
        }
        // 批量插入
        boolean success = questionRecordsService.saveBatch(records);
        if (!success) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "记录保存失败");
        }
        // 计算存储得分（百分制）
        float score = (float) rightNum * 100 / questionsList.size();
        Scores scores = new Scores();
        scores.setStudentId(currentUser.getId());
        scores.setLessonId(lessonId);
        scores.setScore(score);
        scoresService.save(scores);
        // 返回结果
        return ResultUtils.success(records);
    }

    @GetMapping("/getRecords")
    @Operation(summary = "获取某学生某课时做题记录")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
            @Parameter(name = "studentId", description = "学生ID", required = true)
    })
    public BaseResponse<List<GetQuestionRecordsResponse>> get(@RequestParam Long lessonId, @RequestParam Long studentId, HttpServletRequest request) {
        // 课时校验
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        if (lessons.getHasQuestion() == 0) {
            throw new BusinessException(ErrorCode.NO_AUTH, "课时习题未发布");
        }
        // 权限校验
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        User currentUser = userService.getCurrentUser(request);
        if (!Objects.equals(currentUser.getId(), studentId)
                && !(currentUser.getUserRole() == ADMIN_ROLE)
                && !Objects.equals(currentUser.getId(), courses.getTeacherId())
        ) {
            throw new BusinessException(ErrorCode.NO_AUTH, "没有权限查看");
        }
        // 搜索答题记录
        List<QuestionRecords> questionRecordsList = questionRecordsService.getStudentLessonRecords(lessonId, studentId);
        // 封装响应体
        List<GetQuestionRecordsResponse> responses = questionRecordsList.stream().map(record -> {
            GetQuestionRecordsResponse response = new GetQuestionRecordsResponse();
            response.setQuestions(questionsMapper.selectById(record.getQuestionId()));
            response.setQuestionRecords(record);
            return response;
        }).toList();
        return ResultUtils.success(responses);
    }

    @GetMapping("/getLessonRecords")
    @Operation(summary = "获取某课时所有做题记录")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true)
    })
    public BaseResponse<List<QuestionRecords>> getByLesson(@RequestParam Long lessonId, HttpServletRequest request) {
        // 课时校验
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        // 权限校验
        Courses courses = coursesService.getValidCourseById(lessons.getCourseId());
        User currentUser = userService.getCurrentUser(request);
        if (!(currentUser.getUserRole() == ADMIN_ROLE)
                && !Objects.equals(currentUser.getId(), courses.getTeacherId())
        ) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非该课程教师无权限查看");
        }
        // 搜索返回答题记录
        QueryWrapper<QuestionRecords> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        return ResultUtils.success(questionRecordsService.list(queryWrapper));
    }

}
