"""Memory router for AI personalization and user context management."""

from typing import Any, List, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.memory import UserMemory, Embedding, Conversation
from app.services.memory_service import MemoryService
from app.routers.auth import get_current_user, get_optional_current_user

router = APIRouter()


@router.post("/store", response_model=dict)
async def store_memory(
    content: str,
    memory_type: str = "general",
    metadata: Dict[str, Any] = None,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Store a new memory for the user."""
    try:
        memory_service = MemoryService()
        success = memory_service.store_memory(
            user_id=current_user.id,
            content=content,
            memory_type=memory_type,
            metadata=metadata
        )
        
        if success:
            # Also store in database for backup
            db_memory = UserMemory(
                user_id=current_user.id,
                memory_type=memory_type,
                key=f"{memory_type}_{datetime.utcnow().timestamp()}",
                value=content,
                metadata=metadata
            )
            db.add(db_memory)
            db.commit()
            
            return {"message": "Memory stored successfully", "memory_id": db_memory.id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store memory"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing memory: {str(e)}"
        )


@router.get("/search", response_model=List[dict])
async def search_memories(
    query: str,
    memory_type: str = None,
    top_k: int = 5,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Search memories using semantic similarity."""
    try:
        memory_service = MemoryService()
        results = memory_service.search_memories(
            user_id=current_user.id,
            query=query,
            memory_type=memory_type,
            top_k=top_k
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching memories: {str(e)}"
        )


@router.get("/context/{context_type}", response_model=dict)
async def get_user_context(
    context_type: str = "general",
    max_memories: int = 10,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user context for AI personalization."""
    try:
        memory_service = MemoryService()
        context = memory_service.get_user_context(
            user_id=current_user.id,
            context_type=context_type,
            max_memories=max_memories
        )
        
        return context
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user context: {str(e)}"
        )


@router.put("/preferences", response_model=dict)
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user preferences in memory."""
    try:
        memory_service = MemoryService()
        success = memory_service.update_user_preferences(
            user_id=current_user.id,
            preferences=preferences
        )
        
        if success:
            return {"message": "User preferences updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating preferences: {str(e)}"
        )


@router.get("/suggestions/{suggestion_type}", response_model=List[dict])
async def get_personalized_suggestions(
    suggestion_type: str = "general",
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get personalized suggestions based on user memory."""
    try:
        memory_service = MemoryService()
        suggestions = memory_service.get_personalized_suggestions(
            user_id=current_user.id,
            suggestion_type=suggestion_type
        )
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting suggestions: {str(e)}"
        )


@router.post("/conversation", response_model=dict)
async def store_conversation(
    session_id: str,
    message_type: str,
    content: str,
    metadata: Dict[str, Any] = None,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Store a conversation message."""
    db_conversation = Conversation(
        user_id=current_user.id,
        session_id=session_id,
        message_type=message_type,
        content=content,
        metadata=metadata
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    
    return {"message": "Conversation stored successfully", "conversation_id": db_conversation.id}


@router.get("/conversations/{session_id}", response_model=List[dict])
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get conversation history for a session."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at).all()
    
    return [
        {
            "id": conv.id,
            "message_type": conv.message_type,
            "content": conv.content,
            "metadata": conv.metadata,
            "created_at": conv.created_at
        }
        for conv in conversations
    ]


@router.get("/memories", response_model=List[dict])
async def get_user_memories(
    memory_type: str = None,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all memories for the current user."""
    query = db.query(UserMemory).filter(UserMemory.user_id == current_user.id)
    
    if memory_type:
        query = query.filter(UserMemory.memory_type == memory_type)
    
    memories = query.order_by(UserMemory.created_at.desc()).all()
    
    return [
        {
            "id": memory.id,
            "memory_type": memory.memory_type,
            "key": memory.key,
            "value": memory.value,
            "metadata": memory.metadata,
            "importance_score": memory.importance_score,
            "last_accessed": memory.last_accessed,
            "access_count": memory.access_count,
            "created_at": memory.created_at
        }
        for memory in memories
    ]


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a specific memory."""
    memory = db.query(UserMemory).filter(
        UserMemory.id == memory_id,
        UserMemory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    
    db.delete(memory)
    db.commit()
    
    return {"message": "Memory deleted successfully"}


@router.get("/status")
async def get_memory_service_status(
    current_user: User = Depends(get_optional_current_user)
) -> Any:
    """Get memory service status."""
    try:
        memory_service = MemoryService()
        status = memory_service.get_status()
        
        return {
            "service_status": "operational",
            "memory_service": status,
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "service_status": "error",
            "error": str(e),
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
