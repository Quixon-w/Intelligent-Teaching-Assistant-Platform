package org.cancan.usercenter.service;

import jakarta.servlet.http.HttpServletRequest;
import org.cancan.usercenter.model.domain.User;
import com.baomidou.mybatisplus.extension.service.IService;

/**
 *
 * 用户服务
 *
* @author 洪
*/
public interface UserService extends IService<User> {

    /**
     *
     * @param userAccount 用户账户
     * @param userPassword 用户密码
     * @param checkPassword 校验密码
     * @return 用户id
     */
    long userRegister(String userAccount, String userPassword, String checkPassword);

    /**
     *
     * @param userAccount 用户账户
     * @param userPassword 用户密码
     * @return 脱敏后的用户信息
     */
    User userLogin(String userAccount, String userPassword, HttpServletRequest request);

    /**
     *
     * @param  user  用户
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
     * @param id 用户id
     */
    void passwordUpdate(String oldPassword, String newPassword, Long id);

    /**
     * 获取当前用户
     *
     * @param request 请求
     * @return 当前用户
     */
    User getCurrentUser(HttpServletRequest request);

}
