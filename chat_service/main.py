from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import logging


app = FastAPI()


# @app.get("/")
# async def say_hello():
#     return {"message": "Hello its chat_service"}



html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth-service")


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(websocket)
    while True:
        data = await websocket.receive_text()
        logger.info(data)
        await websocket.send_text(f"Message text was: {data}")