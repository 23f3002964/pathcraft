from pydantic import BaseModel
from typing import List, Optional
import datetime
from datetime import date

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    daily_start_hour: int = 9
    daily_end_hour: int = 17
    tier: str = "free"
    goal_limit: int = 3

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True

# --- Team Schemas ---
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: str
    owner_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- TeamMember Schemas ---
class TeamMemberBase(BaseModel):
    user_id: str
    role: str = "member"

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    id: str
    team_id: str

    class Config:
        from_attributes = True

# --- Goal Schemas ---
class GoalBase(BaseModel):
    title: str
    target_date: datetime.datetime
    methodology: str

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: str
    owner_id: str
    team_id: Optional[str] = None

    class Config:
        from_attributes = True

# --- SubGoal Schemas ---
class SubGoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: datetime.datetime

class SubGoalCreate(SubGoalBase):
    goal_id: str

class SubGoal(SubGoalBase):
    id: str
    goal_id: str

    class Config:
        from_attributes = True

# --- Task Schemas ---
class TaskBase(BaseModel):
    sub_goal_id: str
    planned_start: Optional[datetime.datetime] = None
    planned_end: Optional[datetime.datetime] = None
    status: str = "todo"
    priority: int = 1
    dependencies: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str

    class Config:
        from_attributes = True

class RescheduleTask(BaseModel):
    planned_start: datetime.datetime
    planned_end: datetime.datetime

# --- Notification Schemas ---
class NotificationBase(BaseModel):
    user_id: str
    message: str
    notification_time: datetime.datetime
    method: str
    task_id: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: str
    is_sent: bool

    class Config:
        from_attributes = True

# --- Recurring Task Schemas ---
class RecurringTaskBase(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    rrule: str
    start_date: datetime.datetime
    end_date: Optional[datetime.datetime] = None

class RecurringTaskCreate(RecurringTaskBase):
    pass

class RecurringTask(RecurringTaskBase):
    id: str

    class Config:
        from_attributes = True

# --- Calendar Integration Schemas ---
class CalendarIntegrationBase(BaseModel):
    user_id: str
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

class CalendarIntegrationCreate(CalendarIntegrationBase):
    pass

class CalendarIntegration(CalendarIntegrationBase):
    id: str

    class Config:
        from_attributes = True

# Team OKR Schemas
class TeamOKRKeyResultBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_value: float
    current_value: float = 0.0
    unit: str
    status: str = "in_progress"

class TeamOKRKeyResultCreate(TeamOKRKeyResultBase):
    pass

class TeamOKRKeyResult(TeamOKRKeyResultBase):
    id: str
    okr_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class TeamOKRBase(BaseModel):
    team_id: str
    title: str
    description: Optional[str] = None
    objective: str
    quarter: str
    year: int
    status: str = "active"

class TeamOKRCreate(TeamOKRBase):
    key_results: Optional[List[TeamOKRKeyResultCreate]] = []

class TeamOKR(TeamOKRBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    key_results: List[TeamOKRKeyResult] = []

    class Config:
        from_attributes = True

# User Preference Schemas
class UserPreferenceBase(BaseModel):
    user_id: str
    preference_key: str
    preference_value: str

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreference(UserPreferenceBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# User Analytics Schemas
class UserAnalyticsBase(BaseModel):
    user_id: str
    date: date
    tasks_completed: int = 0
    goals_achieved: int = 0
    productivity_score: float = 0.0
    focus_time_minutes: int = 0

class UserAnalyticsCreate(UserAnalyticsBase):
    pass

class UserAnalytics(UserAnalyticsBase):
    id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Learning Platform Schemas
class LearningCourseBase(BaseModel):
    platform_id: str
    course_id: str
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    progress_percentage: float = 0.0
    status: str = "enrolled"

class LearningCourseCreate(LearningCourseBase):
    pass

class LearningCourse(LearningCourseBase):
    id: str
    enrollment_date: datetime.datetime
    completion_date: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class LearningPlatformBase(BaseModel):
    user_id: str
    platform_name: str
    api_key: str
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None
    is_active: bool = True

class LearningPlatformCreate(LearningPlatformBase):
    pass

class LearningPlatform(LearningPlatformBase):
    id: str
    created_at: datetime.datetime
    courses: List[LearningCourse] = []

    class Config:
        from_attributes = True