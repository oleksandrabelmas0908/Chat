# chat_service/redis_manager.py
from redis import asyncio
import json

from shared.core.configs import settings

REDIS_URL = settings.REDIS_URI


class RedisPubSub:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if not self.redis: 
            self.redis = await asyncio.from_url(REDIS_URL, decode_responses=True)


    async def publish(self, channel: str, message: dict):
        await self.connect()
        await self.redis.publish(channel, message=json.dumps(message))

    async def subscribe(self, channel: str):
        await self.connect()
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


redis = RedisPubSub()