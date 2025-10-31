from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
import logging
import json
import asyncio

from shared.core.security import verify_access_token
from shared.core.db import lifespan
from shared.schemas.message import MessageSchemaIn
from shared.tools.websocket_manager import manager
from shared.tools.redis_manager import redis
from routes import router
from crud import create_message, get_user_by_id, is_user_in_chat


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chat-service")


@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, token: str):
    try:
        user_id = verify_access_token(token=token)

        user = await get_user_by_id(user_id)

    except HTTPException as exc:
        logger.warning(f"Unauthorized access attempt: {exc.detail}")
        await websocket.close(code=4001)
        return
    
    if is_user_in_chat(user_id=user_id, chat_id=chat_id):
        await websocket.accept()
        pubsub = await redis.subscribe(chat_id)

        async def redis_listener():
            try:
                async for msg in pubsub.listen():
                    if msg["type"] == "message":
                        data = json.loads(msg["data"])
                        await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Redis listener error: {e}")

        listener_task = asyncio.create_task(redis_listener())
        
        try:
            while True:
                data = await websocket.receive_json()
                logger.info(data)

                message = {
                    "username": user.username,
                    "text": data["text"],
                    "chat": chat_id
                }

                await redis.publish(channel=chat_id, message=message)

                message_scheme = MessageSchemaIn(
                    user=user_id,  
                    text=data["text"],
                    chat=chat_id,
                )
                await create_message(message_scheme=message_scheme)

        except WebSocketDisconnect:
            listener_task.cancel()
            await pubsub.unsubscribe(chat_id)

    else:
         raise HTTPException(status_code=404, detail=f"User:{user_id} is not in chat: {chat_id}")