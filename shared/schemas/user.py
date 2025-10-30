from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime = datetime.now()


class UserLogin(BaseModel):
    email: EmailStr
    password: str