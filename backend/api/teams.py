
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models import models, schemas
from ..database import get_db
from ..core.auth import get_current_user

router = APIRouter()

@router.post("/teams/", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_team = models.Team(**team.dict(), id=str(uuid.uuid4()), owner_id=current_user.id)
    db.add(db_team)
    db.commit()
    # Add the owner as the first member of the team
    db_team_member = models.TeamMember(id=str(uuid.uuid4()), team_id=db_team.id, user_id=current_user.id, role="admin")
    db.add(db_team_member)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.post("/teams/{team_id}/members/", response_model=schemas.TeamMember)
def add_team_member(team_id: str, member: schemas.TeamMemberCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check if the current user is an admin of the team
    db_team_member = db.query(models.TeamMember).filter(models.TeamMember.team_id == team_id, models.TeamMember.user_id == current_user.id).first()
    if not db_team_member or db_team_member.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can add new members")

    # Check if the user is already a member of the team
    db_existing_member = db.query(models.TeamMember).filter(models.TeamMember.team_id == team_id, models.TeamMember.user_id == member.user_id).first()
    if db_existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this team")

    db_new_member = models.TeamMember(**member.dict(), id=str(uuid.uuid4()), team_id=team_id)
    db.add(db_new_member)
    db.commit()
    db.refresh(db_new_member)
    return db_new_member

@router.get("/teams/me", response_model=List[schemas.Team])
def get_my_teams(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all teams the current user is a member of."""
    team_memberships = db.query(models.TeamMember).filter(models.TeamMember.user_id == current_user.id).all()
    teams = [membership.team for membership in team_memberships]
    return teams
