
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user
from ..core.websocket_manager import manager
from ..ml.reminder_optimizer import get_reminder_frequency

router = APIRouter()

@router.post("/notifications/", response_model=schemas.Notification)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create notification for this user")
    
    # If a task is provided, adjust the notification_time relative to task start
    if notification.task_id:
        reminder_frequency = get_reminder_frequency(notification.task_id)
        task = db.query(models.Task).filter(models.Task.id == notification.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        notification.notification_time = task.planned_start - reminder_frequency

    db_notification = models.Notification(**notification.dict(), id=str(uuid.uuid4()))
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/notifications/me", response_model=List[schemas.Notification])
def get_my_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    notifications = db.query(models.Notification).filter(models.Notification.user_id == current_user.id).all()
    return notifications

@router.put("/notifications/{notification_id}/mark_sent", response_model=schemas.Notification)
async def mark_notification_sent(notification_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this notification")
    
    db_notification.is_sent = True
    db.commit()
    db.refresh(db_notification)
    
    # Send real-time notification
    await manager.send_personal_message(f"Notification sent: {db_notification.message}", current_user.id)

    return db_notification
