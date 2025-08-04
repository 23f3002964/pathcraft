from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models import models, schemas
from ..database import get_db
from ..core.decomposition import decompose_goal_ml_enhanced # Import the new service
from ..core.auth import get_current_user

router = APIRouter()

# Create a new goal
@router.post("/goals/", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goal_data = goal.dict()
    goal_data["owner_id"] = current_user.id
    db_goal = models.Goal(**goal_data, id=str(uuid.uuid4()))
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

# Decompose a goal and create sub-goals
@router.post("/goals/{goal_id}/decompose/", response_model=List[schemas.SubGoal])
def decompose_goal_endpoint(goal_id: str, context: str = None, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    sub_goal_descriptions = decompose_goal_ml_enhanced(db_goal.title, context=context)
    created_sub_goals = []
    for desc in sub_goal_descriptions:
        sub_goal = models.SubGoal(
            id=str(uuid.uuid4()),
            parent_goal_id=goal_id,
            description=desc,
            estimated_effort_minutes=60 # Placeholder value
        )
        db.add(sub_goal)
        created_sub_goals.append(sub_goal)
    
    db.commit()
    for sub_goal in created_sub_goals:
        db.refresh(sub_goal)

    return created_sub_goals

# Get all goals
@router.get("/goals/", response_model=List[schemas.Goal])
def read_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    goals = db.query(models.Goal).offset(skip).limit(limit).all()
    return goals

# Get a specific goal by ID
@router.get("/goals/{goal_id}", response_model=schemas.Goal)
def read_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal

# Update a goal
@router.put("/goals/{goal_id}", response_model=schemas.Goal)
def update_goal(goal_id: str, goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    for key, value in goal.dict().items():
        setattr(db_goal, key, value)
    db.commit()
    db.refresh(db_goal)
    return db_goal

# Delete a goal
@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(db_goal)
    db.commit()
    return {"message": "Goal deleted successfully"}