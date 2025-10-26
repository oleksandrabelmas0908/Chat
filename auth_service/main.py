from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from shared.core.configs import settings
from shared.models.user import User
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(database=client.get_default_database(), document_models=[User])
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)


@app.get("/")
async def say_hello():
    return {"message": "Hello its auth_service"}

