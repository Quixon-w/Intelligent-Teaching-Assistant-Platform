from fastapi import APIRouter, status, HTTPException
from typing import List, Dict, Any

from utils.session_manager import session_manager

router = APIRouter()


@router.delete("/v1/users/{user_id}/sessions/{session_id}/dialogues", tags=["Session Management"])
async def clear_session_dialogues(user_id: str, session_id: str, is_teacher: bool = False):
    """清除指定会话的所有对话历史"""
    try:
        deleted_count = session_manager.clear_session_dialogues(user_id, session_id, is_teacher)
        
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} dialogue files"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing dialogues: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions/{session_id}/context", tags=["Session Management"])
async def get_session_context(user_id: str, session_id: str, max_messages: int = 10, is_teacher: bool = False):
    """获取指定会话的上下文消息"""
    try:
        context_messages = session_manager.get_context_messages(user_id, session_id, max_messages=max_messages, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "context_messages": context_messages,
            "message_count": len(context_messages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving context: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions", tags=["Session Management"])
async def get_user_sessions(user_id: str, is_teacher: bool = False):
    """获取用户的所有会话ID"""
    try:
        sessions = session_manager.get_user_sessions(user_id, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "is_teacher": is_teacher,
            "sessions": sessions,
            "session_count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user sessions: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions/{session_id}/dialogues", tags=["Session Management"])
async def get_session_dialogues(user_id: str, session_id: str, limit: int = 10, is_teacher: bool = False):
    """获取指定会话的对话历史"""
    try:
        dialogues = session_manager.get_session_dialogues(user_id, session_id, limit=limit, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "dialogues": dialogues,
            "count": len(dialogues)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dialogues: {str(e)}"
        )


@router.post("/v1/users/{user_id}/sessions/{session_id}/save", tags=["Session Management"])
async def save_session_history(user_id: str, session_id: str, messages: List[Dict[str, Any]], is_teacher: bool = False):
    """保存当前会话的完整历史记录"""
    try:
        success = session_manager.save_session_history(user_id, session_id, messages, is_teacher=is_teacher)
        if success:
            return {
                "user_id": user_id,
                "session_id": session_id,
                "is_teacher": is_teacher,
                "message": "Session history saved successfully",
                "message_count": len(messages)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save session history"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving session history: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions/{session_id}/load", tags=["Session Management"])
async def load_session_history(user_id: str, session_id: str, is_teacher: bool = False):
    """加载指定会话的历史记录"""
    try:
        messages = session_manager.load_session_history(user_id, session_id, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "messages": messages,
            "message_count": len(messages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading session history: {str(e)}"
        ) 