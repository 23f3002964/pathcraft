import datetime
from ..database import get_db
from ..models.models import Task

def get_reminder_frequency(task_id: str | None) -> datetime.timedelta:
    """
    Gets the reminder frequency for a task.
    If the user has set a custom reminder interval for the task, it returns that.
    Otherwise, it returns the default reminder interval.
    """
    if not task_id:
        return datetime.timedelta(minutes=30)

    db = next(get_db())
    task = db.query(Task).filter(Task.id == task_id).first()

    if task and task.reminder_interval:
        return datetime.timedelta(minutes=task.reminder_interval)
    else:
        return datetime.timedelta(minutes=30) # Default to 30 minutes before the task
