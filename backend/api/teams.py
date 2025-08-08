
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

@router.get("/teams/{team_id}", response_model=schemas.Team)
def get_team(team_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get a specific team by ID."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/teams/{team_id}/members", response_model=List[schemas.TeamMember])
def get_team_members(team_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all members of a team."""
    # Check if user is a member of the team
    team_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not team_membership:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    members = db.query(models.TeamMember).filter(models.TeamMember.team_id == team_id).all()
    return members

@router.put("/teams/{team_id}", response_model=schemas.Team)
def update_team(team_id: str, team_update: schemas.TeamCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update team information (only team owner can do this)."""
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only team owner can update team")
    
    for key, value in team_update.dict().items():
        setattr(team, key, value)
    
    db.commit()
    db.refresh(team)
    return team

@router.delete("/teams/{team_id}")
def delete_team(team_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Delete a team (only team owner can do this)."""
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only team owner can delete team")
    
    # Delete all team members first
    db.query(models.TeamMember).filter(models.TeamMember.team_id == team_id).delete()
    # Delete the team
    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}

@router.delete("/teams/{team_id}/members/{user_id}")
def remove_team_member(team_id: str, user_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Remove a member from the team (only team admins can do this)."""
    # Check if the current user is an admin of the team
    current_membership = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == current_user.id
    ).first()
    if not current_membership or current_membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only team admins can remove members")
    
    # Check if the user to be removed is a member
    member_to_remove = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id, 
        models.TeamMember.user_id == user_id
    ).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    # Prevent removing the team owner
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team.owner_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    db.delete(member_to_remove)
    db.commit()
    return {"message": "Member removed successfully"}
