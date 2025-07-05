package org.cancan.usercenter.model.domain.request;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.io.Serial;
import java.io.Serializable;

/**
 * 用户注册请求体
 */
@Data
@Schema(description = "用户注册请求体")
public class UserRegisterRequest implements Serializable {

    @Serial
    private static final long serialVersionUID = -1296280711474158386L;

    @Schema(description = "用户账号")
    private String userAccount;

    @Schema(description = "用户身份")
    private Integer userRole;

    @Schema(description = "用户密码")
    private String userPassword;

    @Schema(description = "校验密码")
    private String checkPassword;
}
