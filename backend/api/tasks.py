from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

# Create a new task
@router.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Validate sub-goal if provided
    if task.sub_goal_id:
        sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == task.sub_goal_id).first()
        if sub_goal is None:
            raise HTTPException(status_code=404, detail="Sub-goal not found")
        # Ensure ownership
        if sub_goal.parent_goal.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create task for this sub-goal")

    db_task = models.Task(**task.dict(), id=str(uuid.uuid4()))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Get all tasks for a sub-goal
@router.get("/sub_goals/{sub_goal_id}/tasks/", response_model=List[schemas.Task])
def read_tasks_for_sub_goal(sub_goal_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == sub_goal_id).first()
    if sub_goal is None:
        raise HTTPException(status_code=404, detail="Sub-goal not found")
    if sub_goal.parent_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view tasks for this sub-goal")
    return sub_goal.tasks

# Get a specific task by ID
@router.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.parent_sub_goal and db_task.parent_sub_goal.parent_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return db_task

# Update an existing task
@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: str, task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Authorization: user must own the parent goal of the sub-goal (if present)
    if db_task.parent_sub_goal and db_task.parent_sub_goal.parent_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    # If sub_goal_id is changing, validate new sub-goal and ownership
    if task.sub_goal_id and task.sub_goal_id != db_task.sub_goal_id:
        new_sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == task.sub_goal_id).first()
        if new_sub_goal is None:
            raise HTTPException(status_code=404, detail="Sub-goal not found")
        if new_sub_goal.parent_goal.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to move task to this sub-goal")

    # Track previous status before applying updates
    previous_status = db_task.status
    for key, value in task.dict().items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    # Generate a notification if the task has been completed
    if previous_status != 'done' and db_task.status == 'done':
        completion_notification = models.Notification(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            task_id=db_task.id,
            message=f"Task completed: {db_task.id}",
            notification_time=datetime.datetime.now(),
            method="push",
            is_sent=False,
        )
        db.add(completion_notification)
        db.commit()

    return db_task

# Delete a task
@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.parent_sub_goal and db_task.parent_sub_goal.parent_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

# Specialized reschedule endpoint
@router.put("/tasks/{task_id}/reschedule", response_model=schemas.Task)
def reschedule_task(task_id: str, reschedule: schemas.RescheduleTask, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if the user is authorized to reschedule the task
    if db_task.parent_sub_goal and db_task.parent_sub_goal.parent_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reschedule this task")

    db_task.planned_start = reschedule.planned_start
    db_task.planned_end = reschedule.planned_end
    db.commit()
    db.refresh(db_task)
    return db_task