from fastapi import FastAPI

from .database import engine
from .models import models
from .api import goals, sub_goals, tasks, users, notifications, recurring_tasks, calendar_integration # Import the new routers

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(goals.router, prefix="/api", tags=["goals"])
app.include_router(sub_goals.router, prefix="/api", tags=["sub_goals"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(recurring_tasks.router, prefix="/api", tags=["recurring_tasks"])
app.include_router(calendar_integration.router, prefix="/api", tags=["calendar_integration"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the PathCraft API"}