package org.cancan.usercenter.controller;

import com.alibaba.fastjson.JSON;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.cancan.usercenter.common.BaseResponse;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.common.ResultUtils;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.model.domain.request.PasswordChangeRequest;
import org.cancan.usercenter.model.domain.request.UserLoginRequest;
import org.cancan.usercenter.model.domain.request.UserRegisterRequest;
import org.cancan.usercenter.service.CoursesService;
import org.cancan.usercenter.service.UserService;
import org.cancan.usercenter.utils.RedisUtil;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

import static org.cancan.usercenter.constant.UserConstant.*;

/**
 * 用户接口
 *
 * @author 洪
 */
@RestController
@RequestMapping("/user")
@CrossOrigin
@Slf4j
@Tag(name = "body参数")
public class UserController {

    @Resource
    private UserService userService;

    @Resource
    private CoursesService coursesService;

    @Resource
    private RedisUtil redisUtil;

    @PostMapping("/register")
    @Operation(summary = "用户注册")
    @Parameters({
            @Parameter(name = "userAccount", description = "用户账号", required = true),
            @Parameter(name = "userPassword", description = "用户密码", required = true),
            @Parameter(name = "checkPassword", description = "确认密码", required = true)
    })
    public BaseResponse<Long> userRegister(@RequestBody UserRegisterRequest userRegisterRequest) {
        if (userRegisterRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        String userAccount = userRegisterRequest.getUserAccount();
        String userPassword = userRegisterRequest.getUserPassword();
        String checkPassword = userRegisterRequest.getCheckPassword();
        if (StringUtils.isAnyBlank(userAccount, userPassword, checkPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        long result = userService.userRegister(userAccount, userPassword, checkPassword);
        return ResultUtils.success(result);
    }

    @PostMapping("/login")
    @Operation(summary = "用户登录")
    @Parameters({
            @Parameter(name = "userAccount", description = "用户账号", required = true),
            @Parameter(name = "userPassword", description = "用户密码", required = true)
    })
    public BaseResponse<User> userLogin(@RequestBody UserLoginRequest userLoginRequest, HttpServletRequest request) {
        if (userLoginRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        String userAccount = userLoginRequest.getUserAccount();
        String userPassword = userLoginRequest.getUserPassword();
        if (StringUtils.isAnyBlank(userAccount, userPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        User result = userService.userLogin(userAccount, userPassword, request);
        if (result == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户名或密码错误");
        }
        return ResultUtils.success(result);
    }

    @PostMapping("/logout")
    @Operation(summary = "用户登出")
    public BaseResponse<Integer> userLogout(HttpServletRequest request) {
        if (request == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        int result = userService.userLogout(request);
        return ResultUtils.success(result);
    }

    @GetMapping("/current")
    @Operation(summary = "获取当前用户")
    public BaseResponse<User> getCurrentUser(HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);

        if (currentUser == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        long userId = currentUser.getId();
        User user = userService.getById(userId);
        if (user.getUserStatus() == 1) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户状态失效");
        }
        User result = userService.getSafetyUser(user);
        return ResultUtils.success(result);
    }

    @PostMapping("/update")
    @Operation(summary = "更新用户")
    @Parameters({
            @Parameter(name = "userAccount", description = "用户账号", required = true),
    })
    public BaseResponse<User> updateUser(@RequestBody User user, HttpServletRequest request) {
        if (user == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        if (user.getUserAccount() == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户账号不能为空");
        }
        User currentUser = userService.getCurrentUser(request);

        if (!Objects.equals(user.getUserAccount(), currentUser.getUserAccount()) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "无权限");
        }
        user.setId(currentUser.getId());
        // 老师有课程时不可变为学生
        if (currentUser.getUserRole() == TEACHER_ROLE && user.getUserRole() == STUDENT_ROLE) {
            QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("teacher_id", currentUser.getId());
            boolean result = coursesService.exists(queryWrapper);
            if (result) {
                throw new BusinessException(ErrorCode.NO_AUTH, "老师有课程时不可变为学生");
            }
        }
        User updateUser = userService.userUpdate(user, request);
        User safeUser = userService.getSafetyUser(updateUser);
        return ResultUtils.success(safeUser);
    }

    @PostMapping("/password")
    @Operation(summary = "修改密码")
    @Parameters({
            @Parameter(name = "oldPassword", description = "旧密码", required = true),
            @Parameter(name = "newPassword", description = "新密码", required = true),
            @Parameter(name = "checkPassword", description = "确认密码", required = true)
    })
    public BaseResponse<Boolean> updatePassword(@RequestBody PasswordChangeRequest passwordChangeRequest, HttpServletRequest request) {
        if (passwordChangeRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        String oldPassword = passwordChangeRequest.getOldPassword();
        String newPassword = passwordChangeRequest.getNewPassword();
        String checkPassword = passwordChangeRequest.getCheckPassword();
        if (StringUtils.isAnyBlank(oldPassword, newPassword, checkPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        // 获取当前用户
        User currentUser = userService.getCurrentUser(request);
        // 修改密码
        if (currentUser != null && currentUser.getId() != null && newPassword.equals(checkPassword)) {
            userService.passwordUpdate(oldPassword, newPassword, currentUser.getId());
        }
        return ResultUtils.success(true);
    }

    @GetMapping("/search")
    @Operation(summary = "获取用户列表")
    @Parameters({
            @Parameter(name = "username", description = "用户名", required = true),
    })
    public BaseResponse<List<User>> searchUsers(@RequestParam String username, HttpServletRequest request) {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        if (StringUtils.isNotBlank(username)) {
            queryWrapper.like("username", username);
        }
        List<User> userList = userService.list(queryWrapper);
        List<User> result = userList.stream().map(user -> userService.getSafetyUser(user)).collect(Collectors.toList());
        return ResultUtils.success(result);
    }

    @PostMapping("/delete")
    @Operation(summary = "删除用户")
    @Parameters({
            @Parameter(name = "id", description = "用户id", required = true),
    })
    public BaseResponse<Boolean> deleteUsers(@RequestBody long id, HttpServletRequest request) {
        // 获取当前用户
        User currentUser = userService.getCurrentUser(request);
        // 仅管理员与本用户可删除
        if (currentUser.getId() != id && !isAdmin(request)) {
            throw new BusinessException(ErrorCode.NO_AUTH);
        }
        if (id <= 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户id <= 0");
        }
        boolean result = userService.removeById(id);
        userService.userLogout(request);
        return ResultUtils.success(result);
    }

    /**
     * 是否为管理员
     *
     * @param request session ID
     * @return result
     */
    private boolean isAdmin(HttpServletRequest request) {
        // 仅管理员可查询
        User user = userService.getCurrentUser(request);
        return user.getUserRole() == ADMIN_ROLE;
    }
}
