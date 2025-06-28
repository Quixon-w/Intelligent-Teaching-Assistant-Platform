import os
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional


class SessionManager:
    """会话管理器，负责存储和检索对话历史"""
    
    def __init__(self, base_path: str = "/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge"):
        self.base_path = base_path
        self.max_dialogues = 10
        self._session_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_user_path(self, user_id: str, is_teacher: bool) -> str:
        """根据userID和isTeacher确定用户路径"""
        user_type = "Teachers" if is_teacher else "Students"
        return os.path.join(self.base_path, user_type, user_id)
    
    def _ensure_user_dialogue_dir(self, user_id: str, session_id: str, is_teacher: bool) -> str:
        """确保用户会话目录存在"""
        user_path = self._get_user_path(user_id, is_teacher)
        dialogue_path = os.path.join(user_path, "dialogue", session_id)
        if not os.path.exists(dialogue_path):
            os.makedirs(dialogue_path, exist_ok=True)
        return dialogue_path
    
    def _get_session_files(self, session_path: str) -> List[str]:
        """获取会话目录下的所有对话文件，按时间排序"""
        if not os.path.exists(session_path):
            return []
        
        files = []
        for file in os.listdir(session_path):
            if file.endswith('.pkl'):
                file_path = os.path.join(session_path, file)
                files.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序，最新的在前
        files.sort(key=lambda x: x[1], reverse=True)
        return [file[0] for file in files]
    
    def _cleanup_old_dialogues(self, session_path: str):
        """清理旧的对话记录，保持最多max_dialogues个"""
        files = self._get_session_files(session_path)
        if len(files) >= self.max_dialogues:
            # 删除最旧的文件
            for old_file in files[self.max_dialogues:]:
                try:
                    os.remove(old_file)
                    print(f"Deleted old dialogue file: {old_file}")
                except Exception as e:
                    print(f"Error deleting file {old_file}: {e}")
    
    def _generate_dialogue_filename(self) -> str:
        """生成对话文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"dialogue_{timestamp}.pkl"
    
    def save_dialogue(self, user_id: str, session_id: str, messages: List[Dict[str, Any]], response: str, is_teacher: bool = False) -> Optional[str]:
        """保存对话记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            
            # 创建对话记录
            dialogue_record = {
                "user_id": user_id,
                "session_id": session_id,
                "user_type": "teacher" if is_teacher else "student",
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "response": response,
                "message_count": len(messages)
            }
            
            # 生成文件名并保存
            filename = self._generate_dialogue_filename()
            file_path = os.path.join(session_path, filename)
            
            with open(file_path, 'wb') as f:
                pickle.dump(dialogue_record, f)
            
            # 清理旧记录
            self._cleanup_old_dialogues(session_path)
            
            # 更新缓存
            cache_key = f"{user_id}_{session_id}_{filename}"
            self._session_cache[cache_key] = dialogue_record
            
            print(f"Saved dialogue for user {user_id}, session {session_id}: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"Error saving dialogue for user {user_id}, session {session_id}: {e}")
            return None
    
    def get_session_dialogues(self, user_id: str, session_id: str, limit: int = 5, is_teacher: bool = False) -> List[Dict[str, Any]]:
        """获取指定会话的对话记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            files = self._get_session_files(session_path)
            dialogues = []
            
            for file_path in files[:limit]:
                try:
                    with open(file_path, 'rb') as f:
                        dialogue = pickle.load(f)
                        dialogues.append(dialogue)
                except Exception as e:
                    print(f"Error loading dialogue file {file_path}: {e}")
                    continue
            
            return dialogues
            
        except Exception as e:
            print(f"Error getting dialogues for user {user_id}, session {session_id}: {e}")
            return []
    
    def get_context_messages(self, user_id: str, session_id: str, max_messages: int = 20, is_teacher: bool = False) -> List[Dict[str, Any]]:
        """获取用于上下文的最近消息"""
        dialogues = self.get_session_dialogues(user_id, session_id, limit=5, is_teacher=is_teacher)
        context_messages = []
        
        for dialogue in reversed(dialogues):  # 从最旧到最新
            if "messages" in dialogue:
                # 确保消息格式正确
                for msg in dialogue["messages"]:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        context_messages.append({
                            "role": msg["role"],
                            "content": msg["content"],
                            "raw": msg.get("raw", False)
                        })
                if len(context_messages) >= max_messages:
                    break
        
        return context_messages[-max_messages:]  # 只返回最近的max_messages条
    
    def save_session_history(self, user_id: str, session_id: str, messages: List[Dict[str, Any]], is_teacher: bool = False) -> bool:
        """保存当前会话的完整历史记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            
            # 创建会话历史记录
            session_history = {
                "user_id": user_id,
                "session_id": session_id,
                "user_type": "teacher" if is_teacher else "student",
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "message_count": len(messages),
                "is_session_history": True  # 标记为会话历史
            }
            
            # 保存为会话历史文件
            history_filename = f"session_history_{session_id}.pkl"
            history_path = os.path.join(session_path, history_filename)
            
            with open(history_path, 'wb') as f:
                pickle.dump(session_history, f)
            
            print(f"Saved session history for user {user_id}, session {session_id}: {history_path}")
            return True
            
        except Exception as e:
            print(f"Error saving session history for user {user_id}, session {session_id}: {e}")
            return False
    
    def load_session_history(self, user_id: str, session_id: str, is_teacher: bool = False) -> List[Dict[str, Any]]:
        """加载指定会话的历史记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            history_filename = f"session_history_{session_id}.pkl"
            history_path = os.path.join(session_path, history_filename)
            
            if not os.path.exists(history_path):
                print(f"Session history not found: {history_path}")
                return []
            
            with open(history_path, 'rb') as f:
                session_history = pickle.load(f)
            
            if "messages" in session_history:
                print(f"Loaded session history for user {user_id}, session {session_id}: {len(session_history['messages'])} messages")
                return session_history["messages"]
            else:
                print(f"No messages found in session history: {history_path}")
                return []
                
        except Exception as e:
            print(f"Error loading session history for user {user_id}, session {session_id}: {e}")
            return []
    
    def get_user_sessions(self, user_id: str, is_teacher: bool = False) -> List[str]:
        """获取用户的所有会话ID"""
        try:
            user_path = self._get_user_path(user_id, is_teacher)
            dialogue_path = os.path.join(user_path, "dialogue")
            
            if not os.path.exists(dialogue_path):
                return []
            
            sessions = []
            for session_dir in os.listdir(dialogue_path):
                session_path = os.path.join(dialogue_path, session_dir)
                if os.path.isdir(session_path):
                    sessions.append(session_dir)
            
            return sessions
            
        except Exception as e:
            print(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    def clear_session_dialogues(self, user_id: str, session_id: str, is_teacher: bool = False) -> int:
        """清除指定会话的所有对话历史，返回删除的文件数量"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            
            # 删除所有对话文件
            files = self._get_session_files(session_path)
            deleted_count = 0
            
            for file_path in files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            
            return deleted_count
            
        except Exception as e:
            print(f"Error clearing dialogues for user {user_id}, session {session_id}: {e}")
            return 0


# 创建全局会话管理器实例
session_manager = SessionManager() 