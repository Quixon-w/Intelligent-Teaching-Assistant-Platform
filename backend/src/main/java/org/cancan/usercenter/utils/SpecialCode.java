package org.cancan.usercenter.utils;

import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.springframework.stereotype.Component;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SpecialCode {

    private static final String validPattern = "[`~!@#$%^&*()+=|{}':;',\\\\[\\\\].<>/?~！@#￥%……&*（）——+|{}【】‘；：”“’。，、？]";

    /**
     * 校验字符
     *
     * @param code 待校验字符
     */
    public static void validateCode(String code) {
        Matcher matcher = Pattern.compile(validPattern).matcher(code);
        if (matcher.find()) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "账号包含特殊字符");
        }
    }
}
