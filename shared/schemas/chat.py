from pydantic import BaseModel
from datetime import datetime


class ChatSchemaIn(BaseModel):
    participants: list[str] = []
    name: str | None = None
    created_at: datetime = datetime.now()


class ChatSchemaOut(ChatSchemaIn):
    id: str
    