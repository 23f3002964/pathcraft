from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid

from .database import engine, get_db
from .models import models
from .core.websocket_manager import manager
from .api import goals, sub_goals, tasks, users, notifications, recurring_tasks, calendar_integration, teams, team_okrs, user_preferences, learning_platforms

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PathCraft API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(goals.router, prefix="/api", tags=["goals"])
app.include_router(sub_goals.router, prefix="/api", tags=["sub_goals"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(recurring_tasks.router, prefix="/api", tags=["recurring_tasks"])
app.include_router(calendar_integration.router, prefix="/api", tags=["calendar_integration"])
app.include_router(teams.router, prefix="/api", tags=["teams"])
app.include_router(team_okrs.router, prefix="/api", tags=["team_okrs"])
app.include_router(user_preferences.router, prefix="/api", tags=["user_preferences"])
app.include_router(learning_platforms.router, prefix="/api", tags=["learning_platforms"])

@app.get("/")
def read_root():
    return {"message": "Welcome to PathCraft API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            await manager.send_personal_message(f"Message received: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        await manager.send_personal_message("Client disconnected", user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)