from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    daily_start_hour = Column(Integer, default=9) # Default 9 AM
    daily_end_hour = Column(Integer, default=17)   # Default 5 PM
    tier = Column(String, default="free") # free, pro, enterprise
    goal_limit = Column(Integer, default=3) # Default goal limit for free tier

    goals = relationship("Goal", back_populates="owner")
    teams = relationship("TeamMember", back_populates="user")

class Team(Base):
    __tablename__ = 'teams'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(String, ForeignKey('users.id'))

    owner = relationship("User", backref="owned_teams")
    members = relationship("TeamMember", back_populates="team")
    goals = relationship("Goal", back_populates="team")

class TeamMember(Base):
    __tablename__ = 'team_members'

    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey('teams.id'))
    user_id = Column(String, ForeignKey('users.id'))
    role = Column(String, default="member") # member, admin

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")

class Goal(Base):
    __tablename__ = 'goals'

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    target_date = Column(DateTime)
    methodology = Column(String) # SMART, OKR, etc.
    owner_id = Column(String, ForeignKey('users.id'))
    team_id = Column(String, ForeignKey('teams.id'), nullable=True)

    # Relationship to User
    owner = relationship("User", back_populates="goals")
    # Relationship to Team
    team = relationship("Team", back_populates="goals")
    # Relationship to SubGoal
    sub_goals = relationship("SubGoal", back_populates="parent_goal")

class SubGoal(Base):
    __tablename__ = 'sub_goals'

    id = Column(String, primary_key=True, index=True)
    parent_goal_id = Column(String, ForeignKey('goals.id'))
    description = Column(Text)
    estimated_effort_minutes = Column(Integer)

    # Relationship to Goal
    parent_goal = relationship("Goal", back_populates="sub_goals")
    # Relationship to Task
    tasks = relationship("Task", back_populates="parent_sub_goal")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, index=True)
    sub_goal_id = Column(String, ForeignKey('sub_goals.id'))
    recurring_task_id = Column(String, ForeignKey('recurring_tasks.id'), nullable=True)
    generated_date = Column(DateTime, nullable=True) # Date for which this recurring task was generated
    planned_start = Column(DateTime)
    planned_end = Column(DateTime)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    status = Column(String, default='todo') # todo, in-progress, done, skipped
    priority = Column(Integer, default=0) # Lower number = higher priority
    dependencies = Column(String, nullable=True) # Comma-separated task IDs
    reminder_interval = Column(Integer, nullable=True) # Reminder interval in minutes
    reminder_policy_id = Column(String, nullable=True)

    # Relationship to SubGoal
    parent_sub_goal = relationship("SubGoal", back_populates="tasks")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    task_id = Column(String, ForeignKey('tasks.id'), nullable=True)
    message = Column(Text)
    notification_time = Column(DateTime)
    method = Column(String) # e.g., 'email', 'push', 'sms'
    is_sent = Column(Boolean, default=False)

    user = relationship("User", backref="notifications")
    task = relationship("Task", backref="notifications")

class RecurringTask(Base):
    __tablename__ = 'recurring_tasks'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    title = Column(String)
    description = Column(Text, nullable=True)
    rrule = Column(String) # Stores recurrence rule in iCalendar RRULE format
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    # Relationship to User
    user = relationship("User", backref="recurring_tasks")

class CalendarIntegration(Base):
    __tablename__ = 'calendar_integrations'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    provider = Column(String) # e.g., 'google', 'outlook'
    access_token = Column(Text) # In a real app, this would be encrypted and managed securely
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="calendar_integrations")