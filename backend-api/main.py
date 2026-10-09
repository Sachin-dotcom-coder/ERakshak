# backend-api/main.py
from fastapi import FastAPI, Depends, WebSocket, HTTPException
from auth import get_current_user, get_websocket_user, TokenData
from routers import auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="E-Rakshak Traffic Intelligence Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Auth Router
app.include_router(auth_router.router)

# Protect REST Endpoints
@app.get("/api/junctions")
def get_junctions(user: TokenData = Depends(get_current_user)):
    # Automatically blocked if valid Bearer token is missing
    return {"status": "success", "user": user.username}

@app.post("/api/junctions/{id}/mode")
def update_junction_mode(id: str, mode: str, user: TokenData = Depends(get_current_user)):
    # Role check: Only admin role can change signal mode
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can modify junction signal mode")
    return {"status": "updated", "junction_id": id, "mode": mode}

@app.get("/api/violations")
def get_violations(user: TokenData = Depends(get_current_user)):
    return {"violations": []}

# backend-api/main.py

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "E-Rakshak API Core",
        "docs": "http://127.0.0.1:8000/docs"
    }

# Protect Live WebSocket Event Bus
@app.websocket("/api/ws/traffic")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Verify token before opening connection
    user = await get_websocket_user(websocket, token)
    await websocket.accept()
    
    try:
        while True:
            # Continue streaming events from mock_generator
            await websocket.send_json({"event": "telemetry_ping", "operator": user.username})
    except Exception:
        await websocket.close()