package org.cancan.usercenter.model.domain.response;

import lombok.Data;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.Enroll;

import java.io.Serial;
import java.io.Serializable;

@Data
public class ListEnrollResponse implements Serializable {

    @Serial
    private static final long serialVersionUID = 12512512234L;

    private Courses course; // 课程信息
    private Enroll enroll; // 选课信息


}
