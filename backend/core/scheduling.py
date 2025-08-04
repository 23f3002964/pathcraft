import datetime
from sqlalchemy.orm import Session
from backend.models.models import Task # Import Task model
from backend.core.prediction import predict_task_duration # Import prediction model
from backend.core.prioritization import predict_task_priority # Import prioritization model
from backend.core.calendar_sync import sync_calendar_events # Import calendar sync

def schedule_tasks(tasks, db: Session, user_daily_start_hour: int = 9, user_daily_end_hour: int = 17, existing_calendar_events: List[Dict] = None):
    """Schedules a list of tasks considering their estimated effort, user availability, priority, and dependencies."""
    scheduled_tasks = []

    # Sort tasks by priority (lower number = higher priority)
    # Use predicted priority if available, otherwise fallback to manually set priority
    tasks.sort(key=lambda task: predict_task_priority(task.description, task.planned_end, user_id=task.parent_sub_goal.parent_goal.owner_id) if task.planned_end else task.priority)

    # Convert existing calendar events to a more usable format (start, end datetime objects)
    if existing_calendar_events is None:
        existing_calendar_events = []
    
    # Sort calendar events by start time
    existing_calendar_events.sort(key=lambda event: event['start'])

    for task in tasks:
        # Check dependencies
        if task.dependencies:
            dependent_task_ids = [dep.strip() for dep in task.dependencies.split(',')]
            for dep_id in dependent_task_ids:
                dependent_task = db.query(Task).filter(Task.id == dep_id).first()
                if dependent_task and dependent_task.status != 'done':
                    # If a dependency is not done, skip this task for now
                    # In a real system, this would involve more complex rescheduling or notification
                    print(f"Skipping task {task.id} due to unmet dependency {dep_id}")
                    continue

        # Ensure tasks stay within daily working hours and avoid calendar conflicts
        current_attempt_start_time = start_time
        task_scheduled = False

        while not task_scheduled:
            # Adjust start_time to be within working hours
            while current_attempt_start_time.hour < user_daily_start_hour or current_attempt_start_time.hour >= user_daily_end_hour:
                if current_attempt_start_time.hour >= user_daily_end_hour:
                    current_attempt_start_time = current_attempt_start_time + datetime.timedelta(days=1) # Move to next day
                current_attempt_start_time = current_attempt_start_time.replace(hour=user_daily_start_hour, minute=0, second=0, microsecond=0)

            duration_minutes = predict_task_duration(task.description, user_id=task.parent_sub_goal.parent_goal.owner_id) # Use predicted duration
            current_attempt_end_time = current_attempt_start_time + datetime.timedelta(minutes=duration_minutes)

            # Check for conflicts with existing calendar events
            conflict_found = False
            for event in existing_calendar_events:
                event_start = event['start']
                event_end = event['end']

                # Check for overlap
                if (current_attempt_start_time < event_end and current_attempt_end_time > event_start):
                    conflict_found = True
                    # Move past the conflicting event
                    current_attempt_start_time = event_end + datetime.timedelta(minutes=15) # Add a small buffer
                    break
            
            if not conflict_found:
                task.planned_start = current_attempt_start_time
                task.planned_end = current_attempt_end_time
                scheduled_tasks.append(task)
                start_time = current_attempt_end_time + datetime.timedelta(minutes=15) # Set next task's start time with a 15-minute break
                task_scheduled = True
            # If conflict found, loop continues to find next available slot

    return scheduled_tasks