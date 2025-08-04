
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import get_db
from backend.models.models import Base
from backend.models.models import User, Goal, SubGoal, Task
from backend.core.auth import get_password_hash

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
def get_test_user_token(client, email="test@example.com", password="testpassword"):
    user_data = {"email": email, "password": password}
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
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_login_for_access_token(client):
    get_test_user_token(client)
    response = client.post(
        "/api/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

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
            "parent_goal_id": goal_id,
            "description": "Sub-goal description",
            "estimated_effort_minutes": 120
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
            "parent_goal_id": goal_id,
            "description": "Test Sub-goal for Task",
            "estimated_effort_minutes": 60
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
            "status": "todo"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "todo"

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
            "parent_goal_id": goal_id,
            "description": "Sub-goal for scheduling",
            "estimated_effort_minutes": 30
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
            "status": "todo"
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
