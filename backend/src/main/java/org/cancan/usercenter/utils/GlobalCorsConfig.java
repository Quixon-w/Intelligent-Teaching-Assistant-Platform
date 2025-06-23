package org.cancan.usercenter.utils;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
/**
 * 配置类：后端 Cors 跨域
 * 告诉浏览器，我允许哪些域名访问，哪些请求方式访问，是否运行携带请求头
 */
@Configuration
public class GlobalCorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")// /** 表示在后端允许匹配客户端发过来的任意请求
                .allowedHeaders("*")//请求带任意头都可以
                .allowedMethods("*")//任意请求方式都可以 get/post/put...
                .allowedOriginPatterns("*")//任意域都可以(任意请求地址或端口号)
                .exposedHeaders("Content-Disposition")
                .allowCredentials(true)//请求可以携带会话相关信息(cookie/session)
                .maxAge(3600);//同一请求一小时内不再检测 直接放行
    }
}
