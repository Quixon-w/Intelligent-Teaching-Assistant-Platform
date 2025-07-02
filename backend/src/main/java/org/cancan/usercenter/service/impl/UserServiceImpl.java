package org.cancan.usercenter.service.impl;

import com.alibaba.fastjson.JSON;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.cancan.usercenter.common.ErrorCode;
import org.cancan.usercenter.exception.BusinessException;
import org.cancan.usercenter.mapper.UserMapper;
import org.cancan.usercenter.model.domain.User;
import org.cancan.usercenter.service.UserService;
import org.cancan.usercenter.utils.RedisUtil;
import org.cancan.usercenter.utils.SpecialCode;
import org.springframework.stereotype.Service;
import org.springframework.util.DigestUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static org.cancan.usercenter.constant.UserConstant.*;

/**
 * @author 洪
 * {@code @description} 针对表【users】的数据库操作Service实现
 */
@Service
@Slf4j
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Resource
    private UserMapper userMapper;

    @Resource
    private RedisUtil redisUtil;

    /**
     * 盐值，混淆密码
     */
    private static final String SALT = "dick";

    @Override
    public long userRegister(String userAccount, String userPassword, String checkPassword) {
        // 校验
        if (StringUtils.isAnyBlank(userAccount, userPassword, checkPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "参数为空");
        }
        if (userAccount.length() < 4) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "账号过短，不少于四位");
        }
        if (userPassword.length() < 8 || checkPassword.length() < 8) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "密码过短，不少于八位");
        }
        // 账户不能包含特殊字符
        SpecialCode.validateCode(userAccount);
        // 密码和校验密码相同
        if (!userPassword.equals(checkPassword)) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "校验失败");
        }
        // 账户不能重复
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_account", userAccount);
        long count = userMapper.selectCount(queryWrapper);
        if (count > 0) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "账号重复");
        }
        // 对密码进行加密
        String encryptPassword = DigestUtils.md5DigestAsHex((SALT + userPassword).getBytes(StandardCharsets.UTF_8));
        // 插入数据
        User user = new User();
        user.setUserAccount(userAccount);
        user.setUserPassword(encryptPassword);
        boolean saveResult = this.save(user);
        if (!saveResult) {
            return -1;
        }
        return user.getId();
    }

    @Override
    public User userLogin(String userAccount, String userPassword, HttpServletRequest request) {
        // 校验
        if (StringUtils.isAnyBlank(userAccount, userPassword)) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "参数为空");
        }
        if (userAccount.length() < 4) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "账号过短，不少于四位");
        }
        if (userPassword.length() < 8) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "密码过短，不少于八位");
        }
        // 账户不能包含特殊字符
        SpecialCode.validateCode(userAccount);
        // 对密码进行加密
        String encryptPassword = DigestUtils.md5DigestAsHex((SALT + userPassword).getBytes(StandardCharsets.UTF_8));
        // 查询用户是否存在
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_account", userAccount);
        queryWrapper.eq("user_password", encryptPassword);
        User user = userMapper.selectOne(queryWrapper);
        // 用户找不到
        if (user == null) {
            return null;
        }
        // 用户脱敏
        User safetyUser = getSafetyUser(user);
        // 将用户登录态存储到 Redis
        String sessionId = request.getSession().getId();
        redisUtil.set(sessionId, JSON.toJSONString(safetyUser), EXPIRE_TIME, TimeUnit.SECONDS);

        return safetyUser;
    }

    @Override
    public User userUpdate(User user, HttpServletRequest request) {
        if (user == null) {
            return null;
        }
        if (
                user.getGender() != null
                        && user.getGender() != UNKNOWN_GENDER
                        && user.getGender() != MALE_GENDER
                        && user.getGender() != FEMALE_GENDER
        ) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "性别参数错误");
        }
        if (user.getUserRole() != STUDENT_ROLE && user.getUserRole() != TEACHER_ROLE) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户角色参数错误");
        }
        // 脱敏，仅返回部分用户信息
        User safetyUser = getSafetyUser(user);
        // 更新用户信息
        safetyUser.setAvatarUrl(null);
        userMapper.updateById(safetyUser);
        // 将用户信息更新到 Redis
        String sessionId = request.getSession().getId(); // 使用 session ID 作为 Redis 的 key
        redisUtil.set(sessionId, JSON.toJSONString(safetyUser), EXPIRE_TIME, TimeUnit.SECONDS); // 1小时过期

        return safetyUser;
    }

    /**
     * 用户脱敏
     *
     * @param originUser 原始用户
     * @return 脱敏后的用户
     */
    @Override
    public User getSafetyUser(User originUser) {
        if (originUser == null) {
            return null;
        }
        User safetyUser = new User();
        safetyUser.setId(originUser.getId());
        safetyUser.setUsername(originUser.getUsername());
        safetyUser.setUserAccount(originUser.getUserAccount());
        safetyUser.setAvatarUrl(originUser.getAvatarUrl());
        safetyUser.setGender(originUser.getGender());
        safetyUser.setPhone(originUser.getPhone());
        safetyUser.setEmail(originUser.getEmail());
        safetyUser.setUserRole(originUser.getUserRole());
        safetyUser.setUserStatus(originUser.getUserStatus());
        return safetyUser;
    }

    @Override
    public int userLogout(HttpServletRequest request) {
        // 移除登录态
        redisUtil.delete(request.getSession().getId());
        return 1;
    }

    /**
     * @param oldPassword 老密码
     * @param newPassword 新密码
     * @param userId      欲更新用户的id
     * @param currentUser 当前操作用户
     */
    @Override
    public void passwordUpdate(String oldPassword, String newPassword, Long userId, User currentUser) {
        if (newPassword.length() < 8) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "密码过短");
        }
        if (currentUser.getUserRole() != ADMIN_ROLE) {
            // 校验旧密码正确
            String encryptOldPassword = DigestUtils.md5DigestAsHex((SALT + oldPassword).getBytes(StandardCharsets.UTF_8));
            QueryWrapper<User> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("id", userId).eq("user_password", encryptOldPassword);
            if (!userMapper.exists(queryWrapper)) {
                throw new BusinessException(ErrorCode.PARAMS_ERROR, "旧密码错误");
            }
        }
        // 更新密码
        UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
        String encryptPassword = DigestUtils.md5DigestAsHex((SALT + newPassword).getBytes(StandardCharsets.UTF_8));
        updateWrapper.eq("id", userId).set("user_password", encryptPassword);
        // 执行更新操作
        int rows = userMapper.update(null, updateWrapper);
        if (rows == 0) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "密码更新失败");
        }
    }

    /**
     * @param request 请求
     * @return 当前用户
     */
    @Override
    public User getCurrentUser(HttpServletRequest request) {
        String sessionId = request.getSession().getId();
        String userJson = redisUtil.get(sessionId);
        if (userJson == null) {
            throw new BusinessException(ErrorCode.NOT_LOGIN);
        }
        User currentUser = JSON.parseObject(userJson, User.class);
        if (currentUser == null) {
            throw new BusinessException(ErrorCode.NO_AUTH);
        }
        // 续期
        redisUtil.expire(sessionId, EXPIRE_TIME, TimeUnit.SECONDS);
        return currentUser;
    }

    /**
     * @param id 用户id
     * @return 有效用户
     */
    @Override
    public User getById(Long id) {
        if (id == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "ID不能为空");
        }
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ErrorCode.NULL_ERROR, "用户不存在");
        }
        return user;
    }

    /**
     * @param id 用户id
     * @return 被删除用户
     */
    @Override
    public User selectDeletedUserById(Long id) {
        return userMapper.selectDeletedUserById(id);
    }

    /**
     * @param id 用户id
     * @return 恢复结果
     */
    @Override
    public boolean restoreUser(Long id) {
        return userMapper.restoreUser(id);
    }

    /**
     * @return 删除用户列表
     */
    @Override
    public List<User> listDeletedUsers() {
        return userMapper.listDeletedUsers();
    }

    /**
     * @param file    文件
     * @param request 请求
     * @return 头像地址
     */
    @Override
    public String updateAvatar(MultipartFile file, HttpServletRequest request) {
        // 生成唯一文件名
        String originalName = file.getOriginalFilename();
        if (originalName == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "文件名错误");
        }
        String fileExt = originalName.substring(originalName.lastIndexOf("."));
        String fileName = UUID.randomUUID() + fileExt;
        // 保存文件
        File dest = new File(System.getProperty("user.dir") + "/backend/uploads/avatars/" + fileName);
        try {
            file.transferTo(dest);
        } catch (IOException e) {
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "保存失败");
        }
        // 删除旧头像文件
        User currentUser = this.getCurrentUser(request);
        String oldAvatarUrl = currentUser.getAvatarUrl();
        if (oldAvatarUrl != null && oldAvatarUrl.startsWith("/api/avatar/")) {
            // 截取文件名
            String oldFileName = oldAvatarUrl.substring(oldAvatarUrl.lastIndexOf("/") + 1);
            String oldPath = System.getProperty("user.dir") + "/backend/uploads/avatars/" + oldFileName;
            File oldFile = new File(oldPath);
            if (oldFile.exists()) {
                boolean deleteResult = oldFile.delete();
                if (!deleteResult) {
                    throw new BusinessException(ErrorCode.SYSTEM_ERROR, "删除旧头像失败");
                }
            }
        }
        // 保存到当前登录用户的 avatar 字段
        String urlPath = "/api/avatar/" + fileName;
        currentUser.setAvatarUrl(urlPath);
        userMapper.updateById(currentUser);
        // 同步更新 Redis 缓存
        String sessionId = request.getSession().getId();
        redisUtil.set(sessionId, JSON.toJSONString(currentUser), EXPIRE_TIME, TimeUnit.SECONDS);

        return urlPath;
    }

}




