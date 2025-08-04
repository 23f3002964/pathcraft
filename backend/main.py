from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .database import engine
from .models import models
from .api import goals, sub_goals, tasks, users, notifications, recurring_tasks, calendar_integration # Import the new routers
from .core.websocket_manager import manager # Import the WebSocket manager

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(goals.router, prefix="/api", tags=["goals"])
app.include_router(sub_goals.router, prefix="/api", tags=["sub_goals"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(recurring_tasks.router, prefix="/api", tags=["recurring_tasks"])
app.include_router(calendar_integration.router, prefix="/api", tags=["calendar_integration"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the PathCraft API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # You can process received data here if needed
            # await manager.send_personal_message(f"You said: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")