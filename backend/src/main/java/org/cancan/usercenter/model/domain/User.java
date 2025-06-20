package org.cancan.usercenter.model.domain;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

/**
 * 用户
 * {@code @TableName} user
 */
@TableName(value ="users")
@Data
public class User {
    /**
     * id
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户昵称
     */
    private String username;

    /**
     * 账号
     */
    private String userAccount;

    /**
     * 用户头像
     */
    private String avatarUrl;

    /**
     * 性别
     */
    private Integer gender;

    /**
     * 密码
     */
    private String userPassword;

    /**
     * 电话
     */
    private String phone;

    /**
     * 邮箱
     */
    private String email;

    /**
     *  状态 0 - 正常
     */
    private Integer userStatus;

    /**
     * 是否删除
     */
    @TableLogic
    private Integer isDelete;

    /**
     * 0 - 学生 1 - 教师 2 - 管理员
     */
    private Integer userRole;

}