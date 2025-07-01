package org.cancan.usercenter.utils;

import jakarta.annotation.Resource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ZSetOperations;
import org.springframework.stereotype.Component;

import java.util.Set;
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

    /**
     * 给排行榜某项增加分数（比如课程被选一次 +1）
     */
    public void incrementScore(String key, String member, double score) {
        stringRedisTemplate.opsForZSet().incrementScore(key, member, score);
    }

    /**
     * 获取排行榜 Top N
     */
    public Set<ZSetOperations.TypedTuple<String>> getTopN(String key, int topN) {
        return stringRedisTemplate.opsForZSet().reverseRangeWithScores(key, 0, topN - 1);
    }

}

