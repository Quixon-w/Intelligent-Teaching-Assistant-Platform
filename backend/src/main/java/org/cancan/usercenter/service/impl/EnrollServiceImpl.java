package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.mapper.EnrollMapper;
import org.cancan.usercenter.mapper.QuestionRecordsMapper;
import org.cancan.usercenter.mapper.UserMapper;
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.service.EnrollService;
import org.cancan.usercenter.service.LessonsService;
import org.cancan.usercenter.service.ScoresService;
import org.cancan.usercenter.utils.RedisUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.ZSetOperations;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * @author 洪
 * {@code @description} 针对表【enrollments】的数据库操作Service实现
 * {@code @createDate} 2025-06-21 11:21:31
 */
@Service
public class EnrollServiceImpl extends ServiceImpl<EnrollMapper, Enroll> implements EnrollService {

    @Resource
    private EnrollMapper enrollMapper;
    @Resource
    private UserMapper userMapper;
    @Resource
    private CoursesMapper coursesMapper;

    @Resource
    private LessonsService lessonsService;
    @Resource
    private ScoresService scoresService;

    @Resource
    private RedisUtil redisUtil;
    @Autowired
    private QuestionRecordsMapper questionRecordsMapper;

    /**
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 是否删除成功
     */
    @Override
    public Boolean dismiss(Long courseId, Long studentId) {
        // 删除学生做题记录
        List<Lessons> lessons = lessonsService.listLessons(courseId);
        if (lessons != null && !lessons.isEmpty()) {
            List<Long> lessonIds = lessons.stream().map(Lessons::getLessonId).toList();
            QueryWrapper<QuestionRecords> queryWrapperM = new QueryWrapper<>();
            queryWrapperM.in("lesson_id", lessonIds);
            queryWrapperM.eq("student_id", studentId);
            questionRecordsMapper.delete(queryWrapperM);
        }
        // 删除选课记录
        QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("courses_id", courseId);
        queryWrapper.eq("student_id", studentId);
        return this.remove(queryWrapper);
    }

    /**
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 选课结果
     */
    @Override
    public Boolean enroll(Long courseId, Long studentId) {
        // 判断是否已选
        if (this.isEnrolled(courseId, studentId)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "该学生已选该课程");
        }
        // 添加选课
        Enroll enroll = new Enroll();
        enroll.setCoursesId(courseId);
        enroll.setStudentId(studentId);
        this.save(enroll);
        redisUtil.incrementScore("hot:course:rank", courseId.toString(), 1);
        return true;
    }

    /**
     * @param studentId 学生id
     * @return 课程列表
     */
    @Override
    public List<Long> getCoursesByStudentId(Long studentId) {
        return enrollMapper.selectCourseIdsByStudentId(studentId);
    }

    /**
     * @param courseId 课程id
     * @return 学生列表
     */
    @Override
    public List<User> getStudentsByCourseId(Long courseId) {
        List<Long> studentIds = enrollMapper.selectStudentIdsByCourseId(courseId);
        if (studentIds == null || studentIds.isEmpty()) {
            return null;
        }
        return userMapper.selectByIds(studentIds);
    }

    /**
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 是否已选
     */
    @Override
    public boolean isEnrolled(Long courseId, Long studentId) {
        QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("courses_id", courseId);
        queryWrapper.eq("student_id", studentId);
        return this.exists(queryWrapper);
    }

    /**
     * @param courseId 课程id
     */
    @Override
    public void calculateStudentsScores(Long courseId) {
        QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("courses_id", courseId);
        List<Enroll> enrollList = enrollMapper.selectList(queryWrapper);
        enrollList.forEach(enroll -> enroll.setFinalScore(this.calculateScore(enroll.getStudentId(), courseId)));
    }

    /**
     * @param studentId 学生ID
     * @param courseId  课程ID
     * @return 该学生的该课程最终得分
     */
    @Override
    public float calculateScore(Long studentId, Long courseId) {
        QueryWrapper<Lessons> queryWrapperL = new QueryWrapper<>();
        queryWrapperL.eq("course_id", courseId);
        List<Lessons> lessonsList = lessonsService.list(queryWrapperL);
        return lessonsList.stream()
                .filter(lesson -> lesson.getHasQuestion() == 0)
                .map(lesson -> scoresService.getScore(lesson.getLessonId(), studentId))
                .reduce(0.0f, Float::sum);
    }

    /**
     * @return 热门课程
     */
    @Override
    public List<Courses> getHighCourses() {
        Set<ZSetOperations.TypedTuple<String>> topCourses = redisUtil.getTopN("hot:course:rank", 10);
        if (topCourses == null || topCourses.isEmpty()) {
            return new ArrayList<>();
        }

        // 提取 courseId 列表
        List<Long> courseIds = topCourses.stream()
                .map(ZSetOperations.TypedTuple::getValue)
                .filter(Objects::nonNull)
                .map(Long::valueOf)
                .toList();
        // 从数据库中查询课程信息
        List<Courses> courses = coursesMapper.selectByIds(courseIds);

        // 排序
        Map<Long, Courses> courseMap = courses.stream().collect(Collectors.toMap(Courses::getId, Function.identity()));
        return courseIds.stream()
                .map(courseMap::get)
                .filter(Objects::nonNull)
                .toList();
    }

}




