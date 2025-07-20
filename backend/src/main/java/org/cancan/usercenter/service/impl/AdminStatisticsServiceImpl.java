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
        
        // 统计教师使用情况（基于课程创建、题目生成等活动）
        QueryWrapper<Courses> courseQuery = new QueryWrapper<>();
        courseQuery.ge("createTime", startTime);
        courseQuery.le("createTime", endTime);
        List<Courses> courses = courseMapper.selectList(courseQuery);
        
        // 统计活跃教师
        Set<Long> activeTeacherIds = courses.stream()
                .map(Courses::getTeacherId)
                .collect(Collectors.toSet());
        
        result.setTotalUsageCount((long) courses.size());
        result.setActiveTeacherCount((long) activeTeacherIds.size());
        result.setAverageUsageCount(activeTeacherIds.isEmpty() ? 0.0 : 
                (double) courses.size() / activeTeacherIds.size());
        
        // 活跃板块统计（模拟数据）
        List<ActiveModuleVO> activeModules = new ArrayList<>();
        final int coursesSize = courses.size();
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("课程管理");
            setUsageCount((long) coursesSize);
            setPercentage(60.0);
            setModuleType("course_management");
        }});
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("题目生成");
            setUsageCount((long) (coursesSize * 0.8));
            setPercentage(30.0);
            setModuleType("question_generation");
        }});
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("学生分析");
            setUsageCount((long) (coursesSize * 0.5));
            setPercentage(10.0);
            setModuleType("student_analysis");
        }});
        result.setActiveModules(activeModules);
        
        // 使用趋势（模拟数据）
        List<UsageTrendVO> usageTrends = generateUsageTrends(startTime, endTime, "teacher");
        result.setUsageTrends(usageTrends);
        
        // 教师排名（模拟数据）
        List<TeacherRankingVO> teacherRankings = new ArrayList<>();
        for (Long teacherId : activeTeacherIds) {
            User teacher = userMapper.selectById(teacherId);
            if (teacher != null) {
                final long courseCount = courses.stream()
                        .filter(course -> course.getTeacherId().equals(teacherId))
                        .count();
                final Long finalTeacherId = teacherId;
                final String teacherName = teacher.getUsername();
                teacherRankings.add(new TeacherRankingVO() {{
                    setTeacherId(finalTeacherId);
                    setTeacherName(teacherName);
                    setUsageCount(courseCount);
                    setRanking(teacherRankings.size() + 1);
                }});
            }
        }
        teacherRankings.sort((a, b) -> Long.compare(b.getUsageCount(), a.getUsageCount()));
        result.setTeacherRankings(teacherRankings);
        
        return result;
    }

    @Override
    public StudentUsageStatisticsVO getStudentUsageStatistics(AdminStatisticsRequest request) {
        StudentUsageStatisticsVO result = new StudentUsageStatisticsVO();
        
        // 获取时间范围
        LocalDateTime startTime = getStartTime(request.getPeriod());
        LocalDateTime endTime = LocalDateTime.now();
        
        // 统计学生使用情况（基于答题记录）
        QueryWrapper<QuestionRecords> recordsQuery = new QueryWrapper<>();
        recordsQuery.ge("submitTime", startTime);
        recordsQuery.le("submitTime", endTime);
        List<QuestionRecords> records = questionRecordsMapper.selectList(recordsQuery);
        
        // 统计活跃学生
        Set<Long> activeStudentIds = records.stream()
                .map(QuestionRecords::getStudentId)
                .collect(Collectors.toSet());
        
        result.setTotalUsageCount((long) records.size());
        result.setActiveStudentCount((long) activeStudentIds.size());
        result.setAverageUsageCount(activeStudentIds.isEmpty() ? 0.0 : 
                (double) records.size() / activeStudentIds.size());
        
        // 活跃板块统计（模拟数据）
        List<ActiveModuleVO> activeModules = new ArrayList<>();
        final int recordsSize = records.size();
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("在线测试");
            setUsageCount((long) (recordsSize * 0.7));
            setPercentage(70.0);
            setModuleType("online_test");
        }});
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("错题练习");
            setUsageCount((long) (recordsSize * 0.2));
            setPercentage(20.0);
            setModuleType("wrong_question_practice");
        }});
        activeModules.add(new ActiveModuleVO() {{
            setModuleName("课程学习");
            setUsageCount((long) (recordsSize * 0.1));
            setPercentage(10.0);
            setModuleType("course_learning");
        }});
        result.setActiveModules(activeModules);
        
        // 使用趋势（模拟数据）
        List<UsageTrendVO> usageTrends = generateUsageTrends(startTime, endTime, "student");
        result.setUsageTrends(usageTrends);
        
        // 学生排名（模拟数据）
        List<StudentRankingVO> studentRankings = new ArrayList<>();
        for (Long studentId : activeStudentIds) {
            User student = userMapper.selectById(studentId);
            if (student != null) {
                final long recordCount = records.stream()
                        .filter(record -> record.getStudentId().equals(studentId))
                        .count();
                final Long finalStudentId = studentId;
                final String studentName = student.getUsername();
                studentRankings.add(new StudentRankingVO() {{
                    setStudentId(finalStudentId);
                    setStudentName(studentName);
                    setUsageCount(recordCount);
                    setRanking(studentRankings.size() + 1);
                }});
            }
        }
        studentRankings.sort((a, b) -> Long.compare(b.getUsageCount(), a.getUsageCount()));
        result.setStudentRankings(studentRankings);
        
        return result;
    }

    @Override
    public TeachingEfficiencyVO getTeachingEfficiency(AdminStatisticsRequest request) {
        TeachingEfficiencyVO result = new TeachingEfficiencyVO();
        
        // 获取所有课程
        List<Courses> courses = courseMapper.selectList(null);
        
        // 计算整体教学效率指数（基于通过率、参与度等）
        double overallEfficiency = 0.0;
        List<CoursePassRateVO> coursePassRates = new ArrayList<>();
        
        for (Courses course : courses) {
            // 获取课程答题记录（通过lessonId关联）
            List<Lessons> lessons = lessonMapper.selectList(new QueryWrapper<Lessons>().eq("courseId", course.getId()));
            List<Long> lessonIds = lessons.stream().map(Lessons::getLessonId).collect(Collectors.toList());
            
            List<QuestionRecords> records = new ArrayList<>();
            if (!lessonIds.isEmpty()) {
                QueryWrapper<QuestionRecords> recordsQuery = new QueryWrapper<>();
                recordsQuery.in("lessonId", lessonIds);
                records = questionRecordsMapper.selectList(recordsQuery);
            }
            
            if (!records.isEmpty()) {
                long totalStudents = records.stream()
                        .map(QuestionRecords::getStudentId)
                        .distinct()
                        .count();
                
                long passedStudents = records.stream()
                        .filter(record -> record.getIsCorrect() == 1)
                        .map(QuestionRecords::getStudentId)
                        .distinct()
                        .count();
                
                double passRate = totalStudents > 0 ? (double) passedStudents / totalStudents * 100 : 0.0;
                // 计算平均分数（基于正确率）
                double averageScore = records.stream()
                        .mapToDouble(record -> record.getIsCorrect() == 1 ? 100.0 : 0.0)
                        .average()
                        .orElse(0.0);
                
                final Long courseId = course.getId();
                final String courseName = course.getName();
                final double finalPassRate = passRate;
                final long finalTotalStudents = totalStudents;
                final long finalPassedStudents = passedStudents;
                final double finalAverageScore = averageScore;
                coursePassRates.add(new CoursePassRateVO() {{
                    setCourseId(courseId);
                    setCourseName(courseName);
                    setPassRate(finalPassRate);
                    setTotalStudents(finalTotalStudents);
                    setPassedStudents(finalPassedStudents);
                    setAverageScore(finalAverageScore);
                }});
                
                overallEfficiency += passRate;
            }
        }
        
        result.setOverallEfficiencyIndex(coursePassRates.isEmpty() ? 0.0 : 
                overallEfficiency / coursePassRates.size());
        result.setCoursePassRates(coursePassRates);
        
        // 需要优化的课程
        List<CourseOptimizationVO> optimizationSuggestions = new ArrayList<>();
        for (CoursePassRateVO passRate : coursePassRates) {
            if (passRate.getPassRate() < 60.0) {
                final Long optCourseId = passRate.getCourseId();
                final String optCourseName = passRate.getCourseName();
                final double optPassRate = passRate.getPassRate();
                optimizationSuggestions.add(new CourseOptimizationVO() {{
                    setCourseId(optCourseId);
                    setCourseName(optCourseName);
                    setIssueType("low_pass_rate");
                    setIssueDescription("通过率偏低，需要加强教学");
                    setSuggestion("建议增加练习题目，加强重点知识点讲解");
                    setPriority(optPassRate < 40.0 ? "high" : "medium");
                    setRelatedData(optPassRate);
                }});
            }
        }
        result.setOptimizationSuggestions(optimizationSuggestions);
        
        // 教学效率趋势（模拟数据）
        List<EfficiencyTrendVO> efficiencyTrends = new ArrayList<>();
        LocalDate today = LocalDate.now();
        for (int i = 6; i >= 0; i--) {
            LocalDate date = today.minusDays(i);
            efficiencyTrends.add(new EfficiencyTrendVO() {{
                setDate(date);
                setEfficiencyIndex(70.0 + Math.random() * 20.0);
                setPassRate(65.0 + Math.random() * 25.0);
            }});
        }
        result.setEfficiencyTrends(efficiencyTrends);
        
        // 学科表现分析（模拟数据）
        List<SubjectPerformanceVO> subjectPerformances = new ArrayList<>();
        subjectPerformances.add(new SubjectPerformanceVO() {{
            setSubjectName("数学");
            setAveragePassRate(75.0);
            setStudentCount(150L);
            setCourseCount(8L);
        }});
        subjectPerformances.add(new SubjectPerformanceVO() {{
            setSubjectName("语文");
            setAveragePassRate(82.0);
            setStudentCount(120L);
            setCourseCount(6L);
        }});
        subjectPerformances.add(new SubjectPerformanceVO() {{
            setSubjectName("英语");
            setAveragePassRate(68.0);
            setStudentCount(100L);
            setCourseCount(5L);
        }});
        result.setSubjectPerformances(subjectPerformances);
        
        return result;
    }

    @Override
    public LearningEffectivenessVO getLearningEffectiveness(AdminStatisticsRequest request) {
        LearningEffectivenessVO result = new LearningEffectivenessVO();
        
        // 获取所有答题记录
        List<QuestionRecords> allRecords = questionRecordsMapper.selectList(null);
        
        if (!allRecords.isEmpty()) {
            // 计算平均正确率
            double averageCorrectRate = allRecords.stream()
                    .mapToDouble(record -> record.getIsCorrect() == 1 ? 100.0 : 0.0)
                    .average()
                    .orElse(0.0);
            result.setAverageCorrectRate(averageCorrectRate);
            
            // 正确率趋势（模拟数据）
            List<CorrectRateTrendVO> correctRateTrends = new ArrayList<>();
            LocalDate today = LocalDate.now();
            for (int i = 6; i >= 0; i--) {
                final LocalDate date = today.minusDays(i);
                correctRateTrends.add(new CorrectRateTrendVO() {{
                    setDate(date);
                    setCorrectRate(65.0 + Math.random() * 25.0);
                    setQuestionCount(50L + (long)(Math.random() * 100));
                }});
            }
            result.setCorrectRateTrends(correctRateTrends);
            
            // 知识点掌握情况（基于错题统计）
            // 获取所有题目信息
            final List<Long> questionIds = allRecords.stream()
                    .map(QuestionRecords::getQuestionId)
                    .distinct()
                    .collect(Collectors.toList());
            
            final Map<Long, Questions> questionMap = new HashMap<>();
            if (!questionIds.isEmpty()) {
                List<Questions> questions = questionsMapper.selectList(new QueryWrapper<Questions>().in("question_id", questionIds));
                questionMap.putAll(questions.stream()
                        .collect(Collectors.toMap(Questions::getQuestionId, q -> q)));
            }
            
            final Map<String, Long> knowledgePointErrors = allRecords.stream()
                    .filter(record -> record.getIsCorrect() == 0)
                    .filter(record -> questionMap.containsKey(record.getQuestionId()))
                    .filter(record -> questionMap.get(record.getQuestionId()).getKnowledge() != null)
                    .collect(Collectors.groupingBy(
                            record -> questionMap.get(record.getQuestionId()).getKnowledge(),
                            Collectors.counting()
                    ));
            
            List<KnowledgePointMasteryVO> knowledgePointMastery = new ArrayList<>();
            for (Map.Entry<String, Long> entry : knowledgePointErrors.entrySet()) {
                final String knowledge = entry.getKey();
                final long errorCount = entry.getValue();
                final long totalCount = allRecords.stream()
                        .filter(record -> questionMap.containsKey(record.getQuestionId()))
                        .filter(record -> knowledge.equals(questionMap.get(record.getQuestionId()).getKnowledge()))
                        .count();
                final double masteryRate = totalCount > 0 ? (double)(totalCount - errorCount) / totalCount * 100 : 0.0;
                
                knowledgePointMastery.add(new KnowledgePointMasteryVO() {{
                    setKnowledgePoint(knowledge);
                    setMasteryRate(masteryRate);
                    setTotalQuestions(totalCount);
                    setCorrectCount(totalCount - errorCount);
                }});
            }
            result.setKnowledgePointMastery(knowledgePointMastery);
            
            // 高频错误知识点
            List<HighFrequencyErrorVO> highFrequencyErrors = knowledgePointErrors.entrySet().stream()
                    .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                    .limit(10)
                    .map(entry -> {
                        final String knowledge = entry.getKey();
                        final long errorCount = entry.getValue();
                        final long totalCount = allRecords.stream()
                                .filter(record -> questionMap.containsKey(record.getQuestionId()))
                                .filter(record -> knowledge.equals(questionMap.get(record.getQuestionId()).getKnowledge()))
                                .count();
                        final double errorRate = totalCount > 0 ? (double) errorCount / totalCount * 100 : 0.0;
                        
                        return new HighFrequencyErrorVO() {{
                            setKnowledgePoint(knowledge);
                            setErrorCount(errorCount);
                            setErrorRate(errorRate);
                            setCourseCount(1L); // 简化处理
                            setStudentCount(allRecords.stream()
                                    .filter(record -> questionMap.containsKey(record.getQuestionId()))
                                    .filter(record -> knowledge.equals(questionMap.get(record.getQuestionId()).getKnowledge()))
                                    .map(QuestionRecords::getStudentId)
                                    .distinct()
                                    .count());
                        }};
                    })
                    .collect(Collectors.toList());
            result.setHighFrequencyErrors(highFrequencyErrors);
            
            // 学习效果分布（模拟数据）
            List<LearningEffectivenessDistributionVO> effectivenessDistribution = new ArrayList<>();
            effectivenessDistribution.add(new LearningEffectivenessDistributionVO() {{
                setLevel("优秀");
                setStudentCount(50L);
                setPercentage(25.0);
                setScoreRange("90-100");
            }});
            effectivenessDistribution.add(new LearningEffectivenessDistributionVO() {{
                setLevel("良好");
                setStudentCount(80L);
                setPercentage(40.0);
                setScoreRange("80-89");
            }});
            effectivenessDistribution.add(new LearningEffectivenessDistributionVO() {{
                setLevel("中等");
                setStudentCount(50L);
                setPercentage(25.0);
                setScoreRange("70-79");
            }});
            effectivenessDistribution.add(new LearningEffectivenessDistributionVO() {{
                setLevel("待提高");
                setStudentCount(20L);
                setPercentage(10.0);
                setScoreRange("0-69");
            }});
            result.setEffectivenessDistribution(effectivenessDistribution);
        }
        
        return result;
    }

    @Override
    public SystemOverviewVO getSystemOverview() {
        SystemOverviewVO result = new SystemOverviewVO();
        
        // 基础统计数据
        result.setTotalCourses(courseMapper.selectCount(null));
        result.setTotalTeachers(userMapper.selectCount(new QueryWrapper<User>().eq("userRole", 1)));
        result.setTotalStudents(userMapper.selectCount(new QueryWrapper<User>().eq("userRole", 0)));
        result.setTotalTests(questionRecordsMapper.selectCount(null));
        
        // 今日活跃用户
        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        LocalDateTime todayEnd = LocalDateTime.now();
        QueryWrapper<QuestionRecords> todayQuery = new QueryWrapper<>();
        todayQuery.ge("submitTime", todayStart);
        todayQuery.le("submitTime", todayEnd);
        long todayActiveUsers = questionRecordsMapper.selectList(todayQuery).stream()
                .map(QuestionRecords::getStudentId)
                .distinct()
                .count();
        result.setTodayActiveUsers(todayActiveUsers);
        
        // 本周活跃用户
        LocalDateTime weekStart = LocalDate.now().minusDays(7).atStartOfDay();
        QueryWrapper<QuestionRecords> weekQuery = new QueryWrapper<>();
        weekQuery.ge("submitTime", weekStart);
        weekQuery.le("submitTime", todayEnd);
        long weekActiveUsers = questionRecordsMapper.selectList(weekQuery).stream()
                .map(QuestionRecords::getStudentId)
                .distinct()
                .count();
        result.setWeekActiveUsers(weekActiveUsers);
        
        // 平均通过率
        List<QuestionRecords> allRecords = questionRecordsMapper.selectList(null);
        if (!allRecords.isEmpty()) {
            double averagePassRate = allRecords.stream()
                    .mapToDouble(record -> record.getIsCorrect() == 1 ? 100.0 : 0.0)
                    .average()
                    .orElse(0.0);
            result.setAveragePassRate(averagePassRate);
        } else {
            result.setAveragePassRate(0.0);
        }
        
        return result;
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