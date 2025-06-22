package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.utils.*;
import org.springframework.stereotype.Service;

/**
* @author 洪
* {@code @description} 针对表【courses】的数据库操作Service实现
* {@code @createDate} 2025-06-21 09:06:32
 */
@Service
public class CoursesServiceImpl extends ServiceImpl<CoursesMapper, Courses> implements CoursesService{

    /**
     * @param courseName 课程名
     * @param teacherId  老师id
     * @return 课程
     */
    @Override
    public Courses addCourse(String courseName, Long teacherId) {
        // 参数校验
        if (courseName == null || teacherId == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR);
        }
        SpecialCode.validateCode(courseName);
        // 课程名长度限制
        if (courseName.length() > 20) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "课程名长度不能超过20");
        }
        // 插入数据
        Courses courses = new Courses();
        courses.setName(courseName);
        courses.setTeacherId(teacherId);
        boolean result = this.save(courses);
        if (!result) {
            return null;
        }
        return courses;
    }

}




