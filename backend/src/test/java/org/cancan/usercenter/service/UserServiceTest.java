package org.cancan.usercenter.service;
import java.util.Date;

import jakarta.annotation.Resource;
import org.cancan.usercenter.model.domain.User;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * 用户服务测试
 *
 * @author can
 */
@SpringBootTest
class UserServiceTest {

    @Resource
    private UserService userService;

    @Test
    public void testAddUser() {
    }

    @Test
    void userRegister() {
    }
}