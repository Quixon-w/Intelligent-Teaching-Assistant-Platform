package org.cancan.usercenter.model.domain.response;

import lombok.Data;
import org.cancan.usercenter.model.domain.QuestionRecords;
import org.cancan.usercenter.model.domain.Questions;

import java.io.Serial;
import java.io.Serializable;

/**
 * 查询学生某课时习题记录响应体
 */
@Data
public class GetQuestionRecordsResponse implements Serializable {

    @Serial
    private static final long serialVersionUID = -1L;

    private Questions questions; // 习题信息
    private QuestionRecords questionRecords; // 学生答题记录
}
