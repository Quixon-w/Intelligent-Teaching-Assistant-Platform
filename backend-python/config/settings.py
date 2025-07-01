import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """项目配置管理类"""
    
    def __init__(self):
        # 基础路径配置
        self.BASE_PATH = os.environ.get('ITAP_BASE_PATH', '/data-extend/wangqianxu/wqxspace/ITAP')
        
        # 服务器配置
        self.HOST = os.environ.get('ITAP_HOST', '127.0.0.1')
        self.PORT = int(os.environ.get('ITAP_PORT', '8001'))
        
        # 模型配置
        self.DEFAULT_MODEL = os.environ.get('ITAP_DEFAULT_MODEL', 'RWKV-x060-World-7B-v3-20241112-ctx4096.pth')
        self.DEFAULT_STRATEGY = os.environ.get('ITAP_DEFAULT_STRATEGY', 'cuda fp16')
        self.EMBEDDING_MODEL = os.environ.get('ITAP_EMBEDDING_MODEL', 'm3e-base')
        
        # BGEM3和Reranker模型配置
        self.BGEM3_MODEL = os.environ.get('ITAP_BGEM3_MODEL', 'bge-m3')
        self.BGE_RERANKER_MODEL = os.environ.get('ITAP_BGE_RERANKER_MODEL', 'bge-reranker-v2-m3')
        
        # ChromaDB配置
        self.CHROMADB_HOST = os.environ.get('ITAP_CHROMADB_HOST', 'localhost')
        self.CHROMADB_PORT = int(os.environ.get('ITAP_CHROMADB_PORT', '8000'))
        
        # 数据库配置
        self.DATABASE_CONFIG = {
            "host": os.environ.get('ITAP_DB_HOST', 'localhost'),
            "port": int(os.environ.get('ITAP_DB_PORT', '9001')),
            "user": os.environ.get('ITAP_DB_USER', 'wqx'),
            "password": os.environ.get('ITAP_DB_PASSWORD', '123456'),
            "database": os.environ.get('ITAP_DB_NAME', 'itap'),
            "charset": os.environ.get('ITAP_DB_CHARSET', 'utf8mb4')
        }
        
        # 文件上传配置
        self.MAX_FILE_SIZE = int(os.environ.get('ITAP_MAX_FILE_SIZE', '100'))  # MB
        self.ALLOWED_EXTENSIONS = os.environ.get('ITAP_ALLOWED_EXTENSIONS', 'pdf,docx,txt,md').split(',')
        
        # 日志配置
        self.LOG_LEVEL = os.environ.get('ITAP_LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.environ.get('ITAP_LOG_FILE', 'api.log')
        
        # 向量数据库配置
        self.VECTOR_DB_CHUNK_SIZE = int(os.environ.get('ITAP_VECTOR_DB_CHUNK_SIZE', '768'))
        self.VECTOR_DB_CHUNK_OVERLAP = int(os.environ.get('ITAP_VECTOR_DB_CHUNK_OVERLAP', '256'))
        
        # 会话配置
        self.SESSION_TIMEOUT = int(os.environ.get('ITAP_SESSION_TIMEOUT', '3600'))  # 秒
        
        # 开发模式配置
        self.DEBUG = os.environ.get('ITAP_DEBUG', 'False').lower() == 'true'
        self.DEPLOY_MODE = os.environ.get('ITAP_DEPLOY_MODE', 'False').lower() == 'true'
        
        # 初始化路径
        self._init_paths()
    
    def _init_paths(self):
        """初始化路径配置"""
        base_path = Path(self.BASE_PATH)
        
        # 模型路径
        self.MODEL_DIR = base_path / "model"
        self.DEFAULT_MODEL_PATH = self.MODEL_DIR / self.DEFAULT_MODEL
        self.EMBEDDING_MODEL_PATH = self.MODEL_DIR / self.EMBEDDING_MODEL
        
        # BGEM3和Reranker模型路径
        self.BGEM3_MODEL_PATH = self.MODEL_DIR / self.BGEM3_MODEL
        self.BGE_RERANKER_MODEL_PATH = self.MODEL_DIR / self.BGE_RERANKER_MODEL
        
        # 知识库路径
        self.KNOWLEDGE_BASE_DIR = base_path / "base-knowledge"
        self.TEACHERS_DIR = self.KNOWLEDGE_BASE_DIR / "Teachers"
        self.STUDENTS_DIR = self.KNOWLEDGE_BASE_DIR / "Students"
        
        # 其他路径
        self.LOGS_DIR = base_path / "logs"
        self.TEMP_DIR = base_path / "temp"
        self.UPLOADS_DIR = base_path / "uploads"
        
        # 确保目录存在
        for path in [self.MODEL_DIR, self.KNOWLEDGE_BASE_DIR, self.TEACHERS_DIR, 
                    self.STUDENTS_DIR, self.LOGS_DIR, self.TEMP_DIR, self.UPLOADS_DIR]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return {
            "model": str(self.DEFAULT_MODEL_PATH),
            "strategy": self.DEFAULT_STRATEGY,
            "tokenizer": "",
            "customCuda": True,
            "deploy": self.DEPLOY_MODE
        }
    
    def get_user_knowledge_path(self, user_type: str, user_id: str) -> Path:
        """获取用户知识库路径"""
        if user_type.lower() == 'teachers':
            base_dir = self.TEACHERS_DIR
        elif user_type.lower() == 'students':
            base_dir = self.STUDENTS_DIR
        else:
            raise ValueError(f"不支持的用户类型: {user_type}")
        
        user_path = base_dir / user_id
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path
    
    def get_vector_kb_path(self, user_type: str, user_id: str, course_id: str = None, lesson_num: str = None) -> Path:
        """获取向量知识库路径"""
        if course_id and lesson_num:
            # 教师模式
            lesson_path = self.get_user_knowledge_path(user_type, user_id) / course_id / lesson_num
            vector_kb_path = lesson_path / "vector_kb"
        else:
            # 学生模式
            user_path = self.get_user_knowledge_path(user_type, user_id)
            vector_kb_path = user_path / "vector_kb"
        
        vector_kb_path.mkdir(parents=True, exist_ok=True)
        return vector_kb_path
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            "BASE_PATH": self.BASE_PATH,
            "HOST": self.HOST,
            "PORT": self.PORT,
            "DEFAULT_MODEL": self.DEFAULT_MODEL,
            "DEFAULT_STRATEGY": self.DEFAULT_STRATEGY,
            "EMBEDDING_MODEL": self.EMBEDDING_MODEL,
            "BGEM3_MODEL": self.BGEM3_MODEL,
            "BGE_RERANKER_MODEL": self.BGE_RERANKER_MODEL,
            "CHROMADB_HOST": self.CHROMADB_HOST,
            "CHROMADB_PORT": self.CHROMADB_PORT,
            "DATABASE_CONFIG": self.DATABASE_CONFIG,
            "MAX_FILE_SIZE": self.MAX_FILE_SIZE,
            "ALLOWED_EXTENSIONS": self.ALLOWED_EXTENSIONS,
            "LOG_LEVEL": self.LOG_LEVEL,
            "LOG_FILE": self.LOG_FILE,
            "VECTOR_DB_CHUNK_SIZE": self.VECTOR_DB_CHUNK_SIZE,
            "VECTOR_DB_CHUNK_OVERLAP": self.VECTOR_DB_CHUNK_OVERLAP,
            "SESSION_TIMEOUT": self.SESSION_TIMEOUT,
            "DEBUG": self.DEBUG,
            "DEPLOY_MODE": self.DEPLOY_MODE,
            "MODEL_DIR": str(self.MODEL_DIR),
            "KNOWLEDGE_BASE_DIR": str(self.KNOWLEDGE_BASE_DIR),
            "TEACHERS_DIR": str(self.TEACHERS_DIR),
            "STUDENTS_DIR": str(self.STUDENTS_DIR),
            "LOGS_DIR": str(self.LOGS_DIR),
            "TEMP_DIR": str(self.TEMP_DIR),
            "UPLOADS_DIR": str(self.UPLOADS_DIR),
            "BGEM3_MODEL_PATH": str(self.BGEM3_MODEL_PATH),
            "BGE_RERANKER_MODEL_PATH": str(self.BGE_RERANKER_MODEL_PATH)
        }


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取全局配置实例"""
    return settings


def reload_settings():
    """重新加载配置"""
    global settings
    settings = Settings()
    return settings 