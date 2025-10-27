from beanie import Document
from pydantic import ConfigDict, EmailStr
from datetime import datetime


class User(Document):
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)

    class Settings:
        name = "users"  
        indexes = ["email"]