from pydantic import BaseModel
from datetime import datetime


class MessageSchemaIn(BaseModel):
    user: str
    chat: str
    text: str
    created_at: datetime = datetime.now()


class MessageSchemaOut(MessageSchemaIn):
    id: str