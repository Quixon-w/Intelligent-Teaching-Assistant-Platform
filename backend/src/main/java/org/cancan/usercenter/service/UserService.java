package org.cancan.usercenter.service;

import com.baomidou.mybatisplus.extension.service.IService;
import jakarta.servlet.http.HttpServletRequest;
import org.cancan.usercenter.model.domain.User;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

/**
 * 用户服务
 *
 * @author 洪
 */
public interface UserService extends IService<User> {

    /**
     * @param userAccount   用户账户
     * @param userPassword  用户密码
     * @param checkPassword 校验密码
     * @return 用户id
     */
    long userRegister(String userAccount, String userPassword, String checkPassword);

    /**
     * @param userAccount  用户账户
     * @param userPassword 用户密码
     * @return 脱敏后的用户信息
     */
    User userLogin(String userAccount, String userPassword, HttpServletRequest request);

    /**
     * @param user 用户
     * @return 脱敏后的用户信息
     */
    User userUpdate(User user, HttpServletRequest request);

    /**
     * 用户脱敏
     *
     * @param originUser 原始用户
     * @return 脱敏后的用户
     */
    User getSafetyUser(User originUser);

    /**
     * 用户登出
     *
     * @param request 请求
     */
    int userLogout(HttpServletRequest request);

    /**
     * 修改密码
     *
     * @param oldPassword 旧密码
     * @param newPassword 新密码
     * @param userId      欲更新用户的id
     * @param currentUser 当前用户
     */
    void passwordUpdate(String oldPassword, String newPassword, Long userId, User currentUser);

    /**
     * 获取当前用户
     *
     * @param request 请求
     * @return 当前用户
     */
    User getCurrentUser(HttpServletRequest request);

    /**
     * 根据id获取用户
     *
     * @param id 用户id
     * @return 有效用户
     */
    User getById(Long id);

    /**
     * 根据id获取被删除用户
     *
     * @param id 用户id
     * @return 被删除用户
     */
    User selectDeletedUserById(Long id);

    /**
     * 恢复用户
     *
     * @param id 用户id
     * @return 是否成功
     */
    boolean restoreUser(Long id);

    /**
     * 获取被删除的用户列表
     *
     * @return 被删除的用户列表
     */
    List<User> listDeletedUsers();

    /**
     * 更新用户头像
     *
     * @param file    文件
     * @param request 请求
     * @return 头像地址
     */
    String updateAvatar(MultipartFile file, HttpServletRequest request);

}
