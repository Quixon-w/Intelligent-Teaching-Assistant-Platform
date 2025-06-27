package org.cancan.usercenter.model.domain.request;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.io.Serial;
import java.io.Serializable;

/**
 * 用户登录请求体
 */
@Data
@Schema(description = "修改密码请求体")
public class PasswordChangeRequest implements Serializable {

    @Serial
    private static final long serialVersionUID = 3191241716373120793L;

    @Schema(description = "用户id")
    private Long userId;

    @Schema(description = "旧密码")
    private String oldPassword;

    @Schema(description = "新密码")
    private String newPassword;

    @Schema(description = "校验密码")
    private String checkPassword;
}
