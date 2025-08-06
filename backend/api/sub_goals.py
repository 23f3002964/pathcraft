from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models import models, schemas
from ..database import get_db
from ..core.scheduling import schedule_tasks # Import the new service
from ..core.auth import get_current_user # Import get_current_user
from ..core.calendar_sync import sync_calendar_events # Import calendar sync

router = APIRouter()

# Create a new sub-goal
@router.post("/sub_goals/", response_model=schemas.SubGoal)
def create_sub_goal(sub_goal: schemas.SubGoalCreate, db: Session = Depends(get_db)):
    db_sub_goal = models.SubGoal(**sub_goal.dict(), id=str(uuid.uuid4()))
    db.add(db_sub_goal)
    db.commit()
    db.refresh(db_sub_goal)
    return db_sub_goal

# Schedule all tasks for a sub-goal
@router.post("/sub_goals/{sub_goal_id}/schedule/", response_model=List[schemas.Task])
def schedule_sub_goal_tasks(sub_goal_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == sub_goal_id).first()
    if db_sub_goal is None:
        raise HTTPException(status_code=404, detail="Sub-goal not found")

    # Fetch user's calendar integrations and sync events
    calendar_integrations = db.query(models.CalendarIntegration).filter(models.CalendarIntegration.user_id == current_user.id).all()
    all_calendar_events = []
    for integration in calendar_integrations:
        events = sync_calendar_events(current_user.id, integration.provider, integration.access_token)
        all_calendar_events.extend(events)

    # Fetch user's calendar integrations and sync events
    calendar_integrations = db.query(models.CalendarIntegration).filter(models.CalendarIntegration.user_id == current_user.id).all()
    all_calendar_events = []
    for integration in calendar_integrations:
        events = sync_calendar_events(current_user.id, integration.provider, integration.access_token)
        all_calendar_events.extend(events)

    tasks_to_schedule = db_sub_goal.tasks
    scheduled_tasks = schedule_tasks(
        tasks_to_schedule,
        db,
        user_daily_start_hour=current_user.daily_start_hour,
        user_daily_end_hour=current_user.daily_end_hour,
        existing_calendar_events=all_calendar_events
    )

    for task in scheduled_tasks:
        db.add(task)
    
    db.commit()
    for task in scheduled_tasks:
        db.refresh(task)

    return scheduled_tasks

# Get all sub-goals for a specific goal
@router.get("/goals/{goal_id}/sub_goals/", response_model=List[schemas.SubGoal])
def read_sub_goals(goal_id: str, db: Session = Depends(get_db)):
    sub_goals = db.query(models.SubGoal).filter(models.SubGoal.parent_goal_id == goal_id).all()
    return sub_goals

# Get a specific sub-goal by ID
@router.get("/sub_goals/{sub_goal_id}", response_model=schemas.SubGoal)
def read_sub_goal(sub_goal_id: str, db: Session = Depends(get_db)):
    db_sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == sub_goal_id).first()
    if db_sub_goal is None:
        raise HTTPException(status_code=404, detail="Sub-goal not found")
    return db_sub_goal

# Update a sub-goal
@router.put("/sub_goals/{sub_goal_id}", response_model=schemas.SubGoal)
def update_sub_goal(sub_goal_id: str, sub_goal: schemas.SubGoalCreate, db: Session = Depends(get_db)):
    db_sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == sub_goal_id).first()
    if db_sub_goal is None:
        raise HTTPException(status_code=404, detail="Sub-goal not found")
    for key, value in sub_goal.dict().items():
        setattr(db_sub_goal, key, value)
    db.commit()
    db.refresh(db_sub_goal)
    return db_sub_goal

# Delete a sub-goal
@router.delete("/sub_goals/{sub_goal_id}")
def delete_sub_goal(sub_goal_id: str, db: Session = Depends(get_db)):
    db_sub_goal = db.query(models.SubGoal).filter(models.SubGoal.id == sub_goal_id).first()
    if db_sub_goal is None:
        raise HTTPException(status_code=404, detail="Sub-goal not found")
    db.delete(db_sub_goal)
    db.commit()
    return {"message": "Sub-goal deleted successfully"}