import os
from pathlib import Path
from typing import Optional


class PathManager:
    """统一的路径管理器，用于管理项目中所有的路径配置"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化路径管理器
        
        Args:
            base_path: 基础路径，如果不提供则使用环境变量或默认路径
        """
        # 设置基础路径
        if base_path:
            self._base_path = Path(base_path)
        else:
            # 优先使用环境变量
            env_base_path = os.environ.get('ITAP_BASE_PATH')
            if env_base_path:
                self._base_path = Path(env_base_path)
            else:
                # 默认路径
                self._base_path = Path("/root/autodl-tmp")
        
        # 确保基础路径存在
        self._base_path.mkdir(parents=True, exist_ok=True)
        
        # 定义各种子路径
        self._init_paths()
    
    def _init_paths(self):
        """初始化各种路径"""
        # 模型相关路径
        self.model_dir = self._base_path / "model"
        self.model_dir.mkdir(exist_ok=True)
        
        # 知识库相关路径
        self.knowledge_base_dir = self._base_path / "base-knowledge"
        self.knowledge_base_dir.mkdir(exist_ok=True)
        
        # 教师和学生知识库路径
        self.teachers_dir = self.knowledge_base_dir / "Teachers"
        self.students_dir = self.knowledge_base_dir / "Students"
        self.teachers_dir.mkdir(exist_ok=True)
        self.students_dir.mkdir(exist_ok=True)
        
        # 日志路径
        self.logs_dir = self._base_path / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # 临时文件路径
        self.temp_dir = self._base_path / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # 上传文件路径
        self.uploads_dir = self._base_path / "uploads"
        self.uploads_dir.mkdir(exist_ok=True)
    
    @property
    def base_path(self) -> Path:
        """获取基础路径"""
        return self._base_path
    
    def get_model_path(self, model_name: str) -> Path:
        """
        获取模型文件路径
        
        Args:
            model_name: 模型文件名
            
        Returns:
            模型文件的完整路径
        """
        return self.model_dir / model_name
    
    def get_user_knowledge_path(self, user_type: str, user_id: str) -> Path:
        """
        获取用户知识库路径
        
        Args:
            user_type: 用户类型 ('Teachers' 或 'Students')
            user_id: 用户ID
            
        Returns:
            用户知识库路径
        """
        if user_type.lower() == 'teachers':
            base_dir = self.teachers_dir
        elif user_type.lower() == 'students':
            base_dir = self.students_dir
        else:
            raise ValueError(f"不支持的用户类型: {user_type}")
        
        user_path = base_dir / user_id
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path
    
    def get_course_path(self, user_type: str, user_id: str, course_id: str) -> Path:
        """
        获取课程路径
        
        Args:
            user_type: 用户类型
            user_id: 用户ID
            course_id: 课程ID
            
        Returns:
            课程路径
        """
        user_path = self.get_user_knowledge_path(user_type, user_id)
        course_path = user_path / course_id
        course_path.mkdir(parents=True, exist_ok=True)
        return course_path
    
    def get_lesson_path(self, user_type: str, user_id: str, course_id: str, lesson_num: str) -> Path:
        """
        获取课程路径
        
        Args:
            user_type: 用户类型
            user_id: 用户ID
            course_id: 课程ID
            lesson_num: 课程编号
            
        Returns:
            课程路径
        """
        course_path = self.get_course_path(user_type, user_id, course_id)
        lesson_path = course_path / lesson_num
        lesson_path.mkdir(parents=True, exist_ok=True)
        return lesson_path
    
    def get_vector_kb_path(self, user_type: str, user_id: str, course_id: str = None, lesson_num: str = None) -> Path:
        """
        获取向量知识库路径
        
        Args:
            user_type: 用户类型
            user_id: 用户ID
            course_id: 课程ID（可选）
            lesson_num: 课程编号（可选）
            
        Returns:
            向量知识库路径
        """
        if course_id and lesson_num:
            # 教师模式：有课程和课程信息
            lesson_path = self.get_lesson_path(user_type, user_id, course_id, lesson_num)
            vector_kb_path = lesson_path / "vector_kb"
        else:
            # 学生模式：只有用户ID
            user_path = self.get_user_knowledge_path(user_type, user_id)
            vector_kb_path = user_path / "vector_kb"
        
        vector_kb_path.mkdir(parents=True, exist_ok=True)
        return vector_kb_path
    
    def get_upload_path(self, user_type: str, user_id: str) -> Path:
        """
        获取上传文件路径
        
        Args:
            user_type: 用户类型
            user_id: 用户ID
            
        Returns:
            上传文件路径
        """
        upload_path = self.uploads_dir / user_type / user_id
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path
    
    def get_temp_path(self, filename: str = None) -> Path:
        """
        获取临时文件路径
        
        Args:
            filename: 文件名（可选）
            
        Returns:
            临时文件路径
        """
        if filename:
            return self.temp_dir / filename
        return self.temp_dir
    
    def get_log_path(self, log_name: str) -> Path:
        """
        获取日志文件路径
        
        Args:
            log_name: 日志文件名
            
        Returns:
            日志文件路径
        """
        return self.logs_dir / log_name
    
    def ensure_path_exists(self, path: Path) -> Path:
        """
        确保路径存在，如果不存在则创建
        
        Args:
            path: 要确保存在的路径
            
        Returns:
            路径对象
        """
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_relative_path(self, absolute_path: Path) -> str:
        """
        获取相对于基础路径的相对路径
        
        Args:
            absolute_path: 绝对路径
            
        Returns:
            相对路径字符串
        """
        try:
            return str(absolute_path.relative_to(self._base_path))
        except ValueError:
            return str(absolute_path)
    
    def __str__(self) -> str:
        """返回路径管理器的字符串表示"""
        return f"PathManager(base_path={self._base_path})"
    
    def __repr__(self) -> str:
        """返回路径管理器的详细表示"""
        return f"""PathManager(
    base_path={self._base_path}
    model_dir={self.model_dir}
    knowledge_base_dir={self.knowledge_base_dir}
    teachers_dir={self.teachers_dir}
    students_dir={self.students_dir}
    logs_dir={self.logs_dir}
    temp_dir={self.temp_dir}
    uploads_dir={self.uploads_dir}
)"""


# 创建全局路径管理器实例
_path_manager = None


def get_path_manager(base_path: Optional[str] = None) -> PathManager:
    """
    获取全局路径管理器实例
    
    Args:
        base_path: 基础路径（仅在首次调用时有效）
        
    Returns:
        路径管理器实例
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager(base_path)
    return _path_manager


def set_base_path(base_path: str):
    """
    设置基础路径（需要在应用启动时调用）
    
    Args:
        base_path: 新的基础路径
    """
    global _path_manager
    _path_manager = PathManager(base_path)


# 便捷函数
def get_model_path(model_name: str) -> Path:
    """获取模型路径的便捷函数"""
    return get_path_manager().get_model_path(model_name)


def get_user_knowledge_path(user_type: str, user_id: str) -> Path:
    """获取用户知识库路径的便捷函数"""
    return get_path_manager().get_user_knowledge_path(user_type, user_id)


def get_vector_kb_path(user_type: str, user_id: str, course_id: str = None, lesson_num: str = None) -> Path:
    """获取向量知识库路径的便捷函数"""
    return get_path_manager().get_vector_kb_path(user_type, user_id, course_id, lesson_num) 