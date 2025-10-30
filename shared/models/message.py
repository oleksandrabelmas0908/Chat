from beanie import Document, Link
from datetime import datetime

from .chat import Chat
from .user import User


class Message(Document):
    user: Link[User]
    chat: Link[Chat]
    text: str
    created_at: datetime = datetime.now()

    class Settings:
        name = "messages"
        indexes = ["user", "chat"]