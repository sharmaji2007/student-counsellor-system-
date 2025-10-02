from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user, get_counselor_user
from app.core.config import settings
from app.models import User, ChatMessage, SOSIncident
from app.schemas import (
    ChatMessage as ChatMessageSchema,
    ChatMessageCreate,
    SOSIncident as SOSIncidentSchema
)
from app.services.notification_service import NotificationService
from app.services.safety_service import SafetyService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
notification_service = NotificationService()
safety_service = SafetyService()

@router.get("/messages", response_model=List[ChatMessageSchema])
async def get_chat_messages(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get chat messages for current user"""
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access private chat"
        )
    
    # Get messages that haven't expired
    now = datetime.utcnow()
    result = await db.execute(
        select(ChatMessage)
        .where(
            and_(
                ChatMessage.user_id == current_user.id,
                ChatMessage.expires_at > now
            )
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    
    messages = result.scalars().all()
    return messages

@router.post("/messages", response_model=ChatMessageSchema)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def send_chat_message(
    request,
    message_data: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a chat message"""
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can send chat messages"
        )
    
    # Calculate expiry date
    expires_at = datetime.utcnow() + timedelta(days=settings.CHAT_RETENTION_DAYS)
    
    # Create message
    db_message = ChatMessage(
        user_id=current_user.id,
        message=message_data.message,
        is_private=message_data.is_private,
        expires_at=expires_at
    )
    
    # Check for safety keywords
    flagged_keywords = safety_service.check_sos_keywords(message_data.message)
    if flagged_keywords:
        db_message.flagged_for_sos = True
        
        # Create SOS incident
        sos_incident = SOSIncident(
            student_id=current_user.id,
            message_id=None,  # Will be set after message is saved
            trigger_keywords=flagged_keywords,
            status="open"
        )
        
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        
        # Update SOS incident with message ID
        sos_incident.message_id = db_message.id
        db.add(sos_incident)
        await db.commit()
        
        # Send notifications
        await notification_service.send_sos_alert(
            student_id=current_user.id,
            student_name=current_user.full_name,
            message=message_data.message,
            keywords=flagged_keywords
        )
        
    else:
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
    
    return db_message

@router.get("/public-messages", response_model=List[ChatMessageSchema])
async def get_public_chat_messages(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_counselor_user)
):
    """Get public chat messages (counselors and admins only)"""
    now = datetime.utcnow()
    result = await db.execute(
        select(ChatMessage)
        .where(
            and_(
                ChatMessage.is_private == False,
                ChatMessage.expires_at > now
            )
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    
    messages = result.scalars().all()
    return messages

@router.get("/sos-incidents", response_model=List[SOSIncidentSchema])
async def get_sos_incidents(
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_counselor_user)
):
    """Get SOS incidents (counselors and admins only)"""
    query = select(SOSIncident)
    
    if status_filter:
        query = query.where(SOSIncident.status == status_filter)
    
    result = await db.execute(
        query.order_by(SOSIncident.created_at.desc())
    )
    
    incidents = result.scalars().all()
    return incidents

@router.put("/sos-incidents/{incident_id}/resolve")
async def resolve_sos_incident(
    incident_id: int,
    notes: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_counselor_user)
):
    """Resolve an SOS incident"""
    result = await db.execute(
        select(SOSIncident).where(SOSIncident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOS incident not found"
        )
    
    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()
    if notes:
        incident.notes = notes
    
    await db.commit()
    
    return {"message": "SOS incident resolved successfully"}

@router.delete("/cleanup-expired")
async def cleanup_expired_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_counselor_user)
):
    """Cleanup expired chat messages (counselors and admins only)"""
    now = datetime.utcnow()
    
    # Delete expired messages that are not flagged for SOS
    result = await db.execute(
        select(ChatMessage).where(
            and_(
                ChatMessage.expires_at <= now,
                ChatMessage.flagged_for_sos == False
            )
        )
    )
    
    expired_messages = result.scalars().all()
    count = len(expired_messages)
    
    for message in expired_messages:
        await db.delete(message)
    
    await db.commit()
    
    return {"message": f"Cleaned up {count} expired messages"}