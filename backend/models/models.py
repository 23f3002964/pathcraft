from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float, Date
from sqlalchemy.orm import relationship, declarative_base
import datetime
from datetime import datetime as dt

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    daily_start_hour = Column(Integer, default=9) # Default 9 AM
    daily_end_hour = Column(Integer, default=17)   # Default 5 PM
    tier = Column(String, default="free") # free, pro, enterprise
    goal_limit = Column(Integer, default=3) # Default goal limit for free tier

    goals = relationship("Goal", back_populates="owner")
    teams = relationship("TeamMember", back_populates="user")
    calendar_integrations = relationship("CalendarIntegration", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")
    analytics = relationship("UserAnalytics", back_populates="user")
    learning_platforms = relationship("LearningPlatform", back_populates="user")

class Team(Base):
    __tablename__ = 'teams'

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    owner_id = Column(String, ForeignKey('users.id'))

    members = relationship("TeamMember", back_populates="team")
    goals = relationship("Goal", back_populates="team")
    okrs = relationship("TeamOKR", back_populates="team")

class TeamMember(Base):
    __tablename__ = 'team_members'

    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey('teams.id'))
    user_id = Column(String, ForeignKey('users.id'))
    role = Column(String, default="member") # admin, member

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")

class Goal(Base):
    __tablename__ = 'goals'

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    target_date = Column(DateTime)
    methodology = Column(String) # SMART, OKR, etc.
    owner_id = Column(String, ForeignKey('users.id'))
    team_id = Column(String, ForeignKey('teams.id'), nullable=True)

    owner = relationship("User", back_populates="goals")
    team = relationship("Team", back_populates="goals")
    sub_goals = relationship("SubGoal", back_populates="parent_goal")

class SubGoal(Base):
    __tablename__ = 'sub_goals'

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    target_date = Column(DateTime)
    goal_id = Column(String, ForeignKey('goals.id'))

    parent_goal = relationship("Goal", back_populates="sub_goals")
    tasks = relationship("Task", back_populates="parent_sub_goal")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, index=True)
    sub_goal_id = Column(String, ForeignKey('sub_goals.id'), nullable=True)
    recurring_task_id = Column(String, ForeignKey('recurring_tasks.id'), nullable=True)
    generated_date = Column(DateTime, nullable=True)  # Date for which this recurring task was generated
    planned_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    status = Column(String, default="todo") # todo, in_progress, done
    priority = Column(Integer, default=1) # 0=high, 1=medium, 2=low
    dependencies = Column(String, nullable=True) # JSON array of task IDs

    parent_sub_goal = relationship("SubGoal", back_populates="tasks")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    task_id = Column(String, ForeignKey('tasks.id'), nullable=True)
    message = Column(String)
    notification_time = Column(DateTime)
    method = Column(String) # push, email, sms
    is_sent = Column(Boolean, default=False)

class RecurringTask(Base):
    __tablename__ = 'recurring_tasks'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String, nullable=True)
    rrule = Column(String) # RRULE string
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)

class CalendarIntegration(Base):
    __tablename__ = 'calendar_integrations'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    provider = Column(String)  # google, outlook, etc.
    access_token = Column(String)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="calendar_integrations")

# Team OKRs (Objectives and Key Results)
class TeamOKR(Base):
    __tablename__ = 'team_okrs'

    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey('teams.id'))
    title = Column(String)
    description = Column(String, nullable=True)
    objective = Column(String)
    quarter = Column(String)  # e.g., "Q1 2024"
    year = Column(Integer)
    status = Column(String, default="active")  # active, completed, archived
    created_at = Column(DateTime, default=dt.utcnow)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)

    team = relationship("Team", back_populates="okrs")
    key_results = relationship("TeamOKRKeyResult", back_populates="okr", cascade="all, delete-orphan")

class TeamOKRKeyResult(Base):
    __tablename__ = 'team_okr_key_results'

    id = Column(String, primary_key=True, index=True)
    okr_id = Column(String, ForeignKey('team_okrs.id'))
    title = Column(String)
    description = Column(String, nullable=True)
    target_value = Column(Float)
    current_value = Column(Float, default=0.0)
    unit = Column(String)  # e.g., "%", "users", "revenue"
    status = Column(String, default="in_progress")  # in_progress, completed, at_risk
    created_at = Column(DateTime, default=dt.utcnow)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)

    okr = relationship("TeamOKR", back_populates="key_results")

# User Preferences and Analytics
class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    preference_key = Column(String)  # e.g., "theme", "notifications", "timezone"
    preference_value = Column(String)
    created_at = Column(DateTime, default=dt.utcnow)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)

    user = relationship("User", back_populates="preferences")

class UserAnalytics(Base):
    __tablename__ = 'user_analytics'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    date = Column(Date)
    tasks_completed = Column(Integer, default=0)
    goals_achieved = Column(Integer, default=0)
    productivity_score = Column(Float, default=0.0)
    focus_time_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=dt.utcnow)

    user = relationship("User", back_populates="analytics")

# HR Learning Platform Integration
class LearningPlatform(Base):
    __tablename__ = 'learning_platforms'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    platform_name = Column(String)  # e.g., "LinkedIn Learning", "Coursera", "Udemy"
    api_key = Column(String)
    api_secret = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.utcnow)

    user = relationship("User", back_populates="learning_platforms")
    courses = relationship("LearningCourse", back_populates="platform")

class LearningCourse(Base):
    __tablename__ = 'learning_courses'

    id = Column(String, primary_key=True, index=True)
    platform_id = Column(String, ForeignKey('learning_platforms.id'))
    course_id = Column(String)  # External course ID from the platform
    title = Column(String)
    description = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    progress_percentage = Column(Float, default=0.0)
    status = Column(String, default="enrolled")  # enrolled, in_progress, completed, dropped
    enrollment_date = Column(DateTime, default=dt.utcnow)
    completion_date = Column(DateTime, nullable=True)

    platform = relationship("LearningPlatform", back_populates="courses")