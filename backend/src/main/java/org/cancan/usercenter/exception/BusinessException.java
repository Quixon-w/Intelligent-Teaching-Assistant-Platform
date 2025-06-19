package org.cancan.usercenter.exception;

import lombok.Getter;
import org.cancan.usercenter.common.ErrorCode;

import java.io.Serial;
import java.io.Serializable;

/**
 * 自定义异常类
 *
 * @author 洪
 */
@Getter
public class BusinessException extends RuntimeException implements Serializable {

    @Serial
    private static final long serialVersionUID = -3940419871022705009L;

    private final int code;

    private final String description;

    public BusinessException(String message, int code, String description) {
        super(message);
        this.code = code;
        this.description = description;
    }

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
        this.description = errorCode.getDescription();
    }

    public BusinessException(ErrorCode errorCode, String description) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
        this.description = description;
    }

}
