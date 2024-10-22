from fastapi import WebSocket
from typing import Dict, Set, Any

TActiveConnections = Dict[str, Set[WebSocket]]

class ConnectionManager:
    def __init__(self):
        self.active_connections: TActiveConnections = {}
    
    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(room_id, set()).add(websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, room_id: str, message: Any):
        for connection in self.active_connections.get(room_id, []):
            await connection.send_json(message)