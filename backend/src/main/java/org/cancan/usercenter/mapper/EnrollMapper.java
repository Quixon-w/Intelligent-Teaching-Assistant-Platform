package org.cancan.usercenter.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.cancan.usercenter.model.domain.Enroll;

import java.util.List;

/**
* @author 洪
* @description 针对表【enrollments】的数据库操作Mapper
* @createDate 2025-06-21 11:21:31
* @Entity generator.domain.Enrollments
*/
public interface EnrollMapper extends BaseMapper<Enroll> {

    List<Long> selectCourseIdsByStudentId(Long studentId);

    List<Long> selectStudentIdsByCourseId(Long courseId);
}




