from .configs import settings
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from contextlib import asynccontextmanager
from beanie import init_beanie

from shared.models import User, Chat, Message
from shared.tools.redis_manager import redis

MONGO_URI = settings.MONGODB_URI
client = AsyncIOMotorClient(MONGO_URI)
db = client["chatdb"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(database=db, document_models=[User, Chat, Message])
    await redis.connect()
    yield
