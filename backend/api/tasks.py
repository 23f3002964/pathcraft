from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user
from ..core.websocket_manager import manager # Import the WebSocket manager

router = APIRouter()

# Create a new task
@router.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict(), id=str(uuid.uuid4()))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Get all tasks for a specific sub-goal
@router.get("/sub_goals/{sub_goal_id}/tasks/", response_model=List[schemas.Task])
def read_tasks(sub_goal_id: str, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter(models.Task.sub_goal_id == sub_goal_id).all()
    return tasks

# Get a specific task by ID
@router.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

# Update a task
@router.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(task_id: str, task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if status is changing to 'done'
    if db_task.status != 'done' and task.status == 'done':
        # Create a notification
        notification_message = f"Task \"{db_task.id}\" marked as done!"
        new_notification = models.Notification(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            task_id=db_task.id,
            message=notification_message,
            notification_time=datetime.datetime.now(),
            method="system" # Or 'push', 'email' etc.
        )
        db.add(new_notification)
        db.flush() # Flush to get ID for refresh
        db.refresh(new_notification)

        # Send real-time notification
            # Send real-time notification
        await manager.send_personal_message(notification_message, current_user.id) # Send to specific user

    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

# Delete a task
@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}