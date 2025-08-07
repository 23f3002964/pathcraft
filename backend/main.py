from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from .database import engine, get_db
from .models import models
from .api import goals, sub_goals, tasks, users, notifications, recurring_tasks, calendar_integration # Import the new routers
from .core.websocket_manager import manager # Import the WebSocket manager
from .core.auth import SECRET_KEY, ALGORITHM # Import for token validation

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# OAuth2 scheme for WebSocket authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Dependency to get current user from WebSocket token
async def get_websocket_current_user(websocket: WebSocket, token: str): # token is passed via query param
    credentials_exception = WebSocketDisconnect("Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = next(get_db()) # Get a new DB session for this dependency
    user = db.query(models.User).filter(models.User.email == email).first()
    db.close()
    if user is None:
        raise credentials_exception
    return user

# Include the routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(goals.router, prefix="/api", tags=["goals"])
app.include_router(sub_goals.router, prefix="/api", tags=["sub_goals"])
from .api import goals, sub_goals, tasks, users, notifications, recurring_tasks, calendar_integration # Import the new routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(goals.router, prefix="/api", tags=["goals"])
app.include_router(sub_goals.router, prefix="/api", tags=["sub_goals"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(recurring_tasks.router, prefix="/api", tags=["recurring_tasks"])
app.include_router(calendar_integration.router, prefix="/api", tags=["calendar_integration"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(recurring_tasks.router, prefix="/api", tags=["recurring_tasks"])
app.include_router(calendar_integration.router, prefix="/api", tags=["calendar_integration"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the PathCraft API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    user = None
    if token:
        try:
            user = await get_websocket_current_user(websocket, token)
        except WebSocketDisconnect:
            print("WebSocket authentication failed.")
            return # Do not accept connection if auth fails

    if user:
        await manager.connect(user.id, websocket)
    else:
        # Handle unauthenticated WebSocket connections if necessary
        # For now, we'll just close it or not accept it
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        while True:
            data = await websocket.receive_text()
            # You can process received data here if needed
            # await manager.send_personal_message(f"You said: {data}", user.id)
    except WebSocketDisconnect:
        if user:
            manager.disconnect(user.id)
        print("Client disconnected")