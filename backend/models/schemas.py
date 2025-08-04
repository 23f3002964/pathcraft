from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    daily_start_hour: Optional[int] = 9
    daily_end_hour: Optional[int] = 17

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool = True # Default to active
    goals: List['Goal'] = []

    class Config:
        orm_mode = True

# --- Task Schemas ---
class TaskBase(BaseModel):
    sub_goal_id: Optional[str] = None
    recurring_task_id: Optional[str] = None
    generated_date: Optional[datetime.datetime] = None
    planned_start: datetime.datetime
    planned_end: datetime.datetime
    status: str = 'todo'
    priority: int = 0
    dependencies: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str

    class Config:
        orm_mode = True

# --- Notification Schemas ---
class NotificationBase(BaseModel):
    user_id: str
    task_id: Optional[str] = None
    message: str
    notification_time: datetime.datetime
    method: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: str
    is_sent: bool

    class Config:
        orm_mode = True

# --- RecurringTask Schemas ---
class RecurringTaskBase(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    recurrence_type: str
    recurrence_value: Optional[int] = None
    start_date: datetime.datetime
    end_date: Optional[datetime.datetime] = None

class RecurringTaskCreate(RecurringTaskBase):
    pass

class RecurringTask(RecurringTaskBase):
    id: str

    class Config:
        orm_mode = True

# --- CalendarIntegration Schemas ---
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
        orm_mode = True

# --- SubGoal Schemas ---
class SubGoalBase(BaseModel):
    parent_goal_id: str
    description: str
    estimated_effort_minutes: int

class SubGoalCreate(SubGoalBase):
    pass

class SubGoal(SubGoalBase):
    id: str
    tasks: List[Task] = []

    class Config:
        orm_mode = True

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
    sub_goals: List[SubGoal] = []

    class Config:
        orm_mode = True

User.update_forward_refs()