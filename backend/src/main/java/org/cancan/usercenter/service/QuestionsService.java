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
     * @param father 父级知识点
     * @return 问题集
     */
    List<Questions> selectByFather(String father);

}
