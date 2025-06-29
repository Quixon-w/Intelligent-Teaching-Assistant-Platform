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
import org.cancan.usercenter.service.QuestionsService;
import org.cancan.usercenter.service.UserService;
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

    @PostMapping("/update")
    @Operation(summary = "修改某课时的一个未发布习题", description = "该习题的questionId必须不变传入")
    public BaseResponse<Boolean> update(@RequestBody Questions question, HttpServletRequest request) {
        // 校验参数
        if (question == null || question.getQuestionId() == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "question参数或questionId为空");
        }
        // 获取当前用户
        QueryWrapper<LessonQuestionMap> queryWrapperQ = new QueryWrapper<>();
        queryWrapperQ.eq("question_id", question.getQuestionId());
        queryWrapperQ.eq("committed", 1);
        if (lessonQuestionMapService.exists(queryWrapperQ)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "该习题已发布过");
        }
        // 校验权限
        Long questionId = question.getQuestionId();
        QueryWrapper<Questions> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("question_id", questionId);
        Questions questions = questionsService.getOne(queryWrapper);
        if (!Objects.equals(questions.getTeacherId(), userService.getCurrentUser(request).getId())) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
        }
        // 修改数据
        UpdateWrapper<Questions> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("question_id", questionId);
        return ResultUtils.success(questionsService.update(question, updateWrapper));
    }

//    @PostMapping("/addByEntity")
//    @Operation(summary = "添加某课时的一个预发布习题", description = "创建新习题，习题id不需要传入")
//    @Parameters({
//            @Parameter(name = "lessonId", description = "课时ID", required = true),
//            @Parameter(name = "question", description = "习题", required = true)
//    })
//    public BaseResponse<LessonQuestionMap> addByEntity(@RequestParam Long lessonId, @RequestBody Questions question, HttpServletRequest request) {
//        // 校验权限
//        User currentUser = userService.getCurrentUser(request);
//        if (!lessonsService.isTeacher(lessonId, currentUser) && currentUser.getUserRole() != ADMIN_ROLE) {
//            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
//        }
//        // 确认课时有效性
//        Lessons lessons = lessonsService.getValidLessonById(lessonId);
//        if (lessons.getHasQuestion() == 1) {
//            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时已发布过习题");
//        }
//        // 添加习题集
//        boolean result = questionsService.addQuestion(question);
//        if (!result) {
//            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加失败");
//        }
//        // 插入 lesson-question 记录
//        LessonQuestionMap lessonQuestionMap = new LessonQuestionMap();
//        lessonQuestionMap.setLessonId(lessonId);
//        lessonQuestionMap.setQuestionId(question.getQuestionId());
//
//
//        return null;
//    }

    @PostMapping("/addByIds")
    @Operation(summary = "批量添加某课时的预发布习题", description = "传入教师个人习题集中的习题，只需要习题id")
    public BaseResponse<Boolean> addByIds(@RequestParam Long lessonId, @RequestParam List<Long> questionIds, HttpServletRequest request) {
        // 校验权限
        if (!lessonsService.isTeacher(lessonId, userService.getCurrentUser(request))) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
        }
        // 确认课时有效性
        if (lessonsService.getValidLessonById(lessonId).getHasQuestion() == 1) {
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

    @PostMapping("/addByEntities")
    @Operation(summary = "批量添加某课时的预发布习题", description = "创建新习题，习题id不需要传入")
    @Parameters({
            @Parameter(name = "lessonId", description = "课时ID", required = true),
    })
    public BaseResponse<List<LessonQuestionMap>> addEntities(@RequestParam Long lessonId, @RequestBody List<Questions> questions, HttpServletRequest request) {
        // 校验权限
        if (!lessonsService.isTeacher(lessonId, userService.getCurrentUser(request))) {
            throw new BusinessException(ErrorCode.NO_AUTH, "非老师本人开设的课时");
        }
        // 确认课时有效性
        if (lessonsService.getValidLessonById(lessonId).getHasQuestion() == 1) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "该课时已发布过习题");
        }
        // 清空习题 id
        questions.forEach(q -> q.setQuestionId(null));
        // 添加习题集
        boolean result = questionsService.addQuestionList(questions);
        if (!result) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加失败");
        }
        // 插入 lesson-question 记录
        List<LessonQuestionMap> records = questions.stream()
                .map(q -> {
                    LessonQuestionMap lq = new LessonQuestionMap();
                    lq.setLessonId(lessonId);
                    lq.setQuestionId(q.getQuestionId());
                    return lq;
                }).toList();
        if (!lessonQuestionMapService.saveBatch(records)) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "添加课时习题映射关系失败");
        }
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
        // 在习题集删除该题
        return ResultUtils.success(questionsService.removeById(questionId));
    }

    @GetMapping("/list")
    @Operation(summary = "获取某课时的所有顺序习题列表", description = "已发布和未发布的")
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
        lessonsService.getValidLessonById(lessonId);
        // 获取顺序课时习题列表
        return ResultUtils.success(lessonQuestionMapService.getOrderedQuestions(lessonId, false));
    }

    @GetMapping("/listCommitted")
    @Operation(summary = "获取某课时的!已发布!顺序习题列表")
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
        if (!lessonsService.isTeacher(lessonId, currentUser)) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有该课程老师可发布习题");
        }
        // 查询发布
        UpdateWrapper<LessonQuestionMap> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("lesson_id", lessonId);
        updateWrapper.in("question_id", questionIds);
        updateWrapper.set("committed", 1);
        boolean update = lessonQuestionMapService.update(updateWrapper);
        if (!update) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "发布失败");
        }
        // 设置该课时已有习题
        Lessons lessons = lessonsService.getValidLessonById(lessonId);
        lessons.setHasQuestion(1);
        lessonsService.updateById(lessons);
        return ResultUtils.success(true);
    }

}
