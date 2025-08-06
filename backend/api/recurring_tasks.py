from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime
from dateutil.rrule import rrulestr

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

@router.post("/recurring_tasks/", response_model=schemas.RecurringTask)
def create_recurring_task(recurring_task: schemas.RecurringTaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if recurring_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create recurring task for this user")
    db_recurring_task = models.RecurringTask(**recurring_task.dict(), id=str(uuid.uuid4()))
    db.add(db_recurring_task)
    db.commit()
    db.refresh(db_recurring_task)
    return db_recurring_task

@router.get("/recurring_tasks/me", response_model=List[schemas.RecurringTask])
def get_my_recurring_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    recurring_tasks = db.query(models.RecurringTask).filter(models.RecurringTask.user_id == current_user.id).all()
    return recurring_tasks

@router.post("/recurring_tasks/{recurring_task_id}/generate_tasks", response_model=List[schemas.Task])
def generate_tasks_from_recurring(recurring_task_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_recurring_task = db.query(models.RecurringTask).filter(models.RecurringTask.id == recurring_task_id).first()
    if db_recurring_task is None:
        raise HTTPException(status_code=404, detail="Recurring task not found")
    if db_recurring_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to generate tasks for this recurring task")

    generated_tasks = []
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Define a reasonable end date for generation (e.g., next 30 days)
    generation_end_date = today + timedelta(days=30)

    # Helper to check if a task for a given recurring_task_id and date already exists
    def _task_exists(recurring_task_id, task_date):
        return db.query(models.Task).filter(
            models.Task.recurring_task_id == recurring_task_id,
            models.Task.generated_date == task_date.date() # Compare only date part
        ).first() is not None

    try:
        # Parse the RRULE string
        # rrule expects a dtstart, so we use the recurring task's start_date
        # We also limit the generation to a reasonable number of occurrences
        rule = rrulestr(db_recurring_task.rrule, dtstart=db_recurring_task.start_date)
        
        # Generate occurrences within the desired range
        for dt in rule.between(today, generation_end_date, inc=True):
            task_date = dt.replace(hour=9, minute=0, second=0, microsecond=0) # Default start time
            
            if not _task_exists(db_recurring_task.id, task_date): # Prevent duplicates
                new_task = models.Task(
                    id=str(uuid.uuid4()),
                    recurring_task_id=db_recurring_task.id,
                    generated_date=task_date.date(), # Store only date part
                    sub_goal_id=None, # Recurring tasks might not have a sub_goal_id initially
                    planned_start=task_date,
                    planned_end=task_date + timedelta(hours=1), # Default 1 hour duration
                    status='todo',
                    priority=0,
                    dependencies=None
                )
                db.add(new_task)
                generated_tasks.append(new_task)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid RRULE: {e}")
    
    db.commit()
    for task in generated_tasks:
        db.refresh(task)

    return generated_tasks