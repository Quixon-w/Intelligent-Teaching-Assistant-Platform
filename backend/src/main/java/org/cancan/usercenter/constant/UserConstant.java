package org.cancan.usercenter.constant;

/**
 * 用户常量
 */
public interface UserConstant {

    // 性别
    /**
     * 未知性别
     */
    int UNKNOWN_GENDER = 0;
    /**
     * 男性别
     */
    int MALE_GENDER = 1;
    /**
     * 女性别
     */
    int FEMALE_GENDER = 2;

    // 权限
    /**
     * 学生权限
     */
    int STUDENT_ROLE = 0;
    /**
     * 教师权限
     */
    int TEACHER_ROLE = 1;
    /**
     * 管理员权限
     */
    int ADMIN_ROLE = 2;
    /**
     * token 过期时间
     */
    long EXPIRE_TIME = 2 * 3600;
}
