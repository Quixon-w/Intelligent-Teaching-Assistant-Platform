package org.cancan.usercenter.controller;

import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 习题接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/api/question")
@Slf4j
@Tag(name = "body参数")
public class QuestionsController {
}
