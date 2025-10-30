from fastapi import WebSocket
import json
from beanie import PydanticObjectId
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket")


class WebsocketManager:
    def __init__(self) -> None:
        self._active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        if chat_id not in self._active_connections:
            self._active_connections[chat_id] = set()
        self._active_connections[chat_id].add(websocket)
        
    def disconnect(self, websocket: WebSocket, chat_id: str):
        if chat_id in self._active_connections:
            self._active_connections[chat_id].discard(websocket)
            if not self._active_connections[chat_id]:
                del self._active_connections[chat_id]
    

    async def broadcast(self, message: dict):
        chat_id = str(message.get("chat"))

        json_payload = message
        dead_connections: set[WebSocket] = set()
        if chat_id in self._active_connections:
            for conn in self._active_connections[chat_id]:
                try:
                    await conn.send_json(json_payload)
                except Exception:         
                    dead_connections.add(conn)

        for dead in dead_connections:
            self.disconnect(dead, chat_id)
        

manager = WebsocketManager()