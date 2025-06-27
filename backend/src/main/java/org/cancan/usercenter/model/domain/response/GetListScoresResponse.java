package org.cancan.usercenter.model.domain.response;

import lombok.Data;
import org.cancan.usercenter.model.domain.User;

import java.io.Serial;
import java.io.Serializable;

/**
 * 查询课时所有学生分数响应体
 */
@Data
public class GetListScoresResponse implements Serializable {

    @Serial
    private static final long serialVersionUID = -2991457539774439991L;

    private User student; // 学生
    private Float score; // 学生分数
}
