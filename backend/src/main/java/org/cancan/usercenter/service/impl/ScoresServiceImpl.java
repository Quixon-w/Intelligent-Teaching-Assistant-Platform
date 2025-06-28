package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.cancan.usercenter.mapper.ScoresMapper;
import org.cancan.usercenter.model.domain.Scores;
import org.cancan.usercenter.service.ScoresService;
import org.springframework.stereotype.Service;

/**
 * @author 洪
 * {@code @description} 针对表【scores】的数据库操作Service实现
 * {@code @createDate} 2025-06-27 10:57:29
 */
@Service
public class ScoresServiceImpl extends ServiceImpl<ScoresMapper, Scores> implements ScoresService {


    /**
     * @param lessonId  课时ID
     * @param studentId 学生ID
     * @return 课时分数
     */
    @Override
    public Float getScore(Long lessonId, Long studentId) {
        QueryWrapper<Scores> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("lesson_id", lessonId);
        queryWrapper.eq("student_id", studentId);
        Scores scores = this.getOne(queryWrapper);
        return scores == null ? null : scores.getScore();
    }
}




