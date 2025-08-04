
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

@router.post("/calendar_integrations/", response_model=schemas.CalendarIntegration)
def create_calendar_integration(integration: schemas.CalendarIntegrationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if integration.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create integration for this user")
    db_integration = models.CalendarIntegration(**integration.dict(), id=str(uuid.uuid4()))
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    return db_integration

@router.get("/calendar_integrations/me", response_model=List[schemas.CalendarIntegration])
def get_my_calendar_integrations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    integrations = db.query(models.CalendarIntegration).filter(models.CalendarIntegration.user_id == current_user.id).all()
    return integrations

@router.delete("/calendar_integrations/{integration_id}")
def delete_calendar_integration(integration_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_integration = db.query(models.CalendarIntegration).filter(models.CalendarIntegration.id == integration_id).first()
    if db_integration is None:
        raise HTTPException(status_code=404, detail="Calendar integration not found")
    if db_integration.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this integration")
    
    db.delete(db_integration)
    db.commit()
    return {"message": "Calendar integration deleted successfully"}
