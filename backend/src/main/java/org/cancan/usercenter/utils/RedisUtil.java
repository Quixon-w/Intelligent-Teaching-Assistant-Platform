package org.cancan.usercenter.utils;

import jakarta.annotation.Resource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

@Component
public class RedisUtil {

    @Resource
    private StringRedisTemplate stringRedisTemplate;

    /**
     * 设置缓存
     */
    public void set(String key, String value, long timeout, TimeUnit unit) {
        stringRedisTemplate.opsForValue().set(key, value, timeout, unit);
    }

    /**
     * 获取缓存
     */
    public String get(String key) {
        return stringRedisTemplate.opsForValue().get(key);
    }

    /**
     * 删除缓存
     */
    public void delete(String key) {
        stringRedisTemplate.delete(key);
    }

    /**
     * 设置 key 的过期时间
     */
    public void expire(String key, long timeout, TimeUnit unit) {
        stringRedisTemplate.expire(key, timeout, unit);
    }

}

