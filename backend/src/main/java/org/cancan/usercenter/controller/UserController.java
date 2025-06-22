package org.cancan.usercenter.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
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
import org.springframework.web.bind.annotation.*;

import java.util.Objects;

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
            @Parameter(name = "id", description = "用户id", required = true),
            @Parameter(name = "userAccount", description = "用户账号", required = true),
    })
    public BaseResponse<User> updateUser(@RequestBody User user, HttpServletRequest request) {
        if (user == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        if (user.getUserAccount() == null || user.getId() == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户id账号不能为空");
        }
        User currentUser = userService.getCurrentUser(request);
        // 更新信息校验
        if (currentUser.getUserRole() != ADMIN_ROLE) {
            if (!Objects.equals(user.getId(), currentUser.getId())) {
                throw new BusinessException(ErrorCode.PARAMS_ERROR, "访问id无权限");
            }
            if (!Objects.equals(user.getUserAccount(), currentUser.getUserAccount())) {
                throw new BusinessException(ErrorCode.NO_AUTH, "账号不可更改");
            }
            // 老师有课程时不可变为学生
            if (user.getUserRole() != null && currentUser.getUserRole() == TEACHER_ROLE && user.getUserRole() == STUDENT_ROLE) {
                QueryWrapper<Courses> queryWrapper = new QueryWrapper<>();
                queryWrapper.eq("teacher_id", currentUser.getId());
                boolean result = coursesService.exists(queryWrapper);
                if (result) {
                    throw new BusinessException(ErrorCode.NO_AUTH, "老师有课程时不可变为学生");
                }
            }
        }
        User updateUser = userService.userUpdate(user, request);
        User safeUser = userService.getSafetyUser(updateUser);
        return ResultUtils.success(safeUser);
    }

    @PostMapping("/password")
    @Operation(summary = "修改密码")
    @Parameters({
            @Parameter(name = "userId", description = "要更新的用户的id", required = true),
            @Parameter(name = "oldPassword", description = "旧密码", required = true),
            @Parameter(name = "newPassword", description = "新密码", required = true),
            @Parameter(name = "checkPassword", description = "确认密码", required = true)
    })
    public BaseResponse<Boolean> updatePassword(@RequestBody PasswordChangeRequest passwordChangeRequest, HttpServletRequest request) {
        if (passwordChangeRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        Long userId = passwordChangeRequest.getUserId();
        String oldPassword = passwordChangeRequest.getOldPassword();
        String newPassword = passwordChangeRequest.getNewPassword();
        String checkPassword = passwordChangeRequest.getCheckPassword();
        if (StringUtils.isAnyBlank(oldPassword, newPassword, checkPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        // 获取当前用户
        User currentUser = userService.getCurrentUser(request);
        // 验证是本人
        if (!Objects.equals(currentUser.getId(), userId) && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "没有权限");
        }
        // 修改密码
        if (!newPassword.equals(checkPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "密码校验失败，两次密码不同");
        }
        userService.passwordUpdate(oldPassword, newPassword, userId, currentUser);
        return ResultUtils.success(true);
    }

    @GetMapping("/searchPage")
    @Operation(summary = "按页获取用户列表")
    @Parameters({
            @Parameter(name = "pageNum", description = "当前页码", required = true),
            @Parameter(name = "pageSize", description = "每页条数", required = true),
            @Parameter(name = "username", description = "用户名", required = true),
    })
    public BaseResponse<Page<User>> searchUsers(
            @RequestParam Integer pageNum,
            @RequestParam Integer pageSize,
            @RequestParam String username,
            HttpServletRequest request) {
        // 校验参数
        if (pageNum == null || pageNum <= 0 || pageSize == null || pageSize <= 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "分页参数非法");
        }
        if (getCurrentUser(request) == null) {
            throw new BusinessException(ErrorCode.NOT_LOGIN);
        }
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        if (StringUtils.isNotBlank(username)) {
            queryWrapper.like("username", username);
        }
        // 分页查询
        Page<User> page = new Page<>(pageNum, pageSize);
        Page<User> resultPage = userService.page(page, queryWrapper);
        return ResultUtils.success(resultPage);
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
        if (currentUser.getId() != id && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH);
        }
        if (id <= 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户id <= 0");
        }
        boolean result = userService.removeById(id);
        userService.userLogout(request);
        return ResultUtils.success(result);
    }

    @GetMapping("/getUser")
    @Operation(summary = "获取用户信息")
    @Parameters({
            @Parameter(name = "id", description = "用户id", required = true),
    })
    public BaseResponse<User> getUserById(long id) {
        if (id <= 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数不合法");
        }
        User user = userService.getById(id);
        if (user == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "用户不存在");
        }
        return ResultUtils.success(user);
    }

}
