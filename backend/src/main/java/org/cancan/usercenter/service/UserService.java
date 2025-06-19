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
     * @param planetCode 星球编号
     * @return 用户id
     */
    long userRegister(String userAccount, String userPassword, String checkPassword, String planetCode);

    /**
     *
     * @param userAccount 用户账户
     * @param userPassword 用户密码
     * @return 脱敏后的用户信息
     */
    User userLogin(String userAccount, String userPassword, HttpServletRequest request);

    /**
     * 用户脱敏
     *
     * @param originUser
     * @return
     */
    User getSafetyUser(User originUser);

    /**
     * 用户登出
     *
     * @param request
     */
    public int userLogout(HttpServletRequest request);
}
