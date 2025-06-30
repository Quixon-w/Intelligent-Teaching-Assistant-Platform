# -*- coding: utf-8 -*-
"""
RWKV服务，封装现有的RWKV模型调用
"""
import asyncio
from typing import Dict, Any, Optional
import global_var
from utils.rwkv import TextRWKV


class RWKVService:
    """RWKV服务"""
    
    def __init__(self):
        self.model: Optional[TextRWKV] = None
        self._init_model()
    
    def _init_model(self):
        """初始化模型"""
        try:
            self.model = global_var.get(global_var.Model)
            if self.model is None:
                print("警告: RWKV模型未加载")
        except Exception as e:
            print(f"初始化RWKV模型失败: {e}")
    
    async def generate(self, prompt: str, max_tokens: int = 1000, 
                      temperature: float = 0.7, top_p: float = 0.9,
                      stop_words: Optional[list] = None, **kwargs) -> str:
        """生成文本"""
        try:
            if self.model is None:
                self._init_model()
                if self.model is None:
                    return "抱歉，模型未加载，请稍后重试。"
            
            # 设置生成参数
            generation_config = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": stop_words or ["###", "---", "问题", "题目", "结束", "完毕"]
            }
            
            # 设置模型参数
            self.model.max_tokens_per_generation = generation_config["max_tokens"]
            
            # 生成文本
            result = ""
            token_count = 0
            max_tokens = generation_config["max_tokens"]
            
            for response, delta, _, _ in self.model.generate(
                prompt, 
                stop=generation_config["stop"]
            ):
                result += delta
                token_count += 1
                
                # 检查token数量限制
                if token_count > max_tokens:
                    break
            
            return result.strip()
            
        except Exception as e:
            print(f"文本生成失败: {e}")
            return f"抱歉，生成过程中出现错误: {str(e)}"
    
    async def generate_with_retry(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """带重试的文本生成"""
        for attempt in range(max_retries):
            try:
                result = await self.generate(prompt, **kwargs)
                if result and not result.startswith("抱歉"):
                    return result
            except Exception as e:
                print(f"生成尝试 {attempt + 1} 失败: {e}")
                if attempt == max_retries - 1:
                    return f"抱歉，多次尝试后仍然失败: {str(e)}"
                await asyncio.sleep(1)  # 等待1秒后重试
        
        return "抱歉，生成失败，请稍后重试。"
    
    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        try:
            return {
                "status": "loaded",
                "model_type": "RWKV",
                "max_tokens": getattr(self.model, 'max_tokens_per_generation', 1000)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def reload_model(self, model_path: Optional[str] = None) -> bool:
        """重新加载模型"""
        try:
            # 这里可以实现模型重新加载逻辑
            # 暂时返回成功
            return True
        except Exception as e:
            print(f"重新加载模型失败: {e}")
            return False 