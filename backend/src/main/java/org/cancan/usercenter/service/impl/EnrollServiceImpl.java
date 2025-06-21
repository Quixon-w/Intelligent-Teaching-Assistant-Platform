package org.cancan.usercenter.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.EnrollMapper;
import org.cancan.usercenter.model.domain.Enroll;
import org.cancan.usercenter.service.EnrollService;
import org.springframework.stereotype.Service;

/**
* @author 洪
* @description 针对表【enrollments】的数据库操作Service实现
* @createDate 2025-06-21 11:21:31
*/
@Service
public class EnrollServiceImpl extends ServiceImpl<EnrollMapper, Enroll> implements EnrollService {

    @Resource
    private EnrollMapper enrollMapper;

    /**
     * @param courseId  课程id
     * @param studentId 学生id
     * @return 是否删除成功
     */
    @Override
    public Boolean dismiss(Long courseId, Long studentId) {
        QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("courses_id", courseId);
        queryWrapper.eq("student_id", studentId);

        return enrollMapper.delete(queryWrapper) > 0;
    }

    /**
     * @param courseId 课程id
     * @param studentId       学生id
     * @return 选课结果
     */
    @Override
    public Boolean enroll(Long courseId, Long studentId) {
        QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("courses_id", courseId);
        queryWrapper.eq("student_id", studentId);
        if (enrollMapper.exists(queryWrapper)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "已选该课程");
        }
        Enroll enroll = new Enroll();
        enroll.setCoursesId(courseId);
        enroll.setStudentId(studentId);
        this.save(enroll);
        return true;
    }
}




