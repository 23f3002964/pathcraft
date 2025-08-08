from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

@router.post("/teams/{team_id}/okrs/", response_model=schemas.TeamOKR)
def create_team_okr(team_id: str, okr: schemas.TeamOKRCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Create a new OKR for a team."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Check if user is admin or owner
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != current_user.id and team_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can create OKRs")
    
    # Create the OKR
    db_okr = models.TeamOKR(**okr.dict(exclude={'key_results'}), id=str(uuid.uuid4()))
    db.add(db_okr)
    db.commit()
    db.refresh(db_okr)
    
    # Create key results if provided
    if okr.key_results:
        for kr_data in okr.key_results:
            db_kr = models.TeamOKRKeyResult(**kr_data.dict(), id=str(uuid.uuid4()), okr_id=db_okr.id)
            db.add(db_kr)
        db.commit()
        db.refresh(db_okr)
    
    return db_okr

@router.get("/teams/{team_id}/okrs/", response_model=List[schemas.TeamOKR])
def get_team_okrs(team_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all OKRs for a team."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    okrs = db.query(models.TeamOKR).filter(models.TeamOKR.team_id == team_id).all()
    return okrs

@router.get("/teams/{team_id}/okrs/{okr_id}", response_model=schemas.TeamOKR)
def get_team_okr(team_id: str, okr_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get a specific OKR by ID."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    okr = db.query(models.TeamOKR).filter(
        models.TeamOKR.id == okr_id,
        models.TeamOKR.team_id == team_id
    ).first()
    if not okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    
    return okr

@router.put("/teams/{team_id}/okrs/{okr_id}", response_model=schemas.TeamOKR)
def update_team_okr(team_id: str, okr_id: str, okr_update: schemas.TeamOKRCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update an OKR (only team admins can do this)."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Check if user is admin or owner
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team.owner_id != current_user.id and team_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can update OKRs")
    
    db_okr = db.query(models.TeamOKR).filter(
        models.TeamOKR.id == okr_id,
        models.TeamOKR.team_id == team_id
    ).first()
    if not db_okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    
    # Update OKR fields
    for key, value in okr_update.dict(exclude={'key_results'}).items():
        setattr(db_okr, key, value)
    
    db_okr.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_okr)
    
    return db_okr

@router.delete("/teams/{team_id}/okrs/{okr_id}")
def delete_team_okr(team_id: str, okr_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Delete an OKR (only team admins can do this)."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Check if user is admin or owner
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team.owner_id != current_user.id and team_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can delete OKRs")
    
    db_okr = db.query(models.TeamOKR).filter(
        models.TeamOKR.id == okr_id,
        models.TeamOKR.team_id == team_id
    ).first()
    if not db_okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    
    db.delete(db_okr)
    db.commit()
    return {"message": "OKR deleted successfully"}

@router.post("/okrs/{okr_id}/key-results/", response_model=schemas.TeamOKRKeyResult)
def add_key_result(okr_id: str, key_result: schemas.TeamOKRKeyResultCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Add a key result to an OKR."""
    # Get the OKR and check permissions
    okr = db.query(models.TeamOKR).filter(models.TeamOKR.id == okr_id).first()
    if not okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == okr.team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Check if user is admin or owner
    team = db.query(models.Team).filter(models.Team.id == okr.team_id).first()
    if team.owner_id != current_user.id and team_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can add key results")
    
    db_kr = models.TeamOKRKeyResult(**key_result.dict(), id=str(uuid.uuid4()), okr_id=okr_id)
    db.add(db_kr)
    db.commit()
    db.refresh(db_kr)
    return db_kr

@router.put("/okrs/{okr_id}/key-results/{kr_id}", response_model=schemas.TeamOKRKeyResult)
def update_key_result(okr_id: str, kr_id: str, key_result_update: schemas.TeamOKRKeyResultCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update a key result."""
    # Get the OKR and check permissions
    okr = db.query(models.TeamOKR).filter(models.TeamOKR.id == okr_id).first()
    if not okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == okr.team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Check if user is admin or owner
    team = db.query(models.Team).filter(models.Team.id == okr.team_id).first()
    if team.owner_id != current_user.id and team_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can update key results")
    
    db_kr = db.query(models.TeamOKRKeyResult).filter(
        models.TeamOKRKeyResult.id == kr_id,
        models.TeamOKRKeyResult.okr_id == okr_id
    ).first()
    if not db_kr:
        raise HTTPException(status_code=404, detail="Key result not found")
    
    for key, value in key_result_update.dict().items():
        setattr(db_kr, key, value)
    
    db_kr.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_kr)
    return db_kr

@router.delete("/okrs/{okr_id}/key-results/{kr_id}")
def delete_key_result(okr_id: str, kr_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Delete a key result."""
    # Get the OKR and check permissions
    okr = db.query(models.TeamOKR).filter(models.TeamOKR.id == okr_id).first()
    if not okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == okr.team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Check if user is admin or owner
    team = db.query(models.Team).filter(models.Team.id == okr.team_id).first()
    if team.owner_id != current_user.id and team_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can delete key results")
    
    db_kr = db.query(models.TeamOKRKeyResult).filter(
        models.TeamOKRKeyResult.id == kr_id,
        models.TeamOKRKeyResult.okr_id == okr_id
    ).first()
    if not db_kr:
        raise HTTPException(status_code=404, detail="Key result not found")
    
    db.delete(db_kr)
    db.commit()
    return {"message": "Key result deleted successfully"}
