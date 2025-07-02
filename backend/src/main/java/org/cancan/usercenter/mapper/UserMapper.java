package org.cancan.usercenter.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import org.cancan.usercenter.model.domain.User;

import java.util.List;

/**
 * @author 洪
 * {@code @description} 针对表【user(用户)】的数据库操作Mapper
 * {@code @createDate} 2025-03-04 13:02:03
 * {@code @Entity} generator.domain.User
 */
public interface UserMapper extends BaseMapper<User> {

    @Select("SELECT * FROM users WHERE id = #{id} AND is_delete = 1")
    User selectDeletedUserById(@Param("id") Long id);

    @Update("UPDATE users SET is_delete = 0 WHERE id = #{id} AND is_delete = 1")
    boolean restoreUser(@Param("id") Long id);

    @Select("SELECT * FROM users WHERE is_delete = 1")
    List<User> listDeletedUsers();

}




