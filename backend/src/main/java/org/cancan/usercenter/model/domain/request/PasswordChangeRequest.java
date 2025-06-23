package org.cancan.usercenter.model.domain.request;

import lombok.Data;

import java.io.Serial;
import java.io.Serializable;

/**
 * 用户登录请求体
 */
@Data
public class PasswordChangeRequest implements Serializable {

    @Serial
    private static final long serialVersionUID = 3191241716373120793L;

    private Long userId;
    private String oldPassword, newPassword, checkPassword;
}
