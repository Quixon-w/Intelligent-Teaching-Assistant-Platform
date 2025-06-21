package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Enroll;

/**
* @author 洪
* @description 针对表【enrollments】的数据库操作Service
* @createDate 2025-06-21 11:21:31
*/
public interface EnrollService extends IService<Enroll> {

    /**
     * 退课
     * @param courseId 课程id
     * @param studentId 学生id
     * @return 退课结果
     */
    Boolean dismiss(Long courseId, Long studentId);

    /**
     * 选课
     * @param courseId 课程id
     * @param studentId 学生id
     * @return 选课结果
     */
    Boolean enroll(Long courseId, Long studentId);
}
