#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import faiss
import pickle
from typing import List, Dict, Any, Optional


class DeleteUtils:
    """删除工具类"""
    
    # 允许删除的路径前缀
    ALLOWED_BASE_PATHS = [
        "/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge/Teachers",
        "/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge/Students"
    ]
    
    @classmethod
    def is_path_allowed(cls, path: str) -> bool:
        """
        检查路径是否在允许的范围内
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 路径是否允许
        """
        for allowed_path in cls.ALLOWED_BASE_PATHS:
            if path.startswith(allowed_path):
                return True
        return False
    
    @classmethod
    def clear_faiss_database(cls, vector_kb_path: str) -> bool:
        """
        清空FAISS向量数据库
        
        Args:
            vector_kb_path: 向量数据库路径
            
        Returns:
            bool: 是否成功清空
        """
        try:
            print(f"正在清空FAISS向量数据库: {vector_kb_path}")
            
            # 检查向量数据库路径是否存在
            if not os.path.exists(vector_kb_path):
                print(f"向量数据库路径不存在: {vector_kb_path}")
                return False
            
            # 检查FAISS文件是否存在
            index_faiss_path = os.path.join(vector_kb_path, "index.faiss")
            index_pkl_path = os.path.join(vector_kb_path, "index.pkl")
            
            if not os.path.exists(index_faiss_path) or not os.path.exists(index_pkl_path):
                print(f"FAISS数据库文件不存在: {vector_kb_path}")
                return False
            
            # 读取现有的FAISS索引以获取维度信息
            index = faiss.read_index(index_faiss_path)
            dimension = index.d
            
            # 创建一个空的FAISS索引
            empty_index = faiss.IndexFlatIP(dimension)  # 使用内积索引
            
            # 创建空的元数据
            empty_metadata = ([], {})  # 空的文档存储和ID映射
            
            # 保存空的索引和元数据
            faiss.write_index(empty_index, index_faiss_path)
            with open(index_pkl_path, 'wb') as f:
                pickle.dump(empty_metadata, f)
            
            print(f"FAISS向量数据库已清空: {vector_kb_path}")
            print(f"新的空索引维度: {dimension}")
            return True
            
        except Exception as e:
            print(f"清空FAISS数据库时出错: {e}")
            return False
    
    @classmethod
    def find_and_clear_faiss_databases(cls, path: str) -> List[str]:
        """
        在指定路径下查找并清空所有FAISS向量数据库
        
        Args:
            path: 要搜索的路径
            
        Returns:
            List[str]: 已清空的数据库路径列表
        """
        cleared_databases = []
        
        if not os.path.exists(path):
            print(f"路径不存在: {path}")
            return cleared_databases
        
        # 递归搜索vector_kb目录
        for root, dirs, files in os.walk(path):
            if "vector_kb" in dirs:
                vector_kb_path = os.path.join(root, "vector_kb")
                if cls.clear_faiss_database(vector_kb_path):
                    cleared_databases.append(vector_kb_path)
        
        return cleared_databases
    
    @classmethod
    def delete_files_recursively(cls, path: str) -> List[str]:
        """
        递归删除指定路径下的所有文件和目录
        
        Args:
            path: 要删除的路径
            
        Returns:
            List[str]: 已删除的文件和目录路径列表
        """
        deleted_items = []
        
        if not os.path.exists(path):
            print(f"路径不存在: {path}")
            return deleted_items
        
        print(f"正在删除路径下的所有文件: {path}")
        
        # 递归删除文件和目录
        for root, dirs, files in os.walk(path, topdown=False):
            # 先删除文件
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_items.append(file_path)
                    print(f"已删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {str(e)}")
            
            # 再删除目录
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_path)
                    deleted_items.append(dir_path)
                    print(f"已删除目录: {dir_path}")
                except Exception as e:
                    print(f"删除目录失败 {dir_path}: {str(e)}")
        
        # 最后删除根目录
        try:
            os.rmdir(path)
            deleted_items.append(path)
            print(f"已删除根目录: {path}")
        except Exception as e:
            print(f"删除根目录失败 {path}: {str(e)}")
        
        return deleted_items
    
    @classmethod
    def delete_path_and_clear_faiss(cls, path: str, clear_faiss_only: bool = False) -> Dict[str, Any]:
        """
        删除指定路径下的所有文件并清空FAISS向量数据库
        
        Args:
            path: 要删除的路径
            clear_faiss_only: 是否只清空FAISS数据库，不删除文件
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        print(f"收到删除请求: 路径={path}, 仅清空FAISS={clear_faiss_only}")
        
        # 安全检查：确保路径在允许的范围内
        if not cls.is_path_allowed(path):
            error_msg = f"路径不在允许的范围内。允许的路径必须以以下之一开头: {cls.ALLOWED_BASE_PATHS}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "path": path,
                "clear_faiss_only": clear_faiss_only,
                "cleared_databases": [],
                "deleted_files": []
            }
        
        # 检查路径是否存在
        if not os.path.exists(path):
            error_msg = f"路径不存在: {path}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "path": path,
                "clear_faiss_only": clear_faiss_only,
                "cleared_databases": [],
                "deleted_files": []
            }
        
        try:
            result = {
                "path": path,
                "clear_faiss_only": clear_faiss_only,
                "success": True,
                "cleared_databases": [],
                "deleted_files": [],
                "errors": []
            }
            
            # 查找并清空FAISS向量数据库
            print("正在查找并清空FAISS向量数据库...")
            cleared_databases = cls.find_and_clear_faiss_databases(path)
            result["cleared_databases"] = cleared_databases
            
            if not clear_faiss_only:
                # 删除所有文件和目录
                deleted_files = cls.delete_files_recursively(path)
                result["deleted_files"] = deleted_files
            
            print(f"操作完成: 清空了 {len(cleared_databases)} 个FAISS数据库")
            if not clear_faiss_only:
                print(f"删除了 {len(result['deleted_files'])} 个文件/目录")
            
            return result
            
        except Exception as e:
            error_msg = f"删除操作失败: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "path": path,
                "clear_faiss_only": clear_faiss_only,
                "cleared_databases": [],
                "deleted_files": []
            }
    
    @classmethod
    def clear_faiss_only(cls, path: str) -> Dict[str, Any]:
        """
        仅清空指定路径下的FAISS向量数据库，不删除文件
        
        Args:
            path: 要清空FAISS的路径
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        return cls.delete_path_and_clear_faiss(path, clear_faiss_only=True)


# 便捷函数，可以直接调用
def delete_path_and_clear_faiss(path: str, clear_faiss_only: bool = False) -> Dict[str, Any]:
    """
    删除指定路径下的所有文件并清空FAISS向量数据库
    
    Args:
        path: 要删除的路径
        clear_faiss_only: 是否只清空FAISS数据库，不删除文件
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    return DeleteUtils.delete_path_and_clear_faiss(path, clear_faiss_only)


def clear_faiss_only(path: str) -> Dict[str, Any]:
    """
    仅清空指定路径下的FAISS向量数据库，不删除文件
    
    Args:
        path: 要清空FAISS的路径
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    return DeleteUtils.clear_faiss_only(path)


def clear_faiss_database(vector_kb_path: str) -> bool:
    """
    清空单个FAISS向量数据库
    
    Args:
        vector_kb_path: 向量数据库路径
        
    Returns:
        bool: 是否成功清空
    """
    return DeleteUtils.clear_faiss_database(vector_kb_path) 