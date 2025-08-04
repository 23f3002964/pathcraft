
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

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
    today = datetime.date.today()
    
    # Helper to check if a task for a given recurring_task_id and date already exists
    def _task_exists(recurring_task_id, task_date):
        return db.query(models.Task).filter(
            models.Task.recurring_task_id == recurring_task_id,
            models.Task.generated_date == task_date
        ).first() is not None

    if db_recurring_task.recurrence_type == 'daily':
        for i in range(7): # Generate for next 7 days
            task_date = today + datetime.timedelta(days=i)
            if not _task_exists(db_recurring_task.id, task_date): # Prevent duplicates
                new_task = models.Task(
                    id=str(uuid.uuid4()),
                    recurring_task_id=db_recurring_task.id,
                    generated_date=task_date,
                    sub_goal_id=None, # Recurring tasks might not have a sub_goal_id initially
                    planned_start=datetime.datetime.combine(task_date, datetime.time(9, 0)),
                    planned_end=datetime.datetime.combine(task_date, datetime.time(10, 0)),
                    status='todo',
                    priority=0,
                    dependencies=None
                )
                db.add(new_task)
                generated_tasks.append(new_task)
    elif db_recurring_task.recurrence_type == 'weekly':
        # recurrence_value: 0=Monday, 1=Tuesday, ..., 6=Sunday
        for i in range(7): # Check next 7 days
            task_date = today + datetime.timedelta(days=i)
            if task_date.weekday() == db_recurring_task.recurrence_value:
                if not _task_exists(db_recurring_task.id, task_date): # Prevent duplicates
                    new_task = models.Task(
                        id=str(uuid.uuid4()),
                        recurring_task_id=db_recurring_task.id,
                        generated_date=task_date,
                        sub_goal_id=None,
                        planned_start=datetime.datetime.combine(task_date, datetime.time(9, 0)),
                        planned_end=datetime.datetime.combine(task_date, datetime.time(10, 0)),
                        status='todo',
                        priority=0,
                        dependencies=None
                    )
                    db.add(new_task)
                    generated_tasks.append(new_task)
    elif db_recurring_task.recurrence_type == 'monthly':
        # recurrence_value: day of the month (1-31)
        # Generate for next 3 months
        for i in range(3):
            target_month = today.month + i
            target_year = today.year
            if target_month > 12:
                target_month -= 12
                target_year += 1
            
            try:
                task_date = datetime.date(target_year, target_month, db_recurring_task.recurrence_value)
                if task_date >= today: # Only generate for future dates
                    if not _task_exists(db_recurring_task.id, task_date): # Prevent duplicates
                        new_task = models.Task(
                            id=str(uuid.uuid4()),
                            recurring_task_id=db_recurring_task.id,
                            generated_date=task_date,
                            sub_goal_id=None,
                            planned_start=datetime.datetime.combine(task_date, datetime.time(9, 0)),
                            planned_end=datetime.datetime.combine(task_date, datetime.time(10, 0)),
                            status='todo',
                            priority=0,
                            dependencies=None
                        )
                        db.add(new_task)
                        generated_tasks.append(new_task)
            except ValueError: # Day of month might not exist for all months
                pass
    
    db.commit()
    for task in generated_tasks:
        db.refresh(task)

    return generated_tasks
