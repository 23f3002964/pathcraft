from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

# Learning Platform Endpoints
@router.post("/learning-platforms/", response_model=schemas.LearningPlatform)
def create_learning_platform(platform: schemas.LearningPlatformCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Create a new learning platform integration."""
    if platform.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only create platforms for yourself")
    
    # Check if platform already exists for this user and platform name
    existing = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.user_id == current_user.id,
        models.LearningPlatform.platform_name == platform.platform_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Platform integration already exists")
    
    db_platform = models.LearningPlatform(**platform.dict(), id=str(uuid.uuid4()))
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform

@router.get("/learning-platforms/", response_model=List[schemas.LearningPlatform])
def get_learning_platforms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all learning platforms for the current user."""
    platforms = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.user_id == current_user.id
    ).all()
    return platforms

@router.get("/learning-platforms/{platform_id}", response_model=schemas.LearningPlatform)
def get_learning_platform(platform_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get a specific learning platform by ID."""
    platform = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.id == platform_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Learning platform not found")
    return platform

@router.put("/learning-platforms/{platform_id}", response_model=schemas.LearningPlatform)
def update_learning_platform(platform_id: str, platform_update: schemas.LearningPlatformCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update a learning platform integration."""
    if platform_update.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own platforms")
    
    db_platform = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.id == platform_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not db_platform:
        raise HTTPException(status_code=404, detail="Learning platform not found")
    
    for key, value in platform_update.dict().items():
        setattr(db_platform, key, value)
    
    db.commit()
    db.refresh(db_platform)
    return db_platform

@router.delete("/learning-platforms/{platform_id}")
def delete_learning_platform(platform_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Delete a learning platform integration."""
    db_platform = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.id == platform_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not db_platform:
        raise HTTPException(status_code=404, detail="Learning platform not found")
    
    db.delete(db_platform)
    db.commit()
    return {"message": "Learning platform deleted successfully"}

# Learning Course Endpoints
@router.post("/learning-platforms/{platform_id}/courses/", response_model=schemas.LearningCourse)
def create_learning_course(platform_id: str, course: schemas.LearningCourseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Create a new learning course."""
    # Verify platform ownership
    platform = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.id == platform_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Learning platform not found")
    
    if course.platform_id != platform_id:
        raise HTTPException(status_code=400, detail="Platform ID mismatch")
    
    # Check if course already exists
    existing = db.query(models.LearningCourse).filter(
        models.LearningCourse.platform_id == platform_id,
        models.LearningCourse.course_id == course.course_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Course already exists")
    
    db_course = models.LearningCourse(**course.dict(), id=str(uuid.uuid4()))
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/learning-platforms/{platform_id}/courses/", response_model=List[schemas.LearningCourse])
def get_learning_courses(platform_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all courses for a learning platform."""
    # Verify platform ownership
    platform = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.id == platform_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Learning platform not found")
    
    courses = db.query(models.LearningCourse).filter(
        models.LearningCourse.platform_id == platform_id
    ).all()
    return courses

@router.get("/learning-courses/{course_id}", response_model=schemas.LearningCourse)
def get_learning_course(course_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get a specific learning course by ID."""
    course = db.query(models.LearningCourse).join(models.LearningPlatform).filter(
        models.LearningCourse.id == course_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Learning course not found")
    return course

@router.put("/learning-courses/{course_id}", response_model=schemas.LearningCourse)
def update_learning_course(course_id: str, course_update: schemas.LearningCourseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update a learning course."""
    # Verify course ownership
    course = db.query(models.LearningCourse).join(models.LearningPlatform).filter(
        models.LearningCourse.id == course_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Learning course not found")
    
    for key, value in course_update.dict().items():
        setattr(course, key, value)
    
    # Update completion date if status changed to completed
    if course_update.status == "completed" and course.status != "completed":
        course.completion_date = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/learning-courses/{course_id}")
def delete_learning_course(course_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Delete a learning course."""
    course = db.query(models.LearningCourse).join(models.LearningPlatform).filter(
        models.LearningCourse.id == course_id,
        models.LearningPlatform.user_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Learning course not found")
    
    db.delete(course)
    db.commit()
    return {"message": "Learning course deleted successfully"}

@router.get("/learning-courses/summary/")
def get_learning_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get learning summary for the current user."""
    platforms = db.query(models.LearningPlatform).filter(
        models.LearningPlatform.user_id == current_user.id,
        models.LearningPlatform.is_active == True
    ).all()
    
    total_courses = 0
    completed_courses = 0
    in_progress_courses = 0
    total_progress = 0.0
    
    for platform in platforms:
        courses = db.query(models.LearningCourse).filter(
            models.LearningCourse.platform_id == platform.id
        ).all()
        
        total_courses += len(courses)
        for course in courses:
            if course.status == "completed":
                completed_courses += 1
            elif course.status == "in_progress":
                in_progress_courses += 1
            total_progress += course.progress_percentage
    
    avg_progress = total_progress / total_courses if total_courses > 0 else 0.0
    
    return {
        "total_platforms": len(platforms),
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "average_progress_percentage": round(avg_progress, 2)
    }
