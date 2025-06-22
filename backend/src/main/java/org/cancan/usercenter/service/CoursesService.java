package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import org.cancan.usercenter.model.domain.Courses;

/**
* @author 洪
* {@code @description} 针对表【courses】的数据库操作Service
* {@code @createDate} 2025-06-21 09:06:32
 */
public interface CoursesService extends IService<Courses> {

    /**
     * 添加课程
     * @param courseName 课程名
     * @param teacherId 老师id
     * @return 课程
     */
    Courses addCourse(String courseName, Long teacherId);

}
