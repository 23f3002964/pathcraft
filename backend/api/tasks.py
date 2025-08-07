from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

@router.put("/tasks/{task_id}/reschedule", response_model=schemas.Task)
def reschedule_task(task_id: str, reschedule: schemas.RescheduleTask, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the user is authorized to reschedule the task
    if db_task.parent_sub_goal.parent_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reschedule this task")

    db_task.planned_start = reschedule.planned_start
    db_task.planned_end = reschedule.planned_end
    db.commit()
    db.refresh(db_task)
    return db_task