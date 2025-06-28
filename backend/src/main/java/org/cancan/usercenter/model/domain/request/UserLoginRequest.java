package org.cancan.usercenter.model.domain.request;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.io.Serial;
import java.io.Serializable;

/**
 * 用户登录请求体
 */
@Data
@Schema(description = "用户登录请求体")
public class UserLoginRequest implements Serializable {

    @Serial
    private static final long serialVersionUID = -2991457539774439991L;

    @Schema(description = "用户账号")
    private String userAccount;

    @Schema(description = "用户密码")
    private String userPassword;
}
