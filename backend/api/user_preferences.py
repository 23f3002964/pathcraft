from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import datetime
from datetime import date

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

# User Preferences Endpoints
@router.post("/preferences/", response_model=schemas.UserPreference)
def create_user_preference(preference: schemas.UserPreferenceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Create a new user preference."""
    if preference.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only create preferences for yourself")
    
    # Check if preference already exists
    existing = db.query(models.UserPreference).filter(
        models.UserPreference.user_id == current_user.id,
        models.UserPreference.preference_key == preference.preference_key
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Preference already exists for this key")
    
    db_preference = models.UserPreference(**preference.dict(), id=str(uuid.uuid4()))
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.get("/preferences/", response_model=List[schemas.UserPreference])
def get_user_preferences(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all preferences for the current user."""
    preferences = db.query(models.UserPreference).filter(
        models.UserPreference.user_id == current_user.id
    ).all()
    return preferences

@router.get("/preferences/{preference_key}", response_model=schemas.UserPreference)
def get_user_preference(preference_key: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get a specific preference by key."""
    preference = db.query(models.UserPreference).filter(
        models.UserPreference.user_id == current_user.id,
        models.UserPreference.preference_key == preference_key
    ).first()
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return preference

@router.put("/preferences/{preference_key}", response_model=schemas.UserPreference)
def update_user_preference(preference_key: str, preference_update: schemas.UserPreferenceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update a user preference."""
    if preference_update.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own preferences")
    
    db_preference = db.query(models.UserPreference).filter(
        models.UserPreference.user_id == current_user.id,
        models.UserPreference.preference_key == preference_key
    ).first()
    if not db_preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    for key, value in preference_update.dict().items():
        setattr(db_preference, key, value)
    
    db_preference.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.delete("/preferences/{preference_key}")
def delete_user_preference(preference_key: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Delete a user preference."""
    db_preference = db.query(models.UserPreference).filter(
        models.UserPreference.user_id == current_user.id,
        models.UserPreference.preference_key == preference_key
    ).first()
    if not db_preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    db.delete(db_preference)
    db.commit()
    return {"message": "Preference deleted successfully"}

# User Analytics Endpoints
@router.post("/analytics/", response_model=schemas.UserAnalytics)
def create_user_analytics(analytics: schemas.UserAnalyticsCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Create a new analytics entry for the current user."""
    if analytics.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only create analytics for yourself")
    
    # Check if analytics already exists for this date
    existing = db.query(models.UserAnalytics).filter(
        models.UserAnalytics.user_id == current_user.id,
        models.UserAnalytics.date == analytics.date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Analytics already exists for this date")
    
    db_analytics = models.UserAnalytics(**analytics.dict(), id=str(uuid.uuid4()))
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

@router.get("/analytics/", response_model=List[schemas.UserAnalytics])
def get_user_analytics(start_date: date = None, end_date: date = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get analytics for the current user with optional date range."""
    query = db.query(models.UserAnalytics).filter(models.UserAnalytics.user_id == current_user.id)
    
    if start_date:
        query = query.filter(models.UserAnalytics.date >= start_date)
    if end_date:
        query = query.filter(models.UserAnalytics.date <= end_date)
    
    analytics = query.order_by(models.UserAnalytics.date.desc()).all()
    return analytics

@router.get("/analytics/{analytics_date}", response_model=schemas.UserAnalytics)
def get_user_analytics_by_date(analytics_date: date, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get analytics for a specific date."""
    analytics = db.query(models.UserAnalytics).filter(
        models.UserAnalytics.user_id == current_user.id,
        models.UserAnalytics.date == analytics_date
    ).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found for this date")
    return analytics

@router.put("/analytics/{analytics_date}", response_model=schemas.UserAnalytics)
def update_user_analytics(analytics_date: date, analytics_update: schemas.UserAnalyticsCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update analytics for a specific date."""
    if analytics_update.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own analytics")
    
    db_analytics = db.query(models.UserAnalytics).filter(
        models.UserAnalytics.user_id == current_user.id,
        models.UserAnalytics.date == analytics_date
    ).first()
    if not db_analytics:
        raise HTTPException(status_code=404, detail="Analytics not found for this date")
    
    for key, value in analytics_update.dict().items():
        setattr(db_analytics, key, value)
    
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

@router.get("/analytics/summary/")
def get_analytics_summary(days: int = 30, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get analytics summary for the last N days."""
    end_date = date.today()
    start_date = end_date - datetime.timedelta(days=days)
    
    analytics = db.query(models.UserAnalytics).filter(
        models.UserAnalytics.user_id == current_user.id,
        models.UserAnalytics.date >= start_date,
        models.UserAnalytics.date <= end_date
    ).all()
    
    if not analytics:
        return {
            "total_tasks_completed": 0,
            "total_goals_achieved": 0,
            "average_productivity_score": 0.0,
            "total_focus_time_minutes": 0,
            "days_with_data": 0
        }
    
    total_tasks = sum(a.tasks_completed for a in analytics)
    total_goals = sum(a.goals_achieved for a in analytics)
    avg_productivity = sum(a.productivity_score for a in analytics) / len(analytics)
    total_focus_time = sum(a.focus_time_minutes for a in analytics)
    
    return {
        "total_tasks_completed": total_tasks,
        "total_goals_achieved": total_goals,
        "average_productivity_score": round(avg_productivity, 2),
        "total_focus_time_minutes": total_focus_time,
        "days_with_data": len(analytics)
    }
