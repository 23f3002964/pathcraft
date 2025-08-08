import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch, Mock

# Mock the websocket manager before it's imported by the app
from backend.core import websocket_manager
mock_manager = AsyncMock()
websocket_manager.manager = mock_manager

from backend.main import app
from backend.database import get_db
from backend.models.models import Base, User, Goal, SubGoal, Task, Notification, RecurringTask, CalendarIntegration
from backend.core.auth import get_password_hash
import datetime
import uuid

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency for testing
@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# Helper to create a test user and get a token
def get_test_user_token(client, email="test@example.com", password="testpassword", daily_start_hour=9, daily_end_hour=17):
    user_data = {"email": email, "password": password, "daily_start_hour": daily_start_hour, "daily_end_hour": daily_end_hour}
    client.post("/api/users/", json=user_data)
    response = client.post(
        "/api/token",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"]

# --- User Tests ---
def test_create_user(client):
    response = client.post(
        "/api/users/",
        json={"email": "test@example.com", "password": "testpassword", "daily_start_hour": 8, "daily_end_hour": 18}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["daily_start_hour"] == 8

def test_login_for_access_token(client):
    get_test_user_token(client)
    response = client.post(
        "/api/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_read_users_me(client):
    token = get_test_user_token(client)
    response = client.get(
        "/api/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_update_user(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    response = client.put(
        f"/api/users/{user_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "email": "updated@example.com",
            "password": "newpassword",
            "daily_start_hour": 7,
            "daily_end_hour": 19
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"
    assert response.json()["daily_start_hour"] == 7

# --- Goal Tests ---
def test_create_goal(client):
    token = get_test_user_token(client)
    response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Learn Python",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Learn Python"

def test_decompose_goal(client):
    token = get_test_user_token(client)
    create_goal_response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Learn Python",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    goal_id = create_goal_response.json()["id"]

    response = client.post(
        f"/api/goals/{goal_id}/decompose/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0 # Expect sub-goals to be created

def test_create_goal_limit(client):
    token = get_test_user_token(client, email="free@example.com")

    # Create 3 goals, which should be allowed
    for i in range(3):
        response = client.post(
            "/api/goals/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "title": f"Goal {i+1}",
                "target_date": "2025-12-31T23:59:59",
                "methodology": "SMART"
            }
        )
        assert response.status_code == 200

    # The 4th goal should be blocked
    response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Goal 4",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    assert response.status_code == 403

# --- SubGoal Tests ---
def test_create_sub_goal(client):
    token = get_test_user_token(client)
    create_goal_response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Goal",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    goal_id = create_goal_response.json()["id"]

    response = client.post(
        "/api/sub_goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "goal_id": goal_id,
            "title": "Test Sub-goal",
            "description": "Sub-goal description",
            "target_date": "2025-12-31T23:59:59"
        }
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Sub-goal description"

# --- Task Tests ---
def test_create_task(client):
    token = get_test_user_token(client)
    create_goal_response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Goal for Task",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    goal_id = create_goal_response.json()["id"]

    create_sub_goal_response = client.post(
        "/api/sub_goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "goal_id": goal_id,
            "title": "Test Sub-goal for Task",
            "description": "Test Sub-goal for Task",
            "target_date": "2025-12-31T23:59:59"
        }
    )
    sub_goal_id = create_sub_goal_response.json()["id"]

    response = client.post(
        "/api/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sub_goal_id": sub_goal_id,
            "planned_start": "2025-08-05T09:00:00",
            "planned_end": "2025-08-05T10:00:00",
            "status": "todo",
            "priority": 1
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "todo"
    assert response.json()["priority"] == 1

def test_schedule_tasks(client):
    token = get_test_user_token(client)
    create_goal_response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Goal for Scheduling",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    goal_id = create_goal_response.json()["id"]

    create_sub_goal_response = client.post(
        "/api/sub_goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "goal_id": goal_id,
            "title": "Sub-goal for scheduling",
            "description": "Sub-goal for scheduling",
            "target_date": "2025-12-31T23:59:59"
        }
    )
    sub_goal_id = create_sub_goal_response.json()["id"]

    # Create a task under this sub-goal
    client.post(
        "/api/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sub_goal_id": sub_goal_id,
            "planned_start": "2025-08-05T09:00:00",
            "planned_end": "2025-08-05T10:00:00",
            "status": "todo",
            "priority": 1
        }
    )

    response = client.post(
        f"/api/sub_goals/{sub_goal_id}/schedule/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["planned_start"] is not None

# --- Notification Tests ---
def test_create_notification(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    response = client.post(
        "/api/notifications/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "message": "Test notification",
            "notification_time": "2025-08-05T10:00:00",
            "method": "email"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Test notification"

def test_get_my_notifications(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    client.post(
        "/api/notifications/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "message": "Another notification",
            "notification_time": "2025-08-05T11:00:00",
            "method": "push"
        }
    )
    response = client.get(
        "/api/notifications/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_mark_notification_sent(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    create_notification_response = client.post(
        "/api/notifications/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "message": "Test notification",
            "notification_time": "2025-08-05T12:00:00",
            "method": "email"
        }
    )
    notification_id = create_notification_response.json()["id"]

    response = client.put(
        f"/api/notifications/{notification_id}/mark_sent",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["is_sent"] == True
    # Assert that send_personal_message was called (mocked globally)
    from backend.core.websocket_manager import manager
    manager.send_personal_message.assert_called_once()

# --- Recurring Task Tests ---
def test_create_recurring_task(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    response = client.post(
        "/api/recurring_tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "title": "Daily Standup",
            "rrule": "FREQ=DAILY",
            "start_date": "2025-08-05T09:00:00"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Daily Standup"

def test_generate_tasks_from_recurring(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    create_recurring_task_response = client.post(
        "/api/recurring_tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "title": "Weekly Report",
            "rrule": "FREQ=WEEKLY;BYDAY=MO", # Weekly on Monday
            "start_date": "2025-08-04T09:00:00" # Start from Monday
        }
    )
    recurring_task_id = create_recurring_task_response.json()["id"]

    response = client.post(
        f"/api/recurring_tasks/{recurring_task_id}/generate_tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["recurring_task_id"] == recurring_task_id

# --- Calendar Integration Tests ---
def test_create_calendar_integration(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    response = client.post(
        "/api/calendar_integrations/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "provider": "google",
            "access_token": "some_google_token",
            "expires_at": "2025-08-05T10:00:00"
        }
    )
    assert response.status_code == 200
    assert response.json()["provider"] == "google"

def test_get_my_calendar_integrations(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    client.post(
        "/api/calendar_integrations/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "provider": "outlook",
            "access_token": "some_outlook_token",
            "expires_at": "2025-08-05T11:00:00"
        }
    )
    response = client.get(
        "/api/calendar_integrations/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_delete_calendar_integration(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    create_integration_response = client.post(
        "/api/calendar_integrations/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "provider": "test_provider",
            "access_token": "token_to_delete",
            "expires_at": "2025-08-05T12:00:00"
        }
    )
    integration_id = create_integration_response.json()["id"]

    response = client.delete(
        f"/api/calendar_integrations/{integration_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    get_response = client.get(
        f"/api/calendar_integrations/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert len(get_response.json()) == 0

# --- Integration Tests ---
def test_goal_decomposition_and_scheduling_integration(client):
    token = get_test_user_token(client)
    user_id = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]

    # 1. Create a goal
    create_goal_response = client.post(
        "/api/goals/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Develop a new AI application",
            "target_date": "2025-12-31T23:59:59",
            "methodology": "SMART"
        }
    )
    assert create_goal_response.status_code == 200
    goal_id = create_goal_response.json()["id"]

    # 2. Decompose the goal
    decompose_response = client.post(
        f"/api/goals/{goal_id}/decompose/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert decompose_response.status_code == 200
    sub_goals = decompose_response.json()
    assert len(sub_goals) > 0
    sub_goal_id = sub_goals[0]["id"]

    # 3. Create a task for the sub-goal (with a dependency and priority)
    task1_response = client.post(
        "/api/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sub_goal_id": sub_goal_id,
            "planned_start": "2025-08-05T09:00:00",
            "planned_end": "2025-08-05T10:00:00",
            "status": "todo",
            "priority": 0, # High priority
            "dependencies": None
        }
    )
    task_id_1 = task1_response.json()["id"]

    task2_response = client.post(
        "/api/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sub_goal_id": sub_goal_id,
            "planned_start": "2025-08-05T10:00:00",
            "planned_end": "2025-08-05T11:00:00",
            "status": "todo",
            "priority": 1, # Lower priority
            "dependencies": task_id_1
        }
    )
    task_id_2 = task2_response.json()["id"]

    # 4. Add a calendar integration (conceptual)
    client.post(
        "/api/calendar_integrations/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "user_id": user_id,
            "provider": "google",
            "access_token": "fake_google_token",
            "expires_at": "2025-08-05T23:59:59"
        }
    )

    # 5. Schedule tasks for the sub-goal
    schedule_response = client.post(
        f"/api/sub_goals/{sub_goal_id}/schedule/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert schedule_response.status_code == 200
    scheduled_tasks = schedule_response.json()
    assert len(scheduled_tasks) > 0

    # Verify scheduling logic (e.g., priority, no conflicts)
    # This is a basic check; more detailed assertions would be needed
    assert scheduled_tasks[0]["planned_start"] is not None

    # 6. Mark a task as done and check notification (conceptual)
    # For this test, we'll just mark it done and check the notification endpoint
    # In a real scenario, the WebSocket would be tested separately
    task_to_mark_done_id = scheduled_tasks[0]["id"]
    client.put(
        f"/api/tasks/{task_to_mark_done_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sub_goal_id": sub_goal_id,
            "planned_start": scheduled_tasks[0]["planned_start"],
            "planned_end": scheduled_tasks[0]["planned_end"],
            "status": "done",
            "priority": scheduled_tasks[0]["priority"]
        }
    )

    # Check if a notification was conceptually triggered (by checking the notification endpoint)
    notifications_response = client.get(
        "/api/notifications/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert notifications_response.status_code == 200
    assert len(notifications_response.json()) > 0
    from backend.core.websocket_manager import manager
    manager.send_personal_message.assert_called() # Check if it was called at least once