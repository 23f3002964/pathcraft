
import datetime
from typing import List, Dict
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
    tasks.sort(key=lambda task: predict_task_priority(task.parent_sub_goal.description, task.planned_end, user_id=task.parent_sub_goal.parent_goal.owner_id) if task.planned_end and task.parent_sub_goal and task.parent_sub_goal.parent_goal else task.priority)

    # Convert existing calendar events to a more usable format (start, end datetime objects)
    if existing_calendar_events is None:
        existing_calendar_events = []
    
    # Sort calendar events by start time
    existing_calendar_events.sort(key=lambda event: event['start'])

    # Initialize the current scheduling pointer
    current_scheduling_pointer = datetime.datetime.now().replace(hour=user_daily_start_hour, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    for task in tasks:
        # Check dependencies
        if task.dependencies:
            dependent_task_ids = [dep.strip() for dep in task.dependencies.split(',')]
            all_dependencies_met = True
            for dep_id in dependent_task_ids:
                dependent_task = db.query(Task).filter(Task.id == dep_id).first()
                if dependent_task and dependent_task.status != 'done':
                    all_dependencies_met = False
                    print(f"Skipping task {task.id} due to unmet dependency {dep_id}")
                    break
            if not all_dependencies_met:
                continue # Skip this task for now

        task_scheduled = False
        attempt_start_time = current_scheduling_pointer # Start attempting from the current pointer

        while not task_scheduled:
            # Adjust attempt_start_time to be within working hours
            while attempt_start_time.hour < user_daily_start_hour or attempt_start_time.hour >= user_daily_end_hour:
                if attempt_start_time.hour >= user_daily_end_hour:
                    attempt_start_time = attempt_start_time + datetime.timedelta(days=1) # Move to next day
                attempt_start_time = attempt_start_time.replace(hour=user_daily_start_hour, minute=0, second=0, microsecond=0)

            duration_minutes = predict_task_duration(task.parent_sub_goal.description, user_id=task.parent_sub_goal.parent_goal.owner_id) # Use predicted duration
            attempt_end_time = attempt_start_time + datetime.timedelta(minutes=duration_minutes)

            # Check for conflicts with existing calendar events
            conflict_found = False
            for event in existing_calendar_events:
                event_start = event['start']
                event_end = event['end']

                # Check for overlap
                if (attempt_start_time < event_end and attempt_end_time > event_start):
                    conflict_found = True
                    attempt_start_time = event_end + datetime.timedelta(minutes=15) # Move past the conflicting event
                    break

            if not conflict_found:
                task.planned_start = attempt_start_time
                task.planned_end = attempt_end_time
                scheduled_tasks.append(task)
                current_scheduling_pointer = attempt_end_time + datetime.timedelta(minutes=15) # Update pointer for next task
                task_scheduled = True
            else:
                # If conflict found, continue the while loop to find next available slot
                pass # attempt_start_time was already updated to move past the conflict

    return scheduled_tasks
