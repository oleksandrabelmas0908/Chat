from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os

from shared.core.configs import settings
from shared.models import User, Chat, Message
from routes import router
from shared.core.db import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(database=db, document_models=[User, Chat, Message])
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)


@app.get("/")
async def say_hello():
    return {"message": "Hello its auth_service"}

