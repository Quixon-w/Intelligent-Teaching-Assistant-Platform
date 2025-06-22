package org.cancan.usercenter.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.cancan.usercenter.model.domain.Enroll;

import java.util.List;

/**
* @author 洪
* {@code @description} 针对表【enrollments】的数据库操作Mapper
* {@code @createDate} 2025-06-21 11:21:31
* {@code @Entity} generator.domain.Enrollments
 */
public interface EnrollMapper extends BaseMapper<Enroll> {

    List<Long> selectCourseIdsByStudentId(Long studentId);

    List<Long> selectStudentIdsByCourseId(Long courseId);
}




