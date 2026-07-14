from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for realtime updates from Supabase Realtime/Custom Redis PubSub.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # For demonstration, we just echo back. In production, this would subscribe to Redis.
            await manager.broadcast(f"Realtime Update: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
