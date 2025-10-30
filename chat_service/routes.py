from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import json
import logging

from shared.schemas import ChatSchemaIn, ChatSchemaOut, MessageSchemaOut
from shared.core.security import verify_access_token
from crud import get_chats_db, create_chat_db, is_user_in_chat, get_message_from_chat


router = APIRouter(prefix="/chat", tags=["chat"])


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chat-service")


@router.get("/")
async def get(chat_id: str, token: str):
    html = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>FastAPI Chat</title>
    <style>
      body {{ font-family: sans-serif; max-width: 600px; margin: 40px auto; }}
      chat {{ border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: auto; margin-bottom: 10px; }}
      input {{ width: 80%; padding: 5px; }}
      send {{ padding: 6px 12px; }}
    </style>
  </head>
  <body>
    <h2>💬 FastAPI WebSocket Chat</h2>
    <div id="chat"></div>
    <input id="input" type="text" placeholder="Type a message..." />
    <button id="send">Send</button>

    <script>
      const CHAT_ID = {json.dumps(chat_id)};
      const TOKEN = {json.dumps(token)};
      console.log(`ws://${{window.location.host}}/ws/chat/${{CHAT_ID}}?token=${{TOKEN}}`);

      const ws = new WebSocket(`ws://${{window.location.host}}/ws/chat/${{CHAT_ID}}?token=${{TOKEN}}`);
      const chat = document.getElementById("chat");
      const input = document.getElementById("input");
      const sendBtn = document.getElementById("send");

      ws.onopen = () => appendMessage("✅ Connected to server");

      ws.onmessage = (event) => {{
        const data = JSON.parse(event.data);
        if (data.error) {{
          appendMessage(`Error: ${{data.error}}`);
          return;
        }}
        appendMessage(`${{data.username}}: ${{data.text}}`);
      }};

      ws.onclose = () => appendMessage("❌ Disconnected");
      
      ws.onerror = (error) => {{
        console.error("WebSocket error:", error);
        appendMessage("⚠️ Connection error");
      }};

      sendBtn.onclick = () => {{
        if (input.value) {{
          const messageData = {{
            text: input.value
          }};
          ws.send(JSON.stringify(messageData));
          input.value = "";
        }}
      }};

      input.addEventListener("keypress", (e) => {{
        if (e.key === "Enter") sendBtn.click();
      }});

      function appendMessage(msg) {{
        const p = document.createElement("p");
        p.textContent = msg;
        chat.appendChild(p);
        chat.scrollTop = chat.scrollHeight;
      }}
    </script>
  </body>
</html>
"""

    return HTMLResponse(html)


@router.get("/all", response_model=list[ChatSchemaOut])
async def get_all_chats(token: str):
    try:
        user_id = verify_access_token(token=token)
        chats = await get_chats_db(user_id)

        return chats
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=ChatSchemaOut)
async def create_chat(token: str, chat: ChatSchemaIn):
    user_id = verify_access_token(token=token)
    chat = await create_chat_db(user_id=user_id, chat_schema=chat)

    return chat


@router.get("/{chat_id}", response_model=list[MessageSchemaOut])
async def get_chat_history(token: str, chat_id: str) -> list[MessageSchemaOut] | None:
    user_id = verify_access_token(token=token)
    if await is_user_in_chat(user_id=user_id, chat_id=chat_id):
        messages = await get_message_from_chat(chat_id=chat_id)
        return messages
    else:
        raise HTTPException(status_code=404, detail=f"User:{user_id} is not in chat: {chat_id}")    

