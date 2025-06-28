package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Scores;

/**
 * @author 洪
 * {@code @description} 针对表【scores】的数据库操作Service
 * {@code @createDate} 2025-06-27 10:57:29
 */
public interface ScoresService extends IService<Scores> {

    /**
     * 获取课时分数
     *
     * @param lessonId  课时ID
     * @param studentId 学生ID
     * @return 分数
     */
    Float getScore(Long lessonId, Long studentId);

}
