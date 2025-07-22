package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.mapper.UserMapper;
import org.cancan.usercenter.mapper.QuestionRecordsMapper;
import org.cancan.usercenter.mapper.EnrollMapper;
import org.cancan.usercenter.mapper.LessonsMapper;
import org.cancan.usercenter.mapper.QuestionsMapper;
import org.cancan.usercenter.model.dto.AdminStatisticsRequest;
import org.cancan.usercenter.model.domain.*;
import org.cancan.usercenter.model.vo.*;
import org.cancan.usercenter.service.AdminStatisticsService;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 管理员统计服务实现
 */
@Service
public class AdminStatisticsServiceImpl implements AdminStatisticsService {

    @Resource
    private CoursesMapper courseMapper;

    @Resource
    private UserMapper userMapper;

    @Resource
    private QuestionRecordsMapper questionRecordsMapper;

    @Resource
    private EnrollMapper enrollMapper;

    @Resource
    private LessonsMapper lessonMapper;

    @Resource
    private QuestionsMapper questionsMapper;

    @Override
    public TeacherUsageStatisticsVO getTeacherUsageStatistics(AdminStatisticsRequest request) {
        TeacherUsageStatisticsVO result = new TeacherUsageStatisticsVO();
        
        // 获取时间范围
        LocalDateTime startTime = getStartTime(request.getPeriod());
        LocalDateTime endTime = LocalDateTime.now();
        
        // 统计教师课时数量
        QueryWrapper<Lessons> lessonQuery = new QueryWrapper<>();
        lessonQuery.ge("create_time", startTime);
        lessonQuery.le("create_time", endTime);
        List<Lessons> lessons = lessonMapper.selectList(lessonQuery);
        
        // 按教师ID分组统计课时数量
        Map<Long, Long> teacherLessonCounts = lessons.stream()
                .collect(Collectors.groupingBy(
                    lesson -> {
                        Courses course = courseMapper.selectById(lesson.getCourseId());
                        return course != null ? course.getTeacherId() : null;
                    },
                    Collectors.counting()
                ));
        
        // 过滤掉null的教师ID
        teacherLessonCounts.remove(null);
        
        // 计算统计数据
        long totalUsageCount = teacherLessonCounts.values().stream().mapToLong(Long::longValue).sum();
        long activeTeacherCount = teacherLessonCounts.size();
        double averageUsageCount = activeTeacherCount > 0 ? (double) totalUsageCount / activeTeacherCount : 0.0;
        
        result.setTotalUsageCount(totalUsageCount);
        result.setActiveTeacherCount(activeTeacherCount);
        result.setAverageUsageCount(averageUsageCount);
        
        // 生成使用趋势（模拟数据）
        result.setUsageTrends(generateUsageTrends(startTime, endTime, "teacher"));
        
        // 活跃板块统计（模拟数据）
        List<ActiveModuleVO> activeModules = new ArrayList<>();
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("课时管理");
            setUsageCount(totalUsageCount);
            setPercentage(100.0);
            setModuleType("lesson_management");
        }});
        result.setActiveModules(activeModules);
        
        return result;
    }

    @Override
    public StudentUsageStatisticsVO getStudentUsageStatistics(AdminStatisticsRequest request) {
        StudentUsageStatisticsVO result = new StudentUsageStatisticsVO();
        
        // 获取时间范围
        LocalDateTime startTime = getStartTime(request.getPeriod());
        LocalDateTime endTime = LocalDateTime.now();
        
        // 统计学生做题记录数量（排除自主练习，只统计课时测试）
        QueryWrapper<QuestionRecords> recordQuery = new QueryWrapper<>();
        recordQuery.ge("submit_time", startTime);
        recordQuery.le("submit_time", endTime);
        // 只统计有课时ID的记录（课时测试），排除自主练习
        recordQuery.isNotNull("lesson_id");
        List<QuestionRecords> records = questionRecordsMapper.selectList(recordQuery);
        
        // 按学生ID分组统计做题记录数量
        Map<Long, Long> studentRecordCounts = records.stream()
                .collect(Collectors.groupingBy(
                    QuestionRecords::getStudentId,
                    Collectors.counting()
                ));
        
        // 计算统计数据
        long totalUsageCount = studentRecordCounts.values().stream().mapToLong(Long::longValue).sum();
        long activeStudentCount = studentRecordCounts.size();
        double averageUsageCount = activeStudentCount > 0 ? (double) totalUsageCount / activeStudentCount : 0.0;
        
        result.setTotalUsageCount(totalUsageCount);
        result.setActiveStudentCount(activeStudentCount);
        result.setAverageUsageCount(averageUsageCount);
        
        // 生成使用趋势（模拟数据）
        result.setUsageTrends(generateUsageTrends(startTime, endTime, "student"));
        
        // 活跃板块统计（模拟数据）
        List<ActiveModuleVO> activeModules = new ArrayList<>();
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("课时测试");
            setUsageCount(totalUsageCount);
            setPercentage(100.0);
            setModuleType("lesson_test");
        }});
        result.setActiveModules(activeModules);
        
        return result;
    }

    @Override
    public TeachingEfficiencyVO getTeachingEfficiency(AdminStatisticsRequest request) {
        TeachingEfficiencyVO result = new TeachingEfficiencyVO();
        
        // 获取时间范围
        LocalDateTime startTime = getStartTime(request.getPeriod());
        LocalDateTime endTime = LocalDateTime.now();
        
        // 获取所有课程
        List<Courses> allCourses = courseMapper.selectList(null);
        
        // 计算每个课程的通过率
        List<CoursePassRateVO> coursePassRates = new ArrayList<>();
        for (Courses course : allCourses) {
            // 获取该课程下的所有课时
            QueryWrapper<Lessons> lessonQuery = new QueryWrapper<>();
            lessonQuery.eq("course_id", course.getId());
            List<Lessons> courseLessons = lessonMapper.selectList(lessonQuery);
            
            if (!courseLessons.isEmpty()) {
                // 获取该课程下所有学生的做题记录
                List<Long> lessonIds = courseLessons.stream()
                        .map(Lessons::getLessonId)
                        .collect(Collectors.toList());
                
                QueryWrapper<QuestionRecords> recordQuery = new QueryWrapper<>();
                recordQuery.in("lesson_id", lessonIds);
                recordQuery.ge("submit_time", startTime);
                recordQuery.le("submit_time", endTime);
                List<QuestionRecords> courseRecords = questionRecordsMapper.selectList(recordQuery);
                
                if (!courseRecords.isEmpty()) {
                    // 计算通过率
                    long totalRecords = courseRecords.size();
                    long correctRecords = courseRecords.stream()
                            .filter(record -> record.getIsCorrect() == 1)
                            .count();
                    double passRate = (double) correctRecords / totalRecords * 100;
                    
                    // 计算平均分数
                    double averageScore = courseRecords.stream()
                            .mapToDouble(record -> record.getIsCorrect() == 1 ? 100.0 : 0.0)
                            .average()
                            .orElse(0.0);
                    
                    // 统计学生数量
                    long totalStudents = courseRecords.stream()
                            .map(QuestionRecords::getStudentId)
                            .distinct()
                            .count();
                    
                    long passedStudents = courseRecords.stream()
                            .filter(record -> record.getIsCorrect() == 1)
                            .map(QuestionRecords::getStudentId)
                            .distinct()
                            .count();
                    
                    coursePassRates.add(new CoursePassRateVO() {{
                        setCourseId(course.getId());
                        setCourseName(course.getName());
                        setPassRate(Math.round(passRate * 10.0) / 10.0); // 保留一位小数
                        setTotalStudents(totalStudents);
                        setPassedStudents(passedStudents);
                        setAverageScore(Math.round(averageScore * 10.0) / 10.0);
                    }});
                }
            }
        }
        
        // 按通过率排序
        coursePassRates.sort((a, b) -> Double.compare(b.getPassRate(), a.getPassRate()));
        
        result.setCoursePassRates(coursePassRates);
        
        // 计算整体教学效率指数（所有课程通过率的平均值）
        double overallEfficiency = coursePassRates.stream()
                .mapToDouble(CoursePassRateVO::getPassRate)
                .average()
                .orElse(0.0);
        result.setOverallEfficiency(Math.round(overallEfficiency * 10.0) / 10.0);
        
        // 教师排名（基于课时数量）
        QueryWrapper<Lessons> teacherLessonQuery = new QueryWrapper<>();
        teacherLessonQuery.ge("create_time", startTime);
        teacherLessonQuery.le("create_time", endTime);
        List<Lessons> teacherLessons = lessonMapper.selectList(teacherLessonQuery);
        
        Map<Long, Long> teacherLessonCounts = teacherLessons.stream()
                .collect(Collectors.groupingBy(
                    lesson -> {
                        Courses course = courseMapper.selectById(lesson.getCourseId());
                        return course != null ? course.getTeacherId() : null;
                    },
                    Collectors.counting()
                ));
        
        teacherLessonCounts.remove(null);
        
        List<TeacherRankingVO> teacherRankings = new ArrayList<>();
        int ranking = 1;
        for (Map.Entry<Long, Long> entry : teacherLessonCounts.entrySet()) {
            User teacher = userMapper.selectById(entry.getKey());
            if (teacher != null) {
                teacherRankings.add(new TeacherRankingVO() {{
                    setTeacherId(entry.getKey());
                    setTeacherName(teacher.getUsername());
                    setUsageCount(entry.getValue());
                    setRanking(ranking++);
                }});
            }
        }
        
        // 按课时数量排序
        teacherRankings.sort((a, b) -> Long.compare(b.getUsageCount(), a.getUsageCount()));
        result.setTeacherRankings(teacherRankings);
        
        return result;
    }

    @Override
    public LearningEffectivenessVO getLearningEffectiveness(AdminStatisticsRequest request) {
        LearningEffectivenessVO result = new LearningEffectivenessVO();
        
        // 获取时间范围
        LocalDateTime startTime = getStartTime(request.getPeriod());
        LocalDateTime endTime = LocalDateTime.now();
        
        // 获取所有课时
        List<Lessons> allLessons = lessonMapper.selectList(null);
        
        // 计算每个课时的通过率
        List<LessonPassRateVO> lessonPassRates = new ArrayList<>();
        for (Lessons lesson : allLessons) {
            // 获取该课时的做题记录
            QueryWrapper<QuestionRecords> recordQuery = new QueryWrapper<>();
            recordQuery.eq("lesson_id", lesson.getLessonId());
            recordQuery.ge("submit_time", startTime);
            recordQuery.le("submit_time", endTime);
            List<QuestionRecords> lessonRecords = questionRecordsMapper.selectList(recordQuery);
            
            if (!lessonRecords.isEmpty()) {
                // 计算通过率
                long totalRecords = lessonRecords.size();
                long correctRecords = lessonRecords.stream()
                        .filter(record -> record.getIsCorrect() == 1)
                        .count();
                double passRate = (double) correctRecords / totalRecords * 100;
                
                // 计算平均分数
                double averageScore = lessonRecords.stream()
                        .mapToDouble(record -> record.getIsCorrect() == 1 ? 100.0 : 0.0)
                        .average()
                        .orElse(0.0);
                
                // 获取课程信息
                Courses course = courseMapper.selectById(lesson.getCourseId());
                String courseName = course != null ? course.getName() : "未知课程";
                
                lessonPassRates.add(new LessonPassRateVO() {{
                    setLessonId(lesson.getLessonId());
                    setLessonName(lesson.getLessonName());
                    setCourseName(courseName);
                    setPassRate(Math.round(passRate * 10.0) / 10.0);
                    setAverageScore(Math.round(averageScore * 10.0) / 10.0);
                    setTotalRecords(totalRecords);
                    setCorrectRecords(correctRecords);
                }});
            }
        }
        
        // 按通过率排序
        lessonPassRates.sort((a, b) -> Double.compare(b.getPassRate(), a.getPassRate()));
        
        result.setLessonPassRates(lessonPassRates);
        
        // 计算整体学习效果指数（所有课时通过率的平均值）
        double overallEffectiveness = lessonPassRates.stream()
                .mapToDouble(LessonPassRateVO::getPassRate)
                .average()
                .orElse(0.0);
        result.setOverallEffectiveness(Math.round(overallEffectiveness * 10.0) / 10.0);
        
        // 学生排名（基于做题记录数量）
        QueryWrapper<QuestionRecords> studentRecordQuery = new QueryWrapper<>();
        studentRecordQuery.ge("submit_time", startTime);
        studentRecordQuery.le("submit_time", endTime);
        studentRecordQuery.isNotNull("lesson_id"); // 只统计课时测试
        List<QuestionRecords> studentRecords = questionRecordsMapper.selectList(studentRecordQuery);
        
        Map<Long, Long> studentRecordCounts = studentRecords.stream()
                .collect(Collectors.groupingBy(
                    QuestionRecords::getStudentId,
                    Collectors.counting()
                ));
        
        List<StudentRankingVO> studentRankings = new ArrayList<>();
        int ranking = 1;
        for (Map.Entry<Long, Long> entry : studentRecordCounts.entrySet()) {
            User student = userMapper.selectById(entry.getKey());
            if (student != null) {
                studentRankings.add(new StudentRankingVO() {{
                    setStudentId(entry.getKey());
                    setStudentName(student.getUsername());
                    setUsageCount(entry.getValue());
                    setRanking(ranking++);
                }});
            }
        }
        
        // 按做题记录数量排序
        studentRankings.sort((a, b) -> Long.compare(b.getUsageCount(), a.getUsageCount()));
        result.setStudentRankings(studentRankings);
        
        return result;
    }

    @Override
    public SystemOverviewVO getSystemOverview() {
        SystemOverviewVO result = new SystemOverviewVO();
        
        // 基础统计数据
        result.setTotalCourses(courseMapper.selectCount(null));
        result.setTotalTeachers(userMapper.selectCount(new QueryWrapper<User>().eq("user_role", 1)));
        result.setTotalStudents(userMapper.selectCount(new QueryWrapper<User>().eq("user_role", 0)));
        
        // 今日活跃用户
        result.setTodayActiveUsers(getActiveUsersCount("today"));
        
        // 本月活跃用户
        result.setMonthActiveUsers(getActiveUsersCount("month"));
        
        return result;
    }

    @Override
    public Long getActiveUsersCount(String period) {
        LocalDateTime startTime;
        LocalDateTime endTime = LocalDateTime.now();
        
        if ("today".equals(period)) {
            startTime = LocalDate.now().atStartOfDay();
        } else if ("month".equals(period)) {
            startTime = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        } else {
            return 0L;
        }
        
        // 统计教师活跃用户（基于课程和课时创建记录）
        QueryWrapper<Courses> courseQuery = new QueryWrapper<>();
        courseQuery.ge("create_time", startTime);
        courseQuery.le("create_time", endTime);
        Set<Long> activeTeacherIds = courseMapper.selectList(courseQuery).stream()
                .map(Courses::getTeacherId)
                .collect(Collectors.toSet());
        
        QueryWrapper<Lessons> lessonQuery = new QueryWrapper<>();
        lessonQuery.ge("create_time", startTime);
        lessonQuery.le("create_time", endTime);
        Set<Long> lessonTeacherIds = lessonMapper.selectList(lessonQuery).stream()
                .map(lesson -> {
                    // 通过课程ID获取教师ID
                    Courses course = courseMapper.selectById(lesson.getCourseId());
                    return course != null ? course.getTeacherId() : null;
                })
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());
        
        activeTeacherIds.addAll(lessonTeacherIds);
        
        // 统计学生活跃用户（基于做题记录）
        QueryWrapper<QuestionRecords> studentQuery = new QueryWrapper<>();
        studentQuery.ge("submit_time", startTime);
        studentQuery.le("submit_time", endTime);
        Set<Long> activeStudentIds = questionRecordsMapper.selectList(studentQuery).stream()
                .map(QuestionRecords::getStudentId)
                .collect(Collectors.toSet());
        
        // 返回总活跃用户数
        return (long) (activeTeacherIds.size() + activeStudentIds.size());
    }
    
    // 辅助方法
    private LocalDateTime getStartTime(String period) {
        LocalDate today = LocalDate.now();
        switch (period) {
            case "today":
                return today.atStartOfDay();
            case "week":
                return today.minusDays(7).atStartOfDay();
            case "month":
                return today.minusDays(30).atStartOfDay();
            default:
                return today.atStartOfDay();
        }
    }
    
    private List<UsageTrendVO> generateUsageTrends(LocalDateTime startTime, LocalDateTime endTime, String userType) {
        List<UsageTrendVO> trends = new ArrayList<>();
        LocalDateTime current = startTime;
        final String finalUserType = userType;
        
        while (!current.isAfter(endTime)) {
            final LocalDateTime finalCurrent = current;
            trends.add(new UsageTrendVO() {{
                setTimePoint(finalCurrent);
                setUsageCount((long) (Math.random() * 100 + 50));
                setUserType(finalUserType);
            }});
            current = current.plusHours(1);
        }
        
        return trends;
    }
} 