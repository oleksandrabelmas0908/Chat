from beanie import Document, Link
from datetime import datetime

from .user import User


class Chat(Document):
    participants: list[Link[User]]
    name: str | None = None
    created_at: datetime = datetime.now()

    class Settings:
        name = "chats"
        indexes = ["participants"]