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
import org.cancan.usercenter.mapper.CoursesMapper;
import org.cancan.usercenter.mapper.EnrollMapper;
import org.cancan.usercenter.mapper.QuestionsMapper;
import org.cancan.usercenter.model.domain.Courses;
import org.cancan.usercenter.model.domain.Enroll;
import org.cancan.usercenter.model.domain.Questions;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.model.domain.request.PasswordChangeRequest;
import org.cancan.usercenter.model.domain.request.UserLoginRequest;
import org.cancan.usercenter.model.domain.request.UserRegisterRequest;
import org.cancan.usercenter.service.UserService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;

import static org.cancan.usercenter.constant.UserConstant.*;

/**
 * 用户接口
 *
 * @author cancan
 */
@RestController
@RequestMapping("/user")
@Slf4j
@Tag(name = "用户")
public class UserController {

    @Resource
    private UserService userService;

    @Resource
    private CoursesMapper coursesMapper;
    @Resource
    private EnrollMapper enrollMapper;
    @Resource
    private QuestionsMapper questionsMapper;

    @PostMapping("/register")
    @Operation(summary = "用户注册")
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
    public BaseResponse<User> userLogin(@RequestBody UserLoginRequest userLoginRequest, HttpServletRequest request) {
        if (userLoginRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        String userAccount = userLoginRequest.getUserAccount();
        String userPassword = userLoginRequest.getUserPassword();
        if (StringUtils.isAnyBlank(userAccount, userPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "账户或密码参数为空");
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
        return ResultUtils.success(userService.getSafetyUser(user));
    }

    @PostMapping("/update")
    @Operation(summary = "更新用户")
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
                QueryWrapper<Questions> queryWrapperQ = new QueryWrapper<>();
                queryWrapper.eq("teacher_id", currentUser.getId());
                queryWrapperQ.eq("teacher_id", currentUser.getId());
                if (coursesMapper.exists(queryWrapper) || questionsMapper.exists(queryWrapperQ)) {
                    throw new BusinessException(ErrorCode.NO_AUTH, "老师身份已确认，有课程或习题时不可变为学生");
                }
            }
            // 学生有课程时不可变为老师
            if (user.getUserRole() != null && currentUser.getUserRole() == STUDENT_ROLE && user.getUserRole() == TEACHER_ROLE) {
                QueryWrapper<Enroll> queryWrapper = new QueryWrapper<>();
                queryWrapper.eq("student_id", currentUser.getId());
                if (enrollMapper.exists(queryWrapper)) {
                    throw new BusinessException(ErrorCode.NO_AUTH, "学生有课程时不可变为老师");
                }
            }
        }
        User updateUser = userService.userUpdate(user, request);
        return ResultUtils.success(userService.getSafetyUser(updateUser));
    }

    @PostMapping("/password")
    @Operation(summary = "修改密码")
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
            @Parameter(name = "username", description = "用户名"),
            @Parameter(name = "userAccount", description = "用户账号"),
    })
    public BaseResponse<Page<User>> listByPage(
            @RequestParam Integer pageNum,
            @RequestParam Integer pageSize,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String userAccount,
            HttpServletRequest request
    ) {
        // 校验参数
        if (pageNum == null || pageNum <= 0 || pageSize == null || pageSize <= 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "分页参数非法");
        }
        User currentUser = userService.getCurrentUser(request);
        if (currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有管理员可查看");
        }
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        if (StringUtils.isNotBlank(username)) {
            queryWrapper.like("username", username);
        }
        if (StringUtils.isNotBlank(userAccount)) {
            queryWrapper.like("user_account", userAccount);
        }
        // 分页查询
        Page<User> page = new Page<>(pageNum, pageSize);
        Page<User> resultPage = userService.page(page, queryWrapper);
        // 对 records 进行脱敏处理
        List<User> safeUserList = resultPage.getRecords().stream()
                .map(userService::getSafetyUser).toList();
        // 构造新的分页结果（保留分页信息，替换 records）
        resultPage.setRecords(safeUserList);
        return ResultUtils.success(resultPage);
    }

    @PostMapping("/delete")
    @Operation(summary = "删除用户")
    @Parameters({
            @Parameter(name = "id", description = "用户id", required = true),
    })
    public BaseResponse<Boolean> negateUser(@RequestParam long id, HttpServletRequest request) {
        // 获取当前用户
        User currentUser = userService.getCurrentUser(request);
        // 仅管理员与本用户可删除
        if (currentUser.getId() != id && currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH);
        }
        User deletedUser = userService.getById(id);
        if (deletedUser == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户不存在或已删除");
        }
        if (deletedUser.getUserRole() == ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "该用户不可被删除");
        }
        boolean result = userService.removeById(id);
        userService.userLogout(request);
        return ResultUtils.success(result);
    }

    @PostMapping("/recover")
    @Operation(summary = "恢复用户", description = "仅管理员可恢复用户")
    @Parameters({
            @Parameter(name = "id", description = "用户id", required = true),
    })
    public BaseResponse<Boolean> recoverUser(@RequestParam long id, HttpServletRequest request) {
        // 验证权限
        User currentUser = userService.getCurrentUser(request);
        if (currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有管理员才可恢复用户");
        }
        // 检索被删除用户
        User deletedUser = userService.selectDeletedUserById(id);
        if (deletedUser == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户不存在或未被删除");
        }
        // 恢复用户
        return ResultUtils.success(userService.restoreUser(id));
    }

    @GetMapping("/listDeleted")
    @Operation(summary = "获取被删除的用户列表")
    public BaseResponse<List<User>> listDeletedUsers(HttpServletRequest request) {
        User currentUser = userService.getCurrentUser(request);
        if (currentUser.getUserRole() != ADMIN_ROLE) {
            throw new BusinessException(ErrorCode.NO_AUTH, "只有管理员才可查看被删除的用户列表");
        }
        List<User> deletedUsers = userService.listDeletedUsers();
        return ResultUtils.success(deletedUsers);
    }

    @PostMapping("/setAvatar")
    @Operation(summary = "上传头像", description = "头像url为‘后端ip:8080+用户avatarUrl字符串’")
    @Parameters({
            @Parameter(name = "file", description = "文件", required = true),
    })
    public BaseResponse<String> uploadAvatar(@RequestParam("file") MultipartFile file, HttpServletRequest request) {
        // 检查文件是否为空
        if (file.isEmpty()) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "文件为空");
        }
        // 检查文件类型
        String contentType = file.getContentType();
        List<String> allowedTypes = Arrays.asList("image/jpeg", "image/png", "image/gif");
        if (!allowedTypes.contains(contentType)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "不支持的文件类型");
        }
        return ResultUtils.success(userService.updateAvatar(file, request));
    }

    @GetMapping("/getTeacherNum")
    @Operation(summary = "获取老师数量")
    public BaseResponse<Long> getTeacherNum() {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_role", 1);
        return ResultUtils.success(userService.count(queryWrapper));
    }

    @GetMapping("/getStudentNum")
    @Operation(summary = "获取学生数量")
    public BaseResponse<Long> getStudentNum() {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_role", 0);
        return ResultUtils.success(userService.count(queryWrapper));
    }

}
