package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.QuestionsMapper;
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.service.QuestionsService;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【questions】的数据库操作Service实现
 * {@code @createDate} 2025-06-22 10:55:25
 */
@Service
public class QuestionsServiceImpl extends ServiceImpl<QuestionsMapper, Questions> implements QuestionsService {

    @Resource
    private QuestionsMapper questionsMapper;

    /**
     * @param father 父级知识点
     * @return 问题集
     */
    @Override
    public List<Questions> selectByFather(String father) {
        if (father == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "父级知识点为空");
        }
        return questionsMapper.selectMatchedQuestions(father);
    }
}




