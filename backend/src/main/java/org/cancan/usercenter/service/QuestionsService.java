package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Questions;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【questions】的数据库操作Service
 * {@code @createDate} 2025-06-22 10:55:25
 */
public interface QuestionsService extends IService<Questions> {

    /**
     * 根据父级知识点查询问题集
     *
     * @param father    父级知识点
     * @param teacherId 教师ID
     * @return 问题集
     */
    List<Questions> selectByFather(String father, Long teacherId);

    /**
     * 添加问题
     *
     * @param question 问题
     * @return 问题
     */
    Questions addQuestion(Questions question);

    /**
     * 批量添加问题
     *
     * @param questions 问题
     * @return 批量添加结果
     */
    Boolean addQuestionList(List<Questions> questions);

    /**
     * 根据教师id获得问题集
     *
     * @param teacherId 教师id
     * @return 问题集
     */
    List<Questions> listByTeacherId(Long teacherId);

}
