package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.EnrollMapper;
import org.cancan.usercenter.mapper.UserMapper;
import org.cancan.usercenter.model.domain.Enroll;
import org.cancan.usercenter.model.domain.Lessons;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.EnrollService;
import org.cancan.usercenter.service.LessonsService;
import org.springframework.stereotype.Service;

import java.util.List;

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
    private LessonsService lessonsService;

    /**
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 是否删除成功
     */
    @Override
    public Boolean dismiss(Long courseId, Long studentId) {
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
                .map(lesson -> lessonsService.getLessonScore(lesson.getLessonId(), studentId))
                .reduce(0.0f, Float::sum);
    }

}




